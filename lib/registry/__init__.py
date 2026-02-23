"""purepoetry.registry — registry-driven invariants and fixes."""

import sys

from .types import Severity, FixTier, InvariantSpec, FixSpec
from .invariants import all_invariants, invariants_by_clump, invariant_by_id, clumps
from .fixes import FIXES

sys.dont_write_bytecode = True
