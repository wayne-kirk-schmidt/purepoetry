"""
Runtime variable initialization.
"""

import sys
sys.dont_write_bytecode = True
import os

def initialize_variables() -> dict:
    userhome = os.path.expanduser("~")

    variables = {
        "encoding": "utf-8",
        "default_srcfile": "pyproject.toml",
        "default_dstfile": "pyproject.toml",
        "home": userhome,
        "config_dir": os.path.join(userhome, ".purepoetry"),
    }

    os.makedirs(variables["config_dir"], exist_ok=True)

    return variables

