import logging
from logging.handlers import RotatingFileHandler

def setup_logging(log_file='dataset_creation.log'):
    """
    Sets up logging for the script.

    Parameters:
    - log_file (str): Path to the log file.

    Returns:
    - logger: Configured logger instance.
    """
    logger = logging.getLogger('IssueDatasetCreator')
    logger.setLevel(logging.DEBUG)  # Capture all levels of logs

    # Prevent adding multiple handlers if the logger already has them
    if not logger.handlers:
        # Create handlers
        c_handler = logging.StreamHandler()
        f_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=2)
        c_handler.setLevel(logging.INFO)
        f_handler.setLevel(logging.DEBUG)

        # Create formatters and add to handlers
        c_format = logging.Formatter('%(levelname)s: %(message)s')
        f_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        c_handler.setFormatter(c_format)
        f_handler.setFormatter(f_format)

        # Add handlers to the logger
        logger.addHandler(c_handler)
        logger.addHandler(f_handler)

    return logger
