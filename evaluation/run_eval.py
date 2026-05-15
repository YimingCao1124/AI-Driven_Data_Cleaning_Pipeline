"""Evaluation harness: run the extractor against a labeled dataset and report accuracy.

Usage:
    # MockLLMClient (no API key required):
    python evaluation/run_eval.py --provider mock

    # Real Anthropic Claude Sonnet 4.6 (requires ANTHROPIC_API_KEY):
    python evaluation/run_eval.py --provider anthropic --model claude-sonnet-4-6

    # Limit rows for a quick smoke test:
    python evaluation/run_eval.py --provider anthropic --limit 5

Outputs a per-field accuracy table, a confusion table for `is_work_experience`,
and a list of failing rows with predicted-vs-expected diffs.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "apps" / "api"))

from app.services.builtin_templates import EDUCATION_EXPERIENCE_CLEANER  # noqa: E402
from app.services.extractor import extract_row  # noqa: E402
from app.services.llm_client import get_llm_client  # noqa: E402

FIELDS = ["from", "to", "school", "major", "scholar", "is_work_experience"]
STATUS_FIELD = "status"  # Optional in expected; values: "success" or "archived"


def load_dataset(path: Path) -> List[Dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_value(field: str, value: Any) -> Any:
    """Normalize values so superficial differences don't count as mismatches."""
    if value is None:
        return None
    if field == "is_work_experience":
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() == "true"
        return bool(value)
    if isinstance(value, str):
        v = value.strip()
        if v == "" or v.lower() in {"none", "null", "n/a"}:
            return None
        return v
    return value


def field_match(field: str, predicted: Any, expected: Any) -> bool:
    p = normalize_value(field, predicted)
    e = normalize_value(field, expected)
    if p is None and e is None:
        return True
    if p is None or e is None:
        return False
    if field == "is_work_experience":
        return p == e
    # For string fields, do a forgiving case-insensitive substring match for
    # school/major, since wording varies ("MIT" vs "MIT (Massachusetts Institute…)"),
    # but require exact match for dates and degree.
    if field in {"school", "major"}:
        ps = str(p).lower()
        es = str(e).lower()
        return ps == es or ps in es or es in ps
    return str(p) == str(e)


