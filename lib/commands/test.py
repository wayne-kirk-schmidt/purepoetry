#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
test.py
"""

import sys
sys.dont_write_bytecode = True

import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional


# ==========================================================
# Configuration
# ==========================================================

# This must be defined somewhere central later if desired.
OUTPUT_DIR = Path("/var/tmp")


# ==========================================================
# Project root resolution
# ==========================================================

def _resolve_project_root(variables: dict) -> Path:
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


# ==========================================================
# Flag helpers
# ==========================================================

def _is_truthy(val: Any) -> bool:
    if val is True:
        return True
    if val is False or val is None:
        return False
    if isinstance(val, (int, float)):
        return val != 0
    if isinstance(val, str):
        return val.strip().lower() in ("1", "true", "t", "yes", "y", "on")
    return False


def _is_verbose(variables: dict) -> bool:
    return _is_truthy(variables.get("verbose"))


def _get_dst(variables: dict) -> Optional[str]:
    v = variables.get("dst")
    if isinstance(v, str) and v.strip():
        return v.strip()
    return None


# ==========================================================
# Persistence
# ==========================================================

def _write_report(report: dict, path: Path) -> Path:
    """
    Write report to disk. Fail loudly if directory cannot be created
    or file cannot be written.
    """

    directory = path.parent

    try:
        directory.mkdir(parents=True, exist_ok=True)
    except Exception:
        print(f"[error] Unable to create output directory: {directory}")
        sys.exit(3)

    try:
        with path.open("w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
    except Exception:
        print(f"[error] Unable to write output file: {path}")
        sys.exit(4)

    return path


# ==========================================================
# Reporting
# ==========================================================

def _print_summary(report: dict) -> None:
    s = report["summary"]

    print("Registry v1 Audit")
    print("-----------------")
    print(f"Total rules: {s['total']}")
    print(f"PASS: {s['pass']}")
    print(f"WARN: {s['warn']}")
    print(f"FAIL: {s['fail']}")
    print()

    if s["fail"] > 0:
        overall = "FAIL"
    elif s["warn"] > 0:
        overall = "WARN"
    else:
        overall = "PASS"

    print(f"STATUS: {overall}")


def _print_verbose(report: dict) -> None:

    for r in sorted(report["results"], key=lambda x: x["id"]):
        status = "PASS" if r["passed"] else (
            "WARN" if r["severity"] == "WARN" else "FAIL"
        )

        description = r.get("description") or ""
        if r.get("error"):
            description = f"{description} (error: {r['error']})"

        print(f"[{r['id']}] {status:5} {description}")

    s = report["summary"]

    print("\n----------------------------------------")
    print("SUMMARY")
    print("----------------------------------------")
    print(f"PASS: {s['pass']}")
    print(f"WARN: {s['warn']}")
    print(f"FAIL: {s['fail']}")
    print("----------------------------------------")

    if s["fail"] > 0:
        overall = "FAIL"
    elif s["warn"] > 0:
        overall = "WARN"
    else:
        overall = "PASS"

    print(f"STATUS: {overall}")


# ==========================================================
# Execution
# ==========================================================

def _filter_rules(rules: List[Any], needle: str) -> List[Any]:
    n = needle.strip().upper()
    return [r for r in rules if n in str(r.id).upper()]


def _execute_rules(project_root: Path, rules: List[Any]) -> Dict[str, Any]:
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
# Entry point
# ==========================================================

def run_action(obj: str | None, value: str | None, variables: dict):

    from lib.registry.engine import discover_rules

    project_root = _resolve_project_root(variables)
    rules = discover_rules()

    if obj:
        selected = _filter_rules(rules, obj)
        if not selected:
            print(f"[error] No rules matched: {obj}")
            return 2
        rules = sorted(selected, key=lambda r: r.id)

    report = _execute_rules(project_root, rules)

    timestamp = datetime.utcnow().strftime("%Y%m%d.%H%M%S")

    dst_override = _get_dst(variables)

    if dst_override:
        output_path = Path(dst_override)
    else:
        output_path = OUTPUT_DIR / f"purepoetry.{report['project']}.{timestamp}.json"

    saved_path = _write_report(report, output_path)

    if _is_verbose(variables):
        _print_verbose(report)
    else:
        _print_summary(report)

    print(f"\nOutput: {saved_path}")

    return 1 if report["summary"]["fail"] > 0 else 0

