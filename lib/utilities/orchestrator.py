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

    if args.verbose:
        variables["verbose"] = True

    # Only propagate dst if explicitly provided
    # (argparse sets dstfile even when defaulted,
    # so we check raw argv for explicit flag presence)
    if any(f in sys.argv for f in ("-d", "--dstfile", "--dst")):
        variables["dst"] = args.dstfile

    if args.help:
        help_dispatch(args, registry)
        return

    result = dispatch(args, variables, registry)

    if isinstance(result, int):
        sys.exit(result)
