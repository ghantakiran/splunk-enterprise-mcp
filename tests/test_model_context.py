from mcp.model_context import ModelContext

def test_model_context_serialization():
    ctx = ModelContext.new("test_model", "0.1", "tester")
    json_str = ctx.to_json()
    ctx2 = ModelContext.from_json(json_str)
    assert ctx.model_id == ctx2.model_id
    assert ctx.name == ctx2.name
    assert ctx.version == ctx2.version
    assert ctx.owner == ctx2.owner

def test_model_context_custom_fields():
    ctx = ModelContext.new("test_model", "0.2", "tester", custom={"foo": "bar"})
    json_str = ctx.to_json()
    ctx2 = ModelContext.from_json(json_str)
    assert ctx2.custom["foo"] == "bar"

def test_model_context_traceability_fields():
    ctx = ModelContext.new("trace_model", "1.0", "trace_owner")
    assert hasattr(ctx, "model_id")
    assert hasattr(ctx, "created_at") 