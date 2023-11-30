"""Custom logger configuration."""
from sys import stdout

from loguru import logger as custom_logger


def log_formatter(record: dict) -> str:
    """
    Formatter for `.logger` records.

    Args:
    - record (dict): Log object containing log metadata & message.

    Returns:
    - str: Formatted log message.
    """
    time_format = "{time:MM-DD-YYYY HH:mm:ss}"
    level_format = "<fg #6ABCFF>{level}</fg #6ABCFF>:"
    message_format = "<light-white>{message}</light-white>\n"

    level_styles = {
        "TRACE": "<fg #DFF0FF>",
        "INFO": "<fg #A2D2FC>",
        "DEBUG": "<fg #889CF8>",
        "WARNING": "<fg #F0B34A>",
        "SUCCESS": "<fg #17F591>",
        "ERROR": "<fg #FA0000>",
    }

    log_level = record["level"].name
    level_style = level_styles.get(log_level, "<fg #C2E3FF>")

    return f"{time_format} | {level_style}{level_format} {message_format}"


def create_logger() -> custom_logger:
    """Create custom logger."""
    custom_logger.remove()
    custom_logger.add(stdout, colorize=True, format=log_formatter)
    return custom_logger


LOGGER = create_logger()
