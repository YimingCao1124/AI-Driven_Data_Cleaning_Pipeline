"""Manual edit endpoint for individual results."""
from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import ExtractionJob, ExtractionResult
from ..schemas.results import ResultResponse, ResultUpdateRequest
from .jobs import _result_to_response

router = APIRouter(prefix="/api/results", tags=["results"])


@router.patch("/{result_id}", response_model=ResultResponse)
def update_result(
    result_id: int, payload: ResultUpdateRequest, db: Session = Depends(get_db)
) -> ResultResponse:
    result = db.query(ExtractionResult).get(result_id)
    if result is None:
        raise HTTPException(status_code=404, detail="result not found")
    previous_status = result.status
    result.output_json = json.dumps(payload.output, ensure_ascii=False)
    # A manual edit clears any prior failure/archive: the human is the source of truth.
    result.status = "success"
    result.validation_status = "ok"
    result.validation_errors_json = "[]"
    # Keep job-level counters consistent.
    if previous_status != "success":
        job = db.query(ExtractionJob).get(result.job_id)
        if job is not None:
            job.success_count += 1
            if previous_status == "failed":
                job.failed_count = max(0, job.failed_count - 1)
            elif previous_status == "archived":
                job.archived_count = max(0, job.archived_count - 1)
    db.commit()
    db.refresh(result)
    return _result_to_response(result)
