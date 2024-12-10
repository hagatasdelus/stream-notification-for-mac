# -*- coding: utf-8 -*-

"""
This module provides a logger for the application.
"""

__author__ = "Hagata"
__version__ = "0.0.1"
__date__ = "2024/12/08 (Created: 2024/10/20)"

import logging

from src.constants import AppConstant

logging.basicConfig(
    level=logging.INFO,
    format=AppConstant.LOG_FORMAT,
    datefmt="%Y-%m-%d %H:%M:%S %Z",
)

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance.
    """
    return logging.getLogger(name)
