from dataclasses import dataclass, field, asdict
from typing import Any, Dict, Optional
import json
import uuid
import datetime

@dataclass
class ModelContext:
    model_id: str
    name: str
    version: str
    owner: str
    created_at: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    custom: Optional[Dict[str, Any]] = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps(asdict(self))

    @staticmethod
    def from_json(data: str) -> 'ModelContext':
        d = json.loads(data)
        # Only keep fields that are in the dataclass
        allowed = {f.name for f in ModelContext.__dataclass_fields__.values()}
        filtered = {k: v for k, v in d.items() if k in allowed}
        return ModelContext(**filtered)

    @staticmethod
    def new(name: str, version: str, owner: str, metadata: Optional[Dict[str, Any]] = None, custom: Optional[Dict[str, Any]] = None) -> 'ModelContext':
        return ModelContext(
            model_id=str(uuid.uuid4()),
            name=name,
            version=version,
            owner=owner,
            metadata=metadata or {},
            custom=custom or {}
        ) 