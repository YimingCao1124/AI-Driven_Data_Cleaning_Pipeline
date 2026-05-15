"""Core extraction orchestrator: prompt → call LLM → validate → retry-on-failure."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .llm_client import BaseLLMClient
from .prompt_builder import build_extraction_prompt
from .validator import build_pydantic_model, validate_output


@dataclass
class ExtractionOutcome:
    success: bool
    output: Dict[str, Any]
    raw_model_output: str
    validation_status: str
    validation_errors: List[Dict[str, Any]] = field(default_factory=list)
    retry_count: int = 0


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
        ok, parsed, errors = validate_output(raw, model_cls)
        if ok:
            return ExtractionOutcome(
                success=True,
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
        success=False,
        output={},
        raw_model_output=last_raw,
        validation_status=last_status,
        validation_errors=last_errors,
        retry_count=max_retries,
    )
