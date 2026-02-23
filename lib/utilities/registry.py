"""
Command registry loader.
"""

import sys
sys.dont_write_bytecode = True

def initialize_registry():
    from lib.commands import get_registry
    return get_registry()
