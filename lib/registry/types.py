#!/usr/bin/env python3
# -*- coding: utf-8 -*-
### ================================================================
"""
purepoetry.registry.types

Shared types for registry-driven invariants and fixes.

Contract:
    - No Poetry imports
    - No filesystem side-effects
    - Stable, small vocabulary used across commands
"""
### ================================================================

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional, Sequence, Any, Dict, List


class Severity(str, Enum):
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"


class FixTier(str, Enum):
    SAFE = "safe"
    CONDITIONAL = "conditional"
    FORBIDDEN = "forbidden"


@dataclass(frozen=True)
class InvariantSpec:
    id: str
    clump: str
    description: str
    fixable: bool
    severity_on_fail: Severity
    # check(ctx) -> bool; implemented in doctor engine later
    check: Callable[[Dict[str, Any]], bool]


@dataclass(frozen=True)
class FixSpec:
    id: str
    invariant_id: str
    description: str
    tier: FixTier
    # apply(ctx) -> None; implemented later
    handler: Callable[[Dict[str, Any]], None]
