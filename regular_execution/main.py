import os
import subprocess
import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from regular_execution.twitch import TwitchAPI


class StreamNotificationApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("StreamNotification")
        self.root.geometry("300x150")

        # スクリプトのベースディレクトリを取得
        self.base_dir = Path(__file__).parent.absolute()

        # GUI要素の作成
        self.label = tk.Label(self.root, text="Streamerのユーザ名を入力してください")
        self.label.pack(pady=10)

        self.entry = tk.Entry(self.root)
        self.entry.pack(pady=10)

        self.submit_button = tk.Button(self.root, text="選択", command=self.handle_submit)
        self.submit_button.pack(pady=10)

        self.twitch_api = TwitchAPI()

    def handle_submit(self):
        username = self.entry.get()
        if not username:
            messagebox.showerror("エラー", "ユーザ名を入力してください")
            return

        broadcaster_id = self.twitch_api.get_broadcaster_id(username)

        if broadcaster_id is None:
            # ユーザーが見つからない場合
            try:
                subprocess.run(
                    ["/usr/bin/osascript", str(self.base_dir / "applescript" / "notfound")],
                    check=True
                )
            except subprocess.CalledProcessError as e:
                messagebox.showerror("エラー", f"通知の表示に失敗しました: {e}")
        else:
            # ユーザーが見つかった場合
            try:
                subprocess.run(
                    ["/usr/bin/osascript", str(self.base_dir / "applescript" / "notification")],
                    check=True
                )
            except subprocess.CalledProcessError as e:
                messagebox.showerror("エラー", f"通知の表示に失敗しました: {e}")

        self.root.destroy()

def open_new_terminal():
    try:
        # osascriptをシェルを使用せずに実行
        script = """
        tell application "Terminal"
            do script "echo StreamNotificationウィンドウで配信通知したいStreamerのユーザ名を入力してください。"
            activate
        end tell
        """
        subprocess.run(
            ["/usr/bin/osascript", "-e", script],
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        print(f"ターミナルの起動に失敗しました: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    # 新しいターミナルウィンドウを開く
    open_new_terminal()

    # GUIアプリケーションの起動
    app = StreamNotificationApp()
    app.root.mainloop()

if __name__ == "__main__":
    main()
