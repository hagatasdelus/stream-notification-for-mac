#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
stream_notification.py

This module contains the implementation of the StreamNotification application,
which monitors the streaming status of a Twitch streamer and provides notifications.
"""

__author__ = "Hagata"
__version__ = "0.0.1"
__date__ = "2024/12/08 (Created: 2024/10/20)"

import asyncio
import contextlib
import os
import re
import subprocess
import sys
import traceback
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

import urllib3.util
from InquirerPy import inquirer
from prompt_toolkit.validation import ValidationError, Validator

from src.constants import AppConstant
from src.enums import NotificationFormat, StreamStatus
from src.twitch import TwitchAPI
from src.utils.logger import get_logger

logger = get_logger(__name__)

def get_base_path() -> Path:
    """Get the base path of the application
    """
    if "__compiled__" in globals():
        return Path(os.path.dirname(os.path.realpath(sys.argv[0])))
    return Path(__file__).parent.resolve()

class UsernameValidator(Validator):
    """UsernameValidator

    UsernameValidator is a prompt_toolkit Validator that validates the username input
    """
    def validate(self, document) -> None:
        """Validate the username input

        Args:
            document (Document): The input document

        Raises:
            ValidationError: The username is empty or contains non-alphanumeric characters
        """
        if not document.text: # 入力が空の場合
            raise ValidationError(message="Username cannot be empty", cursor_position=len(document.text))
        if not re.match(r"^[a-zA-Z0-9_]+$", document.text): # 英数字とアンダースコア以外が含まれている場合
            raise ValidationError(message="Username must be alphanumeric", cursor_position=len(document.text))

class StreamNotification(object):
    """StreamNotification

    StreamNotification is a stream notification application that monitors the streaming status of a Twitch streamer

    Attributes:
        base_dir (Path): The base directory of the application
        twitch_api (TwitchAPI): The Twitch API client
        is_running (bool): The running status of the application
        _cleanup_tasks (list[asyncio.Task]): The cleanup tasks
        cleanup_compelete_event (asyncio.Event): The cleanup complete event
    """

    def __init__(self):
        """Initialize instancee of StreamNotification
        """
        self.base_dir = get_base_path()
        self.twitch_api = TwitchAPI()
        self.is_running = True
        self._cleanup_tasks: list[asyncio.Task] = []
        self.cleanup_compelete_event = asyncio.Event()

    @asynccontextmanager
    async def initialize(self) -> AsyncIterator["StreamNotification"]:
        """Application initialization context manager

        Yields:
            StreamNotification: The StreamNotification instance
        """
        await self.twitch_api.initialize()
        yield self

    async def display_message(self, message: str) -> None:
        """メッセージを非同期に表示"""
        print(message)
        await asyncio.sleep(0)  # イベントループに制御を戻す

    def format_display_message(self, username: str, display_name: str, stream_title: str) -> str:
        """Formats the message to be displayed

        Args:
            username (str): The username of the streamer
            display_name (str): The display name of the streamer
            stream_title (str): The title of the stream

        Returns:
            str: The formatted message

        Example:
            >>> format_display_message("username", "display_name", "stream_title")
            "display_name has started streaming: stream_title"
        """
        base_format = f" has started streaming: {stream_title}"
        if username.lower() == display_name.lower():
            return display_name + base_format
        return f"{display_name}({username})" + base_format

    async def _run_notification_script(self, *arguments) -> None:
        """Run the notification AppleScript to display a notification

        Args:
            *arguments (list[str]): The arguments to pass to the script

        Raises:
            subprocess.SubprocessError: An error occurred while running the script
            FileNotFoundError: The script was not found
        """
        try:
            script_path = Path(self.base_dir, "applescript", "notification.applescript")
        except FileNotFoundError:
            logger.exception(traceback.format_exc())
            return

        try:
            proc = await asyncio.create_subprocess_exec(
                "/usr/bin/osascript",
                script_path,
                arguments[0],   # message
                arguments[1],   # title
                arguments[2].url, # url
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
        except subprocess.SubprocessError:
            logger.exception(traceback.format_exc())
            return


    async def _run_dialog_script(self, message: str, a_url: urllib3.util.Url) -> None:
        """Run the dialog AppleScript to display a dialog box

        Args:
            *arguments (list[str]): The arguments to pass to the script

        Raises:
            subprocess.SubprocessError: An error occurred while running the script
            FileNotFoundError: The script was not found
        """
        try:
            script_path = Path(self.base_dir, "applescript", "dialog.applescript")
        except FileNotFoundError:
            logger.exception(traceback.format_exc())
            return

        icon_path = "AppIcon.png"
        if not self.is_compiled():
            icon_path = os.path.join("..", icon_path)

        script_arguments = [message, a_url.url, icon_path]

        try:
            proc = await asyncio.create_subprocess_exec(
                "/usr/bin/osascript",
                script_path,
                *script_arguments,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
        except subprocess.SubprocessError:
            logger.exception(traceback.format_exc())
            return

    async def _run_starting_dialog_script(self, *arguments) -> None:
        """Run the dialog AppleScript to display a dialog box

        Args:
            *arguments (list[str]): The arguments to pass to the script

        Raises:
            subprocess.SubprocessError: An error occurred while running the script
            FileNotFoundError: The script was not found
        """
        try:
            script_path = Path(self.base_dir, "applescript", "starting_dialog.applescript")
        except FileNotFoundError:
            logger.exception(traceback.format_exc())
            return

        icon_path = "AppIcon.png"
        if not self.is_compiled():
            icon_path = os.path.join("..", icon_path)

        script_arguments = [*arguments, icon_path]

        try:
            proc = await asyncio.create_subprocess_exec(
                "/usr/bin/osascript",
                script_path,
                # arguments[0],   # message
                # arguments[1],   # title
                # icon_path,
                *script_arguments,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
        except subprocess.SubprocessError:
            logger.exception(traceback.format_exc())
            return

    async def check_stream_status(self, username: str, display_format: NotificationFormat) -> None:
        """Check the streaming status of a streamer

        Args:
            username (str): The username of the streamer
            display_format (str): The display format to use

        Raises:
            TwitchAPIError: An error occurred while checking the stream status
        """
        while self.is_running:
            display_name, stream_title = await self.twitch_api.get_stream_by_name(username)

            if stream_title is not None:
                logger.info(
                    "Checking stream status: %s - %s",
                    username,
                    StreamStatus.STREAMING.value.title()
                )

            if display_name and stream_title:
                url_string = f"https://www.twitch.tv/{username}"
                a_url: urllib3.util.Url = urllib3.util.parse_url(url_string)
                print("a_url: "+a_url.url)
                message = self.format_display_message(username, display_name, stream_title)
                script_args = [message, "Stream Started", a_url]
                if display_format == NotificationFormat.notification:
                    await self._run_notification_script(*script_args)
                else:
                    await self._run_dialog_script(message, a_url)
                await self.display_message(message)
                await asyncio.sleep(AppConstant.STREAMING_INTERVAL)
            else:
                await asyncio.sleep(AppConstant.CHECK_INTERVAL)

    async def check_streamer_existence(self, username: str, display_format: NotificationFormat) -> bool:
        """Check if the streamer exists

        Args:
            username (str): The username of the streamer
            display_format (str): The display format to use

        Returns:
            bool: True if the streamer exists, False otherwise

        Raises:
            TwitchAPIError: An error occurred while checking the streamer
        """
        await self.display_message("Please wait a moment.")

        broadcaster_id = await self.twitch_api.get_broadcaster_id(username)
        if not broadcaster_id:
            message = f"{username} not found."
            await self.display_message(message)
            return False

        message = f"{username} found. You will be notified when the streaming starts."
        script_args = [message, "Streamer Found"]
        if display_format == "Notification":
            await self._run_notification_script(*script_args)
        else:
            await self._run_starting_dialog_script(*script_args)

        await self.display_message(message)
        return True

    async def launch_terminal(self) -> None:
        """Open a new terminal window

        Raises:
            subprocess.SubprocessError: An error occurred while running the script
            FileNotFoundError: The script was not found
        """
        try:
            script_path = Path(self.base_dir, "applescript", "launch_terminal.applescript")
        except FileNotFoundError:
            logger.exception(traceback.format_exc())
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
            logger.exception("Failed to launch terminal window")
        except FileNotFoundError:
            logger.exception("Failed to find launch terminal script")

    async def close_terminal(self) -> None:
        """Close the terminal window

        Raises:
            subprocess.SubprocessError: An error occurred while running the script
            FileNotFoundError: The script was not found
        """
        try:
            script_path = Path(self.base_dir, "applescript", "close_terminal.applescript")
        except FileNotFoundError:
            logger.exception(traceback.format_exc())
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

    async def cleanup(self) -> None:
        """Clean up the application

        This method cancels all running tasks, closes the Twitch API client, and sets the cleanup complete event.

        Raises:
            asyncio.CancelledError: The task was cancelled
        """
        if not self.is_running:
            return
        logger.info("Starting application cleanup...")
        self.is_running = False

        # 実行中のタスクをキャンセル
        for task in self._cleanup_tasks:
            if not task.done():
                task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await task

        # Twitchクライアントのクリーンアップ
        await self.twitch_api.close()

        logger.info("Application cleanup completed")
        self.cleanup_compelete_event.set()


    def handle_signal(self, _sig: int, _frame: object | None) -> None:
        """Handle incoming signals and initiate application shutdown

        Args:
            _sig (int): The signal number
            _frame (object | None): The frame object
        """
        print("\nPlease wait a moment, terminating the application...")
        print("Do not change the currently selected tab in the terminal.")
        loop = asyncio.get_event_loop()
        loop.create_task(self.cleanup())

    async def input_monitoring_settings(self) -> tuple[str, "NotificationFormat"]:
        """Prompt the user for monitoring settings

        Returns:
            tuple[str, str]: The username and display format
        """

        username = await inquirer.text( # type: ignore
            message="Which streamer do you want to monitor?",
            validate=UsernameValidator(),
            instruction="[Enter username, not display name]",
            style=AppConstant.CUSTOM_STYLE
        ).execute_async()

        choiced_display_format = await inquirer.fuzzy( # type: ignore
            message="Which notification method do you want to use?",
            choices=[fmt.value for fmt in NotificationFormat.__members__.values()],
            instruction="[Use arrows to move, type to filter]",
            style=AppConstant.CUSTOM_STYLE,
        ).execute_async()
        display_format = NotificationFormat(choiced_display_format)
        return username, display_format # type: ignore

    async def run(self) -> None:
        """Main execution loop of the application

        Prompts the user for the streamer's username and the notification method,
        then checks for the streamer's existence.
        """
        async with self.initialize():
            try:
                # 監視設定の入力
                username, display_format = await self.input_monitoring_settings()
                # ストリーマーの存在確認
                if username and display_format:
                    if not await self.check_streamer_existence(username, display_format):
                        return

                    # 配信状態の監視を開始
                    status_task = asyncio.create_task(self.check_stream_status(username, display_format))
                    self._cleanup_tasks.append(status_task)
                    await status_task
            except (KeyboardInterrupt, asyncio.CancelledError):
                logger.info("Application shutdown requested")
            finally:
                await self.cleanup()

    def is_compiled(self) -> bool:
        """Check if the application is compiled
        """
        return "__compiled__" in globals()

async def notification_run() -> None:
    """Run the StreamNotification application
    """
    app = StreamNotification()
    if "--no-terminal" not in sys.argv and app.is_compiled():
        await app.launch_terminal()
        return
    run_task = asyncio.create_task(app.run())
    await run_task
    await app.cleanup_compelete_event.wait()
    if app.is_compiled():
        await app.close_terminal()

if __name__ == "__main__":
    sys.exit(asyncio.run(notification_run()))
