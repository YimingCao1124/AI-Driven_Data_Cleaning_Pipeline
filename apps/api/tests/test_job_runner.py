"""End-to-end: upload a CSV via the API → create a job → poll until done."""
from __future__ import annotations

import time
from pathlib import Path


def _wait_for_job(client, job_id: int, timeout: float = 15.0) -> dict:
    deadline = time.time() + timeout
    while time.time() < deadline:
        resp = client.get(f"/api/jobs/{job_id}")
        assert resp.status_code == 200
        data = resp.json()
        if data["status"] in {"completed", "failed"}:
            return data
        time.sleep(0.2)
    raise AssertionError(f"job {job_id} did not finish within {timeout}s")


def test_end_to_end_extraction(client, sample_csv_path: Path) -> None:
    # 1. Upload the CSV
    with sample_csv_path.open("rb") as f:
        upload_resp = client.post(
            "/api/files/upload",
            files={"file": ("sample.csv", f, "text/csv")},
        )
    assert upload_resp.status_code == 200, upload_resp.text
    upload = upload_resp.json()
    assert upload["total_rows"] == 3
    assert "experience" in upload["headers"]

    # 2. Get the seeded template
    tpls = client.get("/api/templates").json()
    assert tpls
    template = next(t for t in tpls if t["name"] == "Education Experience Cleaner")

    # 3. Create a job
    job_resp = client.post(
        "/api/jobs",
        json={
            "file_id": upload["file_id"],
            "template_id": template["id"],
            "input_column": "experience",
            "max_rows": 10,
        },
    )
    assert job_resp.status_code == 201, job_resp.text
    job = job_resp.json()

    # 4. Poll until done
    done = _wait_for_job(client, job["id"])
    assert done["status"] == "completed"
    assert done["processed_count"] == 3
    assert done["success_count"] >= 2  # mock LLM is heuristic; tolerate one miss

    # 5. Fetch results
    results = client.get(f"/api/jobs/{job['id']}/results").json()
    assert len(results) == 3
    # The first row's school should be 北京大学.
    by_index = {r["source_row_index"]: r for r in results}
    assert by_index[0]["output"].get("school") == "北京大学"
