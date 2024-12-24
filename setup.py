#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
setup.py

Setup script for initializing the StreamNotification application
"""

__author__ = "Hagata"
__version__ = "0.0.1"
__date__ = "2024/12/23 (Created: 2024/10/20)"

import asyncio
import sys

import src.stream_notification as sn

if __name__ == "__main__":
    sys.exit(asyncio.run(sn.notification_run()))
