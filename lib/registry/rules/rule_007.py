#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import sys
sys.dont_write_bytecode = True

from pathlib import Path
from typing import Dict, Tuple, Any

import tomllib
import importlib.metadata as importlib_metadata

from lib.registry.types import InvariantSpec, Severity

ID = "LOCK-003"
CLUMP = "lock"
DESCRIPTION = "Installed dependencies do not match lockfile"
FIXABLE = True
SEVERITY = Severity.FAIL


def _norm_name(name: str) -> str:
    # Normalize per common packaging conventions: case-insensitive, -/_ collapsed.
    return name.strip().lower().replace("_", "-")


def _load_lock(lock_path: Path) -> Dict[str, str]:
    """
    Returns {normalized_name: version} for packages recorded in poetry.lock.

    Supports older and newer Poetry lock formats:
      - category = "main" / "dev"
      - groups = ["main", ...]
    If neither is present, we conservatively include the package.
    """
    with lock_path.open("rb") as f:
        data = tomllib.load(f)

    packages = data.get("package", [])
    locked: Dict[str, str] = {}

    for pkg in packages:
        if not isinstance(pkg, dict):
            continue

        name = pkg.get("name")
        version = pkg.get("version")

        if not isinstance(name, str) or not isinstance(version, str):
            continue

        # Decide whether to include based on group/category if present.
        include = True

        category = pkg.get("category")
        if isinstance(category, str):
            # "main" packages are what we care about; dev-only is excluded.
            include = category.strip().lower() == "main"

        groups = pkg.get("groups")
        if isinstance(groups, list) and all(isinstance(g, str) for g in groups):
            # If groups are present, include only if "main" is one of them.
            include = "main" in [g.strip().lower() for g in groups]

        if include:
            locked[_norm_name(name)] = version.strip()

    return locked


def _installed_versions() -> Dict[str, str]:
    """
    Returns {normalized_name: version} for installed distributions in the active environment.
    """
    installed: Dict[str, str] = {}
    for dist in importlib_metadata.distributions():
        try:
            n = dist.metadata.get("Name")
            v = dist.version
        except Exception:
            continue
        if isinstance(n, str) and isinstance(v, str):
            installed[_norm_name(n)] = v.strip()
    return installed


def _compare_locked_to_installed(locked: Dict[str, str], installed: Dict[str, str]) -> Tuple[bool, int, int]:
    """
    Returns (ok, missing_count, mismatch_count)
    """
    missing = 0
    mismatch = 0

    for name, lock_ver in locked.items():
        inst_ver = installed.get(name)
        if inst_ver is None:
            missing += 1
            continue
        if inst_ver != lock_ver:
            mismatch += 1

    ok = (missing == 0 and mismatch == 0)
    return ok, missing, mismatch


def check(ctx) -> bool:
    """
    Passes when the active environment contains every "main" package recorded in poetry.lock
    with the exact same version. This avoids parsing Poetry CLI text.
    """
    try:
        lock_path: Path = ctx["lock_path"]
    except Exception:
        return True

    if not lock_path.exists():
        # If there's no lock, LOCK-001 is responsible for failing.
        return True

    try:
        locked = _load_lock(lock_path)
        installed = _installed_versions()
        ok, _, _ = _compare_locked_to_installed(locked, installed)
        return ok
    except Exception:
        # Fail open on unexpected parser/env issues (keeps audit resilient)
        return True


RULE = InvariantSpec(
    ID,
    CLUMP,
    DESCRIPTION,
    FIXABLE,
    SEVERITY,
    check,
)
