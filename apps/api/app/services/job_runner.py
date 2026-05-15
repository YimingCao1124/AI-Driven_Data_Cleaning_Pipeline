"""Background-thread job runner.

The runner is intentionally simple in V1: it spawns a daemon thread per job,
processes the file row-by-row using a thread-pool executor for concurrency,
and writes progress + results back to SQLite.

V6 will replace this module with a proper Celery/Redis worker.
"""
from __future__ import annotations

import json
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from ..config import settings
from ..db import SessionLocal
from ..models import ExtractionJob, ExtractionResult, ExtractionTemplate, UploadedFile
from .excel_parser import parse_table
from .extractor import ExtractionOutcome, extract_row
from .llm_client import get_llm_client

log = logging.getLogger(__name__)


def _load_template(db: Session, template_id: int) -> Dict[str, Any]:
    tpl = db.query(ExtractionTemplate).get(template_id)
    if tpl is None:
        raise ValueError(f"template {template_id} not found")
    return {
        "name": tpl.name,
        "description": tpl.description,
        "extraction_mode": tpl.extraction_mode,
        "instruction": tpl.instruction,
        "fields": json.loads(tpl.fields_json),
        "examples": json.loads(tpl.examples_json),
    }


def _persist_result(
    db: Session,
    job: ExtractionJob,
    row_index: int,
    input_text: str,
    outcome: ExtractionOutcome,
    *,
    existing: Optional[ExtractionResult] = None,
) -> ExtractionResult:
    if existing is None:
        result = ExtractionResult(
            job_id=job.id,
            source_row_index=row_index,
            input_text=input_text,
            output_json=json.dumps(outcome.output, ensure_ascii=False),
            raw_model_output=outcome.raw_model_output,
            validation_status=outcome.validation_status,
            validation_errors_json=json.dumps(outcome.validation_errors, ensure_ascii=False),
            retry_count=outcome.retry_count,
            status="success" if outcome.success else "failed",
        )
        db.add(result)
    else:
        result = existing
        result.input_text = input_text
        result.output_json = json.dumps(outcome.output, ensure_ascii=False)
        result.raw_model_output = outcome.raw_model_output
        result.validation_status = outcome.validation_status
        result.validation_errors_json = json.dumps(outcome.validation_errors, ensure_ascii=False)
        result.retry_count = outcome.retry_count
        result.status = "success" if outcome.success else "failed"
    return result


def _process_rows(
    db: Session,
    job: ExtractionJob,
    file: UploadedFile,
    template: Dict[str, Any],
    rows: List[Dict[str, Any]],
    input_column: str,
) -> None:
    llm = get_llm_client(settings.model_provider)

    def _work(item):
        idx, row = item
        text = str(row.get(input_column, "") or "")
        outcome = extract_row(text, template, llm, max_retries=settings.max_retries)
        return idx, text, outcome

    with ThreadPoolExecutor(max_workers=max(1, settings.max_concurrency)) as pool:
        for idx, text, outcome in pool.map(_work, enumerate(rows)):
            _persist_result(db, job, idx, text, outcome)
            job.processed_count += 1
            if outcome.success:
                job.success_count += 1
            else:
                job.failed_count += 1
            # Commit per-row so the frontend polling sees progress.
            db.commit()


def run_job(job_id: int) -> None:
    """Top-level entry for a job thread."""
    db: Session = SessionLocal()
    try:
        job = db.query(ExtractionJob).get(job_id)
        if job is None:
            log.error("Job %s missing from DB", job_id)
            return
        file = db.query(UploadedFile).get(job.file_id)
        if file is None:
            job.status = "failed"
            db.commit()
            return

        template = _load_template(db, job.template_id)

        parsed = parse_table(Path(file.original_path), file.file_type)
        rows = parsed["rows"][: job.max_rows]

        job.status = "running"
        job.total_count = len(rows)
        job.processed_count = 0
        job.success_count = 0
        job.failed_count = 0
        db.commit()

        _process_rows(db, job, file, template, rows, job.input_column)

        job.status = "completed"
        db.commit()
    except Exception:  # pragma: no cover - last-resort safety
        log.exception("job %s crashed", job_id)
        try:
            job = db.query(ExtractionJob).get(job_id)
            if job is not None:
                job.status = "failed"
                db.commit()
        except Exception:
            db.rollback()
    finally:
        db.close()


def run_job_in_thread(job_id: int) -> threading.Thread:
    t = threading.Thread(target=run_job, args=(job_id,), daemon=True, name=f"job-{job_id}")
    t.start()
    return t


def retry_failed(job_id: int) -> threading.Thread:
    """Re-run only the failed results of a job."""

    def _runner() -> None:
        db: Session = SessionLocal()
        try:
            job = db.query(ExtractionJob).get(job_id)
            if job is None:
                return
            file = db.query(UploadedFile).get(job.file_id)
            if file is None:
                return
            template = _load_template(db, job.template_id)
            llm = get_llm_client(settings.model_provider)

            failed = (
                db.query(ExtractionResult)
                .filter(ExtractionResult.job_id == job_id, ExtractionResult.status == "failed")
                .all()
            )
            if not failed:
                return

            job.status = "running"
            db.commit()

            parsed = parse_table(Path(file.original_path), file.file_type)
            rows = parsed["rows"]

            for result in failed:
                idx = result.source_row_index
                if idx < 0 or idx >= len(rows):
                    continue
                text = str(rows[idx].get(job.input_column, "") or "")
                outcome = extract_row(text, template, llm, max_retries=settings.max_retries)
                before_status = result.status
                _persist_result(db, job, idx, text, outcome, existing=result)
                if outcome.success and before_status == "failed":
                    job.success_count += 1
                    job.failed_count = max(0, job.failed_count - 1)
                db.commit()

            job.status = "completed"
            db.commit()
        except Exception:  # pragma: no cover
            log.exception("retry-failed job %s crashed", job_id)
        finally:
            db.close()

    t = threading.Thread(target=_runner, daemon=True, name=f"job-{job_id}-retry")
    t.start()
    return t
