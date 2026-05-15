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
        "You are a data-cleaning expert. The input is one row of free-form text "
        "that SHOULD describe either a single education record or a single work "
        "record. Extract the fields defined below and return ONE JSON object.\n"
        "\n"
        "Rules:\n"
        "0. ARCHIVING — if the input is empty, garbled, a single character, "
        "pure punctuation, sensor data, an error message, or otherwise clearly "
        "not an education/work record ('today is a nice day', 'hello world', "
        "'???', '123', '今天天气真好', binary noise, etc.), DO NOT try to "
        "extract fields. Instead return EXACTLY:\n"
        "    {\"_unprocessable\": true, \"reason\": \"<one short reason>\"}\n"
        "This signals the row should be archived for human review rather than "
        "filed as a failed extraction. Use this sparingly — only when the input "
        "is genuinely not a record. A messy but plausibly resume-like row "
        "should still be processed normally with nulls for unknown fields.\n"
        "1. If a field cannot be determined from an otherwise valid record, "
        "set it to null. Never invent a value.\n"
        "2. Normalize dates to YYYY-MM when month is given (e.g. '2018年9月' -> "
        "'2018-09', 'Sept 2017' -> '2017-09'). Use YYYY if only a year is known. "
        "Use the literal string 'present' for ongoing entries "
        "(至今, now, present, current, …).\n"
        "3. Date inference for single-date inputs:\n"
        "   a. If only ONE date is given alongside a completion verb (毕业, "
        "graduated, awarded, earned, completed, received), set it as `to` and "
        "leave `from`=null.\n"
        "   b. If only ONE date is given alongside a start verb (入学, started, "
        "enrolled, joined, began), set it as `from` and leave `to`=null.\n"
        "   c. Do NOT infer specific months from season names. If the input "
        "says 'summer 2022', 'fall 2023', '春季 2024', leave both `from` and "
        "`to` as null — the dates are too vague to commit to.\n"
        "4. `scholar` MUST be one of: 'Bachelor', 'Master', 'PhD', or null. Map "
        "BSc/BS/BA/学士/本科 -> 'Bachelor'; MSc/MS/MA/硕士/研究生 -> 'Master'; "
        "PhD/Ph.D./博士/Doctorate -> 'PhD'. If no degree is mentioned, use null.\n"
        "5. `school` is the institution OR company name. Copy it verbatim — "
        "do not translate, expand abbreviations, or add or remove words.\n"
        "6. `major` is the field of study (education) or job title (work). "
        "Copy it verbatim from the input. Do NOT expand CamelCase "
        "('SeniorSWE' stays 'SeniorSWE'). Do NOT expand acronyms ('EE' stays "
        "'EE'). For education records, drop trailing organizational suffixes "
        "that are not part of the field name itself: '数学系' -> '数学', "
        "'Department of Physics' -> 'Physics', 'School of Engineering' -> "
        "'Engineering'. Keep prefixes like 'Senior' / 'Principal' when they "
        "are part of the job title for work records.\n"
        "7. `is_work_experience` is true iff the row describes a job, "
        "internship, or employment; false if it describes an education record.\n"
        "8. Return ONLY the JSON object — no markdown fences, no commentary."
    ),
    "fields": [
        {"name": "from", "type": "string", "description": "Start date as YYYY-MM or YYYY, or null.", "required": False},
        {"name": "to", "type": "string", "description": "End date as YYYY-MM or YYYY, or the string 'present', or null.", "required": False},
        {"name": "school", "type": "string", "description": "Institution or company name, verbatim.", "required": False},
        {"name": "major", "type": "string", "description": "Field of study (education) or job title (work).", "required": False},
        {"name": "scholar", "type": "string", "description": "One of: 'Bachelor', 'Master', 'PhD', or null.", "required": False},
        {"name": "is_work_experience", "type": "boolean", "description": "True iff a work/internship record.", "required": True},
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
    """Upsert built-in templates on every startup.

    Built-in templates are owned by the codebase, not the user. If the
    instruction/fields/examples change between releases, the live DB row is
    overwritten so users always get the latest version. User-created templates
    are never touched.
    """
    for tpl in BUILTIN_TEMPLATES:
        existing = db.query(ExtractionTemplate).filter_by(name=tpl["name"]).one_or_none()
        fields_json = json.dumps(tpl["fields"], ensure_ascii=False)
        examples_json = json.dumps(tpl["examples"], ensure_ascii=False)
        if existing is None:
            db.add(
                ExtractionTemplate(
                    name=tpl["name"],
                    description=tpl["description"],
                    extraction_mode=tpl["extraction_mode"],
                    instruction=tpl["instruction"],
                    fields_json=fields_json,
                    examples_json=examples_json,
                    is_builtin=True,
                )
            )
        else:
            existing.description = tpl["description"]
            existing.extraction_mode = tpl["extraction_mode"]
            existing.instruction = tpl["instruction"]
            existing.fields_json = fields_json
            existing.examples_json = examples_json
            existing.is_builtin = True
    db.commit()
