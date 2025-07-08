import pytest
from integration.splunk_logger import SplunkLogger
from unittest.mock import patch
import json
from mcp.model_context import ModelContext
from mcp.model_event import ModelEvent

def test_splunk_logger_payload():
    logger = SplunkLogger("http://localhost:8088", "dummy-token", "test-index")
    event = {"foo": "bar"}
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        result = logger.log_event(event, sourcetype="test:type")
        assert result is True
        args, kwargs = mock_post.call_args
        assert "http://localhost:8088/services/collector/event" in args
        payload = kwargs["data"]
        assert "foo" in payload
        assert "test:type" in payload or "test:type" in str(payload)

def test_splunk_logger_traceability_fields():
    logger = SplunkLogger("http://localhost:8088", "dummy-token", "test-index")
    ctx = ModelContext.new("trace_model", "1.0", "trace_owner")
    event = ModelEvent.new("trace_event", ctx)
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        logger.log_event(event=json.loads(event.to_json()), sourcetype="test:type")
        args, kwargs = mock_post.call_args
        payload = json.loads(kwargs["data"])
        assert "event" in payload
        assert "event_id" in payload["event"] or "event_id" in str(payload["event"])
        assert "timestamp" in payload["event"] or "timestamp" in str(payload["event"]) 