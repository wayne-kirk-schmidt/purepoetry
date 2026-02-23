#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import sys
sys.dont_write_bytecode = True

from pathlib import Path
import subprocess

from lib.registry.types import (
    InvariantSpec,
    Severity,
    FixSpec,
    FixTier,
)


# ================================================================
# Invariant Metadata
# ================================================================

ID = "LOCK-001"
CLUMP = "lock"
DESCRIPTION = "Lockfile missing"
FIXABLE = True
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
    severity=SEVERITY,   # must match updated types.py
    check=check,
)


# ================================================================
# Fix Definition
# ================================================================

def _fix_lock_missing(ctx) -> None:
    """
    Regenerate lockfile using `poetry lock`.
    Raises CalledProcessError if it fails.
    """
    subprocess.run(
        ["poetry", "lock"],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


FIXES = [
    FixSpec(
        id="FIX-LOCK-001",
        invariant_id=ID,
        description="Regenerate lockfile via poetry lock",
        tier=FixTier.SAFE,
        handler=_fix_lock_missing,
    )
]
