# lib/utilities/dispatcher.py
#
# pylint: disable=too-many-instance-attributes
# pylint: disable=import-error
# pylint: disable=broad-exception-caught
# pylint: disable=too-many-return-statements
# pylint: disable=import-outside-toplevel
#
"""
Command dispatch engine.
"""

import sys
import logging

from lib.utilities.exitcodes import (
    ExitCode,
    EXIT_SUCCESS,
    EXIT_FAILURE
)

sys.dont_write_bytecode = True

logger = logging.getLogger("purepoetry")

def dispatch(args, variables, registry):
    """
    Central command dispatch.

    Responsible for:
        - Verb resolution
        - Module loading
        - Normalizing return types
        - Help fallback
        - Returning ExitCode only
    """

    verb = args.verb
    obj = args.object
    value = args.value

    # ---------------------------------------------------------
    # Help shortcut
    # ---------------------------------------------------------
    if verb is None or verb == "help":
        return help_dispatch(args, registry)

    # ---------------------------------------------------------
    # Unknown verb
    # ---------------------------------------------------------
    if verb not in registry:
        logger.error("Unknown verb: %s", verb)
        return help_dispatch(args, registry)

    module_path = registry[verb]

    # ---------------------------------------------------------
    # Import verb module
    # ---------------------------------------------------------
    try:
        module = __import__(module_path, fromlist=["*"])
    except Exception as my_exception:
        logger.error("Failed to import module for verb '%s': %s", verb, my_exception)
        return EXIT_FAILURE

    if not hasattr(module, "run_action"):
        logger.error("Verb '%s' has no run_action()", verb)
        return EXIT_FAILURE

    # ---------------------------------------------------------
    # Execute verb
    # ---------------------------------------------------------
    try:
        result = module.run_action(obj, value, variables)
    except Exception:
        logger.exception("Unhandled exception for verb '%s'", verb)
        return EXIT_FAILURE

    # ---------------------------------------------------------
    # Normalize return contract
    # ---------------------------------------------------------
    return _normalize_result(result, args, registry)


def _normalize_result(result, args, registry):
    """
    Normalize verb return values into ExitCode.
    Optionally handle help fallback.
    """

    if result is None:
        return EXIT_SUCCESS

    if isinstance(result, ExitCode):
        if result == ExitCode.INVALID_USAGE:
            return help_dispatch(args, registry)
        return result

    if isinstance(result, int):
        try:
            return ExitCode(result)
        except ValueError:
            logger.error("Invalid exit code returned: %s", result)
            return EXIT_FAILURE

    if isinstance(result, tuple):
        exit_code, payload = result
        if payload:
            print(payload)
        if exit_code == ExitCode.INVALID_USAGE:
            return help_dispatch(args, registry)
        return exit_code

    # If string returned, treat as payload success
    if isinstance(result, str):
        print(result)
        return EXIT_SUCCESS

    logger.error("Unsupported return type from verb: %s", type(result))
    return EXIT_FAILURE


def help_dispatch(args, registry):
    """
    Help fallback dispatcher.
    """

    tokens = []

    if args.object:
        tokens.append(str(args.object))

    if args.value:
        tokens.append(str(args.value))

    try:
        from lib.commands.help import run_help
        code = run_help(tokens, registry)
        if isinstance(code, int):
            return ExitCode(code)
        if isinstance(code, ExitCode):
            return code
        return EXIT_SUCCESS
    except Exception as my_exception:
        logger.error("Failed to render help: %s", my_exception)
        return EXIT_FAILURE
