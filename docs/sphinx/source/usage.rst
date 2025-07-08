Usage
=====

.. note::
   **Security:** All credentials (Splunk HEC tokens, passwords) are handled via environment variables. No secrets are hardcoded. Follow best practices for secret management.

.. note::
   **Modularity:** The codebase is organized into modular components (SDK, logging, UI, integration) for maintainability and future expansion.

Install dependencies:

.. code-block:: bash

   pip install -r requirements.txt

Set up Splunk HEC credentials:

.. code-block:: bash

   export SPLUNK_HEC_URL=https://splunk.example.com:8088
   export SPLUNK_HEC_TOKEN=your-token
   export SPLUNK_INDEX=main

Emit a model deployment event:

.. code-block:: python

   from mcp.sdk import MCPClient

   client = MCPClient()
   ctx = client.create_context("my_model", "1.0", "alice", metadata={"framework": "sklearn"})
   event = client.emit_event("model_deployed", ctx, {"deployed_by": "mlops"})
   client.log_event(event)

Search for the event in Splunk:

.. code-block:: spl

   index="main" sourcetype="mcp:model_event"
   | table _time event.event_type event.model_context.name event.details 