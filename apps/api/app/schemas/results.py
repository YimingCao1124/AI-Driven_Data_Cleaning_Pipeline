from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from pydantic import BaseModel


class ResultResponse(BaseModel):
    id: int
    job_id: int
    source_row_index: int
    input_text: str
    output: Dict[str, Any]
    raw_model_output: str
    validation_status: str
    validation_errors: List[Dict[str, Any]]
    retry_count: int
    status: str
    created_at: datetime
    updated_at: datetime


class ResultUpdateRequest(BaseModel):
    output: Dict[str, Any]
