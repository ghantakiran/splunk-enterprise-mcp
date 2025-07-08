import requests
import json
from typing import Dict, Any

class SplunkLogger:
    def __init__(self, hec_url: str, hec_token: str, index: str = "main"):
        self.hec_url = hec_url.rstrip("/") + "/services/collector/event"
        self.hec_token = hec_token
        self.index = index

    def log_event(self, event: Dict[str, Any], sourcetype: str = "mcp:model_event") -> bool:
        headers = {
            "Authorization": f"Splunk {self.hec_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "event": event,
            "sourcetype": sourcetype,
            "index": self.index
        }
        response = requests.post(self.hec_url, headers=headers, data=json.dumps(payload), timeout=5)
        return response.status_code == 200 