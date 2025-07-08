from dataclasses import dataclass, field, asdict
from typing import Any, Dict, Optional
import json
import uuid
import datetime
from mcp.model_context import ModelContext

@dataclass
class ModelEvent:
    event_id: str
    event_type: str
    model_context: ModelContext
    timestamp: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat())
    details: Dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> str:
        data = asdict(self)
        data['model_context'] = json.loads(self.model_context.to_json())
        return json.dumps(data)

    @staticmethod
    def from_json(data: str) -> 'ModelEvent':
        d = json.loads(data)
        d['model_context'] = ModelContext.from_json(json.dumps(d['model_context']))
        return ModelEvent(**d)

    @staticmethod
    def new(event_type: str, model_context: ModelContext, details: Optional[Dict[str, Any]] = None) -> 'ModelEvent':
        if details is None:
            details = {}
        return ModelEvent(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            model_context=model_context,
            details=details
        ) 