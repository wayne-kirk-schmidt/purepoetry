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
    try:
        poetry = data["tool"]["poetry"]
        return (
            "homepage" in poetry
            or "repository" in poetry
            or "documentation" in poetry
        )
    except KeyError:
        return False


RULE = InvariantSpec(
    ID,
    CLUMP,
    DESCRIPTION,
    FIXABLE,
    SEVERITY,
    check,
)

