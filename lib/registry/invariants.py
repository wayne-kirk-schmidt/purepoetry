#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.dont_write_bytecode = True

import pkgutil
import importlib
from typing import List, Optional
from .types import InvariantSpec


def _discover_modules():
    from . import rules
    modules = []

    for mod in pkgutil.iter_modules(rules.__path__):
        modules.append(
            importlib.import_module(f"{rules.__name__}.{mod.name}")
        )

    return modules


def all_invariants() -> List[InvariantSpec]:
    invariants: List[InvariantSpec] = []

    for module in _discover_modules():
        if hasattr(module, "RULE"):
            invariants.append(module.RULE)

    # deterministic ordering by ID
    invariants.sort(key=lambda r: r.id)

    return invariants


def invariant_by_id(invariant_id: str) -> Optional[InvariantSpec]:
    for inv in all_invariants():
        if inv.id == invariant_id:
            return inv
    return None


def invariants_by_clump(clump: str) -> List[InvariantSpec]:
    return [i for i in all_invariants() if i.clump == clump]


def clumps() -> List[str]:
    return sorted({i.clump for i in all_invariants()})

