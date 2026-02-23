#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from lib.registry.types import InvariantSpec, Severity

ID = "LOCK-004"
CLUMP = "lock"
DESCRIPTION = "Editable install mismatch for local package"
FIXABLE = True
SEVERITY = Severity.FAIL


def check(ctx) -> bool:
    # Placeholder until editable detection logic implemented
    return True


RULE = InvariantSpec(
    ID,
    CLUMP,
    DESCRIPTION,
    FIXABLE,
    SEVERITY,
    check,
)

