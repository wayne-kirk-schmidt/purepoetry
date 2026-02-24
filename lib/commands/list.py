#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# pylint: disable = logging-fstring-interpolation, too-many-branches, unused-import
#

"""
show.py

Implements:

    purepoetry list show <dotted.path>
    purepoetry list add <dotted.path>=<string>
    purepoetry list remove <dotted.path>

Dispatcher calls:
    run_action(obj, value, variables)
"""

from __future__ import annotations

import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Any, List

import tomlkit
from tomlkit import table, array

sys.dont_write_bytecode = True

logger = logging.getLogger(__name__)


def _load_toml(src: Path):
    if not src.exists():
        raise FileNotFoundError(f"source file not found: {src}")
    return tomlkit.parse(src.read_text(encoding="utf-8"))


def _write_toml(doc, prefix: str = "purepoetry.list") -> Path:
    ts = datetime.utcnow().strftime("%Y%m%d.%H%M%S")
    out_path = Path(f"/var/tmp/{prefix}.{ts}.toml")
    out_path.write_text(tomlkit.dumps(doc), encoding="utf-8")
    return out_path


def _resolve_list_path(doc, dotted_path: str):
    """
    Walk dotted path.
    Auto-create intermediate tables.
    Ensure final segment is a list (create if missing).
    """
    segments = dotted_path.split(".")
    if not segments:
        raise ValueError("invalid path")

    current = doc

    # Walk intermediate segments
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
    Resolve path but require list to exist.
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


def run_action(obj: str, value: str, variables: dict):
    """
    obj      -> subcommand (add | remove | show)
    value    -> dotted path
    variables["args"] -> remaining CLI args (list value)
    variables["src"]  -> optional source file
    variables["verbose"] -> bool
    """

    action = obj
    dotted_path = value
    args: List[str] = variables.get("args", [])
    src_path = Path(variables.get("src") or "pyproject.toml")
    verbose = bool(variables.get("verbose"))

    if action not in {"add", "remove", "show"}:
        raise ValueError(f"unsupported list action: {action}")

    doc = _load_toml(src_path)

    if action == "show":
        target_list = _get_list_path(doc, dotted_path)
        for item in target_list:
            print(item)
        return

    if not args:
        raise ValueError("missing list value")

    list_value = args[0]

    if not isinstance(list_value, str):
        raise TypeError("only string values supported for list operations")

    if action == "add":
        parent, leaf = _resolve_list_path(doc, dotted_path)
        target_list = parent[leaf]

        if list_value in target_list:
            if verbose:
                logger.info("value already present (no-op)")
        else:
            target_list.append(list_value)
            if verbose:
                logger.info(f"appended '{list_value}'")

        out_path = _write_toml(doc)
        print(f"Output: {out_path}")
        return

    if action == "remove":
        target_list = _get_list_path(doc, dotted_path)

        if list_value in target_list:
            target_list.remove(list_value)
            if verbose:
                logger.info(f"removed '{list_value}'")
        else:
            if verbose:
                logger.info("value not present (no-op)")

        out_path = _write_toml(doc)
        print(f"Output: {out_path}")
        return
