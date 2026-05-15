"""Exporter tests — verify CSV / XLSX bytes look right after a real job."""
from __future__ import annotations

import io
import time
from pathlib import Path

import pandas as pd


def _run_job_via_api(client, sample_csv_path: Path) -> int:
    with sample_csv_path.open("rb") as f:
        upload = client.post(
            "/api/files/upload", files={"file": ("sample.csv", f, "text/csv")}
        ).json()
    tpls = client.get("/api/templates").json()
    template = next(t for t in tpls if t["name"] == "Education Experience Cleaner")
    job = client.post(
        "/api/jobs",
        json={
            "file_id": upload["file_id"],
            "template_id": template["id"],
            "input_column": "experience",
            "max_rows": 10,
        },
    ).json()
    deadline = time.time() + 15
    while time.time() < deadline:
        info = client.get(f"/api/jobs/{job['id']}").json()
        if info["status"] in {"completed", "failed"}:
            return job["id"]
        time.sleep(0.2)
    raise AssertionError("job did not finish")


def test_export_csv_appends_extracted_columns(client, sample_csv_path: Path) -> None:
    job_id = _run_job_via_api(client, sample_csv_path)

    resp = client.get(f"/api/jobs/{job_id}/export?format=csv")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/csv")

    df = pd.read_csv(io.BytesIO(resp.content))
    # Original columns preserved
    for c in ("id", "name", "experience"):
        assert c in df.columns
    # Extracted columns appended
    for c in ("from", "to", "school", "major", "scholar", "is_work_experience"):
        assert c in df.columns
    assert len(df) == 3


def test_export_xlsx_returns_excel(client, sample_csv_path: Path) -> None:
    job_id = _run_job_via_api(client, sample_csv_path)

    resp = client.get(f"/api/jobs/{job_id}/export?format=xlsx")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    # XLSX is a ZIP archive; magic bytes are PK\x03\x04.
    assert resp.content[:2] == b"PK"

    df = pd.read_excel(io.BytesIO(resp.content), engine="openpyxl")
    assert "school" in df.columns
    assert "is_work_experience" in df.columns
