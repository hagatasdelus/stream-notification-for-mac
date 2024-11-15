import asyncio
import contextlib
import os
import subprocess
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator, NoReturn

from InquirerPy import inquirer
from prompt_toolkit.validation import ValidationError, Validator

from src.constants import AppConstant
from src.logger import get_logger
from src.stream_status import StreamStatus
from src.twitch import TwitchAPI, TwitchAPIError

logger = get_logger(__name__)

def get_base_path() -> Path:
    """実行ファイルのベースパスを取得"""
    if "__compiled__" in globals():
        return Path(os.path.dirname(os.path.realpath(sys.argv[0])))
    return Path(__file__).parent.resolve()

class UsernameValidator(Validator):
    """ユーザー名のバリデーション"""
    def validate(self, document) -> None:
        """ユーザー名のバリデーション"""
        if not document.text: # 入力が空の場合
            raise ValidationError(message="Username cannot be empty", cursor_position=len(document.text))
        if not document.text.isalnum() or not document.text.isascii(): # 英数字でない場合
            raise ValidationError(message="Username must be alphanumeric", cursor_position=len(document.text))

class StreamNotificationApp:
    def __init__(self):
        self.base_dir = get_base_path()
        self.twitch_api = TwitchAPI()
        self.is_running = True
        self._cleanup_tasks: list[asyncio.Task] = []
        self.cleanup_compelete_event = asyncio.Event()

    @asynccontextmanager
    async def initialize(self) -> AsyncIterator["StreamNotificationApp"]:
        """アプリケーションの初期化とクリーンアップを管理"""
        await self.twitch_api.initialize()
        yield self

    def _handle_script_not_found(self, script_path: Path) -> NoReturn:
        """スクリプトが見つからない場合のエラー処理"""
        error_msg = f"Script not found: {script_path}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)

    async def display_message(self, message: str) -> None:
        """メッセージを非同期に表示"""
        print(message)
        await asyncio.sleep(0)  # イベントループに制御を戻す

    def format_display_message(self, username: str, display_name: str, stream_title: str) -> str:
        """表示メッセージのフォーマット"""
        base_format = f" has started streaming: {stream_title}"
        if username.lower() == display_name.lower():
            return display_name + base_format
        return f"{display_name}({username})" + base_format

    async def _run_notification_script(self, message: str, title: str) -> None:
        """通知用のAppleScriptを非同期に実行"""
        try:
            script_path = Path(self.base_dir, "applescript", "notification.applescript")
            if not script_path.exists():
                self._handle_script_not_found(script_path)

            proc = await asyncio.create_subprocess_exec(
                "/usr/bin/osascript",
                script_path,
                message,
                title,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()

        except (subprocess.SubprocessError, FileNotFoundError):
            logger.exception("Notification failed")
            await self.display_message("Failed to send notification")

    async def _run_dialog_script(self, message: str, title: str) -> None:
        """ダイアログ表示用のAppleScriptを非同期に実行"""
        try:
            script_path = Path(self.base_dir, "applescript", "dialog.applescript")
            if not script_path.exists():
                self._handle_script_not_found(script_path)
            icon_path = "AppIcon.png"
            if not self.is_compiled():
                icon_path = os.path.join("..", icon_path)
            proc = await asyncio.create_subprocess_exec(
                "/usr/bin/osascript",
                script_path,
                message,
                title,
                icon_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()

        except (subprocess.SubprocessError, FileNotFoundError):
            logger.exception("Dialog failed")
            await self.display_message("Failed to display dialog")

    async def check_stream_status(self, username: str, display_format: str) -> None:
        """配信状態を定期的にチェック"""
        while self.is_running:
            try:
                display_name, stream_title = await self.twitch_api.get_stream_by_name(username)
                is_streaming = stream_title is not None
                status = StreamStatus.STREAMING if is_streaming else StreamStatus.NOTSTREAMING

                logger.info(
                    "Checking stream status: %s - %s",
                    username,
                    status.value.title()
                )

                if display_name and stream_title:
                    message = self.format_display_message(username, display_name, stream_title)
                    script_args = [message, "Stream Started"]
                    if display_format == "Notification":
                        await self._run_notification_script(*script_args)
                    else:
                        await self._run_dialog_script(*script_args)
                    await self.display_message(message)
                    await asyncio.sleep(AppConstant.STREAMING_INTERVAL)
                else:
                    await asyncio.sleep(AppConstant.CHECK_INTERVAL)

            except TwitchAPIError:
                logger.exception("Failed to check stream status")
                await asyncio.sleep(AppConstant.CHECK_INTERVAL)
            except Exception:
                logger.exception("Unexpected error while checking stream status")
                await asyncio.sleep(AppConstant.CHECK_INTERVAL)

    async def check_streamer_existence(self, username: str, display_format: str) -> bool:
        """ストリーマーの存在確認"""
        try:
            await self.display_message("Please wait a moment.")

            broadcaster_id = await self.twitch_api.get_broadcaster_id(username)
            if broadcaster_id:
                message = f"{username} found. You will be notified when the streaming starts."
                script_args = [message, "Streamer Found"]
                if display_format == "Notification":
                    await self._run_notification_script(*script_args)
                else:
                    await self._run_dialog_script(*script_args)

                await self.display_message(message)
                return True

            message = f"{username} not found."
            await self.display_message(message)
            return False

        except TwitchAPIError:
            logger.exception("Failed to check streamer existence")
            await self.display_message("Failed to check streamer existence.")
            return False
        except Exception:
            logger.exception("Unexpected error while checking streamer")
            await self.display_message("An unexpected error occurred.")
            return False

    async def launch_terminal(self) -> None:
        """新しいターミナルウィンドウを非同期に開く"""
        script_path = Path(self.base_dir, "applescript", "launch_terminal.applescript")
        try:
            proc = await asyncio.create_subprocess_exec(
                "/usr/bin/osascript",
                script_path,
                self.base_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()

        except FileNotFoundError:
            logger.exception("AppleScript file not found")
        except subprocess.SubprocessError:
            logger.exception("Failed to execute AppleScript")

    async def close_terminal(self) -> None:
        """ターミナルウィンドウを非同期に閉じる"""
        try:
            script_path = Path(self.base_dir, "applescript", "close_terminal.applescript")
            if not script_path.exists():
                self._handle_script_not_found(script_path)
            print("Closing terminal window...")
            proc = await asyncio.create_subprocess_exec(
                "/usr/bin/osascript",
                script_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            if proc.returncode != 0:
                logger.error("Failed to close terminal window: %s", stderr.decode())
                if stderr:
                    logger.error("Error output: %s", stderr.decode())
        except FileNotFoundError:
            logger.exception("AppleScript file not found")
        except subprocess.SubprocessError:
            logger.exception("Failed to close terminal window")

    async def cleanup(self) -> None:
        """アプリケーションのクリーンアップ処理"""
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
        """シグナルハンドラ"""
        print("\nPlease wait a moment, terminating the application...")
        print("Do not change the currently selected tab in the terminal.")
        loop = asyncio.get_event_loop()
        loop.create_task(self.cleanup())

    async def run(self) -> None:
        """メインの実行ループ"""
        async with self.initialize():
            try:
                username = await inquirer.text( # type: ignore
                    message="Which streamer do you want to monitor?",
                    validate=UsernameValidator(),
                    instruction="[Enter username, not display name]",
                    style=AppConstant.CUSTOM_STYLE
                ).execute_async()

                display_format = await inquirer.fuzzy( # type: ignore
                    message="Which notification method do you want to use?",
                    choices=["Notification", "Dialog"],
                    instruction="[Use arrows to move, type to filter]",
                    style=AppConstant.CUSTOM_STYLE,
                ).execute_async()

                # ストリーマーの存在確認
                if username and display_format:
                    if not await self.check_streamer_existence(username, display_format):
                        return

                    # 配信状態の監視を開始
                    status_task = asyncio.create_task(self.check_stream_status(username, display_format))
                    self._cleanup_tasks.append(status_task)
                    await status_task

            except (asyncio.CancelledError, KeyboardInterrupt):
                logger.info("Application shutdown requested")
            except Exception:
                logger.exception("Unexpected error in main loop")
            finally:
                await self.cleanup()

    def is_compiled(self) -> bool:
        """アプリケーションがバンドル化されているか確認"""
        return "__compiled__" in globals()

async def main() -> None:
    """非同期メイン関数"""
    app = StreamNotificationApp()
    if "--no-terminal" not in sys.argv and app.is_compiled():
        await app.launch_terminal()
        return
    run_task = asyncio.create_task(app.run())
    await run_task
    await app.cleanup_compelete_event.wait()
    if app.is_compiled():
        await app.close_terminal()

if __name__ == "__main__":
    asyncio.run(main())
