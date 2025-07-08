from mcp.model_context import ModelContext
from mcp.model_event import ModelEvent
from integration.splunk_logger import SplunkLogger
from typing import Optional, Dict, Any
import json

class MCPClient:
    def __init__(self, hec_url: str, hec_token: str, index: str = "main"):
        self.logger = SplunkLogger(hec_url, hec_token, index)

    def create_context(self, name: str, version: str, owner: str, metadata: Optional[Dict[str, Any]] = None, custom: Optional[Dict[str, Any]] = None) -> ModelContext:
        return ModelContext.new(name, version, owner, metadata, custom)

    def emit_event(self, event_type: str, context: ModelContext, details: Optional[Dict[str, Any]] = None) -> ModelEvent:
        return ModelEvent.new(event_type, context, details)

    def log_event(self, event: ModelEvent, sourcetype: str = "mcp:model_event") -> bool:
        return self.logger.log_event(event=json.loads(event.to_json()), sourcetype=sourcetype) 