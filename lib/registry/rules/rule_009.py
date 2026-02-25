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

ID = "META-002"
CLUMP = "meta"
DESCRIPTION = "Missing author information"
FIXABLE = True
SEVERITY = Severity.WARN

def check(ctx) -> bool:
    """ checking on specific document information """
    data = ctx.get("pyproject_data", {})
    project = data.get("project", {})

    authors = project.get("authors")

    if not authors:
        return False

    if not isinstance(authors, list):
        return False

    if len(authors) == 0:
        return False

    # Accept if at least one author has name or email
    for entry in authors:
        if isinstance(entry, dict):
            if entry.get("name") or entry.get("email"):
                return True

    return False

RULE = InvariantSpec(
    ID,
    CLUMP,
    DESCRIPTION,
    FIXABLE,
    SEVERITY,
    check,
)
