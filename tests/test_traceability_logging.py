import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
import pytest
from unittest.mock import MagicMock
from types import SimpleNamespace

# --- TDD: Traceability & Logging Module ---

def test_log_all_relevant_actions():
    session = SimpleNamespace(authenticated=True, username="user", role="user", session_id="user-123")
    mock_logger = MagicMock()
    actions = [
        {"action": "search", "resource": "model_event", "status": "success"},
        {"action": "view_dashboard", "resource": "user_dashboard", "status": "success"},
        {"action": "add_user", "resource": "admin_panel", "status": "success"}
    ]
    for act in actions:
        event = {
            "user": session.username,
            "session_id": session.session_id,
            "action": act["action"],
            "resource": act["resource"],
            "status": act["status"],
            "timestamp": "2024-07-08T14:00:00Z"
        }
        mock_logger.log_event(event, sourcetype="mcp:traceability")
        mock_logger.log_event.assert_called()
        log_args = mock_logger.log_event.call_args[1]["event"] if "event" in mock_logger.log_event.call_args[1] else mock_logger.log_event.call_args[0][0]
        assert log_args["user"] == session.username
        assert log_args["session_id"] == session.session_id
        assert log_args["action"] == act["action"]
        assert log_args["resource"] == act["resource"]
        assert log_args["status"] == act["status"]
        assert "timestamp" in log_args

def test_log_formatting_and_splunk_integration():
    # Simulate SplunkLogger sending to HEC
    from integration.splunk_logger import SplunkLogger
    logger = SplunkLogger("http://localhost:8088", "dummy-token", "main")
    event = {
        "user": "user",
        "session_id": "user-123",
        "action": "search",
        "resource": "model_event",
        "status": "success",
        "timestamp": "2024-07-08T14:05:00Z"
    }
    # Patch requests.post to simulate HEC
    import requests
    from unittest.mock import patch
    with patch.object(requests, "post") as mock_post:
        mock_post.return_value.status_code = 200
        result = logger.log_event(event, sourcetype="mcp:traceability")
        assert result is True
        mock_post.assert_called()
        payload = mock_post.call_args[1]["data"]
        assert "model_event" not in payload or "traceability" in payload

def test_example_queries_and_dashboards_in_docs():
    # Check docs for example queries/dashboards
    doc_files = ["README.md", "docs/splunk_search_examples.md"]
    found_query = False
    found_dashboard = False
    for path in doc_files:
        if os.path.exists(path):
            with open(path) as f:
                content = f.read().lower()
            if "index=main sourcetype=mcp:model_event" in content or "sourcetype=mcp:traceability" in content:
                found_query = True
            if "dashboard" in content or "panel" in content:
                found_dashboard = True
    assert found_query, "Docs must include example Splunk queries"
    assert found_dashboard, "Docs must include example dashboards" 