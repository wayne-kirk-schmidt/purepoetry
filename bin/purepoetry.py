#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# SPDX-License-Identifier: Apache-2.0
#
# pylint: disable=import-error, wrong-import-position
#

"""
purepoetry — CLI Entrypoint (Shim)

Thin execution boundary for the purepoetry control plane.
All orchestration logic lives under lib/.

"""

__project__	= "purepoetry"
__component__	= "CLI Entrypoint Shim"
__version__	= "0.6.0"
__author__	= "Wayne Schmidt (wayne.kirk.schmidt@gmail.com)"
__license__	= "Apache License 2.0"
__license_url__	= "https://www.apache.org/licenses/LICENSE-2.0"

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from lib.utilities.orchestrator import run

if __name__ == "__main__":
    run()
