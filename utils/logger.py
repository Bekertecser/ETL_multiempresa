import logging
from datetime import datetime

def setup_logger(log_file):
    logger = logging.getLogger("etl_logger")

    if not logger.handlers:
        logger.setLevel(logging.INFO)

        handler = logging.FileHandler(log_file, encoding="utf-8")
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s"
        )

        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger

def log_event(logger, server, db, action, status, message, rows=None):
    log_msg = f"""
    server={server} |
    db={db} |
    action={action} |
    status={status} |
    rows={rows if rows is not None else 'N/A'} |
    message={message}
    """

    if status == "ERROR":
        logger.error(log_msg.strip())
    else:
        logger.info(log_msg.strip())