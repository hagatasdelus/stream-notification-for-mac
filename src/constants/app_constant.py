# -*- coding: utf-8 -*-

"""
This module defines constants used throughout the application.
"""

from InquirerPy.utils import InquirerPyStyle, get_style

from .strict_constant import StrictConstant


class AppConstant(StrictConstant):
    """
    Constants used throughout the application.

    Attributes:
        CHECK_INTERVAL (int): Normal check interval (seconds).
        STREAMING_INTERVAL (int): Check interval when streaming (seconds).
        TIMEOUT_SECONDS (int): Timeout seconds for requests.
        GRANT_TYPE (str): Grant type for the Twitch API.
        ERROR_SESSION_NOT_INITIALIZED (str): Error message for uninitialized session.
        ERROR_ACCESS_TOKEN_NOT_AVAILABLE (str): Error message for unavailable access token.
        ERROR_ACCESS_TOKEN_FAILED (str): Error message for failed access token retrieval.
        ERROR_API_REQUEST_FAILED (str): Error message for failed API requests.
        STYLE (dict): Style settings for the interactive interface.
        CUSTOM_STYLE (InquirerPyStyle): Custom style for the interactive interface.
        LOG_FORMAT (str): Log format.
        LOG_FILE (str): Log file name.
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
