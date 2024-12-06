import enum


class StreamStatus(enum.Enum):
    """Enum class for stream status.

    Attributes:
        STREAMING: Streaming status.
        NOTSTREAMING: Not streaming status.
    """
    STREAMING = "streaming"
    NOTSTREAMING = "not streaming"
