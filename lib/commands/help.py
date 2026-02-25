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
help.py

Strict, fully data-driven help system.

All help content is delegated to verbs via get_help().

Each verb must implement:

    def get_help() -> dict:
        {
            "name": str,
            "summary": str,
            "description": str,
            "usage": list[str],
        }

If any key is missing, help will fail loudly.
"""

from __future__ import annotations

import sys
from typing import Dict, List, Tuple

from lib.utilities.exitcodes import ExitCode

sys.dont_write_bytecode = True

_REGISTRY_CATEGORIES: Tuple[str, ...] = ("types", "invariants", "fixes")


# ==========================================================
# Contract Enforcement
# ==========================================================

def _validate_help_shape(help_data: Dict) -> None:
    """
    Enforce strict get_help() contract.

    Required keys:
        - name (str)
        - summary (str)
        - description (str)
        - usage (list[str])
    """
    required = {"name", "summary", "description", "usage"}
    missing = required - set(help_data.keys())

    if missing:
        raise RuntimeError(
            f"Invalid get_help() shape. Missing keys: {sorted(missing)}"
        )

    if not isinstance(help_data["usage"], list):
        raise RuntimeError("get_help()['usage'] must be a list of strings")


# ==========================================================
# Rendering
# ==========================================================

def _render_header() -> List[str]:
    """
    Render the standard PurePoetry header frame.
    """
    return [
        "PurePoetry — governance CLI for Poetry projects",
        "",
        "Usage:",
        "  purepoetry <verb> <object> [keypath|options]",
        "",
    ]


def _render_full_help(help_data: Dict) -> List[str]:
    """
    Render a full help block for a specific verb.
    """
    lines: List[str] = []
    lines.append(f"Command: {help_data['name']}")
    lines.append("")
    lines.append("Purpose:")
    lines.append(f"  {help_data['description']}")
    lines.append("")
    lines.append("Usage:")
    for line in help_data["usage"]:
        lines.append(f"  {line}")
    lines.append("")
    return lines


# ==========================================================
# run_help() — REQUIRED by bin/purepoetry.py
# ==========================================================

def run_help(tokens: List[str], registry: Dict[str, str]) -> ExitCode:
    """
    Render help output for PurePoetry.

    This function is imported and called by bin/purepoetry.py.

    Args:
        tokens: CLI tokens after 'help' (e.g., ['test']).
        registry: Mapping of verb -> module path.

    Returns:
        ExitCode
    """
    lines: List[str] = []
    lines.extend(_render_header())

    # ---------------------------------------------------------
    # MAIN HELP
    # ---------------------------------------------------------
    if not tokens:
        lines.append("Available commands:")

        for verb in sorted(registry.keys()):
            module_path = registry[verb]
            module = __import__(module_path, fromlist=["*"])

            if not hasattr(module, "get_help"):
                raise RuntimeError(f"Verb '{verb}' missing get_help()")

            help_data = module.get_help()
            _validate_help_shape(help_data)

            lines.append(f"  {verb:6} {help_data['summary']}")

        print("\n".join(lines))
        return ExitCode.SUCCESS

    topic = tokens[0].strip().lower()

    # ---------------------------------------------------------
    # VERB-SPECIFIC HELP
    # ---------------------------------------------------------
    if topic in registry:
        module_path = registry[topic]
        module = __import__(module_path, fromlist=["*"])

        if not hasattr(module, "get_help"):
            raise RuntimeError(f"Verb '{topic}' missing get_help()")

        help_data = module.get_help()
        _validate_help_shape(help_data)

        lines.append("-" * 56)
        lines.extend(_render_full_help(help_data))

        print("\n".join(lines))
        return ExitCode.SUCCESS

    # ---------------------------------------------------------
    # REGISTRY INFO
    # ---------------------------------------------------------
    if topic == "registry":
        lines.append("-" * 56)
        lines.append("Registry defines what PurePoetry knows about the system.")
        lines.append("")
        lines.append("Categories:")
        for c in _REGISTRY_CATEGORIES:
            lines.append(f"  {c}")

        print("\n".join(lines))
        return ExitCode.SUCCESS

    # ---------------------------------------------------------
    # UNKNOWN
    # ---------------------------------------------------------
    lines.append("-" * 56)
    lines.append(f"[error] Unknown help topic: {topic}")

    print("\n".join(lines))
    return ExitCode.INVALID_USAGE


# ==========================================================
# Verb contract entry point
# ==========================================================

def run_action(obj: str | None, _value: str | None, variables: dict):
    """
    Contract-compliant entry point for the help verb.

    Args:
        obj: topic (e.g., 'test', 'registry') or None for main help
        value: unused
        variables: must include 'registry'

    Returns:
        (ExitCode, payload) where payload is empty because run_help prints output.
    """
    registry = variables.get("registry")
    if not isinstance(registry, dict):
        return (ExitCode.FAILURE, "[error] help requires registry in variables")

    tokens: List[str] = []
    if obj:
        tokens.append(obj)

    code = run_help(tokens, registry)
    return (code, "")


# ==========================================================
# Help Metadata
# ==========================================================

def get_help():
    """
    Structured help metadata for the help verb itself.
    """
    return {
        "name": "help",
        "summary": "Show help information for commands and registry.",
        "description": (
            "Display global help, command-specific help, "
            "or registry information."
        ),
        "usage": [
            "purepoetry help",
            "purepoetry help <command>",
            "purepoetry help registry",
        ],
    }
