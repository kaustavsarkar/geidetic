import logging
from logging.handlers import RotatingFileHandler


def create_rotating_logger(name, filename, max_bytes=1000000, backup_count=5) -> logging.Logger:
    """Creates a rotating logger."""

    lowger = logging.getLogger(name)
    lowger.setLevel(logging.DEBUG)

    # Create a rotating file handler
    handler = RotatingFileHandler(
        filename, maxBytes=max_bytes, backupCount=backup_count)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Add the handler to the logger
    lowger.addHandler(handler)

    return lowger


logger = create_rotating_logger('ain_logger', 'ain.log')