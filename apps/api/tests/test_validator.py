def test_valid_payload_passes(app_module) -> None:
    from app.services.validator import build_pydantic_model, validate_output

    fields = [
        {"name": "school", "type": "string", "required": False},
        {"name": "is_work_experience", "type": "boolean", "required": True},
    ]
    model_cls = build_pydantic_model(fields)
    ok, parsed, errors = validate_output('{"school":"MIT","is_work_experience":false}', model_cls)
    assert ok
    assert parsed["school"] == "MIT"
    assert parsed["is_work_experience"] is False
    assert errors == []


def test_missing_required_field_fails(app_module) -> None:
    from app.services.validator import build_pydantic_model, validate_output

    fields = [{"name": "is_work_experience", "type": "boolean", "required": True}]
    model_cls = build_pydantic_model(fields)
    ok, _, errors = validate_output("{}", model_cls)
    assert not ok
    assert any("is_work_experience" in str(e["loc"]) for e in errors)


def test_invalid_type_fails(app_module) -> None:
    from app.services.validator import build_pydantic_model, validate_output

    fields = [{"name": "year", "type": "integer", "required": True}]
    model_cls = build_pydantic_model(fields)
    ok, _, errors = validate_output('{"year":"not a number"}', model_cls)
    assert not ok
    assert errors


def test_strips_code_fences(app_module) -> None:
    from app.services.validator import build_pydantic_model, validate_output

    fields = [{"name": "x", "type": "string", "required": True}]
    model_cls = build_pydantic_model(fields)
    raw = "```json\n{\"x\":\"hello\"}\n```"
    ok, parsed, errors = validate_output(raw, model_cls)
    assert ok
    assert parsed["x"] == "hello"


def test_invalid_json_reported(app_module) -> None:
    from app.services.validator import build_pydantic_model, validate_output

    fields = [{"name": "x", "type": "string", "required": True}]
    model_cls = build_pydantic_model(fields)
    ok, _, errors = validate_output("not json at all", model_cls)
    assert not ok
    assert "invalid_json" in errors[0]["msg"]


def test_enum_validation(app_module) -> None:
    from app.services.validator import build_pydantic_model, validate_output

    fields = [
        {
            "name": "color",
            "type": "enum",
            "required": True,
            "enum_options": ["red", "blue"],
        }
    ]
    model_cls = build_pydantic_model(fields)
    ok, _, errors = validate_output('{"color":"green"}', model_cls)
    assert not ok
    assert any("color" in str(e["loc"]) for e in errors)
