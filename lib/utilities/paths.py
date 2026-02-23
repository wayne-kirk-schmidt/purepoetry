"""
Path normalization utilities.
"""

import sys
sys.dont_write_bytecode = True
import os


def normalize_path(path: str | None) -> str | None:
    """
    Normalize filesystem path.
    """
    if not path:
        return None
    return os.path.abspath(os.path.expanduser(path))
