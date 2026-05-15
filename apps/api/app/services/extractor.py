"""Core extraction orchestrator: prompt -> call LLM -> validate -> retry-on-failure.

A row can end in one of three terminal states:
    success      — model returned a JSON object that passed schema validation.
    failed       — model never produced a valid JSON object after all retries.
    archived     — model declared the input itself as unprocessable (random
                   text, garbled bytes, single char, etc.) by emitting
                   `{"_unprocessable": true, "reason": "..."}`.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .llm_client import BaseLLMClient
from .prompt_builder import build_extraction_prompt
from .validator import build_pydantic_model, validate_output

_FENCED_BLOCK = re.compile(r"```(?:json)?\s*(\{.*\})\s*```", re.DOTALL | re.IGNORECASE)
_FIRST_OBJECT = re.compile(r"\{.*\}", re.DOTALL)


@dataclass
class ExtractionOutcome:
    status: str  # "success" | "failed" | "archived"
    output: Dict[str, Any]
    raw_model_output: str
    validation_status: str
    validation_errors: List[Dict[str, Any]] = field(default_factory=list)
    retry_count: int = 0
    archive_reason: Optional[str] = None

    @property
    def success(self) -> bool:
        return self.status == "success"


def _check_archive_signal(raw: str) -> Optional[str]:
    """If the model emitted `{"_unprocessable": true}`, return its reason string.

    Returns None when the signal is absent. Strips markdown fences first so the
    LLM can produce either fenced or bare JSON.
    """
    text = raw.strip()
    m = _FENCED_BLOCK.search(text)
    if m:
        text = m.group(1)
    else:
        m2 = _FIRST_OBJECT.search(text)
        if m2:
            text = m2.group(0)
    try:
        data = json.loads(text)
    except (json.JSONDecodeError, ValueError):
        return None
    if isinstance(data, dict) and data.get("_unprocessable") is True:
        reason = data.get("reason")
        if not isinstance(reason, str):
            reason = "unprocessable input"
        return reason
    return None


def extract_row(
    input_text: str,
    template: Dict[str, Any],
    llm_client: BaseLLMClient,
    *,
    max_retries: int = 2,
) -> ExtractionOutcome:
    """Run the extraction loop for a single row of input text."""
    model_cls = build_pydantic_model(template.get("fields", []))
    previous_error: Optional[str] = None
    last_raw = ""
    last_errors: List[Dict[str, Any]] = []
    last_status = "ok"

    for attempt in range(max_retries + 1):
        prompt = build_extraction_prompt(template, input_text, previous_error=previous_error)
        raw = llm_client.extract(prompt)
        last_raw = raw

        # Archive short-circuit: the model decided this input is not a record.
        reason = _check_archive_signal(raw)
        if reason is not None:
            return ExtractionOutcome(
                status="archived",
                output={},
                raw_model_output=raw,
                validation_status="archived",
                validation_errors=[],
                retry_count=attempt,
                archive_reason=reason,
            )

        ok, parsed, errors = validate_output(raw, model_cls)
        if ok:
            return ExtractionOutcome(
                status="success",
                output=parsed,
                raw_model_output=raw,
                validation_status="ok",
                validation_errors=[],
                retry_count=attempt,
            )
        last_errors = errors
        last_status = "invalid_json" if any("invalid_json" in str(e.get("msg", "")) for e in errors) else "schema_error"
        previous_error = json.dumps(errors, ensure_ascii=False)

    return ExtractionOutcome(
        status="failed",
        output={},
        raw_model_output=last_raw,
        validation_status=last_status,
        validation_errors=last_errors,
        retry_count=max_retries,
    )
