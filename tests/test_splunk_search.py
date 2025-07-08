import pytest
from unittest.mock import patch, MagicMock
from integration.splunk_search import SplunkSearchHelper

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