import pytest
import streamlit as st
from types import SimpleNamespace

USERS = {
    "admin": {"password": "adminpass", "role": "admin"},
    "user": {"password": "userpass", "role": "user"}
}

def authenticate(username, password, session_state):
    if username in USERS and USERS[username]["password"] == password:
        session_state.authenticated = True
        session_state.username = username
        session_state.role = USERS[username]["role"]
        return True
    else:
        session_state.authenticated = False
        return False

def test_auth_success():
    session = SimpleNamespace(authenticated=False, username="", role="")
    assert authenticate("admin", "adminpass", session) is True
    assert session.authenticated is True
    assert session.username == "admin"
    assert session.role == "admin"

def test_auth_failure():
    session = SimpleNamespace(authenticated=False, username="", role="")
    assert authenticate("admin", "wrongpass", session) is False
    assert session.authenticated is False
    assert session.username == ""
    assert session.role == ""

def test_auth_role_assignment():
    session = SimpleNamespace(authenticated=False, username="", role="")
    authenticate("user", "userpass", session)
    assert session.role == "user" 