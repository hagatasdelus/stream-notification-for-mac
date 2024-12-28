# -*- coding: utf-8 -*-

"""
This module provides a function to get the base path of the application.
"""

__author__ = "Hagata"
__version__ = "0.0.1"
__date__ = "2024/12/29 (Created: 2024/12/29)"

import os
import sys
from pathlib import Path


def get_base_path() -> Path:
    """Get the base path of the application
    """
    if "__compiled__" in globals():
        return Path(os.path.dirname(os.path.realpath(sys.argv[0])))
    return Path(__file__).parent.resolve()
