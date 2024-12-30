# -*- coding: utf-8 -*-

"""
terminal.py
This module provides a class for interacting with the terminal.
"""

__author__ = "Hagata"
__version__ = "0.0.1"
__date__ = "2024/12/29 (Created: 2024/12/29)"

import asyncio
import subprocess
import traceback
from pathlib import Path

from src.utils import get_logger

logger = get_logger(__name__)

class Terminal(object):
    """Class for interacting with the terminal.

    Attributes:
        base_dir (Path): The base directory of the application.
    """
    def __init__(self, base_dir: Path) -> None:
        """Initialize the terminal class.
        """
        self.base_dir = base_dir

    async def launch_terminal(self) -> None:
        """Launch a new terminal window.

        Raises:
            FileNotFoundError: If the applescript file is not found.
            SubprocessError: If an error occurs while executing the applescript.
        """
        try:
            script_path = Path(self.base_dir, "applescript", "launch_terminal.applescript")
        except FileNotFoundError:
            return

        try:
            proc = await asyncio.create_subprocess_exec(
                "/usr/bin/osascript",
                script_path,
                self.base_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
        except subprocess.SubprocessError:
            logger.exception(traceback.format_exc())
            await self.close_terminal()
            return

    async def close_terminal(self) -> None:
        """Close the current terminal window.

        Raises:
            FileNotFoundError: If the applescript file is not found.
            SubprocessError: If an error occurs while executing the applescript.
        """
        try:
            script_path = Path("applescript", "close_terminal.applescript")
        except FileNotFoundError:
            return

        try:
            proc = await asyncio.create_subprocess_exec(
                "/usr/bin/osascript",
                script_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
        except subprocess.SubprocessError:
            logger.exception(traceback.format_exc())
            return
