# -*- coding: utf-8 -*-

"""
This module provides an enum class for stream status.
"""

__author__ = "Hagata"
__version__ = "0.0.1"
__date__ = "2024/12/08 (Created: 2024/10/20)"

import enum


class StreamStatus(enum.Enum):
    """Enum class for stream status.

    Attributes:
        STREAMING: Streaming status.
        NOTSTREAMING: Not streaming status.
    """
    STREAMING = "streaming"
    NOTSTREAMING = "not streaming"
