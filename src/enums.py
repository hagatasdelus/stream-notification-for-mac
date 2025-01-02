# -*- coding: utf-8 -*-

"""
This module provides an enum class for stream status.
"""

__author__ = "Hagata"
__version__ = "0.0.1"
__date__ = "2025/1/3 (Created: 2024/10/20)"

import enum


class NotificationFormat(enum.Enum):
    """Enum class for notification format.

    Attributes:
        notification: Notification format.
        dialog: Dialog format.
    """
    NOTIFICATION = "Notification"
    DIALOG = "Dialog"
