import pytest
from mcp.sdk import MCPClient
from mcp.model_event import ModelEvent
from mcp.model_context import ModelContext

def test_event_creation_for_lifecycle_types():
    client = MCPClient("http://localhost:8088", "dummy-token", "test-index")
    ctx = client.create_context("test_model", "1.0", "tester")
    for event_type in ["model_created", "model_updated", "model_deployed", "model_inferenced", "model_deprecated"]:
        event = client.emit_event(event_type, ctx, {"info": "test"})
        assert event.event_type == event_type
        assert event.model_context.model_id == ctx.model_id
        assert event.details["info"] == "test"

def test_event_has_unique_id_and_timestamp():
    client = MCPClient("http://localhost:8088", "dummy-token", "test-index")
    ctx = client.create_context("test_model", "1.0", "tester")
    event1 = client.emit_event("model_created", ctx)
    event2 = client.emit_event("model_created", ctx)
    assert event1.event_id != event2.event_id
    assert event1.timestamp != ""
    assert event2.timestamp != ""

def test_event_serialization_roundtrip():
    client = MCPClient("http://localhost:8088", "dummy-token", "test-index")
    ctx = client.create_context("test_model", "1.0", "tester")
    event = client.emit_event("model_deployed", ctx, {"foo": "bar"})
    json_str = event.to_json()
    event2 = ModelEvent.from_json(json_str)
    assert event.event_id == event2.event_id
    assert event.event_type == event2.event_type
    assert event.model_context.model_id == event2.model_context.model_id
    assert event.details == event2.details 