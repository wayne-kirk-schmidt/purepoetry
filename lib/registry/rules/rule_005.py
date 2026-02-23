#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import sys
from lib.registry.types import InvariantSpec, Severity

ID = "ENV-003"
CLUMP = "env"
DESCRIPTION = "Python version out of declared range"
FIXABLE = False
SEVERITY = Severity.FAIL


def check(ctx) -> bool:
    data = ctx.get("pyproject_data", {})
    try:
        declared = data["tool"]["poetry"]["dependencies"]["python"]
    except KeyError:
        return True

    current = sys.version.split()[0]

    # Minimal enforcement for now
    return current in declared


RULE = InvariantSpec(
    ID,
    CLUMP,
    DESCRIPTION,
    FIXABLE,
    SEVERITY,
    check,
)

