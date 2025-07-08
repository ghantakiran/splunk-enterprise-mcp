import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
import pytest
import streamlit as st
from types import SimpleNamespace
from unittest.mock import patch, MagicMock
import datetime
from common.auth import authenticate, logout, is_admin

# USERS dict is now in common.auth

def test_auth_success():
    session = SimpleNamespace(authenticated=False, username="", role="", session_id="")
    assert authenticate("admin", "adminpass", session, logger_override=None) is True
    assert session.authenticated is True
    assert session.username == "admin"
    assert session.role == "admin"

def test_auth_failure():
    session = SimpleNamespace(authenticated=False, username="", role="", session_id="")
    assert authenticate("admin", "wrongpass", session, logger_override=None) is False
    assert session.authenticated is False
    assert session.username == ""
    assert session.role == ""

def test_auth_role_assignment():
    session = SimpleNamespace(authenticated=False, username="", role="", session_id="")
    authenticate("user", "userpass", session, logger_override=None)
    assert session.role == "user"

def test_auth_action_logging():
    session = SimpleNamespace(authenticated=False, username="", role="", session_id="")
    mock_logger = MagicMock()
    authenticate("admin", "adminpass", session, logger_override=mock_logger)
    mock_logger.log_event.assert_called()
    log_args = mock_logger.log_event.call_args[1]["event"] if "event" in mock_logger.log_event.call_args[1] else mock_logger.log_event.call_args[0][0]
    assert log_args["action"] == "login"
    assert log_args["user"] == "admin"
    assert "timestamp" in log_args

def test_rbac_enforcement():
    session = SimpleNamespace(authenticated=True, username="user", role="user", session_id="")
    assert not is_admin(session)
    session_admin = SimpleNamespace(authenticated=True, username="admin", role="admin", session_id="")
    assert is_admin(session_admin)

def test_logout_resets_session():
    session = SimpleNamespace(authenticated=True, username="user", role="user", session_id="user-123")
    logout(session, logger_override=None)
    assert session.authenticated is False
    assert session.username == ""
    assert session.role == ""
    assert session.session_id == ""

def test_auth_log_traceability():
    session = SimpleNamespace(authenticated=False, username="", role="", session_id="")
    mock_logger = MagicMock()
    authenticate("user", "userpass", session, logger_override=mock_logger)
    mock_logger.log_event.assert_called()
    log_args = mock_logger.log_event.call_args[1]["event"] if "event" in mock_logger.log_event.call_args[1] else mock_logger.log_event.call_args[0][0]
    assert "user" in log_args
    assert "session_id" in log_args or "username" in log_args
    assert "timestamp" in log_args
    assert log_args["action"] in ["login", "logout"] 