# -*- coding: utf-8 -*-

"""
This module provides a logger for the application.
"""

import logging

from src.constants import AppConstant

logging.basicConfig(
    level=logging.INFO,
    format=AppConstant.LOG_FORMAT,
    datefmt="%Y-%m-%d %H:%M:%S %Z",
)

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name (str): The name of the logger.

    Returns:
        logging.Logger: The logger instance.
            """
    """Get a logger instance.
    """
    return logging.getLogger(name)
