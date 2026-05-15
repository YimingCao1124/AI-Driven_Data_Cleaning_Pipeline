"""Built-in extraction templates seeded on first startup.

V1 ships exactly one built-in template: the Education Experience Cleaner —
the same shape as the original internship script that this project productizes.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from ..models import ExtractionTemplate


EDUCATION_EXPERIENCE_CLEANER: Dict[str, Any] = {
    "name": "Education Experience Cleaner",
    "description": (
        "Extract structured education- or work-experience records from a single "
        "row of free-form text. Mirrors the fields produced by the original "
        "internship Python script."
    ),
    "extraction_mode": "row-wise",
    "instruction": (
        "You are a data-cleaning expert. From the input text below, extract the "
        "start date, end date, school/company, major or position, degree, and "
        "decide whether the row describes a work experience rather than an "
        "education record. Use null for any field that cannot be determined. "
        "Dates should be normalized to YYYY-MM where possible, or YYYY if only "
        "a year is known. Use the string 'present' for ongoing entries."
    ),
    "fields": [
        {"name": "from", "type": "string", "description": "Start date (YYYY or YYYY-MM)", "required": False},
        {"name": "to", "type": "string", "description": "End date or 'present'", "required": False},
        {"name": "school", "type": "string", "description": "Institution or company name", "required": False},
        {"name": "major", "type": "string", "description": "Field of study or position", "required": False},
        {"name": "scholar", "type": "string", "description": "Degree (Bachelor / Master / PhD)", "required": False},
        {"name": "is_work_experience", "type": "boolean", "description": "True iff a work record", "required": True},
    ],
    "examples": [
        {
            "input": "2018年9月-2022年6月 北京大学 计算机科学与技术 本科",
            "output": {
                "from": "2018-09",
                "to": "2022-06",
                "school": "北京大学",
                "major": "计算机科学与技术",
                "scholar": "Bachelor",
                "is_work_experience": False,
            },
        },
        {
            "input": "June 2018 - present, Google, Senior Software Engineer, search infra team",
            "output": {
                "from": "2018-06",
                "to": "present",
                "school": "Google",
                "major": "Senior Software Engineer",
                "scholar": None,
                "is_work_experience": True,
            },
        },
    ],
}


BUILTIN_TEMPLATES: List[Dict[str, Any]] = [EDUCATION_EXPERIENCE_CLEANER]


def seed_builtin_templates(db: Session) -> None:
    """Insert built-in templates if they are not already present."""
    for tpl in BUILTIN_TEMPLATES:
        existing = db.query(ExtractionTemplate).filter_by(name=tpl["name"]).one_or_none()
        if existing is not None:
            continue
        row = ExtractionTemplate(
            name=tpl["name"],
            description=tpl["description"],
            extraction_mode=tpl["extraction_mode"],
            instruction=tpl["instruction"],
            fields_json=json.dumps(tpl["fields"], ensure_ascii=False),
            examples_json=json.dumps(tpl["examples"], ensure_ascii=False),
            is_builtin=True,
        )
        db.add(row)
    db.commit()
