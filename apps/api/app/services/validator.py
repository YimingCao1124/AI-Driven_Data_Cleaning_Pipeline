"""Dynamic Pydantic validator built from a template's field schema."""
from __future__ import annotations

import json
import re
from datetime import date
from typing import Any, Dict, List, Optional, Tuple, Type

from pydantic import BaseModel, ConfigDict, Field, ValidationError, create_model


_TYPE_MAP: Dict[str, type] = {
    "string": str,
    "integer": int,
    "float": float,
    "boolean": bool,
    "date": date,
    "enum": str,
}


def build_pydantic_model(fields: List[Dict[str, Any]], model_name: str = "ExtractedRecord") -> Type[BaseModel]:
    """Construct a Pydantic model class from a template's field definitions."""
    field_kwargs: Dict[str, Any] = {}
    for f in fields:
        py_type = _TYPE_MAP.get(f["type"], str)
        if not f.get("required", False):
            py_type = Optional[py_type]  # type: ignore[assignment]
            default: Any = None
        else:
            default = ...
        constraints: Dict[str, Any] = {"description": f.get("description", "")}
        if f.get("min_length") is not None:
            constraints["min_length"] = f["min_length"]
        if f.get("max_length") is not None:
            constraints["max_length"] = f["max_length"]
        if f.get("minimum") is not None:
            constraints["ge"] = f["minimum"]
        if f.get("maximum") is not None:
            constraints["le"] = f["maximum"]
        field_kwargs[f["name"]] = (py_type, Field(default, **constraints))

    model = create_model(model_name, __config__=ConfigDict(extra="ignore"), **field_kwargs)

    # Enum validation is handled with a post-validator hook because Pydantic
    # `create_model` doesn't accept Literal types built from a list cleanly.
    enum_fields = {f["name"]: f.get("enum_options") for f in fields if f["type"] == "enum" and f.get("enum_options")}
    if enum_fields:
        original_validate = model.model_validate

        def _validate(data: Dict[str, Any]) -> BaseModel:  # type: ignore[override]
            errors: List[Dict[str, Any]] = []
            for name, opts in enum_fields.items():
                v = data.get(name)
                if v is not None and v not in opts:
                    errors.append({"loc": [name], "msg": f"value '{v}' not in allowed options {opts}"})
            if errors:
                raise EnumValidationError(errors)
            return original_validate(data)

        model.model_validate = _validate  # type: ignore[method-assign]

    return model


class EnumValidationError(Exception):
    def __init__(self, errors: List[Dict[str, Any]]) -> None:
        super().__init__("enum validation failed")
        self.errors = errors


_FENCED_BLOCK = re.compile(r"```(?:json)?\s*(\{.*\})\s*```", re.DOTALL | re.IGNORECASE)
_FIRST_OBJECT = re.compile(r"\{.*\}", re.DOTALL)


def _strip_to_json(raw: str) -> str:
    raw = raw.strip()
    m = _FENCED_BLOCK.search(raw)
    if m:
        return m.group(1)
    m = _FIRST_OBJECT.search(raw)
    if m:
        return m.group(0)
    return raw


def validate_output(
    raw: str, model_cls: Type[BaseModel]
) -> Tuple[bool, Dict[str, Any], List[Dict[str, Any]]]:
    """Parse and validate `raw` against `model_cls`.

    Returns `(ok, parsed_dict, errors)`. `errors` is `[]` on success.
    """
    cleaned = _strip_to_json(raw)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        return False, {}, [{"loc": [], "msg": f"invalid_json: {e.msg} (pos {e.pos})"}]
    if not isinstance(data, dict):
        return False, {}, [{"loc": [], "msg": "expected a JSON object"}]
    try:
        instance = model_cls.model_validate(data)
    except EnumValidationError as e:
        return False, {}, e.errors
    except ValidationError as e:
        errors = [
            {"loc": list(err.get("loc", ())), "msg": err.get("msg", "")} for err in e.errors()
        ]
        return False, {}, errors
    return True, instance.model_dump(mode="json"), []
