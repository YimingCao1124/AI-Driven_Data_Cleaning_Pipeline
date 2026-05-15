"""Manual edit endpoint for individual results."""
from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import ExtractionResult
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
    result.output_json = json.dumps(payload.output, ensure_ascii=False)
    # A manual edit clears any prior failure: the human is the source of truth.
    result.status = "success"
    result.validation_status = "ok"
    result.validation_errors_json = "[]"
    db.commit()
    db.refresh(result)
    return _result_to_response(result)
