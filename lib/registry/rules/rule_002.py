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
    Validate required PEP 621 metadata fields:
      - project.name
      - project.version
      - project.requires-python
    """

    data = ctx.get("pyproject_data", {})
    project = data.get("project", {})

    if not project.get("name"):
        return False

    if not project.get("version"):
        return False

    if not project.get("requires-python"):
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
