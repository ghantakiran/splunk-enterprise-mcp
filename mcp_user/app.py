import streamlit as st
from integration.splunk_search import SplunkSearchHelper
import pandas as pd
from datetime import datetime, timedelta
from integration.export_utils import export_to_csv, export_to_excel
import os
from integration.splunk_logger import SplunkLogger
from common.auth import authenticate, logout, is_admin

# --- Branding ---
st.image("https://splunk-marketing.s3.amazonaws.com/logos/splunk-logo.png", width=180, caption="Model Context Protocol Dashboard", use_column_width=False)
st.title("Splunk Enterprise User MCP Dashboard")

# --- Simple Authentication (demo only) ---
# Setup SplunkLogger for auth logging
SPLUNK_HEC_URL = os.getenv("SPLUNK_HEC_URL")
SPLUNK_HEC_TOKEN = os.getenv("SPLUNK_HEC_TOKEN")
SPLUNK_INDEX = os.getenv("SPLUNK_INDEX", "main")
logger = None
if SPLUNK_HEC_URL and SPLUNK_HEC_TOKEN:
    logger = SplunkLogger(SPLUNK_HEC_URL, SPLUNK_HEC_TOKEN, SPLUNK_INDEX)

def log_auth_action(user, action, status, session_id=None):
    if logger:
        event = {
            "user": user,
            "action": action,
            "status": status,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "session_id": session_id or user
        }
        logger.log_event(event, sourcetype="mcp:auth_event")

if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ''
if 'role' not in st.session_state:
    st.session_state['role'] = ''
if 'session_id' not in st.session_state:
    st.session_state['session_id'] = ''

