import os
from mcp.model_context import ModelContext
from mcp.model_event import ModelEvent
from integration.splunk_logger import SplunkLogger
from typing import Optional, Dict, Any
import json

class MCPClient:
    """
    MCPClient provides a modular interface for creating model contexts, emitting events, and logging to Splunk.
    Credentials are loaded from environment variables by default for security.
    """
    def __init__(self, hec_url: Optional[str] = None, hec_token: Optional[str] = None, index: Optional[str] = None):
        self.hec_url = hec_url or os.getenv("SPLUNK_HEC_URL")
        self.hec_token = hec_token or os.getenv("SPLUNK_HEC_TOKEN")
        self.index = index or os.getenv("SPLUNK_INDEX", "main")
        if not self.hec_url or not self.hec_token:
            raise ValueError("Splunk HEC URL and token must be provided via arguments or environment variables.")
        self.logger = SplunkLogger(self.hec_url, self.hec_token, self.index)

    def create_context(self, name: str, version: str, owner: str, metadata: Optional[Dict[str, Any]] = None, custom: Optional[Dict[str, Any]] = None) -> ModelContext:
        """Create a new model context. Easily extensible for new fields."""
        return ModelContext.new(name, version, owner, metadata, custom)

    def emit_event(self, event_type: str, context: ModelContext, details: Optional[Dict[str, Any]] = None) -> ModelEvent:
        """Emit a new model event. Easily extensible for new event types."""
        return ModelEvent.new(event_type, context, details)

    def log_event(self, event: ModelEvent, sourcetype: str = "mcp:model_event") -> bool:
        """Log a model event to Splunk. Only logs to Splunk, never prints sensitive data."""
        return self.logger.log_event(event=json.loads(event.to_json()), sourcetype=sourcetype) 