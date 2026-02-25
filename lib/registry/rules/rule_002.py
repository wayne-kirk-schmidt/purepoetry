#!/usr/bin/env python3
#
# pylint: disable=import-error
# pylint: disable=broad-exception-caught
# pylint: disable=import-outside-toplevel
#
# -*- coding: utf-8 -*-

""" rule specific module """

from __future__ import annotations

import sys
from lib.registry.types import InvariantSpec, Severity
sys.dont_write_bytecode = True

ID = "META-001"
CLUMP = "meta"
DESCRIPTION = "Missing required metadata (name/version/python)"
FIXABLE = False
SEVERITY = Severity.WARN

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

RULE = InvariantSpec(
    id=ID,
    clump=CLUMP,
    description=DESCRIPTION,
    fixable=FIXABLE,
    severity=SEVERITY,
    check=check,
)
