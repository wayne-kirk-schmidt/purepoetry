#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# pylint: disable=import-error
# pylint: disable=import-outside-toplevel
# pylint: disable=broad-exception-caught
# pylint: disable=too-many-return-statements
# pylint: disable=too-many-locals
#
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

import sys

sys.dont_write_bytecode = True

class Severity(str, Enum):
    """ this is a class that only has result data/values and no methods """
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"


class FixTier(str, Enum):
    """ this is a class that only has fixes data/values and no methods """
    SAFE = "safe"
    CONDITIONAL = "conditional"
    FORBIDDEN = "forbidden"


@dataclass(frozen=True)
class InvariantSpec:
    """ and this is our rule, to speak. """
    id: str
    clump: str
    description: str
    fixable: bool
    severity: Severity
    # check(ctx) -> bool; implemented in doctor engine later
    check: Callable[[Dict[str, Any]], bool]


@dataclass(frozen=True)
class FixSpec:
    """ and this is our fix specification, to speak. """
    id: str
    invariant_id: str
    description: str
    tier: FixTier
    # apply(ctx) -> None; implemented later
    handler: Callable[[Dict[str, Any]], None]
