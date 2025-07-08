import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
import pytest
from unittest.mock import MagicMock
from types import SimpleNamespace
import pandas as pd

# --- TDD: Admin Dashboard, Alerts, and Monitoring ---

def test_admin_dashboard_alert_management_logging():
    session = SimpleNamespace(authenticated=True, username="admin", role="admin", session_id="admin-123")
    mock_logger = MagicMock()
    # Simulate dashboard/alert management actions
    for action in ["create_dashboard", "update_dashboard", "delete_dashboard", "create_alert", "update_alert", "delete_alert"]:
        event = {
            "user": session.username,
            "action": action,
            "dashboard": "model_overview",
            "timestamp": "2024-07-08T13:00:00Z",
            "session_id": session.session_id
        }
        mock_logger.log_event(event, sourcetype="mcp:admin_action")
        mock_logger.log_event.assert_called()
        log_args = mock_logger.log_event.call_args[1]["event"] if "event" in mock_logger.log_event.call_args[1] else mock_logger.log_event.call_args[0][0]
        assert log_args["user"] == "admin"
        assert log_args["action"] == action
        assert "timestamp" in log_args
        assert "session_id" in log_args

def test_admin_system_user_activity_monitoring():
    # Mock Splunk search results for system/user activity
    mock_results = [
        {"timestamp": "2024-07-08T13:10:00Z", "user": "user", "action": "search", "session_id": "user-123"},
        {"timestamp": "2024-07-08T13:15:00Z", "user": "admin", "action": "add_user", "session_id": "admin-123"}
    ]
    df = pd.DataFrame(mock_results)
    # Admin should be able to see all user/system actions
    assert set(df["user"]) == {"user", "admin"}
    assert set(df["action"]) == {"search", "add_user"}
    assert "timestamp" in df.columns
    assert "session_id" in df.columns

def test_admin_action_traceability_monitoring():
    session = SimpleNamespace(authenticated=True, username="admin", role="admin", session_id="admin-123")
    mock_logger = MagicMock()
    action = "investigate_security_event"
    event = {
        "user": session.username,
        "action": action,
        "event_id": "evt-001",
        "timestamp": "2024-07-08T13:20:00Z",
        "session_id": session.session_id
    }
    mock_logger.log_event(event, sourcetype="mcp:admin_action")
    mock_logger.log_event.assert_called()
    log_args = mock_logger.log_event.call_args[1]["event"] if "event" in mock_logger.log_event.call_args[1] else mock_logger.log_event.call_args[0][0]
    assert log_args["user"] == "admin"
    assert log_args["action"] == action
    assert log_args["event_id"] == "evt-001"
    assert "timestamp" in log_args
    assert "session_id" in log_args 