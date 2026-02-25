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

ID = "ENV-001"
CLUMP = "env"
DESCRIPTION = "Python interpreter mismatch"
FIXABLE = False
SEVERITY = Severity.FAIL

def check(ctx) -> bool:
    """ check on the specific environment file for poetry """
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
