import logging
import os
from datetime import datetime
from pathlib import Path

LOG_DIR_NAME = "Log Files"
LOG_BASE_DIR = os.path.join(str(Path.home()), "ProjectBudgetinator", LOG_DIR_NAME)
LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
MAX_LOG_FILES = 10

# Ensure log directory exists
os.makedirs(LOG_BASE_DIR, exist_ok=True)

def get_log_filename(level):
    today = datetime.now().strftime("%d-%m-%Y")
    return os.path.join(LOG_BASE_DIR, f"{today}-{level}.log")

def setup_logging():
    # Remove old log files if more than MAX_LOG_FILES exist
    log_files = sorted([f for f in os.listdir(LOG_BASE_DIR) if f.endswith('.log')])
    if len(log_files) > MAX_LOG_FILES:
        for f in log_files[:-MAX_LOG_FILES]:
            try:
                os.remove(os.path.join(LOG_BASE_DIR, f))
            except Exception:
                pass
    # Set up root logger with handlers for each level
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    # Remove existing handlers
    for h in logger.handlers[:]:
        logger.removeHandler(h)
    # Add a handler for each log level
    for level in LOG_LEVELS:
        handler = logging.FileHandler(get_log_filename(level))
        handler.setLevel(getattr(logging, level))
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(module)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    # Also log to console (INFO+)
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s | %(message)s')
    console.setFormatter(formatter)
    logger.addHandler(console)
    return logger

# Usage: import and call setup_logging() at app startup
# Then use logging.debug/info/warning/error/critical as needed
