#!/usr/bin/env python3
#
# pylint: disable=import-error
# pylint: disable=import-outside-toplevel
# pylint: disable=broad-exception-caught
# pylint: disable=too-many-return-statements
# pylint: disable=too-many-locals
#
# -*- coding: utf-8 -*-

"""
edit.py

Non-destructive TOML editor.

Behavior:
    - Never mutates original file
    - Writes modified copy to disk
    - Honors --dst if provided
    - Defaults to project directory if --dst not provided
    - Returns (ExitCode, payload)
"""

from __future__ import annotations

import sys
from pathlib import Path
from datetime import datetime
from typing import Tuple, Any

import tomlkit

from lib.utilities.exitcodes import ExitCode

sys.dont_write_bytecode = True


# ==========================================================
# Path Resolution
# ==========================================================

def _resolve_project_root(variables: dict) -> Path:
    """
    Determine project root directory from variables.

    Returns:
        Resolved Path
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

def _load_toml(path: Path):
    """
    Load TOML document from disk.

    Raises:
        FileNotFoundError if missing.
    """
    if not path.exists():
        raise FileNotFoundError("pyproject.toml not found")
    return tomlkit.parse(path.read_text(encoding="utf-8"))


def _write_toml(doc, path: Path) -> Path:
    """
    Write TOML document to specified path.

    Returns:
        Path written.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(tomlkit.dumps(doc), encoding="utf-8")
    return path


def _navigate_path(data, dotted: str) -> Tuple[Any, str]:
    """
    Traverse TOML document using dotted path.

    Returns:
        (parent_node, leaf_key)

    Returns (None, "") if path invalid.
    """
    parts = dotted.split(".")
    current = data

    for part in parts[:-1]:
        if part not in current:
            return None, ""
        current = current[part]

    return current, parts[-1]


# ==========================================================
# Entry Point
# ==========================================================

def run_action(obj: str | None, value: str | None, variables: dict):
    """
    Execute edit operation.

    Args:
        obj: dotted path
        value: new value
        variables: CLI context

    Returns:
        (ExitCode, payload)
    """

    if not obj or value is None:
        return (
            ExitCode.INVALID_USAGE,
            "[error] edit requires <dotted.path> <value>",
        )

    project_root = _resolve_project_root(variables)
    source_path = project_root / "pyproject.toml"

    try:
        doc = _load_toml(source_path)
    except FileNotFoundError as exc:
        return (ExitCode.FAILURE, f"[error] {exc}")

    parent, key = _navigate_path(doc, obj)

    if parent is None or key == "":
        return (
            ExitCode.INVALID_USAGE,
            f"[error] path not found: {obj}",
        )

    old_value = parent.get(key)

    # No change case
    if old_value == value:
        return (
            ExitCode.SUCCESS,
            f"NO CHANGE {obj}",
        )

    # Type coercion for existing keys
    if key in parent:
        try:
            if isinstance(old_value, bool):
                coerced = value.lower() in ("1", "true", "yes", "on")
            elif isinstance(old_value, int):
                coerced = int(value)
            elif isinstance(old_value, float):
                coerced = float(value)
            else:
                coerced = value
        except Exception as exc:
            return (
                ExitCode.INVALID_USAGE,
                f"[error] type conversion failed: {exc}",
            )

        parent[key] = coerced

        payload = (
            f"UPDATED {obj}\n"
            f"  old: {old_value}\n"
            f"  new: {coerced}"
        )

    else:
        parent[key] = value
        payload = (
            f"ADDED {obj}\n"
            f"  value: {value}"
        )

    output_path = _resolve_output_path(
        variables,
        "purepoetry.edit",
        project_root,
    )

    written = _write_toml(doc, output_path)

    payload += f"\n\nOutput: {written}"

    return (ExitCode.SUCCESS, payload)


# ==========================================================
# Help Metadata
# ==========================================================

def get_help():
    """
    Structured help metadata for edit verb.
    """
    return {
        "name": "edit",
        "summary": "Modify keys and values in configuration safely",
        "description": (
            "Safely modify values in pyproject.toml. "
            "Writes changes to a new file and never mutates the source file. "
            "Honors --dst if provided."
        ),
        "usage": [
            "purepoetry edit <dotted.path> <value>",
            "purepoetry edit <dotted.path> <value> --dst <output.toml>",
        ],
    }
