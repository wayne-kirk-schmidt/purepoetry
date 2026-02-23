# lib/utilities/args.py
"""
CLI argument parsing for purepoetry (SVO grammar).
"""

import sys
sys.dont_write_bytecode = True
import argparse
from dataclasses import dataclass
from lib.utilities.paths import normalize_path


@dataclass
class CLIArgs:
    verb: str | None
    object: str | None
    value: str | None
    srcfile: str
    dstfile: str
    verbose: bool
    help: bool

def parse_arguments(defaults: dict) -> CLIArgs:
    """
    Grammar:
        purepoetry <verb> <object> <value>
    """

    parser = argparse.ArgumentParser(
        prog="purepoetry",
        description="purepoetry — Poetry TOML config manager (SVO mode)",
        add_help=False,
    )

    parser.add_argument("verb", nargs="?")
    parser.add_argument("object", nargs="?")
    parser.add_argument("value", nargs="?")

    parser.add_argument("-s", "--srcfile")
    parser.add_argument("-d", "--dstfile")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-h", "--help", action="store_true")

    args = parser.parse_args()

    srcfile = args.srcfile if args.srcfile else defaults["default_srcfile"]
    dstfile = args.dstfile if args.dstfile else defaults["default_dstfile"]

    return CLIArgs(
        verb=args.verb,
        object=args.object,
        value=args.value,
        srcfile=normalize_path(srcfile),
        dstfile=normalize_path(dstfile),
        verbose=args.verbose,
        help=args.help,
    )
