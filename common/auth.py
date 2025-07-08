import os
from integration.splunk_logger import SplunkLogger
from datetime import datetime

USERS = {
    "admin": {"password": "adminpass", "role": "admin"},
    "user": {"password": "userpass", "role": "user"}
}

# Setup SplunkLogger for auth logging
SPLUNK_HEC_URL = os.getenv("SPLUNK_HEC_URL")
SPLUNK_HEC_TOKEN = os.getenv("SPLUNK_HEC_TOKEN")
SPLUNK_INDEX = os.getenv("SPLUNK_INDEX", "main")
logger = None
if SPLUNK_HEC_URL and SPLUNK_HEC_TOKEN:
    logger = SplunkLogger(SPLUNK_HEC_URL, SPLUNK_HEC_TOKEN, SPLUNK_INDEX)

def authenticate(username, password, session_state, logger_override=None):
    log = logger_override if logger_override is not None else logger
    session_id = getattr(session_state, 'session_id', None) or f"{username}-{datetime.utcnow().timestamp()}"
    if username in USERS and USERS[username]["password"] == password:
        session_state.authenticated = True
        session_state.username = username
        session_state.role = USERS[username]["role"]
        session_state.session_id = session_id
        status = "success"
        result = True
    else:
        session_state.authenticated = False
        session_state.username = ""
        session_state.role = ""
        session_state.session_id = ""
        status = "failure"
        result = False
    if log:
        event = {
            "user": username,
            "action": "login",
            "status": status,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "session_id": session_id
        }
        log.log_event(event, sourcetype="mcp:auth_event")
    return result

def logout(session_state, logger_override=None):
    log = logger_override if logger_override is not None else logger
    username = getattr(session_state, 'username', '')
    session_id = getattr(session_state, 'session_id', '')
    if log and username:
        event = {
            "user": username,
            "action": "logout",
            "status": "success",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "session_id": session_id
        }
        log.log_event(event, sourcetype="mcp:auth_event")
    session_state.authenticated = False
    session_state.username = ""
    session_state.role = ""
    session_state.session_id = ""
    return True

def is_admin(session_state):
    return getattr(session_state, 'role', '') == 'admin' 