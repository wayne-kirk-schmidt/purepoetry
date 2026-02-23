#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import sys
from pathlib import Path
from lib.registry.types import InvariantSpec, Severity

ID = "ENV-001"
CLUMP = "env"
DESCRIPTION = "Python interpreter mismatch"
FIXABLE = False
SEVERITY = Severity.FAIL


def check(ctx) -> bool:
    poetry_env = ctx.get("poetry_env_path")
    if not poetry_env:
        return True

    active = Path(sys.executable).resolve()
    env_python = (poetry_env / "bin" / "python").resolve()

    return active == env_python


RULE = InvariantSpec(
    ID,
    CLUMP,
    DESCRIPTION,
    FIXABLE,
    SEVERITY,
    check,
)

