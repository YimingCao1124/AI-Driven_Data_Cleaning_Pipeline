from pathlib import Path


def test_parse_csv(sample_csv_path: Path, app_module) -> None:
    from app.services.excel_parser import parse_table

    parsed = parse_table(sample_csv_path, "csv")
    assert parsed["headers"] == ["id", "name", "experience"]
    assert parsed["total_rows"] == 3
    assert len(parsed["preview_rows"]) == 3
    assert "北京大学" in parsed["rows"][0]["experience"]


def test_parse_xlsx(sample_xlsx_path: Path, app_module) -> None:
    from app.services.excel_parser import parse_table

    parsed = parse_table(sample_xlsx_path, "xlsx")
    assert parsed["headers"] == ["id", "name", "experience"]
    assert parsed["total_rows"] == 3
    assert "Stanford" in parsed["rows"][1]["experience"]


def test_parse_unsupported_extension_raises(tmp_path: Path, app_module) -> None:
    from app.services.excel_parser import parse_table

    p = tmp_path / "foo.docx"
    p.write_text("not actually a docx")
    import pytest

    with pytest.raises(ValueError):
        parse_table(p, "docx")
