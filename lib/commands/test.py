#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
test.py

Evaluate project configuration against registry-defined invariant rules.

Behavior:
    - Executes invariant rules discovered from registry
    - Produces structured JSON report
    - Honors --dst override if provided
    - Returns (ExitCode, payload)
    - Does NOT print directly
"""

from __future__ import annotations

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List

from lib.utilities.exitcodes import ExitCode

sys.dont_write_bytecode = True

DEFAULT_OUTPUT_DIR = Path("/var/tmp")


# ==========================================================
# Help Metadata
# ==========================================================

def get_help() -> dict:
    """
    Provide structured help metadata for dynamic help rendering.

    Returns:
        dict:
            {
                "name": str,
                "summary": str,
                "description": str,
                "usage": list[str],
            }
    """
    return {
        "name": "test",
        "summary": "Evaluate project configuration against invariant rules",
        "description": (
            "Execute registry-driven invariant rules against the project. "
            "Produces structured JSON audit report."
        ),
        "usage": [
            "purepoetry test",
            "purepoetry test <rule-id>",
            "purepoetry test --verbose",
            "purepoetry test --dst <output.json>",
        ],
    }


# ==========================================================
# Path / Flag Helpers
# ==========================================================

def _resolve_project_root(variables: dict) -> Path:
    """
    Resolve project root directory from CLI variables.

    Args:
        variables (dict): CLI variable dictionary.

    Returns:
        Path: Absolute resolved project root.
    """
    project_arg = variables.get("project")

    if not project_arg:
        return Path.cwd().resolve()

    p = Path(project_arg).expanduser()

    if str(p).lower().endswith(".toml"):
        return p.parent.resolve()

    if p.exists():
        if p.is_dir():
            return p.resolve()
        return p.parent.resolve()

    return p.resolve()


def _is_truthy(val: Any) -> bool:
    """
    Interpret CLI flag values into boolean.

    Args:
        val (Any): Value from CLI variables.

    Returns:
        bool: True if value represents truth.
    """
    if val is True:
        return True
    if val in (False, None):
        return False
    if isinstance(val, (int, float)):
        return val != 0
    if isinstance(val, str):
        return val.strip().lower() in ("1", "true", "t", "yes", "y", "on")
    return False


def _is_verbose(variables: dict) -> bool:
    """
    Determine whether verbose mode is enabled.

    Args:
        variables (dict): CLI variable dictionary.

    Returns:
        bool: True if verbose output requested.
    """
    return _is_truthy(variables.get("verbose"))


def _resolve_output_path(variables: dict, project_name: str) -> Path:
    """
    Determine output path for JSON report.

    Resolution order:
        1. variables["dst"] if provided
        2. default /var/tmp with timestamp

    Args:
        variables (dict): CLI variables.
        project_name (str): Name of project (for filename).

    Returns:
        Path: Output file path.
    """
    dst_override = variables.get("dst")

    if isinstance(dst_override, str) and dst_override.strip():
        return Path(dst_override).expanduser()

    ts = datetime.utcnow().strftime("%Y%m%d.%H%M%S")
    return DEFAULT_OUTPUT_DIR / f"purepoetry.{project_name}.{ts}.json"


# ==========================================================
# Persistence
# ==========================================================

def _write_report(report: dict, path: Path) -> Path:
    """
    Write JSON audit report to disk.

    Args:
        report (dict): Audit report payload.
        path (Path): Target output file path.

    Returns:
        Path: Written file path.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return path


# ==========================================================
# Rule Execution
# ==========================================================

def _filter_rules(rules: List[Any], needle: str) -> List[Any]:
    """
    Filter rules by substring match against rule ID.

    Args:
        rules (List[Any]): Rule objects.
        needle (str): Filter string.

    Returns:
        List[Any]: Filtered rule set.
    """
    n = needle.strip().upper()
    return [r for r in rules if n in str(r.id).upper()]


