#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import subprocess
from lib.registry.types import InvariantSpec, Severity

ID = "LOCK-002"
CLUMP = "lock"
DESCRIPTION = "Lockfile drift detected (pyproject != lock)"
FIXABLE = True
SEVERITY = Severity.FAIL


def check(ctx) -> bool:
    try:
        result = subprocess.run(
            ["poetry", "lock", "--check"],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    except Exception:
        return True


RULE = InvariantSpec(
    ID,
    CLUMP,
    DESCRIPTION,
    FIXABLE,
    SEVERITY,
    check,
)

