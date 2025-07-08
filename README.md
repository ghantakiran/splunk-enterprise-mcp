# Splunk Enterprise Managed Control Panel (MCP)

This project provides a modular Managed Control Panel (MCP) for Splunk Enterprise, built with Python and Streamlit. It is split into two main modules:

- **User MCP**: For end-users to interact with Splunk data and dashboards.
- **Admin MCP**: For administrators to manage users, permissions, and monitor activity.

All actions are traceable and auditable within Splunk.

## Project Structure

```
MCP-Works/
│
├── mcp_user/      # User MCP Streamlit app
├── mcp_admin/     # Admin MCP Streamlit app
├── common/        # Shared utilities (logging, Splunk SDK wrappers, etc.)
├── .streamlit/    # Streamlit configuration
├── requirements.txt
└── README.md
```

## Getting Started

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the User MCP:
   ```bash
   streamlit run mcp_user/app.py
   ```
3. Run the Admin MCP:
   ```bash
   streamlit run mcp_admin/app.py
   ```

## Features
- Modular codebase for easy maintenance
- Full traceability of user and admin actions
- Modern, interactive UI with Streamlit
- Integration with Splunk Enterprise via SDK and REST API

---
For more details, see the documentation in each module.
