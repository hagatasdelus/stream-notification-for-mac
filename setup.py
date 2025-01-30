#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
setup.py

Setup script for initializing the StreamNotification application
"""

import asyncio
import sys

import src.stream_notification as sn

if __name__ == "__main__":
    sys.exit(asyncio.run(sn.run_stream_notification()))
