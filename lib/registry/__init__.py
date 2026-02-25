"""purepoetry.registry — registry-driven invariants and fixes."""

import sys

from .types import Severity, InvariantSpec
from .invariants import all_invariants, invariants_by_clump, invariant_by_id, clumps

sys.dont_write_bytecode = True
