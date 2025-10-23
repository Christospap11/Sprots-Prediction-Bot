"""
Logging configuration for the Football Betting Prediction Bot.
"""

import logging
import logging.handlers
import os
from datetime import datetime
from config.settings import settings


def setup_logging():
    """Set up comprehensive logging for the application."""
    
    # Create logs directory if it doesn't exist
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler for general logs
    today = datetime.now().strftime('%Y-%m-%d')
    file_handler = logging.handlers.RotatingFileHandler(
        f"logs/app_{today}.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(file_handler)
    
    # Error file handler
    error_handler = logging.handlers.RotatingFileHandler(
        f"logs/errors_{today}.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(error_handler)
    
    # Data collection specific logger
    data_logger = logging.getLogger('data_collection')
    data_handler = logging.handlers.RotatingFileHandler(
        f"logs/data_collection_{today}.log",
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    data_handler.setLevel(logging.INFO)
    data_handler.setFormatter(detailed_formatter)
    data_logger.addHandler(data_handler)
    data_logger.propagate = False  # Don't duplicate in root logger
    
    # Model training specific logger
    model_logger = logging.getLogger('model_training')
    model_handler = logging.handlers.RotatingFileHandler(
        f"logs/model_training_{today}.log",
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    model_handler.setLevel(logging.INFO)
    model_handler.setFormatter(detailed_formatter)
    model_logger.addHandler(model_handler)
    model_logger.propagate = False
    
    # Betting specific logger
    betting_logger = logging.getLogger('betting')
    betting_handler = logging.handlers.RotatingFileHandler(
        f"logs/betting_{today}.log",
        maxBytes=5*1024*1024,  # 5MB
        backupCount=10  # Keep more betting logs
    )
    betting_handler.setLevel(logging.INFO)
    betting_handler.setFormatter(detailed_formatter)
    betting_logger.addHandler(betting_handler)
    betting_logger.propagate = False
    
    # Performance logger
    performance_logger = logging.getLogger('performance')
    performance_handler = logging.handlers.RotatingFileHandler(
        f"logs/performance_{today}.log",
        maxBytes=5*1024*1024,  # 5MB
        backupCount=5
    )
    performance_handler.setLevel(logging.INFO)
    performance_handler.setFormatter(detailed_formatter)
    performance_logger.addHandler(performance_handler)
    performance_logger.propagate = False
    
    # Suppress noisy third-party loggers
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('selenium').setLevel(logging.WARNING)
    
    logging.info("Logging configuration completed")
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name."""
    return logging.getLogger(name)


# Convenience functions for specific loggers
def get_data_logger():
    """Get the data collection logger."""
    return logging.getLogger('data_collection')


def get_model_logger():
    """Get the model training logger."""
    return logging.getLogger('model_training')


def get_betting_logger():
    """Get the betting logger."""
    return logging.getLogger('betting')


def get_performance_logger():
    """Get the performance logger."""
    return logging.getLogger('performance')


# Initialize logging when module is imported
if not logging.getLogger().handlers:
    setup_logging() 