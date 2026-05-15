import json


def test_mock_returns_valid_json_for_education_prompt(education_template, app_module) -> None:
    from app.services.llm_client import MockLLMClient
    from app.services.prompt_builder import build_extraction_prompt

    client = MockLLMClient()
    prompt = build_extraction_prompt(
        education_template, "2018年9月-2022年6月 北京大学 计算机科学与技术 本科"
    )
    raw = client.extract(prompt)
    data = json.loads(raw)
    assert data["school"] == "北京大学"
    assert data["scholar"] == "Bachelor"
    assert data["from"] == "2018-09"
    assert data["to"] == "2022-06"
    assert data["is_work_experience"] is False


def test_mock_detects_work_experience(education_template, app_module) -> None:
    from app.services.llm_client import MockLLMClient
    from app.services.prompt_builder import build_extraction_prompt

    client = MockLLMClient()
    prompt = build_extraction_prompt(
        education_template, "June 2018 - present, Google, Senior Software Engineer"
    )
    data = json.loads(client.extract(prompt))
    assert data["is_work_experience"] is True
    assert data["school"] == "Google" or data["school"] is None


def test_mock_parses_embedded_json(education_template, app_module) -> None:
    from app.services.llm_client import MockLLMClient
    from app.services.prompt_builder import build_extraction_prompt

    client = MockLLMClient()
    prompt = build_extraction_prompt(
        education_template,
        '{"from":"2019","to":"2023","school":"MIT","major":"EE","degree":"MS"}',
    )
    data = json.loads(client.extract(prompt))
    assert data["school"] == "MIT"
    assert data["scholar"] == "MS"


def test_factory_rejects_unimplemented_providers(app_module) -> None:
    import pytest
    from app.services.llm_client import get_llm_client

    with pytest.raises(NotImplementedError):
        get_llm_client("openai")
    with pytest.raises(NotImplementedError):
        get_llm_client("deepseek")


def test_factory_anthropic_requires_api_key(app_module, monkeypatch) -> None:
    """Anthropic is implemented but requires ANTHROPIC_API_KEY at construction."""
    import pytest
    from app.services.llm_client import get_llm_client

    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
        get_llm_client("anthropic")
