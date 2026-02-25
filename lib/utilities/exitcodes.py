# lib/utilities/exitcodes.py
"""
Global exit status definitions for PurePoetry.

Exit codes are transport-layer signals between verbs and dispatcher.
They are not business logic.
"""

from enum import IntEnum

import sys
sys.dont_write_bytecode = True

class ExitCode(IntEnum):
    """ Define a basic ExitCode class. no methods, but a holder for data """
    SUCCESS = 0
    FAILURE = 1
    INVALID_USAGE = 2
    REDIRECT = 3


EXIT_SUCCESS = ExitCode.SUCCESS
EXIT_FAILURE = ExitCode.FAILURE
EXIT_INVALID_USAGE = ExitCode.INVALID_USAGE
EXIT_REDIRECT = ExitCode.REDIRECT
