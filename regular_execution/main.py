import asyncio
import os
import signal
import subprocess
import sys
from pathlib import Path
from typing import NoReturn

from regular_execution.logger import get_logger
from regular_execution.stream_status import StreamStatus
from regular_execution.twitch import TwitchAPI

logger = get_logger(__name__)

def get_base_path():
    """実行ファイルのベースパスを取得"""
    if "__compiled__" in globals():
        return Path(os.path.dirname(os.path.realpath(sys.argv[0])))
    return Path(__file__).parent.resolve()


class StreamNotificationApp:
    def __init__(self):
        self.base_dir = get_base_path()
        self.twitch_api = TwitchAPI()
        self.is_running = True

    def _handle_script_not_found(self, script_path: Path) -> NoReturn:
        """スクリプトが見つからない場合のエラー処理"""
        error_msg = f"Script not found: {script_path}"
        raise FileNotFoundError(error_msg)

    def display_message(self, message: str) -> None:
        """メッセージを現在のターミナルに表示"""
        print(message)

    def format_display_message(self, username: str, display_name: str, stream_title: str) -> str:
        base_format = f" has started streaming: {stream_title}"
        if username == display_name:
            return display_name + base_format
        return f"{display_name}({username})"+ base_format

    def _run_notification_script(self, message: str, title: str) -> None:
        """通知用のAppleScriptを実行する"""
        try:
            script_path = self.base_dir / "applescript" / "notification.applescript"
            if not script_path.exists():
                self._handle_script_not_found(script_path)

            cmd = ["/usr/bin/osascript", str(script_path), message, title]
            subprocess.run(cmd, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.exception("Notification failed")

    async def check_stream_status(self, username: str) -> None:
        """配信状態を定期的にチェック"""
        while self.is_running:
            try:
                display_name, stream_title = self.twitch_api.get_stream_by_name(username)

                is_streaming = stream_title is not None
                status_message = StreamStatus.STREAMING if is_streaming else StreamStatus.NOTSTREAMING
                logger.info("Checking stream status: %s - %s", username, status_message.value.title())

                if display_name and stream_title:
                    # 配信開始を検知
                    message = self.format_display_message(username, display_name, stream_title)
                    self._run_notification_script(message, "Stream Started")
                    self.display_message(message)
                    await asyncio.sleep(3600)  # 配信検知後は1時間待機
                else:
                    await asyncio.sleep(60)  # 1分ごとにチェック

            except (subprocess.SubprocessError, OSError):
                logger.exception("Error checking stream status")
                await asyncio.sleep(60)

    async def check_streamer_existence(self, username: str) -> bool:
        """ストリーマーの存在確認"""
        try:
            # 待機メッセージを表示
            self.display_message("Please wait a moment.")

            broadcaster_id = self.twitch_api.get_broadcaster_id(username)
            if broadcaster_id:
                message = f"{username} found. You will be notified when the streaming starts."
                self._run_notification_script(message, "Streamer Found")
                self.display_message(message)
                return True

            # ストリーマーが見つからない場合
            message = f"{username} not found."
            self.display_message(message)
            return False

        except (subprocess.SubprocessError, OSError, ValueError):
            logger.exception("Error checking streamer existence")
            self.display_message("An error occurred while checking streamer.")
            return False

    def cleanup(self) -> None:
        """アプリケーションのクリーンアップ処理"""
        self.is_running = False

    def handle_signal(self, _sig: int, _frame: object | None) -> None:
        """シグナルハンドラ"""
        self.cleanup()
        sys.exit(0)

    async def run(self) -> None:
        """メインの実行ループ"""
        try:
            # シグナルハンドラの設定
            signal.signal(signal.SIGINT, self.handle_signal)

            # 標準入力からユーザー名を読み取り
            while True:
                username = input("Enter Twitch username: ").strip()
                if username:
                    break

            # ストリーマーの存在確認
            if not await self.check_streamer_existence(username):
                return

            # 配信状態の監視を開始
            await self.check_stream_status(username)

        except (KeyboardInterrupt, subprocess.SubprocessError, OSError):
            logger.exception("An error occurred")
            self.cleanup()

def launch_terminal():
    """新しいターミナルウィンドウを開いてスクリプトを実行"""
    base_path = get_base_path()

    script_path = Path(__file__).parent / "applescript" / "launch_terminal.applescript"

    try:
        with open(script_path, "r") as file:
            script_content = file.read().replace("{{base_path}}", str(base_path))

        subprocess.run(["/usr/bin/osascript", "-e", script_content], check=True)

    except FileNotFoundError:
        logger.exception("AppleScript file not found")
    except subprocess.CalledProcessError:
        logger.exception("Failed to execute AppleScript")


def main() -> None:
    # コマンドライン引数をチェック
    if "--no-terminal" not in sys.argv and "__compiled__" in globals():
        # バンドル化されている場合と通常実行の場合で処理を分ける
        launch_terminal()
        return

    app = StreamNotificationApp()
    asyncio.run(app.run())


if __name__ == "__main__":
    main()
