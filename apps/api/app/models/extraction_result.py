from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..db import Base


class ExtractionResult(Base):
    __tablename__ = "extraction_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("extraction_jobs.id"), nullable=False, index=True)
    source_row_index: Mapped[int] = mapped_column(Integer, nullable=False)
    input_text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    output_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    raw_model_output: Mapped[str] = mapped_column(Text, nullable=False, default="")
    validation_status: Mapped[str] = mapped_column(String(32), nullable=False, default="ok")
    validation_errors_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="success")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
