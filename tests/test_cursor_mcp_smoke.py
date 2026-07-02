from __future__ import annotations

import importlib.util
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "cursor_mcp_smoke.py"
SPEC = importlib.util.spec_from_file_location("cursor_mcp_smoke", MODULE_PATH)
assert SPEC is not None
cursor_mcp_smoke = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(cursor_mcp_smoke)


def test_resolve_string_substitutes_known_inputs() -> None:
    inputs = {"github_pat": "ghp_secret_value"}

    resolved = cursor_mcp_smoke.resolve_string("--token=${input:github_pat}", inputs)

    assert resolved == "--token=ghp_secret_value"


def test_resolve_string_keeps_unknown_placeholders() -> None:
    resolved = cursor_mcp_smoke.resolve_string("${input:unknown_key}", {"github_pat": "x"})

    assert resolved == "${input:unknown_key}"


def test_mask_inputs_restores_placeholders() -> None:
    inputs = {"github_pat": "ghp_secret_value"}

    masked = cursor_mcp_smoke.mask_inputs("cmd --token=ghp_secret_value --v", inputs)

    assert masked == "cmd --token=${input:github_pat} --v"
    assert "ghp_secret_value" not in masked


def test_mask_inputs_ignores_empty_values() -> None:
    masked = cursor_mcp_smoke.mask_inputs("plain text", {"github_pat": ""})

    assert masked == "plain text"


def test_build_command_wraps_windows_launchers() -> None:
    assert cursor_mcp_smoke.build_command("server.cmd", ["--x"])[:3] == ["cmd.exe", "/d", "/c"]
    assert cursor_mcp_smoke.build_command("server.ps1", [])[0] == "powershell.exe"
    assert cursor_mcp_smoke.build_command("node", ["main.js"]) == ["node", "main.js"]
