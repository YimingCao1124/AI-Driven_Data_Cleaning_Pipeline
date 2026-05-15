from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from pydantic import BaseModel


class FileUploadResponse(BaseModel):
    file_id: int
    filename: str
    file_type: str
    headers: List[str]
    preview_rows: List[Dict[str, Any]]
    total_rows: int
    created_at: datetime


class TextUploadRequest(BaseModel):
    title: str
    text: str
