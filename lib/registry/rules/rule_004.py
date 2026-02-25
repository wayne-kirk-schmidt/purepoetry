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

ID = "ENV-002"
CLUMP = "env"
DESCRIPTION = "Multiple Poetry virtualenvs bound to project"
FIXABLE = False
SEVERITY = Severity.FAIL

def check(_ctx) -> bool:
    """ checking on the environmeent from the poetry command """
    try:
        result = subprocess.run(
            ["poetry", "env", "list"],
            capture_output=True,
            text=True,
            check=True,
        )
        envs = [l for l in result.stdout.splitlines() if l.strip()]
        return len(envs) <= 1
    except Exception:
        return True

RULE = InvariantSpec(
    ID,
    CLUMP,
    DESCRIPTION,
    FIXABLE,
    SEVERITY,
    check,
)