if not st.session_state['authenticated']:
    st.sidebar.header("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if authenticate(username, password, st.session_state):
            st.success(f"Logged in as {username} ({st.session_state['role']})")
        else:
            st.error("Invalid username or password.")
    st.stop()
else:
    # Show logout button
    if st.sidebar.button("Logout"):
        logout(st.session_state)
        try:
            rerun_fn = getattr(st, 'experimental_rerun', None) or getattr(st, '_rerun', None)
            if rerun_fn:
                rerun_fn()
        except Exception:
            pass
role = st.session_state.get('role', 'user')

# --- UI/UX: Dark mode toggle ---
if 'dark_mode' not in st.session_state:
    st.session_state['dark_mode'] = False
if st.sidebar.checkbox('Dark Mode', value=st.session_state['dark_mode'], help='Toggle dark mode for the dashboard.'):
    st.session_state['dark_mode'] = True
    st.markdown('<style>body { background-color: #222; color: #eee; }</style>', unsafe_allow_html=True)
else:
    st.session_state['dark_mode'] = False

# --- Sidebar filters ---
event_types = ["model_created", "model_deployed", "model_updated", "model_deleted", "custom_event_type"]
st.sidebar.header("Filters")
default_start = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")
default_end = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
start_date = st.sidebar.text_input("Start Date (UTC, ISO)", value=default_start, help="Start date for event search (ISO format)")
end_date = st.sidebar.text_input("End Date (UTC, ISO)", value=default_end, help="End date for event search (ISO format)")
selected_types = st.sidebar.multiselect("Event Types", event_types, default=event_types, help="Filter by event type")

# --- SPL query builder ---
def build_spl_query(types, start, end):
    type_filter = " OR ".join([f'event_type="{t}"' for t in types])
    return f'search index=main sourcetype=mcp:model_event earliest="{start}" latest="{end}" ({type_filter}) | table _time event_type model_context.name model_context.version details'

query = build_spl_query(selected_types, start_date, end_date)

# --- User Dashboard Access Control ---
if 'dashboards' not in st.session_state:
    # Assign dashboards based on user/role (demo: user gets user_dashboard, admin gets all)
    if st.session_state.get('role') == 'admin':
        st.session_state['dashboards'] = ["user_dashboard", "model_overview", "admin_dashboard"]
    else:
        st.session_state['dashboards'] = ["user_dashboard", "model_overview"]

assigned_dashboards = st.session_state['dashboards']

# --- User Dashboard Selector ---
st.sidebar.header("Dashboards")
selected_dashboard = st.sidebar.selectbox("Select Dashboard", assigned_dashboards)

def log_user_action(action, **kwargs):
    if logger:
        event = {
            "user": st.session_state.get('username', ''),
            "action": action,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "session_id": st.session_state.get('session_id', '')
        }
        event.update(kwargs)
        logger.log_event(event, sourcetype="mcp:user_action")

# --- Dashboard Access Control ---
def can_access_dashboard(dashboard):
    return dashboard in assigned_dashboards

if not can_access_dashboard(selected_dashboard):
    st.error("You do not have access to this dashboard.")
    log_user_action("dashboard_access_denied", dashboard=selected_dashboard)
    st.stop()
else:
    log_user_action("view_dashboard", dashboard=selected_dashboard)
    st.success(f"Accessing dashboard: {selected_dashboard}")

# --- Main dashboard (search/visualization) ---
st.header("MCP Event Search & Visualization")
st.subheader("SPL Query")
st.code(query, language="spl")

if st.button("Run Search & Visualize"):
    with st.spinner("Searching Splunk and preparing dashboard..."):
        helper = SplunkSearchHelper()
        results = helper.search_mcp_events(query)
        log_user_action("search", query=query, result_count=len(results) if results else 0)
        if results:
            st.success(f"Found {len(results)} events.")
            df = pd.DataFrame(results)
            # Show table
            st.dataframe(df)
            # Export options
            st.markdown("**Export Results:**")
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="Download CSV",
                    data=export_to_csv(df),
                    file_name="mcp_events.csv",
                    mime="text/csv"
                )
            with col2:
                st.download_button(
                    label="Download Excel",
                    data=export_to_excel(df),
                    file_name="mcp_events.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            # Timechart: event count by type
            if "_time" in df.columns and "event_type" in df.columns:
                df["_time"] = pd.to_datetime(df["_time"], errors="coerce")
                timechart = df.groupby([pd.Grouper(key="_time", freq="D"), "event_type"]).size().unstack(fill_value=0)
                st.subheader("Event Count Over Time (Timechart)")
                st.line_chart(timechart)
            # Bar chart: event type distribution
            if "event_type" in df.columns:
                type_counts = df["event_type"].value_counts()
                st.subheader("Event Type Distribution")
                st.bar_chart(type_counts)
            # --- Advanced Analytics ---
            st.markdown("---")
            st.header("Advanced Analytics")
            # Anomaly detection: highlight days with unusually high/low event counts
            if "_time" in df.columns:
                daily_counts = df.groupby(df["_time"].dt.date).size()
                mean, std = daily_counts.mean(), daily_counts.std()
                anomalies = daily_counts[(daily_counts > mean + 2*std) | (daily_counts < mean - 2*std)]
                st.subheader("Anomaly Detection (Event Count)")
                st.write(f"Mean: {mean:.2f}, Std: {std:.2f}")
                if isinstance(anomalies, pd.Series) and not anomalies.empty:
                    st.warning(f"Anomalies detected on: {', '.join(str(d) for d in anomalies.index)}")
                    st.dataframe(anomalies.reset_index().rename(columns={0: 'event_count'}))
                else:
                    st.success("No anomalies detected in event counts.")
            # Compliance: flag models missing metadata or suspicious activity
            st.subheader("Compliance Checks")
            if "details" in df.columns:
                missing_meta = df[df["details"].apply(lambda x: isinstance(x, dict) and not x)]
                if not missing_meta.empty:
                    st.warning(f"{len(missing_meta)} events with missing details/metadata.")
                    st.dataframe(missing_meta)
                else:
                    st.success("All events have details/metadata.")
            # User activity breakdown
            st.subheader("User Activity Breakdown")
            if "model_context.name" in df.columns:
                top_models = df["model_context.name"].value_counts().head(5)
                st.write("Top 5 Models by Event Count:")
                st.bar_chart(top_models)
            if "event_type" in df.columns:
                st.write("Event Type Timeline:")
                timeline = df.groupby([pd.Grouper(key="_time", freq="D"), "event_type"]).size().unstack(fill_value=0)
                st.line_chart(timeline)
            # Admin-only features
            if role == 'admin':
                st.markdown("---")
                st.header("Admin-Only Features")
                st.info("You are viewing admin-only analytics and controls.")
                # --- Splunk Alerting Integration ---
                st.subheader("Splunk Alerting Integration")
                st.markdown("""
**How to set up a Splunk alert for MCP events:**
1. Go to Splunk > Search & Reporting > Alerts > Create Alert.
2. Use an SPL like:
```spl
index=main sourcetype=mcp:model_event event_type="model_deleted"
```
3. Set alert conditions (e.g., if count > 0 in last 5 minutes).
4. Choose actions (email, webhook, etc.).
5. Save and enable the alert.
                """)
                if st.button("Trigger Test Alert Event"):
                    from mcp.sdk import MCPClient
                    client = MCPClient()
                    ctx = client.create_context("test_model_alert", "1.0", st.session_state['username'])
                    event = client.emit_event("test_alert", ctx, {"triggered_by": st.session_state['username']})
                    client.log_event(event)
                    st.success("Test alert event sent to Splunk!")
        else:
            st.warning("No results found or error occurred.")

# --- Dashboard Studio Helper ---
st.header("Splunk Dashboard Studio Integration")
st.markdown("""
Copy and use these SPL queries and XML snippets in Splunk Dashboard Studio for advanced dashboards:

**SPL: List All Model Events**
```spl
index="main" sourcetype="mcp:model_event"
| table _time event.event_type event.model_context.name event.model_context.version event.details
```

**SPL: Model Lifecycle Timeline**
```spl
index="main" sourcetype="mcp:model_event"
| stats list(event.event_type) as events by event.model_context.model_id, event.model_context.name, event.model_context.version
```

**Dashboard Studio XML Panel Example:**
```xml
<panel>
  <title>Model Events Over Time</title>
  <chart>
    <search>
      <query>index="main" sourcetype="mcp:model_event" | timechart count by event.event_type</query>
    </search>
    <option name="charting.chart">line</option>
  </chart>
</panel>
```

For more, see the [Splunk Search Examples](../docs/splunk_search_examples.md).
""")

# --- Help Popover ---
with st.expander("Help & About", expanded=False):
    st.markdown("""
**Model Context Protocol (MCP) Dashboard**
- Use the sidebar to filter events and switch dark mode.
- Login as 'admin' (adminpass) or 'user' (userpass) to see different features.
- Admins can trigger test alert events and see admin-only analytics.
- For production, use a secure authentication system!
    """)

# Placeholder for future features
st.info("User features coming soon: search, dashboards, activity logs, and more.") 