"""Compose the structured prompt fed to the LLM client."""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional


def _serialize_fields(fields: List[Dict[str, Any]]) -> str:
    return json.dumps(fields, ensure_ascii=False, indent=2)


def _serialize_examples(examples: List[Dict[str, Any]]) -> str:
    if not examples:
        return ""
    parts: List[str] = []
    for i, ex in enumerate(examples, 1):
        parts.append(f"Example {i}:")
        parts.append(f"  Input: {ex.get('input', '')}")
        parts.append(
            "  Output: " + json.dumps(ex.get("output", {}), ensure_ascii=False)
        )
    return "\n".join(parts)


def build_extraction_prompt(
    template: Dict[str, Any],
    input_text: str,
    *,
    previous_error: Optional[str] = None,
) -> str:
    """Render the full prompt string for a single row-wise extraction call.

    The prompt is deterministic so that the MockLLMClient can rely on its
    structure for keyword matching, and so that tests can pin its output.
    """
    instruction = template.get("instruction", "").strip()
    fields = template.get("fields", [])
    examples = template.get("examples", [])

    lines: List[str] = []
    lines.append("You are an expert data-cleaning assistant.")
    if instruction:
        lines.append(instruction)
    lines.append("")
    lines.append("Field schema (extract exactly these fields):")
    lines.append(_serialize_fields(fields))
    lines.append("")
    ex_block = _serialize_examples(examples)
    if ex_block:
        lines.append(ex_block)
        lines.append("")
    if previous_error:
        lines.append("Your previous response had this problem:")
        lines.append(previous_error)
        lines.append("Please correct the issue and respond again.")
        lines.append("")
    lines.append("Input text:")
    lines.append(input_text)
    lines.append("")
    lines.append(
        "Respond with ONE JSON object containing the fields above. "
        "Do not include markdown code fences, prose, or any text outside the JSON object."
    )
    return "\n".join(lines)
