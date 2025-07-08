from mcp.model_context import ModelContext
from mcp.model_event import ModelEvent

def test_model_event_serialization():
    ctx = ModelContext.new("test_model", "0.1", "tester")
    event = ModelEvent.new("model_created", ctx, {"foo": "bar"})
    json_str = event.to_json()
    event2 = ModelEvent.from_json(json_str)
    assert event.event_id == event2.event_id
    assert event.event_type == event2.event_type
    assert event.model_context.model_id == event2.model_context.model_id
    assert event.details == event2.details

def test_model_event_lifecycle():
    ctx = ModelContext.new("test_model", "1.0", "tester")
    event = ModelEvent.new("model_deployed", ctx, {"deployed_by": "alice"})
    assert event.event_type == "model_deployed"
    assert event.model_context.model_id == ctx.model_id
    assert "deployed_by" in event.details
    assert event.event_id is not None
    assert event.timestamp is not None

def test_model_event_traceability_fields():
    ctx = ModelContext.new("trace_model", "1.0", "trace_owner")
    event = ModelEvent.new("trace_event", ctx)
    assert hasattr(event, "event_id")
    assert hasattr(event, "timestamp") 