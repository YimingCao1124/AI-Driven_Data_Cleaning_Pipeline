"""Export endpoint: returns a CSV or XLSX merging original rows + extracted fields."""
from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import ExtractionJob, ExtractionResult, ExtractionTemplate, UploadedFile
from ..services.exporter import export_results

router = APIRouter(prefix="/api/jobs", tags=["export"])


@router.get("/{job_id}/export")
def export_job(
    job_id: int,
    fmt: Literal["csv", "xlsx"] = Query(default="csv", alias="format"),
    db: Session = Depends(get_db),
) -> Response:
    job = db.query(ExtractionJob).get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    file = db.query(UploadedFile).get(job.file_id)
    template = db.query(ExtractionTemplate).get(job.template_id)
    if file is None or template is None:
        raise HTTPException(status_code=404, detail="associated file or template missing")

    results = db.query(ExtractionResult).filter(ExtractionResult.job_id == job_id).all()
    payload = export_results(file, template, job, results, fmt=fmt)

    if fmt == "csv":
        media = "text/csv; charset=utf-8"
        filename = f"job_{job_id}.csv"
    else:
        media = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        filename = f"job_{job_id}.xlsx"

    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return Response(content=payload, media_type=media, headers=headers)
