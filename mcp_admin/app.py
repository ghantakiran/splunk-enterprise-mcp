import streamlit as st
from integration.splunk_search import SplunkSearchHelper
import pandas as pd
from datetime import datetime, timedelta
from integration.export_utils import export_to_csv, export_to_excel
import os
from integration.splunk_logger import SplunkLogger
from common.auth import authenticate, logout, is_admin
from integration.splunk_user_mgmt import SplunkUserManager

# --- Branding ---
st.image("https://splunk-marketing.s3.amazonaws.com/logos/splunk-logo.png", width=180, caption="Model Context Protocol Dashboard", use_column_width=False)
st.title("Splunk Enterprise Admin MCP Dashboard")

# --- Simple Authentication (demo only) ---
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
    if st.sidebar.button("Logout"):
        logout(st.session_state)
        try:
            rerun_fn = getattr(st, 'experimental_rerun', None) or getattr(st, '_rerun', None)
            if rerun_fn:
                rerun_fn()
        except Exception:
            pass
role = st.session_state.get('role', 'admin')

# --- Admin User Management (sidebar, admin only) ---
def log_admin_action(action, **kwargs):
    SPLUNK_HEC_URL = os.getenv("SPLUNK_HEC_URL")
    SPLUNK_HEC_TOKEN = os.getenv("SPLUNK_HEC_TOKEN")
    SPLUNK_INDEX = os.getenv("SPLUNK_INDEX", "main")
    logger = None
    if SPLUNK_HEC_URL and SPLUNK_HEC_TOKEN:
        logger = SplunkLogger(SPLUNK_HEC_URL, SPLUNK_HEC_TOKEN, SPLUNK_INDEX)
    if logger:
        event = {
            "user": st.session_state.get('username', ''),
            "action": action,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "session_id": st.session_state.get('session_id', '')
        }
        event.update(kwargs)
        logger.log_event(event, sourcetype="mcp:admin_action")

if is_admin(st.session_state):
    with st.sidebar.expander("User Management", expanded=False):
        st.markdown("**Add User**")
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        new_role = st.selectbox("Role", ["user", "admin"])
        if st.button("Add User"):
            try:
                mgr = SplunkUserManager()
                result = mgr.add_user(new_username, new_password, new_role)
                st.success(f"User {result['username']} added as {result['role']}.")
                log_admin_action("add_user", target_user=new_username, target_role=new_role)
            except Exception as e:
                st.error(f"Failed to add user: {e}")
        st.markdown("**Update User Role**")
        upd_username = st.text_input("Update Username")
        upd_role = st.selectbox("New Role", ["user", "admin"], key="upd_role")
        if st.button("Update User Role"):
            try:
                mgr = SplunkUserManager()
                result = mgr.update_user_role(upd_username, upd_role)
                st.success(f"User {result['username']} role updated to {result['role']}.")
                log_admin_action("update_user_role", target_user=upd_username, target_role=upd_role)
            except Exception as e:
                st.error(f"Failed to update user role: {e}")
        st.markdown("**Remove User**")
        del_username = st.text_input("Delete Username")
        if st.button("Remove User"):
            try:
                mgr = SplunkUserManager()
                mgr.remove_user(del_username)
                st.success(f"User {del_username} removed.")
                log_admin_action("remove_user", target_user=del_username)
            except Exception as e:
                st.error(f"Failed to remove user: {e}")
    # --- Dashboard/Alert Management ---
    with st.sidebar.expander("Dashboard & Alert Management", expanded=False):
        st.markdown("**Manage Dashboards**")
        dash_action = st.selectbox("Action", ["create_dashboard", "update_dashboard", "delete_dashboard"])
        dash_name = st.text_input("Dashboard Name")
        if st.button("Submit Dashboard Action"):
            log_admin_action(dash_action, dashboard=dash_name)
            st.success(f"{dash_action.replace('_', ' ').title()} for {dash_name} logged.")
        st.markdown("**Manage Alerts**")
        alert_action = st.selectbox("Alert Action", ["create_alert", "update_alert", "delete_alert"])
        alert_name = st.text_input("Alert Name")
        if st.button("Submit Alert Action"):
            log_admin_action(alert_action, alert=alert_name)
            st.success(f"{alert_action.replace('_', ' ').title()} for {alert_name} logged.")
    # --- System/User Activity Monitoring ---
    with st.sidebar.expander("System & User Activity Monitoring", expanded=False):
        if st.button("View All Activity Logs"):
            helper = SplunkSearchHelper()
            query = 'search index=main sourcetype=mcp:user_action OR sourcetype=mcp:admin_action | table timestamp user action session_id dashboard alert event_id details'
            logs = helper.search_mcp_events(query)
            if logs:
                df = pd.DataFrame(logs)
                st.dataframe(df)
                log_admin_action("view_all_activity_logs")
            else:
                st.info("No activity log entries found.")
    # --- Security/Compliance Investigation ---
    with st.sidebar.expander("Security/Compliance Investigation", expanded=False):
        event_id = st.text_input("Event ID to Investigate")
        if st.button("Investigate Event"):
            log_admin_action("investigate_security_event", event_id=event_id)
            st.success(f"Investigation of event {event_id} logged.")

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
default_start = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
default_end = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
start_date = st.sidebar.text_input("Start Date (UTC, ISO)", value=default_start, help="Start date for event search (ISO format)")
end_date = st.sidebar.text_input("End Date (UTC, ISO)", value=default_end, help="End date for event search (ISO format)")
selected_types = st.sidebar.multiselect("Event Types", event_types, default=event_types, help="Filter by event type")

# --- SPL query builder ---
def build_spl_query(types, start, end):
    type_filter = " OR ".join([f'event_type="{t}"' for t in types])
    return f'search index=main sourcetype=mcp:model_event earliest="{start}" latest="{end}" ({type_filter}) | table _time event_type model_context.name model_context.version details'

query = build_spl_query(selected_types, start_date, end_date)

# --- Main dashboard ---
st.header("MCP Event Monitoring & Analytics")
st.subheader("SPL Query")
st.code(query, language="spl")

if st.button("Run Admin Search & Visualize"):
    with st.spinner("Searching Splunk and preparing admin dashboard..."):
        helper = SplunkSearchHelper()
        results = helper.search_mcp_events(query)
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
                    file_name="mcp_events_admin.csv",
                    mime="text/csv"
                )
            with col2:
                st.download_button(
                    label="Download Excel",
                    data=export_to_excel(df),
                    file_name="mcp_events_admin.xlsx",
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
**Model Context Protocol (MCP) Admin Dashboard**
- Use the sidebar to filter events and switch dark mode.
- Login as 'admin' (adminpass) or 'user' (userpass) to see different features.
- Admins can trigger test alert events and see admin-only analytics.
- For production, use a secure authentication system!
    """)

# Admin info panel
st.info("Admin features: user management, monitoring, audit logs, advanced analytics, and export. Use filters and visualizations to monitor model activity and compliance.") 