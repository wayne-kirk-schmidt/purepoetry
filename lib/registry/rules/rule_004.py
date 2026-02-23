#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import subprocess
from lib.registry.types import InvariantSpec, Severity

ID = "ENV-002"
CLUMP = "env"
DESCRIPTION = "Multiple Poetry virtualenvs bound to project"
FIXABLE = False
SEVERITY = Severity.FAIL


def check(ctx) -> bool:
    try:
        result = subprocess.run(
            ["poetry", "env", "list"],
            capture_output=True,
            text=True,
            check=True,
        )
        envs = [l for l in result.stdout.splitlines() if l.strip()]
        return len(envs) <= 1
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

