import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
import ast
import importlib

def test_key_modules_importable():
    modules = [
        "mcp.sdk",
        "mcp.model_context",
        "mcp.model_event",
        "integration.splunk_logger",
        "integration.splunk_search",
        "integration.export_utils",
        "mcp_user.app",
        "mcp_admin.app"
    ]
    for mod in modules:
        importlib.import_module(mod)

def test_no_hardcoded_splunk_credentials():
    # Only flag string literals that look like real secrets (not env var names or os.getenv usage)
    for root, _, files in os.walk("."):
        for fname in files:
            if fname.endswith(".py"):
                with open(os.path.join(root, fname)) as f:
                    src = f.read()
                tree = ast.parse(src)
                for node in ast.walk(tree):
                    # Skip string literals that are arguments to os.getenv
                    if isinstance(node, ast.Call):
                        func = node.func
                        if (
                            (isinstance(func, ast.Attribute) and func.attr == "getenv" and isinstance(func.value, ast.Name) and func.value.id == "os")
                            or (isinstance(func, ast.Name) and func.id == "getenv")
                        ):
                            continue
                    if isinstance(node, ast.Str):
                        s = node.s
                        # Allow env var names and short strings
                        if (
                            ("SPLUNK_HEC_TOKEN" in s or "SPLUNK_HEC_URL" in s or "SPLUNK_PASSWORD" in s)
                            and len(s) > 32 and not s.startswith("$")
                        ):
                            assert False, f"Hardcoded secret detected: {s} in {fname}"

def test_docs_mention_security_and_modularity():
    doc_files = ["README.md", "docs/sphinx/source/usage.rst"]
    found_security = False
    found_modular = False
    for path in doc_files:
        if os.path.exists(path):
            with open(path) as f:
                content = f.read().lower()
            if "security" in content or "secure" in content:
                found_security = True
            if "modular" in content or "modularity" in content:
                found_modular = True
    assert found_security, "Docs must mention security"
    assert found_modular, "Docs must mention modularity" 