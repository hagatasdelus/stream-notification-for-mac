# -*- coding: utf-8 -*-

"""
This module provides an enum class for stream status.
"""

import enum


class NotificationFormat(enum.Enum):
    """Enum class for notification format.

    Attributes:
        notification: Notification format.
        dialog: Dialog format.
    """
    NOTIFICATION = "Notification"
    DIALOG = "Dialog"
