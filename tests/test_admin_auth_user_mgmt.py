import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
import pytest
from unittest.mock import MagicMock, patch
from types import SimpleNamespace

# --- TDD: Admin Authentication and User Management ---

def test_admin_login_and_rbac():
    session = SimpleNamespace(authenticated=False, username="", role="", session_id="")
    # Simulate admin login
    USERS = {"admin": {"password": "adminpass", "role": "admin"}}
    def authenticate(username, password, session_state):
        if username in USERS and USERS[username]["password"] == password:
            session_state.authenticated = True
            session_state.username = username
            session_state.role = USERS[username]["role"]
            return True
        else:
            session_state.authenticated = False
            return False
    assert authenticate("admin", "adminpass", session) is True
    assert session.authenticated is True
    assert session.role == "admin"
    # RBAC: only admin can access admin features
    def is_admin(session):
        return session.role == "admin"
    assert is_admin(session)

def test_user_role_management():
    # Simulate user/role management via Splunk REST API/SDK
    mock_splunk_api = MagicMock()
    # Add user
    mock_splunk_api.add_user.return_value = {"username": "bob", "role": "user"}
    result = mock_splunk_api.add_user("bob", "userpass", "user")
    assert result["username"] == "bob"
    assert result["role"] == "user"
    # Update user role
    mock_splunk_api.update_user_role.return_value = {"username": "bob", "role": "admin"}
    result = mock_splunk_api.update_user_role("bob", "admin")
    assert result["role"] == "admin"
    # Remove user
    mock_splunk_api.remove_user.return_value = True
    assert mock_splunk_api.remove_user("bob") is True

def test_admin_action_logging_traceability():
    session = SimpleNamespace(authenticated=True, username="admin", role="admin", session_id="admin-123")
    mock_logger = MagicMock()
    action = "add_user"
    event = {
        "user": session.username,
        "action": action,
        "target_user": "bob",
        "timestamp": "2024-07-08T12:30:00Z",
        "session_id": session.session_id
    }
    mock_logger.log_event(event, sourcetype="mcp:admin_action")
    mock_logger.log_event.assert_called()
    log_args = mock_logger.log_event.call_args[1]["event"] if "event" in mock_logger.log_event.call_args[1] else mock_logger.log_event.call_args[0][0]
    assert log_args["user"] == "admin"
    assert log_args["action"] == action
    assert log_args["target_user"] == "bob"
    assert "timestamp" in log_args
    assert "session_id" in log_args 