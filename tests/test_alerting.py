import pytest
from unittest.mock import patch, MagicMock
from mcp.sdk import MCPClient

def test_trigger_test_alert_event():
    with patch("mcp.sdk.SplunkLogger") as MockLogger:
        mock_logger = MockLogger.return_value
        mock_logger.log_event.return_value = True
        client = MCPClient("http://localhost:8088", "dummy-token", "test-index")
        ctx = client.create_context("test_model_alert", "1.0", "admin")
        event = client.emit_event("test_alert", ctx, {"triggered_by": "admin"})
        result = client.log_event(event)
        assert result is True
        mock_logger.log_event.assert_called_once()
        args, kwargs = mock_logger.log_event.call_args
        # log_event is called with event=... as a kwarg
        event_arg = kwargs.get('event') if 'event' in kwargs else (args[0] if args else None)
        assert event_arg is not None
        assert "event_id" in event_arg or "event_id" in str(event_arg) 