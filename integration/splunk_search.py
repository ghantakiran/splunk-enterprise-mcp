import os
from splunklib.client import Service
from splunklib.results import ResultsReader
from typing import List, Dict, Any

class SplunkSearchHelper:
    def __init__(self, host=None, port=None, username=None, password=None, app=None):
        self.host = host or os.getenv("SPLUNK_HOST", "localhost")
        self.port = port or int(os.getenv("SPLUNK_PORT", 8089))
        self.username = username or os.getenv("SPLUNK_USER", "admin")
        self.password = password or os.getenv("SPLUNK_PASSWORD", "changeme")
        self.app = app or os.getenv("SPLUNK_APP", "search")
        self.service = Service(
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            app=self.app
        )

    def search_mcp_events(self, query: str, earliest_time: str = "-24h", latest_time: str = "now") -> List[Dict[str, Any]]:
        """
        Search for MCP events in Splunk using the provided SPL query.
        Returns a list of event dicts.
        """
        try:
            job = self.service.jobs.create(query, earliest_time=earliest_time, latest_time=latest_time)
            results = []
            for result in ResultsReader(job.results()):
                if isinstance(result, dict):
                    results.append(result)
            return results
        except Exception as e:
            print(f"Splunk search error: {e}")
            return [] 