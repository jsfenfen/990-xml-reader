import logging
from .settings import LOG_KEY, KEYERROR_LOG


def configure_logging(name=LOG_KEY):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    # Format
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Setup console logging
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # Setup file logging
    fh = logging.FileHandler(KEYERROR_LOG)
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger
