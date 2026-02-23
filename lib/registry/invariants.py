#!/usr/bin/env python3
# -*- coding: utf-8 -*-
### ================================================================
"""
purepoetry.registry.invariants

Invariant registry (v1).

This module is the single source of truth for:
  - what can be checked (checkup)
  - what is fixable (heal/fix)
  - what help should explain

Notes:
  - Checks are stubs in v1. Real implementations will be introduced in
    the doctor/heal engine layer.
"""
### ================================================================

from __future__ import annotations

from typing import Dict, Any, List, Optional

from .types import InvariantSpec, Severity


def _stub_check(_ctx: Dict[str, Any]) -> bool:
    """Placeholder check function (always true)."""
    return True


# Clumps:
#   env  – interpreter & virtualenv consistency (check-only)
#   lock – lockfile & dependency graph integrity (fixable)
#   pkg  – packaging/layout/entrypoints (mostly fixable)
#   meta – required metadata (fixable with placeholders)
#   sys  – platform/system constraints (check-only)

INVARIANTS: List[InvariantSpec] = [
    # ENV (check-only)
    InvariantSpec("ENV-001", "env", "Python interpreter mismatch", False, Severity.FAIL, _stub_check),
    InvariantSpec("ENV-002", "env", "Multiple Poetry virtualenvs bound to project", False, Severity.FAIL, _stub_check),
    InvariantSpec("ENV-003", "env", "Python version out of declared range", False, Severity.FAIL, _stub_check),

    # LOCK (fixable)
    InvariantSpec("LOCK-001", "lock", "Lockfile missing", True, Severity.FAIL, _stub_check),
    InvariantSpec("LOCK-002", "lock", "Lockfile drift detected (pyproject != lock)", True, Severity.FAIL, _stub_check),
    InvariantSpec("LOCK-003", "lock", "Installed dependencies do not match lockfile", True, Severity.FAIL, _stub_check),
    InvariantSpec("LOCK-004", "lock", "Editable install mismatch for local package", True, Severity.FAIL, _stub_check),

    # PKG (mixed)
    InvariantSpec("PKG-001", "pkg", "Declared package path missing", True, Severity.FAIL, _stub_check),
    InvariantSpec("PKG-002", "pkg", "Missing __init__.py (package not importable)", True, Severity.FAIL, _stub_check),
    InvariantSpec("PKG-003", "pkg", "Script entrypoint target missing", True, Severity.FAIL, _stub_check),
    InvariantSpec("PKG-004", "pkg", "Import fails at runtime (beyond structure)", False, Severity.FAIL, _stub_check),

    # META (mostly fixable)
    InvariantSpec("META-001", "meta", "Missing required metadata (name/version/python)", True, Severity.FAIL, _stub_check),
    InvariantSpec("META-002", "meta", "Missing author information", True, Severity.WARN, _stub_check),
    InvariantSpec("META-003", "meta", "Missing project URLs (homepage/repo/docs)", False, Severity.WARN, _stub_check),

    # SYS (check-only)
    InvariantSpec("SYS-001", "sys", "Platform build risk detected", False, Severity.WARN, _stub_check),
    InvariantSpec("SYS-002", "sys", "Native dependency requires system libraries/toolchain", False, Severity.WARN, _stub_check),
]


def all_invariants() -> List[InvariantSpec]:
    return list(INVARIANTS)


def invariants_by_clump(clump: str) -> List[InvariantSpec]:
    return [i for i in INVARIANTS if i.clump == clump]


def invariant_by_id(invariant_id: str) -> Optional[InvariantSpec]:
    for inv in INVARIANTS:
        if inv.id == invariant_id:
            return inv
    return None


def clumps() -> List[str]:
    return sorted({i.clump for i in INVARIANTS})
