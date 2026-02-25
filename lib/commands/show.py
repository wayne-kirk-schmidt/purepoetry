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
show.py

Implements:

    purepoetry show config
    purepoetry show config <string>
    purepoetry show config <dotted.path>

    purepoetry show rules
    purepoetry show rules <string>
    purepoetry show rules <rule.name>

Grammar enforced by dispatcher:
    verb   = show
    object = domain (config | rules)
    value  = optional string / dotted.path

Dispatcher calls:
    run_action(obj, value, variables)
"""

from __future__ import annotations

import sys
import json
import tomllib
from pathlib import Path

from lib.utilities.exitcodes import ExitCode

sys.dont_write_bytecode = True


# ==========================================================
# Utilities
# ==========================================================

def _error(message: str):
    return (ExitCode.INVALID_USAGE, f"[error] {message}")


def _success(payload: str):
    return (ExitCode.SUCCESS, payload)


def _normalize_value(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped if stripped else None


# ==========================================================
# CONFIG DOMAIN
# ==========================================================

def _load_pyproject(variables: dict) -> dict:
    path = variables.get("src") or variables.get("default_srcfile", "pyproject.toml")
    pyproject_path = Path(path)

    if not pyproject_path.exists():
        raise FileNotFoundError(f"pyproject.toml not found at: {pyproject_path}")

    with pyproject_path.open("rb") as f:
        return tomllib.load(f)


def _collect_dotted_paths(data, prefix=""):
    paths = []

    if isinstance(data, dict):
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            paths.append(full_key)
            paths.extend(_collect_dotted_paths(value, full_key))

    return paths


def _resolve_dotted_path(data, dotted_path):
    keys = dotted_path.split(".")
    current = data

    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            raise KeyError(dotted_path)

    return current


def _handle_config(value: str | None, variables: dict):
    value = _normalize_value(value)

    try:
        data = _load_pyproject(variables)
    except FileNotFoundError as exc:
        return _error(str(exc))

    all_paths = sorted(_collect_dotted_paths(data))

    if value is None:
        return _success("\n".join(all_paths))

    if value in all_paths:
        try:
            resolved = _resolve_dotted_path(data, value)
        except KeyError:
            return _error(f"Path not found: {value}")

        if isinstance(resolved, (dict, list)):
            formatted = json.dumps(resolved, indent=2)
        else:
            formatted = str(resolved)

        return _success(f"{value}\n{formatted}")

    matches = [p for p in all_paths if value in p]

    if matches:
        return _success("\n".join(sorted(matches)))

    return _error(f"Path not found: {value}")


# ==========================================================
# RULES DOMAIN
# ==========================================================

def _handle_rules(value: str | None):
    value = _normalize_value(value)

    from lib.registry.invariants import all_invariants, invariant_by_id

    invariants = all_invariants()
    rule_ids = sorted(inv.id for inv in invariants)

    if value is None:
        return _success("\n".join(rule_ids))

    inv = invariant_by_id(value)
    if inv is not None:
        formatted = (
            f"{inv.id}\n"
            f"  clump:            {inv.clump}\n"
            f"  severity_on_fail: {inv.severity_on_fail.value}\n"
            f"  fixable:          {inv.fixable}\n"
            f"  description:      {inv.description}"
        )
        return _success(formatted)

    matches = [rid for rid in rule_ids if value.upper() in rid]

    if matches:
        return _success("\n".join(matches))

    return _error(f"Rule not found: {value}")


# ==========================================================
# Help Metadata
# ==========================================================

def get_help():
    """
    Structured help metadata for show verb.
    """
    return {
        "name": "show",
        "summary": "Display configuration or rule metadata (read-only)",
        "description": (
            "Display configuration keys or rule metadata in read-only mode. "
            "Supports dotted path resolution and substring matching."
        ),
        "usage": [
            "purepoetry show config",
            "purepoetry show config <dotted.path>",
            "purepoetry show rules",
            "purepoetry show rules <rule-id>",
        ],
    }


# ==========================================================
# Entry Point
# ==========================================================

def run_action(obj: str | None, value: str | None, variables: dict):
    """ define the run action for show, as we have objects and then sub objects """
    if obj is None:
        return _error(
            "You must provide an object for 'show'. "
            "Try: purepoetry show config | purepoetry show rules"
        )

    if obj == "config":
        return _handle_config(value, variables)

    if obj == "rules":
        return _handle_rules(value)

    return _error(
        f"Unsupported object for show: {obj}. "
        "Supported objects: config, rules"
    )
