import pytest
from integration.splunk_logger import SplunkLogger
from unittest.mock import patch

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