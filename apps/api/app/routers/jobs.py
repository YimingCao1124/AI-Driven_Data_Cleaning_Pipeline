"""Job lifecycle endpoints."""
from __future__ import annotations

import json
from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import ExtractionJob, ExtractionResult, ExtractionTemplate, UploadedFile
from ..schemas.jobs import JobCreateRequest, JobResponse
from ..schemas.results import ResultResponse
from ..services.job_runner import retry_failed, run_job_in_thread

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


def _result_to_response(r: ExtractionResult) -> ResultResponse:
    try:
        output = json.loads(r.output_json) if r.output_json else {}
    except json.JSONDecodeError:
        output = {}
    try:
        errors = json.loads(r.validation_errors_json) if r.validation_errors_json else []
    except json.JSONDecodeError:
        errors = []
    return ResultResponse(
        id=r.id,
        job_id=r.job_id,
        source_row_index=r.source_row_index,
        input_text=r.input_text,
        output=output,
        raw_model_output=r.raw_model_output,
        validation_status=r.validation_status,
        validation_errors=errors,
        retry_count=r.retry_count,
        status=r.status,
        created_at=r.created_at,
        updated_at=r.updated_at,
    )


@router.post("", response_model=JobResponse, status_code=201)
def create_job(payload: JobCreateRequest, db: Session = Depends(get_db)) -> JobResponse:
    file = db.query(UploadedFile).get(payload.file_id)
    if file is None:
        raise HTTPException(status_code=404, detail="file not found")
    template = db.query(ExtractionTemplate).get(payload.template_id)
    if template is None:
        raise HTTPException(status_code=404, detail="template not found")

    headers = json.loads(file.headers_json)
    if payload.input_column not in headers:
        raise HTTPException(
            status_code=400,
            detail=f"input_column '{payload.input_column}' is not a header of file {file.id}. "
                   f"Available: {headers}",
        )

    job = ExtractionJob(
        file_id=payload.file_id,
        template_id=payload.template_id,
        input_column=payload.input_column,
        max_rows=payload.max_rows,
        status="pending",
        total_count=min(payload.max_rows, file.total_rows),
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    run_job_in_thread(job.id)
    return JobResponse.from_model(job)


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)) -> JobResponse:
    job = db.query(ExtractionJob).get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    return JobResponse.from_model(job)


@router.post("/{job_id}/retry-failed", response_model=JobResponse)
def retry_failed_endpoint(job_id: int, db: Session = Depends(get_db)) -> JobResponse:
    job = db.query(ExtractionJob).get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    retry_failed(job_id)
    return JobResponse.from_model(job)


@router.get("/{job_id}/results", response_model=List[ResultResponse])
def get_results(
    job_id: int,
    status_filter: Literal["all", "success", "failed"] = Query(default="all", alias="status"),
    limit: int = Query(default=500, ge=1, le=10000),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> List[ResultResponse]:
    job = db.query(ExtractionJob).get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    q = db.query(ExtractionResult).filter(ExtractionResult.job_id == job_id)
    if status_filter != "all":
        q = q.filter(ExtractionResult.status == status_filter)
    rows = (
        q.order_by(ExtractionResult.source_row_index.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [_result_to_response(r) for r in rows]
