import os
import pytest
from unittest.mock import patch
from integration.splunk_logger import SplunkLogger

def test_logging_module_emits_logs():
    logger = SplunkLogger("http://localhost:8088", "dummy-token", "test-index")
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        result = logger.log_event({"foo": "bar"}, sourcetype="test:type")
        assert result is True
        mock_post.assert_called_once()

def test_example_spl_dashboard_queries_exist():
    assert os.path.exists("docs/splunk_search_examples.md")
    with open("docs/splunk_search_examples.md") as f:
        content = f.read()
    assert (
        'index="main" sourcetype="mcp:model_event"' in content
        or 'index=main sourcetype=mcp:model_event' in content
    )

def test_documentation_files_exist_and_nonempty():
    doc_files = ["docs/splunk_search_examples.md", "docs/sphinx/source/usage.rst"]
    for path in doc_files:
        assert os.path.exists(path)
        with open(path) as f:
            content = f.read().strip()
        assert len(content) > 0 