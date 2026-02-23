#!/usr/bin/env python3
# -*- coding: utf-8 -*-
### ================================================================
"""
purepoetry.registry.fixes

Fix registry (v1).

This module declares *what* can be fixed (and how), but handlers are stubs.
heal/fix orchestration should consult this registry and only apply:
  - for failed invariants
  - where fix exists
  - respecting --dry-run

No side-effects should happen at import time.
"""
### ================================================================

from __future__ import annotations

from typing import Dict, Any, List

from .types import FixSpec, FixTier


def _stub_fix(_ctx: Dict[str, Any]) -> None:
    raise NotImplementedError("Fix handler not implemented yet.")


# Fix IDs should be stable and tied to an invariant.
# Convention: <INVARIANT>-<LETTER> (e.g., LOCK-002-A)
FIXES: List[FixSpec] = [
    FixSpec("LOCK-001-A", "LOCK-001", "Regenerate poetry.lock", FixTier.SAFE, _stub_fix),
    FixSpec("LOCK-002-A", "LOCK-002", "Regenerate poetry.lock", FixTier.SAFE, _stub_fix),
    FixSpec("LOCK-003-A", "LOCK-003", "Sync environment to lockfile (poetry install)", FixTier.CONDITIONAL, _stub_fix),
    FixSpec("LOCK-004-A", "LOCK-004", "Reinstall local package editable state", FixTier.CONDITIONAL, _stub_fix),

    FixSpec("PKG-001-A", "PKG-001", "Repair declared package path (structure-only)", FixTier.CONDITIONAL, _stub_fix),
    FixSpec("PKG-002-A", "PKG-002", "Create missing __init__.py files", FixTier.SAFE, _stub_fix),
    FixSpec("PKG-003-A", "PKG-003", "Validate/fix script entrypoint targets (structure-only)", FixTier.CONDITIONAL, _stub_fix),

    FixSpec("META-001-A", "META-001", "Insert missing required metadata placeholders", FixTier.SAFE, _stub_fix),
    FixSpec("META-002-A", "META-002", "Insert missing author placeholder", FixTier.SAFE, _stub_fix),
]
