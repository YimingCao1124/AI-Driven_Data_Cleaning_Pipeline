"""File upload endpoint."""
from __future__ import annotations

import json
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from ..config import settings
from ..db import get_db
from ..models import UploadedFile
from ..schemas.files import FileUploadResponse
from ..services.excel_parser import parse_table
from ..utils.paths import is_within

router = APIRouter(prefix="/api/files", tags=["files"])


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)) -> FileUploadResponse:
    if file.filename is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing filename")

    ext = Path(file.filename).suffix.lower()
    if ext not in settings.allowed_upload_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(settings.allowed_upload_extensions)}.",
        )

    settings.ensure_dirs()
    safe_name = f"{uuid.uuid4().hex}__{Path(file.filename).name}"
    dest = (settings.upload_path / safe_name).resolve()
    if not is_within(dest, settings.upload_path):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid upload path")

    data = await file.read()
    if len(data) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds {settings.max_upload_bytes // (1024 * 1024)} MB limit",
        )
    dest.write_bytes(data)

    try:
        parsed = parse_table(dest, ext.lstrip("."))
    except Exception as e:
        dest.unlink(missing_ok=True)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to parse file: {e}") from e

    record = UploadedFile(
        filename=Path(file.filename).name,
        file_type=ext.lstrip("."),
        original_path=str(dest),
        headers_json=json.dumps(parsed["headers"], ensure_ascii=False),
        preview_rows_json=json.dumps(parsed["preview_rows"], ensure_ascii=False),
        total_rows=parsed["total_rows"],
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return FileUploadResponse(
        file_id=record.id,
        filename=record.filename,
        file_type=record.file_type,
        headers=parsed["headers"],
        preview_rows=parsed["preview_rows"],
        total_rows=parsed["total_rows"],
        created_at=record.created_at,
    )


@router.get("/{file_id}", response_model=FileUploadResponse)
def get_file(file_id: int, db: Session = Depends(get_db)) -> FileUploadResponse:
    record = db.query(UploadedFile).get(file_id)
    if record is None:
        raise HTTPException(status_code=404, detail="file not found")
    return FileUploadResponse(
        file_id=record.id,
        filename=record.filename,
        file_type=record.file_type,
        headers=json.loads(record.headers_json),
        preview_rows=json.loads(record.preview_rows_json),
        total_rows=record.total_rows,
        created_at=record.created_at,
    )
