#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
setup.py

Setup script for initializing the StreamNotification application
"""

import asyncio
import sys

from src.stream_notification import StreamNotification


async def run_stream_notification() -> None:
    """Run the StreamNotification application
    """
    app = StreamNotification()
    if "--no-terminal" not in sys.argv and app.is_compiled():
        await app.terminal.launch_terminal()
        return
    if not app.is_compiled():
        sys.exit("The application must be compiled to run without a terminal.")
    run_task = asyncio.create_task(app.run())
    await run_task
    await app.cleanup_complete_event.wait()
    await app.terminal.close_terminal()

if __name__ == "__main__":
    sys.exit(asyncio.run(run_stream_notification()))
