"""Export job results to CSV or XLSX with original columns + extracted fields.

A `_status` column is always appended so a downstream consumer can tell
success / failed / archived rows apart. For XLSX a second sheet `archived`
holds just the archived rows with their LLM-provided reason — to make the
"unprocessable bucket" easy to hand off for human review.
"""
from __future__ import annotations

import io
import json
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from ..models import ExtractionJob, ExtractionResult, ExtractionTemplate, UploadedFile


def _field_names(template: ExtractionTemplate) -> List[str]:
    fields = json.loads(template.fields_json)
    return [f["name"] for f in fields]


def _row_index_to_result(results: List[ExtractionResult]) -> Dict[int, ExtractionResult]:
    out: Dict[int, ExtractionResult] = {}
    for r in results:
        # If the same row was retried, keep the most recent record.
        prev = out.get(r.source_row_index)
        if prev is None or r.updated_at >= prev.updated_at:
            out[r.source_row_index] = r
    return out


def _build_main_dataframe(
    file: UploadedFile,
    template: ExtractionTemplate,
    results: List[ExtractionResult],
) -> pd.DataFrame:
    from .excel_parser import parse_table  # local import to avoid cycle at import-time

    parsed = parse_table(Path(file.original_path), file.file_type)
    rows = parsed["rows"]
    headers = parsed["headers"]

    field_names = _field_names(template)
    indexed = _row_index_to_result(results)

    df = pd.DataFrame(rows, columns=headers)
    for fname in field_names:
        df[fname] = ""
    df["_status"] = ""

    for idx, result in indexed.items():
        if idx < 0 or idx >= len(df):
            continue
        df.at[idx, "_status"] = result.status
        if result.status != "success":
            continue
        try:
            out = json.loads(result.output_json)
        except json.JSONDecodeError:
            out = {}
        for fname in field_names:
            v = out.get(fname)
            if v is None:
                df.at[idx, fname] = ""
            elif isinstance(v, bool):
                df.at[idx, fname] = "true" if v else "false"
            else:
                df.at[idx, fname] = v
    return df


def _build_archived_dataframe(
    file: UploadedFile,
    results: List[ExtractionResult],
) -> pd.DataFrame:
    """One row per archived result — original input plus the LLM's reason."""
    indexed = _row_index_to_result(results)
    rows: List[Dict[str, Any]] = []
    for idx in sorted(indexed):
        r = indexed[idx]
        if r.status != "archived":
            continue
        try:
            errors = json.loads(r.validation_errors_json)
        except json.JSONDecodeError:
            errors = []
        reason = ""
        if errors and isinstance(errors[0], dict):
            reason = errors[0].get("msg") or ""
        rows.append({
            "source_row_index": idx,
            "input_text": r.input_text,
            "reason": reason,
        })
    return pd.DataFrame(rows, columns=["source_row_index", "input_text", "reason"])


def export_results(
    file: UploadedFile,
    template: ExtractionTemplate,
    job: ExtractionJob,
    results: List[ExtractionResult],
    *,
    fmt: str,
) -> bytes:
    main_df = _build_main_dataframe(file, template, results)
    archived_df = _build_archived_dataframe(file, results)
    fmt = fmt.lower()
    if fmt == "csv":
        # CSV is single-sheet; archived rows still appear in main_df with
        # `_status=archived`, and downstream tools can filter on that column.
        # utf-8-sig so Excel on Windows handles CJK correctly.
        text = main_df.to_csv(index=False)
        return text.encode("utf-8-sig")
    if fmt == "xlsx":
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            main_df.to_excel(writer, index=False, sheet_name=f"job_{job.id}")
            if not archived_df.empty:
                archived_df.to_excel(writer, index=False, sheet_name="archived")
        return buf.getvalue()
    raise ValueError(f"Unsupported export format: {fmt}")
