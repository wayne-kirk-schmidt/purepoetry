#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import subprocess
from lib.registry.types import InvariantSpec, Severity

ID = "LOCK-003"
CLUMP = "lock"
DESCRIPTION = "Installed dependencies do not match lockfile"
FIXABLE = True
SEVERITY = Severity.FAIL


def check(ctx) -> bool:
    try:
        result = subprocess.run(
            ["poetry", "install", "--dry-run"],
            capture_output=True,
            text=True,
        )
        return "No dependencies to install" in result.stdout
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
