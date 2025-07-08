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