def test_prompt_contains_instruction_fields_examples_and_directive(education_template, app_module) -> None:
    from app.services.prompt_builder import build_extraction_prompt

    prompt = build_extraction_prompt(education_template, "2018年9月-2022年6月 北京大学 计算机科学 本科")
    assert education_template["instruction"][:30] in prompt
    assert "is_work_experience" in prompt
    assert "Example 1" in prompt
    assert "Input text:" in prompt
    assert "Respond with ONE JSON object" in prompt
    assert "code fence" in prompt.lower() or "markdown" in prompt.lower()


def test_prompt_includes_error_feedback_on_retry(education_template, app_module) -> None:
    from app.services.prompt_builder import build_extraction_prompt

    prompt = build_extraction_prompt(
        education_template, "abc", previous_error="missing field is_work_experience"
    )
    assert "previous response" in prompt.lower()
    assert "is_work_experience" in prompt