def _execute_rules(project_root: Path, rules: List[Any]) -> Dict[str, Any]:
    """
    Execute rules against project context.

    Args:
        project_root (Path): Target project root.
        rules (List[Any]): Rule objects to execute.

    Returns:
        dict: Structured audit report.
    """
    from lib.registry.engine import build_context

    started_at = datetime.utcnow()
    ctx = build_context(project_root)

    results: List[Dict[str, Any]] = []

    for rule in rules:
        try:
            passed = bool(rule.check(ctx))
            error = None
        except Exception as exc:
            passed = False
            error = str(exc)

        results.append({
            "id": rule.id,
            "clump": rule.clump,
            "description": rule.description,
            "severity": rule.severity.name,
            "fixable": rule.fixable,
            "passed": passed,
            "error": error,
        })

    pass_count = sum(1 for r in results if r["passed"])
    warn_count = sum(1 for r in results if not r["passed"] and r["severity"] == "WARN")
    fail_count = sum(1 for r in results if not r["passed"] and r["severity"] != "WARN")

    summary = {
        "total": len(results),
        "pass": pass_count,
        "warn": warn_count,
        "fail": fail_count,
    }

    return {
        "started_at": started_at.isoformat(),
        "project": ctx["project_root"].name,
        "summary": summary,
        "results": results,
    }


# ==========================================================
# Rendering
# ==========================================================

def _render_summary(report: dict, verbose: bool) -> str:
    """
    Render audit results into human-readable text.

    Args:
        report (dict): Structured audit report.
        verbose (bool): Whether to render detailed results.

    Returns:
        str: Rendered output string.
    """
    s = report["summary"]

    if s["fail"] > 0:
        overall = "FAIL"
    elif s["warn"] > 0:
        overall = "WARN"
    else:
        overall = "PASS"

    if not verbose:
        return (
            "Registry v1 Audit\n"
            "-----------------\n"
            f"Total rules: {s['total']}\n"
            f"PASS: {s['pass']}\n"
            f"WARN: {s['warn']}\n"
            f"FAIL: {s['fail']}\n\n"
            f"STATUS: {overall}"
        )

    lines = []
    for r in sorted(report["results"], key=lambda x: x["id"]):
        status = "PASS" if r["passed"] else (
            "WARN" if r["severity"] == "WARN" else "FAIL"
        )
        desc = r.get("description") or ""
        if r.get("error"):
            desc = f"{desc} (error: {r['error']})"
        lines.append(f"[{r['id']}] {status:5} {desc}")

    lines.append("\n----------------------------------------")
    lines.append("SUMMARY")
    lines.append("----------------------------------------")
    lines.append(f"PASS: {s['pass']}")
    lines.append(f"WARN: {s['warn']}")
    lines.append(f"FAIL: {s['fail']}")
    lines.append("----------------------------------------")
    lines.append(f"STATUS: {overall}")

    return "\n".join(lines)


# ==========================================================
# Entry Point
# ==========================================================

def run_action(obj: str | None, value: str | None, variables: dict):
    """
    Execute the test verb.

    Behavior:
        - Always returns ExitCode.SUCCESS for governance results
        - Only returns non-zero if execution fails or invalid usage occurs
        - Governance FAIL/WARN states are encoded in the report payload

    Args:
        obj (Optional[str]): Optional rule ID filter.
        value (Optional[str]): Reserved (unused).
        variables (dict): CLI context variables.

    Returns:
        (ExitCode, str): Exit code and rendered payload.
    """
    from lib.registry.engine import discover_rules

    project_root = _resolve_project_root(variables)
    rules = discover_rules()

    if obj:
        selected = _filter_rules(rules, obj)
        if not selected:
            return (
                ExitCode.INVALID_USAGE,
                f"[error] No rules matched: {obj}",
            )
        rules = sorted(selected, key=lambda r: r.id)

    report = _execute_rules(project_root, rules)

    output_path = _resolve_output_path(
        variables,
        report["project"],
    )

    written = _write_report(report, output_path)

    payload = _render_summary(
        report,
        _is_verbose(variables),
    )

    payload += f"\n\nOutput: {written}"

    return (ExitCode.SUCCESS, payload)
