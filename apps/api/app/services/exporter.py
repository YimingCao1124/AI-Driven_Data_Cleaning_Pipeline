"""Export job results to CSV or XLSX with original columns + extracted fields."""
from __future__ import annotations

import io
import json
from typing import Any, Dict, List

import pandas as pd

from ..models import ExtractionJob, ExtractionResult, ExtractionTemplate, UploadedFile


def _field_names(template: ExtractionTemplate) -> List[str]:
    fields = json.loads(template.fields_json)
    return [f["name"] for f in fields]


def _row_index_to_result(results: List[ExtractionResult]) -> Dict[int, ExtractionResult]:
    out: Dict[int, ExtractionResult] = {}
    for r in results:
        # If the same row was retried, keep the most recent record.
        prev = out.get(r.source_row_index)
        if prev is None or r.updated_at >= prev.updated_at:
            out[r.source_row_index] = r
    return out


def _build_dataframe(
    file: UploadedFile,
    template: ExtractionTemplate,
    results: List[ExtractionResult],
) -> pd.DataFrame:
    headers: List[str] = json.loads(file.headers_json)
    rows: List[Dict[str, Any]] = json.loads(file.preview_rows_json)  # placeholder: original CSV preview

    # The export must include the FULL rowset, not just the preview. Reload from disk.
    from .excel_parser import parse_table  # local import to avoid cycle at import-time
    from pathlib import Path

    parsed = parse_table(Path(file.original_path), file.file_type)
    rows = parsed["rows"]
    headers = parsed["headers"]

    field_names = _field_names(template)
    indexed = _row_index_to_result(results)

    df = pd.DataFrame(rows, columns=headers)
    for fname in field_names:
        df[fname] = ""

    for idx, result in indexed.items():
        if idx < 0 or idx >= len(df):
            continue
        if result.status != "success":
            continue
        try:
            out = json.loads(result.output_json)
        except json.JSONDecodeError:
            out = {}
        for fname in field_names:
            v = out.get(fname)
            if v is None:
                df.at[idx, fname] = ""
            elif isinstance(v, bool):
                df.at[idx, fname] = "true" if v else "false"
            else:
                df.at[idx, fname] = v
    return df


def export_results(
    file: UploadedFile,
    template: ExtractionTemplate,
    job: ExtractionJob,
    results: List[ExtractionResult],
    *,
    fmt: str,
) -> bytes:
    df = _build_dataframe(file, template, results)
    buf = io.BytesIO()
    fmt = fmt.lower()
    if fmt == "csv":
        # utf-8-sig so Excel on Windows handles CJK characters correctly.
        text = df.to_csv(index=False)
        return text.encode("utf-8-sig")
    if fmt == "xlsx":
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name=f"job_{job.id}")
        return buf.getvalue()
    raise ValueError(f"Unsupported export format: {fmt}")
