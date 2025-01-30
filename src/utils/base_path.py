# -*- coding: utf-8 -*-

"""
This module provides a function to get the base path of the application.
"""

import os
import sys
from pathlib import Path


def get_base_path() -> Path:
    """Get the base path of the application
    Returns the path from the root path to src

    Returns:
        Path: The base path of the application
    """
    if "__compiled__" in globals():
        return Path(os.path.dirname(os.path.realpath(sys.argv[0])))
    return Path(__file__).parent.parent.resolve()
