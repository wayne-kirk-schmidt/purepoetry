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

ID = "LOCK-004"
CLUMP = "lock"
DESCRIPTION = "Editable install mismatch for local package"
FIXABLE = True
SEVERITY = Severity.FAIL

def check(_ctx) -> bool:
    """ Placeholder until editable detection logic implemented """
    return True

RULE = InvariantSpec(
    ID,
    CLUMP,
    DESCRIPTION,
    FIXABLE,
    SEVERITY,
    check,
)
