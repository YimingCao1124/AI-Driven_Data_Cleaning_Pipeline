from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class JobCreateRequest(BaseModel):
    file_id: int
    template_id: int
    input_column: str
    max_rows: int = Field(default=100, ge=1, le=10000)


class JobResponse(BaseModel):
    id: int
    file_id: int
    template_id: int
    input_column: str
    max_rows: int
    status: str
    total_count: int
    processed_count: int
    success_count: int
    failed_count: int
    archived_count: int
    progress_percent: float
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, job) -> "JobResponse":
        pct = (job.processed_count / job.total_count * 100.0) if job.total_count else 0.0
        return cls(
            id=job.id,
            file_id=job.file_id,
            template_id=job.template_id,
            input_column=job.input_column,
            max_rows=job.max_rows,
            status=job.status,
            total_count=job.total_count,
            processed_count=job.processed_count,
            success_count=job.success_count,
            failed_count=job.failed_count,
            archived_count=getattr(job, "archived_count", 0) or 0,
            progress_percent=round(pct, 2),
            created_at=job.created_at,
            updated_at=job.updated_at,
        )
