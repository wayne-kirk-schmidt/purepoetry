"""
Command dispatch engine.
"""

import sys
sys.dont_write_bytecode = True
import logging


def dispatch(args, variables, registry):
    verb = args.verb
    obj = args.object
    value = args.value

    if verb is None or verb == "help":
        result = help_dispatch(args, registry)
        if isinstance(result, str):
            print(result)
        return result

    if verb not in registry:
        print(f"[error] Unknown verb: {verb}")
        print(f"Available verbs: {', '.join(registry.keys())}")
        return

    module_path = registry[verb]

    try:
        module = __import__(module_path, fromlist=["*"])
    except Exception as e:
        print(f"[fatal] Failed to import module for verb '{verb}': {e}")
        return

    if hasattr(module, "run_action"):
        result = module.run_action(obj, value, variables)
        if isinstance(result, str):
            print(result)
        return result

    print(f"[error] Verb '{verb}' exists but has no run_action() method.")


def help_dispatch(args, registry):
    tokens = []

    if args.object:
        tokens.append(str(args.object))

    if args.value:
        tokens.append(str(args.value))

    try:
        from lib.commands.help import run_help
        return run_help(tokens, registry)
    except Exception as e:
        logging.getLogger("purepoetry").error(
            f"Error: failed to render help: {e}"
        )
        return 2
