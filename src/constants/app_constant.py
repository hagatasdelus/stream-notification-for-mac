# -*- coding: utf-8 -*-

__author__ = "Hagata"
__version__ = "0.0.1"
__date__ = "2024/12/08 (Created: 2024/10/20)"

from InquirerPy.utils import InquirerPyStyle, get_style

from .strict_constant import StrictConstant


class AppConstant(StrictConstant):
    """
    アプリケーション全体で使用する定数を定義するクラス
    """
    # Twitch API関連
    CHECK_INTERVAL: int = 60  # 通常の確認間隔（秒）
    STREAMING_INTERVAL: int = 3600  # 配信中の確認間隔（秒）

    TIMEOUT_SECONDS: int = 10
    GRANT_TYPE: str = "client_credentials"

    # エラーメッセージの定義
    ERROR_SESSION_NOT_INITIALIZED: str = "Session not initialized"
    ERROR_ACCESS_TOKEN_NOT_AVAILABLE: str = "Access token not available" # noqa: S105
    ERROR_ACCESS_TOKEN_FAILED: str = "Failed to get access token" # noqa: S105
    ERROR_API_REQUEST_FAILED: str = "API request failed"

    STYLE: dict = {
        "questionmark": "#a7e22e bold",  # ?マークの色
        "answermark": "#a7e22e bold",    # 回答マークの色
        "instruction": "#56abb9",  # 説明文の色
        "answer": "#65daef bold",  # 選択された項目の色
        "pointer": "#65daef",     # 現在選択中の項目の色
        "input": "#ffffff bold",   # 入力中の色
    }

    # 対話型インターフェイスのスタイル
    CUSTOM_STYLE: InquirerPyStyle = get_style(style=STYLE, style_override=False)

    # ロガーの設定
    LOG_FORMAT = "%(asctime)s - %(message)s"
    LOG_FILE = "notification.log"
