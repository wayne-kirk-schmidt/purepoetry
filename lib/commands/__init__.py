"""
@name           purepoetry.commands
@version        0.2.0
@date           2024-11-01
@author         Wayne Kirk Schmidt
@email-address  wayne.kirk.schmidt@gmail.com
@license-name   Apache-2.0
@license-url    https://www.apache.org/licenses/LICENSE-2.0
@brief          Dynamic command discovery for purepoetry.

@description

    This package automatically discovers command modules at runtime.
    Any *.py file in this directory that does not begin with "__"
    is treated as a command verb module.

    Example:
        read.py      → "read"
        backup.py    → "backup"
        show.py      → "show"

    Each command module must provide:
        help()               → print help stub / description
        run(data, args)      → execute the command

    This dynamic discovery approach allows plugins, future expansion,
    and less maintenance as verbs grow.

Usage:
    Modules discovered dynamically via load_commands()

"""

import sys
import pathlib
sys.dont_write_bytecode = True

### ====================================================================
### load_commands()
### ====================================================================


def load_commands():
    """
    Discover commands in this directory.
    Returns:
        dict: { "verb": "lib.commands.verb" }
    """

    directory = pathlib.Path(__file__).parent
    modules = {}

    for file in directory.iterdir():
        if file.is_file() and file.suffix == ".py" and not file.name.startswith("__"):
            verb = file.stem
            modules[verb] = f"lib.commands.{verb}"

    return modules


### ====================================================================
### get_registry() — public registry interface
### ====================================================================


def get_registry():
    """
    Build and return the dynamic registry.
    """
    return load_commands()


### Exported verbs:
__all__ = ["get_registry"]
