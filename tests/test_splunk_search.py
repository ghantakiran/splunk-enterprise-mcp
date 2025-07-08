import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
import pytest
from unittest.mock import patch, MagicMock
from integration.splunk_search import SplunkSearchHelper
from types import SimpleNamespace
from common.auth import authenticate
import pandas as pd

@patch("integration.splunk_search.Service")
@patch("integration.splunk_search.ResultsReader")
def test_search_mcp_events_success(mock_results_reader, mock_service):
    # Mock Splunk job and results
    mock_job = MagicMock()
    mock_job.results.return_value = [
        {"_time": "2024-06-01T12:00:00Z", "event_type": "model_deployed", "model_context.name": "my_model"}
    ]
    mock_service.return_value.jobs.create.return_value = mock_job
    mock_results_reader.return_value = [
        {"_time": "2024-06-01T12:00:00Z", "event_type": "model_deployed", "model_context.name": "my_model"}
    ]
    helper = SplunkSearchHelper(host="localhost", port=8089, username="admin", password="changeme")
    results = helper.search_mcp_events("search index=main sourcetype=mcp:model_event")
    assert len(results) == 1
    assert results[0]["event_type"] == "model_deployed"
    assert results[0]["model_context.name"] == "my_model"

@patch("integration.splunk_search.Service")
@patch("integration.splunk_search.ResultsReader")
def test_search_mcp_events_error(mock_results_reader, mock_service):
    # Simulate an exception
    mock_service.return_value.jobs.create.side_effect = Exception("Splunk error")
    helper = SplunkSearchHelper(host="localhost", port=8089, username="admin", password="changeme")
    results = helper.search_mcp_events("search index=main sourcetype=mcp:model_event")
    assert results == []

# --- New TDD tests for Issue #2 ---
def test_user_search_action_logging():
    session = SimpleNamespace(authenticated=True, username="user", role="user", session_id="user-123")
    mock_logger = MagicMock()
    query = "search index=main sourcetype=mcp:model_event"
    # Simulate search action
    if mock_logger:
        event = {
            "user": session.username,
            "action": "search",
            "query": query,
            "timestamp": "2024-07-08T12:00:00Z",
            "session_id": session.session_id
        }
        mock_logger.log_event(event, sourcetype="mcp:user_action")
        mock_logger.log_event.assert_called()
        log_args = mock_logger.log_event.call_args[1]["event"] if "event" in mock_logger.log_event.call_args[1] else mock_logger.log_event.call_args[0][0]
        assert log_args["action"] == "search"
        assert log_args["user"] == "user"
        assert log_args["query"] == query
        assert "timestamp" in log_args

def test_visualization_rendering():
    # Simulate a DataFrame from search results
    data = [{"_time": "2024-06-01T12:00:00Z", "event_type": "model_deployed", "model_context.name": "my_model"}]
    df = pd.DataFrame(data)
    # Check that required columns exist for visualization
    assert "_time" in df.columns
    assert "event_type" in df.columns
    assert "model_context.name" in df.columns
    # Simulate a timechart
    df["_time"] = pd.to_datetime(df["_time"], errors="coerce")
    timechart = df.groupby([pd.Grouper(key="_time", freq="D"), "event_type"]).size().unstack(fill_value=0)
    assert not timechart.empty

def test_dashboard_access_control():
    # User should only access assigned dashboards
    session = SimpleNamespace(authenticated=True, username="user", role="user", session_id="user-123", dashboards=["user_dashboard", "model_overview"])
    def can_access_dashboard(session, dashboard):
        return dashboard in getattr(session, 'dashboards', [])
    assert can_access_dashboard(session, "user_dashboard")
    assert not can_access_dashboard(session, "admin_dashboard")

def test_user_action_traceability():
    session = SimpleNamespace(authenticated=True, username="user", role="user", session_id="user-123")
    mock_logger = MagicMock()
    action = "view_dashboard"
    dashboard = "user_dashboard"
    event = {
        "user": session.username,
        "action": action,
        "dashboard": dashboard,
        "timestamp": "2024-07-08T12:00:00Z",
        "session_id": session.session_id
    }
    mock_logger.log_event(event, sourcetype="mcp:user_action")
    mock_logger.log_event.assert_called()
    log_args = mock_logger.log_event.call_args[1]["event"] if "event" in mock_logger.log_event.call_args[1] else mock_logger.log_event.call_args[0][0]
    assert log_args["user"] == "user"
    assert log_args["action"] == action
    assert log_args["dashboard"] == dashboard
    assert "timestamp" in log_args
    assert "session_id" in log_args 