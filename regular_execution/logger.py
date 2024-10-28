import logging

LOG_FORMAT = "%(asctime)s - %(message)s"

logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    datefmt="%Y-%m-%d %H:%M:%S %Z",
)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
