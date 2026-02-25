#
# pylint: disable=import-error
#
"""
PurePoetry orchestration layer.
"""


import sys

from lib.utilities.variables import initialize_variables
from lib.utilities.registry import initialize_registry
from lib.utilities.dispatcher import dispatch, help_dispatch
from lib.utilities.args import parse_arguments
from lib.utilities.logging_config import configure_logging

sys.dont_write_bytecode = True

def run() -> None:
    """ defines the run method we pass to other verbs """
    variables = initialize_variables()
    registry = initialize_registry()

    args = parse_arguments(variables)

    # Propagate trailing positional arguments (used by list verb)
    variables["args"] = getattr(args, "args", [])

    configure_logging(args.verbose)

    if args.verbose:
        variables["verbose"] = True

    # ---------------------------------------------------------
    # Propagate SRC if explicitly provided
    # ---------------------------------------------------------
    if any(flag in sys.argv for flag in ("-s", "--srcfile", "--src")):
        variables["src"] = args.srcfile

    # ---------------------------------------------------------
    # Propagate DST if explicitly provided
    # ---------------------------------------------------------
    if any(flag in sys.argv for flag in ("-d", "--dstfile", "--dst")):
        variables["dst"] = args.dstfile

    if args.help:
        help_dispatch(args, registry)
        return

    result = dispatch(args, variables, registry)

    if isinstance(result, int):
        sys.exit(result)
