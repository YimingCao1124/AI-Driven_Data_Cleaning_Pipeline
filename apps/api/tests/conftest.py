"""Shared test fixtures.

We set DATABASE_URL and other env vars to point at a fresh temp directory,
then clear and re-import the app modules so they pick up the new config.
The TestClient context manager triggers the app's startup hook which creates
the schema and seeds the built-in templates.

Using a real SQLite file (not :memory:) so that the job-runner thread —
which opens its own session via SessionLocal — sees writes from the test
thread.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient

# Make the app importable.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def _clear_app_modules() -> None:
    for mod_name in list(sys.modules):
        if mod_name == "app" or mod_name.startswith("app."):
            sys.modules.pop(mod_name, None)


@pytest.fixture()
def tmp_storage(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    upload_dir = tmp_path / "uploads"
    export_dir = tmp_path / "exports"
    data_dir = tmp_path / "data"
    upload_dir.mkdir()
    export_dir.mkdir()
    data_dir.mkdir()
    db_path = data_dir / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    monkeypatch.setenv("UPLOAD_DIR", str(upload_dir))
    monkeypatch.setenv("EXPORT_DIR", str(export_dir))
    monkeypatch.setenv("BACKEND_CORS_ORIGINS", "http://localhost:3000")
    monkeypatch.setenv("MODEL_PROVIDER", "mock")
    monkeypatch.setenv("MAX_CONCURRENCY", "1")
    monkeypatch.setenv("MAX_RETRIES", "1")
    return tmp_path


@pytest.fixture()
def app_module(tmp_storage: Path):
    """Reload the app so it reads our test env vars."""
    _clear_app_modules()
    from app import main as main_module  # noqa: F401  (re-imports config/db transitively)

    return main_module


@pytest.fixture()
def client(app_module) -> Generator[TestClient, None, None]:
    with TestClient(app_module.app) as c:
        yield c


@pytest.fixture()
def sample_csv_path() -> Path:
    csv = Path(tempfile.mkdtemp()) / "sample.csv"
    csv.write_text(
        "id,name,experience\n"
        "1,张伟,2018年9月-2022年6月 北京大学 计算机科学与技术 本科\n"
        "2,Alice,\"2015/09 - 2019/06, Stanford University, Computer Science, BSc\"\n"
        "3,Bob,\"June 2018 - present, Google, Senior Software Engineer\"\n",
        encoding="utf-8",
    )
    return csv


@pytest.fixture()
def sample_xlsx_path(sample_csv_path: Path) -> Path:
    import pandas as pd

    xlsx = sample_csv_path.with_suffix(".xlsx")
    pd.read_csv(sample_csv_path).to_excel(xlsx, index=False, engine="openpyxl")
    return xlsx


@pytest.fixture()
def education_template() -> dict:
    """The V1 built-in template as a plain dict."""
    _clear_app_modules()
    from app.services.builtin_templates import EDUCATION_EXPERIENCE_CLEANER

    return json.loads(json.dumps(EDUCATION_EXPERIENCE_CLEANER))  # deep copy
