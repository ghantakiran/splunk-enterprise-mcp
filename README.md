# Model Context Protocol (MCP) for Splunk

This project implements a Model Context Protocol (MCP) for managing, exchanging, and tracing the context of machine learning/data models within Splunk.

## Security & Modularity
- **Security:** All credentials (Splunk HEC tokens, passwords) are handled via environment variables. No secrets are hardcoded. Follow best practices for secret management.
- **Modularity:** The codebase is organized into modular components (SDK, logging, UI, integration) for maintainability and future expansion.

## Quickstart

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Set up Splunk HEC credentials:**
   - Set environment variables:
     - `SPLUNK_HEC_URL` (e.g., `https://splunk.example.com:8088`)
     - `SPLUNK_HEC_TOKEN` (your HEC token)
     - `SPLUNK_INDEX` (optional, default: `main`)
3. **Run an example:**
   ```bash
   python examples/emit_model_event.py
   ```

## Example Usage

```python
from mcp.sdk import MCPClient

client = MCPClient()
ctx = client.create_context("my_model", "1.0", "alice", metadata={"framework": "sklearn"})
event = client.emit_event("model_deployed", ctx, {"deployed_by": "mlops"})
client.log_event(event)
```

## Documentation
- [Sphinx Docs (API, Usage, Guides)](docs/sphinx/build/html/index.html)
- [GitHub Wiki](https://github.com/ghantakiran/splunk-enterprise-mcp/wiki)
- [Splunk Search Examples](docs/splunk_search_examples.md)

## Features
- Model context schema and serialization
- Model lifecycle event tracking
- Splunk integration for logging and traceability
- Python SDK for easy integration
- TDD and CI ready

## Issues & Roadmap
See the GitHub Issues for protocol, integration, TDD, and documentation tasks.
