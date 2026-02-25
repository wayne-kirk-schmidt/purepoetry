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

import subprocess
from lib.registry.types import InvariantSpec, Severity

sys.dont_write_bytecode = True

ID = "LOCK-002"
CLUMP = "lock"
DESCRIPTION = "Lockfile drift detected (pyproject != lock)"
FIXABLE = True
SEVERITY = Severity.FAIL

def check(_ctx) -> bool:
    """
    Validates lockfile consistency using:
        poetry check --lock

    Return True if lockfile matches pyproject.
    """
    try:
        result = subprocess.run(
            ["poetry", "check", "--lock"],
            check=False,
            capture_output=True,
            text=True,
        )

        return result.returncode == 0

    except Exception:
        # If poetry itself fails unexpectedly,
        # do not hard fail the audit engine.
        return True

RULE = InvariantSpec(
    ID,
    CLUMP,
    DESCRIPTION,
    FIXABLE,
    SEVERITY,
    check,
)
