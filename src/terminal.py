# -*- coding: utf-8 -*-

import asyncio
import subprocess
import traceback
from pathlib import Path

from src.utils import get_logger

logger = get_logger(__name__)

class Terminal(object):
    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir

    async def launch_terminal(self) -> None:
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
            return

    async def close_terminal(self) -> None:
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