def evaluate_row(row: Dict[str, Any], llm) -> Tuple[Dict[str, Any], Dict[str, bool], Optional[str], str]:
    """Run extractor on one row.

    Returns (predicted_output, per-field match map, error, predicted_status).
    For archived predictions, predicted_status="archived" and `predicted` is {}.
    """
    expected = row["expected"]
    expected_status = expected.get(STATUS_FIELD, "success")
    try:
        outcome = extract_row(row["input"], EDUCATION_EXPERIENCE_CLEANER, llm, max_retries=1)
    except Exception as e:
        return ({}, {f: False for f in FIELDS}, f"{type(e).__name__}: {e}", "error")

    predicted_status = outcome.status

    if expected_status == "archived":
        # Only the status matters for archive rows. Mark every field True if
        # predicted_status matches; otherwise False across the board.
        ok = (predicted_status == "archived")
        return ({}, {f: ok for f in FIELDS}, None if ok else f"expected archive; got {predicted_status}", predicted_status)

    # Expected "success" — predicted must be success AND fields must match.
    if predicted_status != "success":
        return (
            outcome.output,
            {f: False for f in FIELDS},
            f"expected success; got {predicted_status} ({outcome.archive_reason or outcome.validation_errors})",
            predicted_status,
        )
    predicted = outcome.output
    matches = {f: field_match(f, predicted.get(f), expected.get(f)) for f in FIELDS}
    return predicted, matches, None, predicted_status


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", default="mock", choices=["mock", "anthropic"])
    parser.add_argument("--model", default="claude-sonnet-4-6", help="Used only for anthropic")
    parser.add_argument("--limit", type=int, default=None, help="Run only the first N rows")
    parser.add_argument(
        "--dataset", default=str(Path(__file__).parent / "eval_dataset.json")
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=4,
        help="Parallel API calls (for anthropic; mock ignores)",
    )
    parser.add_argument(
        "--show-failures",
        type=int,
        default=20,
        help="Maximum number of failing rows to print in detail",
    )
    args = parser.parse_args()

    dataset = load_dataset(Path(args.dataset))
    if args.limit:
        dataset = dataset[: args.limit]

    if args.provider == "anthropic" and not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY env var is not set.", file=sys.stderr)
        return 2

    llm_kwargs = {}
    if args.provider == "anthropic":
        llm_kwargs = {"model": args.model, "temperature": 0.0}
    llm = get_llm_client(args.provider, **llm_kwargs)

    print(
        f"Evaluating {len(dataset)} rows against provider={args.provider}"
        + (f" model={args.model}" if args.provider == "anthropic" else "")
    )
    t0 = time.time()

    if args.provider == "anthropic":
        with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
            results = list(pool.map(lambda r: (r, evaluate_row(r, llm)), dataset))
    else:
        results = [(r, evaluate_row(r, llm)) for r in dataset]

    elapsed = time.time() - t0

    field_correct = {f: 0 for f in FIELDS}
    field_total = {f: 0 for f in FIELDS}
    row_correct = 0
    failures: List[Tuple[Dict[str, Any], Dict[str, Any], Dict[str, bool], Optional[str]]] = []
    confusion = {"tp": 0, "fp": 0, "tn": 0, "fn": 0}
    archive_stats = {"expected": 0, "correct": 0}

    for row, (predicted, matches, error, predicted_status) in results:
        expected_status = row["expected"].get(STATUS_FIELD, "success")
        if expected_status == "archived":
            archive_stats["expected"] += 1
            if predicted_status == "archived":
                archive_stats["correct"] += 1

        all_ok = True
        for f in FIELDS:
            field_total[f] += 1
            if matches[f]:
                field_correct[f] += 1
            else:
                all_ok = False
        if all_ok:
            row_correct += 1
        else:
            failures.append((row, predicted, matches, error))

        if not error and expected_status == "success":
            expected_wk = normalize_value("is_work_experience", row["expected"].get("is_work_experience"))
            predicted_wk = normalize_value("is_work_experience", predicted.get("is_work_experience"))
            if expected_wk is True and predicted_wk is True:
                confusion["tp"] += 1
            elif expected_wk is True and predicted_wk is False:
                confusion["fn"] += 1
            elif expected_wk is False and predicted_wk is False:
                confusion["tn"] += 1
            elif expected_wk is False and predicted_wk is True:
                confusion["fp"] += 1

    n = len(dataset)
    print(f"\n=== Aggregate ({elapsed:.1f}s, {len(dataset)/elapsed:.1f} rows/s) ===")
    print(f"Full-row accuracy: {row_correct}/{n}  ({row_correct / n * 100:.1f}%)")
    print("\nPer-field accuracy:")
    for f in FIELDS:
        c = field_correct[f]
        t = field_total[f]
        print(f"  {f:<22} {c}/{t}  ({c / t * 100:.1f}%)")

    print("\nis_work_experience confusion matrix (excluding archive rows):")
    print(f"            pred work   pred edu")
    print(f"  actual work   {confusion['tp']:>3}        {confusion['fn']:>3}")
    print(f"  actual edu    {confusion['fp']:>3}        {confusion['tn']:>3}")

    if archive_stats["expected"]:
        pct = archive_stats["correct"] / archive_stats["expected"] * 100.0
        print(f"\nArchive routing: {archive_stats['correct']}/{archive_stats['expected']} ({pct:.1f}%)")

    if failures:
        print(f"\n=== Failures ({len(failures)}/{n}) ===")
        for i, (row, predicted, matches, error) in enumerate(failures[: args.show_failures]):
            print(f"\n#{row['id']} [{row['category']}]")
            print(f"  input:    {row['input']}")
            if error:
                print(f"  ERROR:    {error}")
                continue
            for f in FIELDS:
                marker = "  " if matches[f] else "!!"
                print(
                    f"  {marker} {f:<22} expected={row['expected'].get(f)!r}  predicted={predicted.get(f)!r}"
                )
        if len(failures) > args.show_failures:
            print(f"\n... and {len(failures) - args.show_failures} more failing rows.")

    return 0 if row_correct == n else 1


if __name__ == "__main__":
    sys.exit(main())
