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

ID = "META-003"
CLUMP = "meta"
DESCRIPTION = "Missing project URLs (homepage/repo/docs)"
FIXABLE = False
SEVERITY = Severity.WARN

def check(ctx) -> bool:
    """ check on defind project information in the ocnfig file """
    data = ctx.get("pyproject_data", {})
    project = data.get("project", {})

    urls = project.get("urls", {})

    if not isinstance(urls, dict):
        return False

    return any(
        key in urls
        for key in ("homepage", "repository", "documentation")
    )

RULE = InvariantSpec(
    ID,
    CLUMP,
    DESCRIPTION,
    FIXABLE,
    SEVERITY,
    check,
)
