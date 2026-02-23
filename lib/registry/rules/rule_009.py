#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from lib.registry.types import InvariantSpec, Severity

ID = "META-002"
CLUMP = "meta"
DESCRIPTION = "Missing author information"
FIXABLE = True
SEVERITY = Severity.WARN

def check(ctx) -> bool:
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
