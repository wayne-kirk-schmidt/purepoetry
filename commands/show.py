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

import sys
sys.dont_write_bytecode = True

import json
import tomllib
from pathlib import Path


# ==========================================================
# CONFIG DOMAIN
# ==========================================================

def _load_pyproject(variables: dict) -> dict:
    path = variables.get("pyproject_path", "pyproject.toml")
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
            raise KeyError(f"Path not found: {dotted_path}")

    return current


def _handle_config(value: str | None, variables: dict):
    data = _load_pyproject(variables)
    all_paths = sorted(_collect_dotted_paths(data))

    if value is None:
        return "\n".join(all_paths)

    if value in all_paths:
        resolved = _resolve_dotted_path(data, value)
        if isinstance(resolved, (dict, list)):
            return f"{value}\n{json.dumps(resolved, indent=2)}"
        else:
            return f"{value}\n{resolved}"

    matches = [p for p in all_paths if value in p]

    if matches:
        return "\n".join(sorted(matches))

    print(f"[error] Path not found: {value}")
    return 2


# ==========================================================
# RULES DOMAIN
# ==========================================================

def _handle_rules(value: str | None):
    from lib.registry.invariants import all_invariants, invariant_by_id

    invariants = all_invariants()
    rule_ids = sorted(inv.id for inv in invariants)

    # show rules
    if value is None:
        return "\n".join(rule_ids)

    # exact match
    inv = invariant_by_id(value)
    if inv is not None:
        return (
            f"{inv.id}\n"
            f"  clump:            {inv.clump}\n"
            f"  severity_on_fail: {inv.severity_on_fail.value}\n"
            f"  fixable:          {inv.fixable}\n"
            f"  description:      {inv.description}"
        )

    # substring match
    matches = [rid for rid in rule_ids if value.upper() in rid]

    if matches:
        return "\n".join(matches)

    print(f"[error] Rule not found: {value}")
    return 2


# ==========================================================
# ENTRY POINT
# ==========================================================

def run_action(obj: str | None, value: str | None, variables: dict):

    if obj is None:
        print("[error] You must provide an object for 'show'.")
        print("Try:")
        print("  purepoetry show config")
        print("  purepoetry show rules")
        return 2

    if obj == "config":
        return _handle_config(value, variables)

    if obj == "rules":
        return _handle_rules(value)

    print(f"[error] Unsupported object for show: {obj}")
    print("Supported objects:")
    print("  config")
    print("  rules")
    return 2

