from .strict_constant import StrictConstant


class AppConstant(StrictConstant):
    """
    アプリケーション全体で使用する定数を定義するクラス
    """
    # エラーメッセージ
    CHECK_INTERVAL: int = 60  # 通常の確認間隔（秒）
    STREAMING_INTERVAL: int = 3600  # 配信中の確認間隔（秒）

    TIMEOUT_SECONDS: int = 10
    GRANT_TYPE: str = "client_credentials"

    # エラーメッセージの定義
    ERROR_SESSION_NOT_INITIALIZED: str = "Session not initialized"
    ERROR_ACCESS_TOKEN_NOT_AVAILABLE: str = "Access token not available" # noqa: S105
    ERROR_ACCESS_TOKEN_FAILED: str = "Failed to get access token" # noqa: S105
    ERROR_API_REQUEST_FAILED: str = "API request failed"
