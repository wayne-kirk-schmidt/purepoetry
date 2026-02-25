# lib/utilities/logging.py
"""
Logging configuration utilities for purepoetry.
"""

import sys
import logging

sys.dont_write_bytecode = True

def configure_logging(verbose: bool = False) -> None:
    """
    Configure console logging for deterministic CLI output.

    Args:
        verbose: If True, enable DEBUG level logging.
    """
    level = logging.DEBUG if verbose else logging.INFO

    logging.basicConfig(
        level=level,
        format="%(message)s",
    )
