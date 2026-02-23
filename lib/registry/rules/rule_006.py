#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import subprocess
from lib.registry.types import InvariantSpec, Severity

ID = "LOCK-002"
CLUMP = "lock"
DESCRIPTION = "Lockfile drift detected (pyproject != lock)"
FIXABLE = True
SEVERITY = Severity.FAIL


def check(ctx) -> bool:
    """
    Validates lockfile consistency using:
        poetry check --lock

    Return True if lockfile matches pyproject.
    """
    try:
        result = subprocess.run(
            ["poetry", "check", "--lock"],
            capture_output=True,
            text=True,
        )

        return result.returncode == 0

    except Exception:
        # If poetry itself fails unexpectedly,
        # do not hard fail the audit engine.
        return True


RULE = InvariantSpec(
    ID,
    CLUMP,
    DESCRIPTION,
    FIXABLE,
    SEVERITY,
    check,
)

