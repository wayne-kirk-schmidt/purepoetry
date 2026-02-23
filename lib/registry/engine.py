#!/usr/bin/env python3
# -*- coding: utf-8 -*-
### ================================================================
"""
purepoetry.registry.engine

Invariant execution engine.

Responsibilities:
  - Build execution context
  - Discover rule modules
  - Execute rule checks
  - Normalize results
  - Persist structured report to disk
  - Return structured report (no printing)
"""
### ================================================================

from __future__ import annotations

import sys
sys.dont_write_bytecode = True

from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import subprocess
import pkgutil
import importlib
import tomllib
import json


# ----------------------------------------------------------------
# Context Builder
# ----------------------------------------------------------------

def build_context(project_root: Path) -> Dict[str, Any]:
    project_root = project_root.resolve()

    pyproject_path = project_root / "pyproject.toml"
    lock_path = project_root / "poetry.lock"

    pyproject_data: Dict[str, Any] = {}
    if pyproject_path.exists():
        with pyproject_path.open("rb") as f:
            pyproject_data = tomllib.load(f)

    poetry_env_path = None
    try:
        result = subprocess.run(
            ["poetry", "env", "info", "--path"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
        )
        poetry_env_path = Path(result.stdout.strip())
    except Exception:
        poetry_env_path = None

    return {
        "project_root": project_root,
        "pyproject_path": pyproject_path,
        "lock_path": lock_path,
        "pyproject_data": pyproject_data,
        "poetry_env_path": poetry_env_path,
    }


# ----------------------------------------------------------------
# Rule Discovery
# ----------------------------------------------------------------

def discover_rules() -> List[Any]:
    from . import rules

    discovered = []

    for mod in pkgutil.iter_modules(rules.__path__):
        module = importlib.import_module(f"{rules.__name__}.{mod.name}")
        if hasattr(module, "RULE"):
            discovered.append(module.RULE)

    discovered.sort(key=lambda r: r.id)
    return discovered


# ----------------------------------------------------------------
# Engine Execution
# ----------------------------------------------------------------

def run(project_root: Path) -> Dict[str, Any]:
    started_at = datetime.utcnow()

    ctx = build_context(project_root)
    rules = discover_rules()

    results = []

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

    # ------------------------------------------------------------
    # Summary Classification
    # ------------------------------------------------------------

    pass_count = 0
    warn_count = 0
    fail_count = 0

    for r in results:
        if r["passed"]:
            pass_count += 1
        else:
            if r["severity"] == "WARN":
                warn_count += 1
            else:
                fail_count += 1

    summary = {
        "total": len(results),
        "pass": pass_count,
        "warn": warn_count,
        "fail": fail_count,
    }

    finished_at = datetime.utcnow()

    report = {
        "started_at": started_at.isoformat(),
        "finished_at": finished_at.isoformat(),
        "project": ctx["project_root"].name,
        "summary": summary,
        "results": results,
    }

    # ------------------------------------------------------------
    # Persist Report
    # ------------------------------------------------------------

    timestamp = started_at.strftime("%Y%m%d.%H%M%S")
    project_name = ctx["project_root"].name
    output_path = Path(f"/var/tmp/purepoetry.{project_name}.{timestamp}.json")

    try:
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
    except Exception:
        pass  # engine never throws on persistence failure

    return report

