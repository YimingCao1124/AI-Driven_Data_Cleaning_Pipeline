"""Parse .xlsx and .csv into headers + rows + a preview window."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import pandas as pd


PREVIEW_ROW_COUNT = 20


def _read_dataframe(path: Path, ext: str) -> pd.DataFrame:
    ext = ext.lower().lstrip(".")
    if ext == "csv":
        # Read all values as strings so we don't lose precision or coerce numbers
        # to floats and back. The extraction layer treats every cell as text.
        return pd.read_csv(path, dtype=str, keep_default_na=False)
    if ext == "xlsx":
        return pd.read_excel(path, dtype=str, keep_default_na=False, engine="openpyxl")
    raise ValueError(f"Unsupported file extension: .{ext}")


def parse_table(path: Path, ext: str) -> Dict[str, Any]:
    """Return headers, the full rowset, a preview window, and the total row count.

    Each row is a dict keyed by column name. All cell values are strings.
    """
    df = _read_dataframe(path, ext)
    df = df.fillna("")
    headers: List[str] = [str(c) for c in df.columns]
    rows: List[Dict[str, Any]] = df.to_dict(orient="records")
    # Coerce every value to a plain string so the JSON serializer is happy
    # and downstream code can treat values uniformly.
    rows = [{str(k): "" if v is None else str(v) for k, v in r.items()} for r in rows]
    preview = rows[:PREVIEW_ROW_COUNT]
    return {
        "headers": headers,
        "rows": rows,
        "preview_rows": preview,
        "total_rows": len(rows),
    }
