"""Generate examples/education_experience_sample.xlsx from the CSV counterpart.

Usage:
    python scripts/generate_sample_xlsx.py

Requires pandas and openpyxl (already in apps/api/requirements.txt).
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "examples" / "education_experience_sample.csv"
XLSX_PATH = ROOT / "examples" / "education_experience_sample.xlsx"


def main() -> None:
    df = pd.read_csv(CSV_PATH)
    df.to_excel(XLSX_PATH, index=False, engine="openpyxl")
    print(f"Wrote {XLSX_PATH} ({len(df)} rows)")


if __name__ == "__main__":
    main()
