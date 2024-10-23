import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime


def setup_logging(__name__=None, log_level="INFO"):
    """
    Set up logging configuration.
    """
    log_format = "%(asctime)s - %(name)s:%(lineno)s - %(levelname)s - %(message)s"
    log_level = logging.getLevelName(log_level)

    # File path for the log file
    log_file_path = "server.log"

    # Create a logger
    logger = logging.getLogger(name=__name__)
    logger.setLevel(log_level)

    # Create a file handler with rotating capability and UTF-8 encoding
    try:
        file_handler = RotatingFileHandler(
            log_file_path,
            maxBytes=10 * 1024 * 1024,
            backupCount=0,
            encoding="utf-8",  # 10 MB, no backup count, UTF-8 encoding
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(logging.Formatter(log_format))
        logger.addHandler(file_handler)

    except PermissionError as e:
        print(f"PermissionError: {e} - Log file is being used by another process.")
        # Handling permission error: Create a new log file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_log_file_path = f"server_{timestamp}.log"
        try:
            file_handler = RotatingFileHandler(
                new_log_file_path,
                maxBytes=10 * 1024 * 1024,
                backupCount=0,
                encoding="utf-8",  # UTF-8 encoding
            )
            file_handler.setLevel(log_level)
            file_handler.setFormatter(logging.Formatter(log_format))
            logger.addHandler(file_handler)
            print(f"Created new log file: {new_log_file_path}")
        except Exception as e:
            print(f"Failed to create new log file: {e}")

    except Exception as e:
        print(f"Failed to set up logging: {e}")

    return logger
