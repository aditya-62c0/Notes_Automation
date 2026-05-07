import logging
from datetime import datetime
from pathlib import Path

from config.environment import Reporting


def get_logger(name: str) -> logging.Logger:

    log_dir = Path(Reporting.LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / f"test_run_{datetime.now().strftime('%Y%m%d')}.log"

    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # File handler → stores complete logs
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    # Prevent duplicate logs
    logger.propagate = False

    return logger