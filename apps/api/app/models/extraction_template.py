from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..db import Base


class ExtractionTemplate(Base):
    __tablename__ = "extraction_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    extraction_mode: Mapped[str] = mapped_column(String(32), nullable=False, default="row-wise")
    instruction: Mapped[str] = mapped_column(Text, nullable=False, default="")
    fields_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    examples_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    is_builtin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
