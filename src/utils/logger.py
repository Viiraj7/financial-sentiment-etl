#
# src/utils/logger.py
#
# This script sets up a centralized logging system for the entire application.
# It creates a logger that writes messages to both the console and a file.
#

# Import the standard Python logging library
import logging
# Import our function to load settings
from src.utils.config_loader import load_config

def setup_logger():
    """
    Configures and returns a logger based on settings in the config file.

    Returns:
        logging.Logger: A configured logger object.
    """
    # Load our settings from the YAML file
    config = load_config()
    log_config = config.get('logging', {}) # Get the 'logging' section
    log_path = log_config.get('path', 'data/logs/pipeline.log')
    log_level_str = log_config.get('level', 'INFO')

    # Convert the string log level (e.g., "INFO") into a logging constant (e.g., logging.INFO)
    log_level = getattr(logging, log_level_str.upper(), logging.INFO)

    # Get a logger instance. Using a name is good practice if you have multiple loggers.
    logger = logging.getLogger('ETL_Pipeline_Logger')
    logger.setLevel(log_level)
    
    # Prevent messages from being duplicated if the function is called multiple times
    if logger.hasHandlers():
        logger.handlers.clear()

    # Define the format for our log messages
    # Example: 2025-10-20 20:45:15,123 - INFO - This is a log message.
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # --- Create Handlers ---
    # Handlers are responsible for sending the log messages to a destination.

    # 1. File Handler: Writes log messages to our log file.
    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(formatter)
    
    # 2. Stream Handler: Writes log messages to the console (terminal).
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    # Add both handlers to our logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger

# Create a single logger instance to be imported by other modules
logger = setup_logger()