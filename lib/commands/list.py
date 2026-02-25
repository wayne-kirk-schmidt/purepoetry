#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# pylint: disable=import-error
# pylint: disable=import-outside-toplevel
# pylint: disable=broad-exception-caught
# pylint: disable=too-many-return-statements
# pylint: disable=too-many-locals
#

"""
list.py

List manipulation verb for PurePoetry.

Supports:

    purepoetry list show <dotted.path>
    purepoetry list add <dotted.path> <value>
    purepoetry list remove <dotted.path> <value>

Behavior:
    - Non-destructive
    - Writes modified copy to disk
    - Honors --dst if provided
    - Defaults to project directory if --dst not provided
    - Never mutates original pyproject.toml
    - Returns (ExitCode, payload)
"""

from __future__ import annotations

import sys
from pathlib import Path
from datetime import datetime
from typing import Any, List, Tuple

import tomlkit
from tomlkit import table, array

from lib.utilities.exitcodes import ExitCode

sys.dont_write_bytecode = True


# ==========================================================
# Path Resolution
# ==========================================================

def _resolve_project_root(variables: dict) -> Path:
    """
    Determine project root directory from variables.
    """
    project = variables.get("project")
    if project:
        p = Path(project).expanduser()
        if p.is_file():
            return p.parent.resolve()
        return p.resolve()
    return Path.cwd().resolve()


def _resolve_output_path(
    variables: dict,
    prefix: str,
    project_root: Path,
) -> Path:
    """
    Resolve output file path.

    Order:
        1. variables["dst"] if provided
        2. project_root with timestamped filename
    """
    dst_override = variables.get("dst")
    if isinstance(dst_override, str) and dst_override.strip():
        return Path(dst_override).expanduser()

    ts = datetime.utcnow().strftime("%Y%m%d.%H%M%S")
    return project_root / f"{prefix}.{ts}.toml"


# ==========================================================
# TOML Utilities
# ==========================================================

def _load_toml(src: Path):
    """
    Load TOML file from provided path.

    Raises:
        FileNotFoundError if file does not exist.
    """
    if not src.exists():
        raise FileNotFoundError(f"source file not found: {src}")
    return tomlkit.parse(src.read_text(encoding="utf-8"))


def _write_toml(doc, output_path: Path) -> Path:
    """
    Write TOML document to specified path.

    Creates parent directories if needed.

    Returns:
        Path to written file.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(tomlkit.dumps(doc), encoding="utf-8")
    return output_path


# ==========================================================
# Path Resolution Helpers
# ==========================================================

def _resolve_list_path(doc, dotted_path: str) -> Tuple[Any, str]:
    """
    Resolve dotted path for add operations.

    Auto-creates intermediate tables if missing.
    Ensures final leaf is a list (creates if absent).
    """
    segments = dotted_path.split(".")
    if not segments:
        raise ValueError("invalid path")

    current = doc

    for segment in segments[:-1]:
        if segment not in current:
            current[segment] = table()
        elif not isinstance(current[segment], dict):
            raise TypeError(f"path segment '{segment}' is not a table")
        current = current[segment]

    leaf = segments[-1]

    if leaf not in current:
        current[leaf] = array()
    elif not isinstance(current[leaf], list):
        raise TypeError(f"target '{leaf}' is not a list")

    return current, leaf


def _get_list_path(doc, dotted_path: str):
    """
    Resolve dotted path for show/remove operations.

    Requires list to already exist.
    """
    segments = dotted_path.split(".")
    if not segments:
        raise ValueError("invalid path")

    current = doc

    for segment in segments[:-1]:
        if segment not in current:
            raise KeyError(f"path segment '{segment}' not found")
        if not isinstance(current[segment], dict):
            raise TypeError(f"path segment '{segment}' is not a table")
        current = current[segment]

    leaf = segments[-1]

    if leaf not in current:
        raise KeyError(f"list '{leaf}' not found")
    if not isinstance(current[leaf], list):
        raise TypeError(f"target '{leaf}' is not a list")

    return current[leaf]


# ==========================================================
# Entry Point
# ==========================================================

def run_action(obj: str | None, value: str | None, variables: dict):
    """
    Dispatcher entry point for list verb.

    Returns:
        (ExitCode, payload)
    """

    if not obj or not value:
        return (
            ExitCode.INVALID_USAGE,
            "[error] list requires <action> <dotted.path> [value]",
        )

    action = obj
    dotted_path = value
    args: List[str] = variables.get("args", [])

    project_root = _resolve_project_root(variables)
    src_path = Path(variables.get("src") or project_root / "pyproject.toml")

    if action not in {"add", "remove", "show"}:
        return (
            ExitCode.INVALID_USAGE,
            f"[error] unsupported list action: {action}",
        )

    try:
        doc = _load_toml(src_path)
    except FileNotFoundError as exc:
        return (ExitCode.FAILURE, f"[error] {exc}")

    try:
        # ------------------------------------------
        # SHOW
        # ------------------------------------------
        if action == "show":
            target_list = _get_list_path(doc, dotted_path)
            payload = "\n".join(str(item) for item in target_list)
            return (ExitCode.SUCCESS, payload)

        # ------------------------------------------
        # ADD / REMOVE require value
        # ------------------------------------------
        if not args:
            return (
                ExitCode.INVALID_USAGE,
                "[error] missing list value",
            )

        list_value = args[0]

        if not isinstance(list_value, str):
            return (
                ExitCode.INVALID_USAGE,
                "[error] only string values supported",
            )

        if action == "add":
            parent, leaf = _resolve_list_path(doc, dotted_path)
            target_list = parent[leaf]

            if list_value not in target_list:
                target_list.append(list_value)

        if action == "remove":
            target_list = _get_list_path(doc, dotted_path)

            if list_value in target_list:
                target_list.remove(list_value)

        output_path = _resolve_output_path(
            variables,
            "purepoetry.list",
            project_root,
        )

        written = _write_toml(doc, output_path)
        return (ExitCode.SUCCESS, f"Output: {written}")

    except (ValueError, KeyError, TypeError) as exc:
        return (ExitCode.INVALID_USAGE, f"[error] {exc}")
    except Exception as exc:
        return (ExitCode.FAILURE, f"[error] {exc}")

    return ExitCode.SUCCESS


# ==========================================================
# Help Metadata
# ==========================================================

def get_help():
    """
    Structured help metadata for list verb.
    """
    return {
        "name": "list",
        "summary": "Modify lists in configuration files",
        "description": (
            "Safely display, add, or remove values from list fields "
            "in pyproject.toml. Writes changes to a new file "
            "and never mutates the source file. Honors --dst if provided."
        ),
        "usage": [
            "purepoetry list show <dotted.path>",
            "purepoetry list add <dotted.path> <value>",
            "purepoetry list remove <dotted.path> <value>",
            "purepoetry list add <dotted.path> <value> --dst <output.toml>",
        ],
    }
