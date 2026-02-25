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

from pathlib import Path
from lib.registry.types import InvariantSpec, Severity

sys.dont_write_bytecode = True

ID = "LOCK-001"
CLUMP = "lock"
DESCRIPTION = "Lockfile missing"
FIXABLE = False
SEVERITY = Severity.FAIL

def check(ctx) -> bool:
    """
    Returns True if poetry.lock exists in the project root.
    """
    lock_path: Path = ctx["lock_path"]
    return lock_path.exists()

RULE = InvariantSpec(
    id=ID,
    clump=CLUMP,
    description=DESCRIPTION,
    fixable=FIXABLE,
    severity=SEVERITY,
    check=check,
)
