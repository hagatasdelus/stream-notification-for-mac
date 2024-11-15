import logging

from src.constants import AppConstant

logging.basicConfig(
    level=logging.INFO,
    format=AppConstant.LOG_FORMAT,
    datefmt="%Y-%m-%d %H:%M:%S %Z",
)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
