"""Tests for the `archived` extraction path (LLM-declared unprocessable rows)."""
from __future__ import annotations

import json
import time
from pathlib import Path


def test_extractor_recognizes_unprocessable_signal(education_template, app_module) -> None:
    """If the LLM returns `_unprocessable`, the outcome should be archived."""
    from app.services.extractor import extract_row
    from app.services.llm_client import BaseLLMClient

    class _Stub(BaseLLMClient):
        name = "stub"

        def extract(self, prompt: str) -> str:
            return json.dumps({"_unprocessable": True, "reason": "just noise"})

    outcome = extract_row("???", education_template, _Stub(), max_retries=0)
    assert outcome.status == "archived"
    assert outcome.archive_reason == "just noise"
    assert outcome.output == {}


def test_extractor_accepts_unprocessable_inside_code_fence(education_template, app_module) -> None:
    from app.services.extractor import extract_row
    from app.services.llm_client import BaseLLMClient

    class _Stub(BaseLLMClient):
        name = "stub"

        def extract(self, prompt: str) -> str:
            return "```json\n{\"_unprocessable\": true, \"reason\": \"garbled\"}\n```"

    outcome = extract_row("???", education_template, _Stub(), max_retries=0)
    assert outcome.status == "archived"


def test_mock_archives_empty_and_garbage_inputs(education_template, app_module) -> None:
    """MockLLMClient should route obviously-bad inputs to archive."""
    from app.services.extractor import extract_row
    from app.services.llm_client import MockLLMClient

    client = MockLLMClient()
    for garbage in ("", "   ", "?", "123", "...", "啊"):
        outcome = extract_row(garbage, education_template, client, max_retries=0)
        assert outcome.status == "archived", f"expected archived for {garbage!r}"
        assert outcome.archive_reason


def test_mock_still_processes_messy_but_valid_input(education_template, app_module) -> None:
    """A messy resume-like row should not be archived."""
    from app.services.extractor import extract_row
    from app.services.llm_client import MockLLMClient

    outcome = extract_row(
        "2018年9月-2022年6月 北京大学 计算机科学与技术 本科",
        education_template,
        MockLLMClient(),
        max_retries=0,
    )
    assert outcome.status == "success"
    assert outcome.output["school"] == "北京大学"


def test_job_runner_counts_archived_rows(client, tmp_path: Path) -> None:
    """End-to-end: a CSV with some garbage rows produces archived results
    and the job-level archived_count matches."""
    csv = tmp_path / "mixed.csv"
    csv.write_text(
        "id,experience\n"
        "1,2018年9月-2022年6月 北京大学 计算机科学 本科\n"
        "2,???\n"
        "3,June 2018 - present Google Senior SWE\n"
        "4,   \n"
        "5,今天天气真好\n",
        encoding="utf-8",
    )

    with csv.open("rb") as f:
        upload = client.post(
            "/api/files/upload", files={"file": ("mixed.csv", f, "text/csv")}
        ).json()
    template = next(
        t for t in client.get("/api/templates").json()
        if t["name"] == "Education Experience Cleaner"
    )
    job = client.post(
        "/api/jobs",
        json={
            "file_id": upload["file_id"],
            "template_id": template["id"],
            "input_column": "experience",
            "max_rows": 10,
        },
    ).json()

    deadline = time.time() + 20
    while time.time() < deadline:
        info = client.get(f"/api/jobs/{job['id']}").json()
        if info["status"] in {"completed", "failed"}:
            break
        time.sleep(0.2)

    info = client.get(f"/api/jobs/{job['id']}").json()
    assert info["status"] == "completed"
    assert info["success_count"] >= 2
    # Mock heuristic should archive at least the "???" and "   " rows.
    assert info["archived_count"] >= 2
    assert info["success_count"] + info["failed_count"] + info["archived_count"] == info["processed_count"]


def test_filter_archived_results(client, tmp_path: Path) -> None:
    csv = tmp_path / "g.csv"
    csv.write_text("id,exp\n1,???\n2,2018年 北京大学 本科\n", encoding="utf-8")
    with csv.open("rb") as f:
        upload = client.post(
            "/api/files/upload", files={"file": ("g.csv", f, "text/csv")}
        ).json()
    template = next(
        t for t in client.get("/api/templates").json()
        if t["name"] == "Education Experience Cleaner"
    )
    job = client.post(
        "/api/jobs",
        json={
            "file_id": upload["file_id"],
            "template_id": template["id"],
            "input_column": "exp",
            "max_rows": 10,
        },
    ).json()

    deadline = time.time() + 10
    while time.time() < deadline:
        if client.get(f"/api/jobs/{job['id']}").json()["status"] in {"completed", "failed"}:
            break
        time.sleep(0.2)

    archived = client.get(f"/api/jobs/{job['id']}/results?status=archived").json()
    assert len(archived) == 1
    assert archived[0]["status"] == "archived"
    assert archived[0]["validation_errors"][0]["msg"]  # reason text present


def test_manual_edit_promotes_archived_to_success(client, tmp_path: Path) -> None:
    csv = tmp_path / "h.csv"
    csv.write_text("id,exp\n1,???\n", encoding="utf-8")
    with csv.open("rb") as f:
        upload = client.post(
            "/api/files/upload", files={"file": ("h.csv", f, "text/csv")}
        ).json()
    template = next(
        t for t in client.get("/api/templates").json()
        if t["name"] == "Education Experience Cleaner"
    )
    job = client.post(
        "/api/jobs",
        json={
            "file_id": upload["file_id"],
            "template_id": template["id"],
            "input_column": "exp",
            "max_rows": 10,
        },
    ).json()
    deadline = time.time() + 10
    while time.time() < deadline:
        if client.get(f"/api/jobs/{job['id']}").json()["status"] in {"completed", "failed"}:
            break
        time.sleep(0.2)

    info_before = client.get(f"/api/jobs/{job['id']}").json()
    assert info_before["archived_count"] == 1
    archived = client.get(f"/api/jobs/{job['id']}/results?status=archived").json()
    rid = archived[0]["id"]
    patched = client.patch(
        f"/api/results/{rid}",
        json={"output": {"school": "Manual", "is_work_experience": False}},
    ).json()
    assert patched["status"] == "success"

    info_after = client.get(f"/api/jobs/{job['id']}").json()
    assert info_after["archived_count"] == 0
    assert info_after["success_count"] == info_before["success_count"] + 1
