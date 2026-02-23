"""
PurePoetry orchestration layer.
"""

import sys
sys.dont_write_bytecode = True

from lib.utilities.variables import initialize_variables
from lib.utilities.registry import initialize_registry
from lib.utilities.dispatcher import dispatch, help_dispatch
from lib.utilities.args import parse_arguments
from lib.utilities.logging import configure_logging

def run() -> None:
    variables = initialize_variables()
    registry = initialize_registry()

    args = parse_arguments(variables)

    configure_logging(args.verbose)

    if args.help:
        help_dispatch(args, registry)
        return

    dispatch(args, variables, registry)

