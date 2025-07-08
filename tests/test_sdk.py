from mcp.sdk import MCPClient
from unittest.mock import patch

def test_mcp_client_workflow():
    client = MCPClient("http://localhost:8088", "dummy-token", "test-index")
    ctx = client.create_context("test_model", "1.0", "tester", metadata={"foo": "bar"})
    event = client.emit_event("model_created", ctx, {"created_by": "alice"})
    assert event.event_type == "model_created"
    assert event.model_context.name == "test_model"
    with patch("integration.splunk_logger.requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        result = client.log_event(event, sourcetype="test:type")
        assert result is True

def test_mcp_client_env_vars(monkeypatch):
    monkeypatch.setenv("SPLUNK_HEC_URL", "http://localhost:8088")
    monkeypatch.setenv("SPLUNK_HEC_TOKEN", "dummy-token")
    client = MCPClient()
    assert client.hec_url == "http://localhost:8088"
    assert client.hec_token == "dummy-token"

def test_mcp_client_missing_creds(monkeypatch):
    monkeypatch.delenv("SPLUNK_HEC_URL", raising=False)
    monkeypatch.delenv("SPLUNK_HEC_TOKEN", raising=False)
    try:
        MCPClient()
        assert False, "Should raise ValueError if credentials are missing"
    except ValueError:
        pass

def test_mcp_client_extensible_event():
    client = MCPClient("http://localhost:8088", "dummy-token", "test-index")
    ctx = client.create_context("test_model", "1.0", "tester")
    event = client.emit_event("custom_event_type", ctx, {"foo": "bar"})
    assert event.event_type == "custom_event_type"
    assert event.details["foo"] == "bar" 