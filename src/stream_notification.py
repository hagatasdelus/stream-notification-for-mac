# -*- coding: utf-8 -*-

"""
stream_notification.py

This module contains the implementation of the StreamNotification application,
which monitors the streaming status of a Twitch streamer and provides notifications.
"""

import asyncio
import contextlib
import os
import subprocess
import sys
import termios
import traceback
import tty
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

import urllib3.util
from InquirerPy import inquirer

from src.constants import AppConstant
from src.enums import NotificationFormat
from src.terminal import Terminal
from src.twitch import TwitchAPI
from src.utils import FormatValidator, UsernameValidator, get_base_path, get_logger

logger = get_logger(__name__)

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
        self.cleanup_complete_event = asyncio.Event()
        self.terminal = Terminal(self.base_dir)

    @asynccontextmanager
    async def initialize(self) -> AsyncIterator["StreamNotification"]:
        """Application initialization context manager

        Yields:
            StreamNotification: The StreamNotification instance
        """
        await self.twitch_api.initialize()
        yield self

    async def display_message(self, message: str) -> None:
        """Display a message to the user"""
        print(message)
        await asyncio.sleep(0)

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

    async def _run_notification_script(self, message: str, title: str) -> None:
        """Run the notification AppleScript to display a notification

        Args:
            message (str): The message to display
            title (str): The title of the notification

        Raises:
            subprocess.SubprocessError: An error occurred while running the script
            FileNotFoundError: The script was not found
        """
        try:
            script_path = Path(self.base_dir, "applescript", "notification.applescript")
        except FileNotFoundError:
            logger.exception(traceback.format_exc())
            return

        script_arguments = [message, title]

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


    async def _run_dialog_script(self, message: str, title: str, a_url: urllib3.util.Url) -> None:
        """Run to display a dialogue Applescript informing that the monitored object has started a stream

        Args:
            message (str): The message to display
            title (str): The title of the dialog
            a_url (urllib3.util.Url): The URL to open

        Raises:
            subprocess.SubprocessError: An error occurred while running the script
            FileNotFoundError: The script was not found
        """
        try:
            script_path = Path(self.base_dir, "applescript", "dialog.applescript")
        except FileNotFoundError:
            logger.exception(traceback.format_exc())
            return

        filename = getattr(self, "downloaded_profile_image_name", None) or "profile_image.png"
        icon_full_path = os.path.join(
            self.base_dir.parent.as_posix(),
            "Resources",
            filename
        )
        script_arguments = [message, title, a_url.url, icon_full_path]

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

    async def _run_starting_dialog_script(self, message: str, title: str, icon_full_path: str) -> None:
        """Run to display dialog Applescript to start monitoring

        Args:
            message (str): The message to display
            title (str): The title of the dialog
            icon_full_path (str): The full path to the icon

        Raises:
            subprocess.SubprocessError: An error occurred while running the script
            FileNotFoundError: The script was not found
        """
        try:
            script_path = Path(self.base_dir, "applescript", "starting_dialog.applescript")
        except FileNotFoundError:
            logger.exception(traceback.format_exc())
            return

        script_arguments = [message, title, icon_full_path]

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

            if display_name and stream_title:
                url_string = f"https://www.twitch.tv/{username}"
                a_url: urllib3.util.Url = urllib3.util.parse_url(url_string)
                message = self.format_display_message(username, display_name, stream_title)
                notification_title = "Stream Started"
                if display_format == NotificationFormat.NOTIFICATION:
                    await self._run_notification_script(message, notification_title)
                else:
                    await self._run_dialog_script(message, notification_title, a_url)
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

        resources_dir = Path(os.path.join(self.base_dir.parent.as_posix(), "Resources"))
        result = await self.twitch_api.get_broadcaster_id(username, resources_dir)
        if not result or not result[0]:
            message = f"{username} not found."
            await self.display_message(message)
            return False

        broadcaster_id, image_filename = result
        image_filename = image_filename or "profile_image.png"
        self.downloaded_profile_image_name = image_filename

        message = f"{username} found. You will be notified when the streaming starts."

        found_title = "Streamer Found"
        if display_format == NotificationFormat.NOTIFICATION:
            await self._run_notification_script(message, found_title)
        else:
            icon_path = os.path.join(resources_dir.as_posix(), image_filename)
            await self._run_starting_dialog_script(message, found_title, icon_path)

        await self.display_message(message)
        how_to_quit = "Type [q] to quit the application."
        await self.display_message(how_to_quit)
        return True

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

        try:
            if hasattr(self, "downloaded_profile_image_name"):
                filename = self.downloaded_profile_image_name or "profile_image.png"
                resources_path = Path(self.base_dir.parent.as_posix(), "Resources", filename)
                if resources_path.exists():
                    resources_path.unlink()
        except OSError:
            logger.warning("Failed to remove downloaded profile image.")

        logger.info("Application cleanup completed")
        self.cleanup_complete_event.set()


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
            validate=FormatValidator(),
            instruction="[Use arrows to move, type to filter]",
            style=AppConstant.CUSTOM_STYLE,
        ).execute_async()
        display_format = NotificationFormat(choiced_display_format)
        return username, display_format # type: ignore

    async def listen_for_quit(self) -> None:
        """This method listens for the 'q' keypress and triggers the cleanup process when detected.

        Raises:
            EOFError: If the input stream is closed
            KeyboardInterrupt: If the input stream is interrupted
        """
        def _read_char() -> str:
            # 標準入力の設定を保存
            old_settings = termios.tcgetattr(sys.stdin)
            try:
                tty.setraw(sys.stdin.fileno()) # 標準入力を非カノニカルモードに設定
                return sys.stdin.read(1)
            finally:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings) # 標準入力の設定を元に戻す

        loop = asyncio.get_event_loop()
        while self.is_running:
            char = await loop.run_in_executor(None, _read_char)
            if char.lower() == "q":
                print("\nQuit command received. Terminating application...")
                await self.cleanup()
                break

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
                    quit_task = asyncio.create_task(self.listen_for_quit())
                    self._cleanup_tasks.append(quit_task)
                    await asyncio.wait([status_task, quit_task], return_when=asyncio.FIRST_COMPLETED)
            except (KeyboardInterrupt, asyncio.CancelledError):
                logger.info("Application shutdown requested")
            finally:
                await self.cleanup()

    def is_compiled(self) -> bool:
        """Check if the application is compiled
        """
        return "__compiled__" in globals()

async def run_stream_notification() -> None:
    """Run the StreamNotification application
    """
    app = StreamNotification()
    if "--no-terminal" not in sys.argv and app.is_compiled():
        await app.terminal.launch_terminal()
        return
    print(f"app.base_dir: {app.base_dir}")
    run_task = asyncio.create_task(app.run())
    await run_task
    await app.cleanup_complete_event.wait()
    if app.is_compiled():
        await app.terminal.close_terminal()
