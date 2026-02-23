#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import sys
sys.dont_write_bytecode = True

from lib.registry.types import InvariantSpec, Severity


# ================================================================
# Invariant Metadata
# ================================================================

ID = "META-001"
CLUMP = "meta"
DESCRIPTION = "Missing required metadata (name/version/python)"
FIXABLE = False
SEVERITY = Severity.WARN


# ================================================================
# Check
# ================================================================

def check(ctx) -> bool:
    """
    Validate required Poetry metadata fields:
      - tool.poetry.name
      - tool.poetry.version
      - tool.poetry.dependencies.python
    """

    data = ctx.get("pyproject_data", {})

    tool = data.get("tool", {})
    poetry = tool.get("poetry", {})
    deps = poetry.get("dependencies", {})

    if not poetry.get("name"):
        return False

    if not poetry.get("version"):
        return False

    if not deps.get("python"):
        return False

    return True


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
