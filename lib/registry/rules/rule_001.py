#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import sys
from pathlib import Path

from lib.registry.types import InvariantSpec, Severity

sys.dont_write_bytecode = True


# ================================================================
# Invariant Metadata
# ================================================================

ID = "LOCK-001"
CLUMP = "lock"
DESCRIPTION = "Lockfile missing"
FIXABLE = False
SEVERITY = Severity.FAIL


# ================================================================
# Check
# ================================================================

def check(ctx) -> bool:
    """
    Returns True if poetry.lock exists in the project root.
    """
    lock_path: Path = ctx["lock_path"]
    return lock_path.exists()


# ================================================================
# Rule Object
# ================================================================

RULE = InvariantSpec(
    id=ID,
    clump=CLUMP,
    description=DESCRIPTION,
    fixable=FIXABLE,
    severity=SEVERITY,
    check=check,
)
