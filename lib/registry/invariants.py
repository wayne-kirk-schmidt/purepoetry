#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# pylint: disable=import-error
# pylint: disable=import-outside-toplevel
# pylint: disable=broad-exception-caught
# pylint: disable=too-many-return-statements
# pylint: disable=too-many-locals
#
""" Define the structure and methods for the rules (invariants) """

import sys

import pkgutil
import importlib
from typing import List, Optional
from .types import InvariantSpec

sys.dont_write_bytecode = True

def _discover_modules():
    """ import the modules we need dynamically """
    from . import rules
    modules = []

    for mod in pkgutil.iter_modules(rules.__path__):
        modules.append(
            importlib.import_module(f"{rules.__name__}.{mod.name}")
        )

    return modules


def all_invariants() -> List[InvariantSpec]:
    """ list all of the rules we need to adhere to """
    invariants: List[InvariantSpec] = []

    for module in _discover_modules():
        if hasattr(module, "RULE"):
            invariants.append(module.RULE)

    # deterministic ordering by ID
    invariants.sort(key=lambda r: r.id)

    return invariants


def invariant_by_id(invariant_id: str) -> Optional[InvariantSpec]:
    """ ensure we have the rules defined by id as well as string """
    for inv in all_invariants():
        if inv.id == invariant_id:
            return inv
    return None


def invariants_by_clump(clump: str) -> List[InvariantSpec]:
    """ a clump is a string we can use also to define rules """
    return [i for i in all_invariants() if i.clump == clump]


def clumps() -> List[str]:
    """ find the clumps in the rules files """
    return sorted({i.clump for i in all_invariants()})
