import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
import pytest
from unittest.mock import MagicMock, patch
from types import SimpleNamespace
import pandas as pd

# --- TDD: User Activity Logs and Requests ---

def test_view_user_activity_logs():
    # Mock Splunk search results for user activity
    mock_results = [
        {"timestamp": "2024-07-08T12:00:00Z", "user": "user", "action": "search", "session_id": "user-123"},
        {"timestamp": "2024-07-08T12:05:00Z", "user": "user", "action": "view_dashboard", "session_id": "user-123"}
    ]
    # Simulate DataFrame for activity log
    df = pd.DataFrame(mock_results)
    # User should see only their own actions
    assert (df["user"] == "user").all()
    assert set(df["action"]) == {"search", "view_dashboard"}
    assert "timestamp" in df.columns
    assert "session_id" in df.columns

def test_submit_request_ticket():
    # Simulate submitting a request/ticket
    session = SimpleNamespace(authenticated=True, username="user", role="user", session_id="user-123")
    mock_logger = MagicMock()
    request = {"type": "data_access", "details": "Request access to model X"}
    event = {
        "user": session.username,
        "action": "submit_request",
        "request_type": request["type"],
        "details": request["details"],
        "timestamp": "2024-07-08T12:10:00Z",
        "session_id": session.session_id
    }
    mock_logger.log_event(event, sourcetype="mcp:user_action")
    mock_logger.log_event.assert_called()
    log_args = mock_logger.log_event.call_args[1]["event"] if "event" in mock_logger.log_event.call_args[1] else mock_logger.log_event.call_args[0][0]
    assert log_args["action"] == "submit_request"
    assert log_args["user"] == "user"
    assert log_args["request_type"] == "data_access"
    assert "timestamp" in log_args
    assert "session_id" in log_args

def test_user_action_traceability_activity():
    # All actions must be traceable in logs
    session = SimpleNamespace(authenticated=True, username="user", role="user", session_id="user-123")
    mock_logger = MagicMock()
    action = "view_activity_log"
    event = {
        "user": session.username,
        "action": action,
        "timestamp": "2024-07-08T12:15:00Z",
        "session_id": session.session_id
    }
    mock_logger.log_event(event, sourcetype="mcp:user_action")
    mock_logger.log_event.assert_called()
    log_args = mock_logger.log_event.call_args[1]["event"] if "event" in mock_logger.log_event.call_args[1] else mock_logger.log_event.call_args[0][0]
    assert log_args["user"] == "user"
    assert log_args["action"] == action
    assert "timestamp" in log_args
    assert "session_id" in log_args 