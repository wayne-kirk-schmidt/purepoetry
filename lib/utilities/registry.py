#
# pylint: disable=import-error
# pylint: disable=import-outside-toplevel
#
"""
Command registry loader.
"""

import sys
sys.dont_write_bytecode = True

def initialize_registry():
    """ dynamically collect commands to present to the shim from lib/commands """
    from lib.commands import get_registry
    return get_registry()
