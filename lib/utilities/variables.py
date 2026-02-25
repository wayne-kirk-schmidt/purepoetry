"""
Runtime variable initialization.
"""

import os
import sys

sys.dont_write_bytecode = True

def initialize_variables() -> dict:
    """ setup specific defaults and register the behavior we want """
    userhome = os.path.expanduser("~")

    variables = {
        "encoding": "utf-8",
        "default_srcfile": "pyproject.toml",
        "default_dstfile": "pyproject.toml",
        "home": userhome,
        "config_dir": os.path.join(userhome, ".purepoetry"),
    }

    return variables
