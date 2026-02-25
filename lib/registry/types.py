#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# pylint: disable=import-error
# pylint: disable=import-outside-toplevel
#
### ================================================================
"""
purepoetry.registry.types

Shared types for registry-driven invariants.

Contract:
    - No Poetry imports
    - No filesystem side-effects
    - Stable, small vocabulary used across commands
    - Audit-only model (no fix definitions)
"""
### ================================================================

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Any, Dict

import sys

sys.dont_write_bytecode = True


class Severity(str, Enum):
    """Result classification for invariant evaluation."""
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"


@dataclass(frozen=True)
class InvariantSpec:
    """Registry definition of a single invariant rule."""
    id: str
    clump: str
    description: str
    fixable: bool
    severity: Severity
    check: Callable[[Dict[str, Any]], bool]
