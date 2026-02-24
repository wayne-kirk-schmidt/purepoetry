#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
edit.py

Non-destructive TOML editor.
Creates a modified copy in /var/tmp.
Never mutates source file.
Preserves formatting and comments.
"""

from pathlib import Path
from datetime import datetime
from typing import Tuple, Any

import sys
import tomlkit

sys.dont_write_bytecode = True

OUTPUT_DIR = Path("/var/tmp")


def _resolve_project_root(variables: dict) -> Path:
    """ determine the location of the project root based on input """
    project = variables.get("project")
    if project:
        p = Path(project).expanduser()
        if p.is_file():
            return p.parent.resolve()
        return p.resolve()
    return Path.cwd().resolve()


def _load_toml(path: Path):
    """ load the toml file of the project as specified """
    with path.open("r", encoding="utf-8") as f:
        return tomlkit.parse(f.read())


def _write_toml(doc, path: Path) -> None:
    """ write out a toml file of the project as specified """
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write(tomlkit.dumps(doc))


def _navigate_path(data, dotted: str) -> Tuple[Any, str]:
    """ traverse the toml file as a dotted path """
    parts = dotted.split(".")
    current = data

    for part in parts[:-1]:
        if part not in current:
            return None, ""
        current = current[part]

    return current, parts[-1]


def run_action(obj: str | None, value: str | None, variables: dict):
    """ this is an run_action helping the file determine either run or help """
    if not obj or value is None:
        print("[error] edit requires <path> <value>")
        return 2

    project_root = _resolve_project_root(variables)
    source_path = project_root / "pyproject.toml"

    if not source_path.exists():
        print("[error] pyproject.toml not found")
        return 3

    doc = _load_toml(source_path)

    parent, key = _navigate_path(doc, obj)

    if parent is None or key == "":
        print(f"[error] path not found: {obj}")
        return 4

    old_value = parent.get(key)

    if old_value == value:
        print(f"NO CHANGE {obj}")
        return 0

    if key in parent:
        # Preserve existing type
        if isinstance(old_value, bool):
            coerced = value.lower() in ("1", "true", "yes", "on")
        elif isinstance(old_value, int):
            coerced = int(value)
        elif isinstance(old_value, float):
            coerced = float(value)
        else:
            coerced = value

        parent[key] = coerced

        print(f"UPDATED {obj}")
        print(f"  old: {old_value}")
        print(f"  new: {coerced}")

    else:
        # For new keys, keep as string for now (safe default)
        parent[key] = value
        print(f"ADDED {obj}")
        print(f"  value: {value}")

    timestamp = datetime.utcnow().strftime("%Y%m%d.%H%M%S")
    output_path = OUTPUT_DIR / f"purepoetry.edit.{timestamp}.toml"

    _write_toml(doc, output_path)

    print(f"\nOutput: {output_path}")

    return 0
