#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import sys
sys.dont_write_bytecode = True

from packaging.version import Version
from packaging.specifiers import SpecifierSet

from lib.registry.types import InvariantSpec, Severity


ID = "ENV-003"
CLUMP = "env"
DESCRIPTION = "Python version out of declared range"
FIXABLE = False
SEVERITY = Severity.FAIL


def check(ctx) -> bool:
    """
    Validates the active interpreter version against
    project.requires-python using PEP 440 specifiers.
    """

    data = ctx.get("pyproject_data", {})
    project = data.get("project", {})

    declared = project.get("requires-python")
    if not declared:
        # If no constraint declared, do not fail
        return True

    try:
        spec = SpecifierSet(declared)
        current = Version(sys.version.split()[0])
        return current in spec
    except Exception:
        # If spec parsing fails, do not hard-fail the project
        return True


RULE = InvariantSpec(
    ID,
    CLUMP,
    DESCRIPTION,
    FIXABLE,
    SEVERITY,
    check,
)
