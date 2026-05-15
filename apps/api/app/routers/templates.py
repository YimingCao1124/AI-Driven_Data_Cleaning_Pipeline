"""Template list + detail endpoints (read-only in V1)."""
from __future__ import annotations

import json
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import ExtractionTemplate
from ..schemas.templates import FewShotExample, FieldDefinition, TemplateResponse

router = APIRouter(prefix="/api/templates", tags=["templates"])


def _to_response(tpl: ExtractionTemplate) -> TemplateResponse:
    return TemplateResponse(
        id=tpl.id,
        name=tpl.name,
        description=tpl.description,
        extraction_mode=tpl.extraction_mode,
        instruction=tpl.instruction,
        fields=[FieldDefinition(**f) for f in json.loads(tpl.fields_json)],
        examples=[FewShotExample(**e) for e in json.loads(tpl.examples_json)],
        is_builtin=tpl.is_builtin,
        created_at=tpl.created_at,
        updated_at=tpl.updated_at,
    )


@router.get("", response_model=List[TemplateResponse])
def list_templates(db: Session = Depends(get_db)) -> List[TemplateResponse]:
    rows = db.query(ExtractionTemplate).order_by(ExtractionTemplate.id.asc()).all()
    return [_to_response(t) for t in rows]


@router.get("/{template_id}", response_model=TemplateResponse)
def get_template(template_id: int, db: Session = Depends(get_db)) -> TemplateResponse:
    tpl = db.query(ExtractionTemplate).get(template_id)
    if tpl is None:
        raise HTTPException(status_code=404, detail="template not found")
    return _to_response(tpl)
