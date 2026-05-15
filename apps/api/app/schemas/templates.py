from __future__ import annotations

from datetime import datetime
from typing import Any, List, Literal, Optional

from pydantic import BaseModel, Field

FieldType = Literal["string", "integer", "float", "boolean", "enum", "date"]


class FieldDefinition(BaseModel):
    name: str
    type: FieldType
    description: str = ""
    required: bool = False
    enum_options: Optional[List[str]] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    minimum: Optional[float] = None
    maximum: Optional[float] = None


class FewShotExample(BaseModel):
    input: str
    output: dict[str, Any]


class TemplateResponse(BaseModel):
    id: int
    name: str
    description: str
    extraction_mode: str
    instruction: str
    fields: List[FieldDefinition]
    examples: List[FewShotExample] = Field(default_factory=list)
    is_builtin: bool
    created_at: datetime
    updated_at: datetime
