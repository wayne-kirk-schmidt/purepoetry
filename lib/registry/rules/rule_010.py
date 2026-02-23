#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from lib.registry.types import InvariantSpec, Severity

ID = "META-003"
CLUMP = "meta"
DESCRIPTION = "Missing project URLs (homepage/repo/docs)"
FIXABLE = False
SEVERITY = Severity.WARN

def check(ctx) -> bool:
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

