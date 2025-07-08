import pytest
from mcp.model_context import ModelContext

def test_create_model_context_with_required_fields():
    ctx = ModelContext.new("test_model", "1.0", "tester")
    assert ctx.name == "test_model"
    assert ctx.version == "1.0"
    assert ctx.owner == "tester"
    assert ctx.model_id is not None
    assert ctx.created_at is not None

def test_model_context_serialization_roundtrip():
    ctx = ModelContext.new("test_model", "1.0", "tester", metadata={"framework": "sklearn"})
    json_str = ctx.to_json()
    ctx2 = ModelContext.from_json(json_str)
    assert ctx.model_id == ctx2.model_id
    assert ctx.name == ctx2.name
    assert ctx.version == ctx2.version
    assert ctx.owner == ctx2.owner
    assert ctx.metadata == ctx2.metadata

def test_model_context_extensibility_custom_fields():
    ctx = ModelContext.new("test_model", "1.0", "tester", custom={"foo": "bar"})
    json_str = ctx.to_json()
    ctx2 = ModelContext.from_json(json_str)
    assert ctx2.custom["foo"] == "bar"

def test_model_context_schema_versioning():
    ctx = ModelContext.new("test_model", "1.0", "tester")
    # Simulate adding a version field to the schema
    ctx_dict = ctx.__dict__.copy()
    ctx_dict["schema_version"] = "1.0"
    import json
    json_str = json.dumps(ctx_dict)
    ctx2 = ModelContext.from_json(json_str)
    assert ctx2.name == ctx.name
    # schema_version is ignored if not in dataclass, but test should not fail 