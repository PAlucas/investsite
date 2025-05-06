import logging
import sys
from typing import Optional

# Global logger configuration
_logger_configured: bool = False
_log_level: int = logging.INFO
_log_format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

def set_log_level(level: int) -> None:
    """Set the global log level"""
    global _log_level
    _log_level = level

def set_log_format(format_str: str) -> None:
    """Set the global log format"""
    global _log_format
    _log_format = format_str

def configure_logging() -> logging.Logger:
    """Configure logging for the application"""
    global _logger_configured
    
    # Create root logger
    logger = logging.getLogger()
    
    # Only configure once
    if not _logger_configured:
        # Clear existing handlers
        for handler in logger.handlers[:]:  # Make a copy of the list
            logger.removeHandler(handler)
        
        # Set level from global configuration
        logger.setLevel(_log_level)
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(_log_level)
        
        # Create formatter
        formatter = logging.Formatter(_log_format)
        console_handler.setFormatter(formatter)
        
        # Add console handler to logger
        logger.addHandler(console_handler)
        
        # Configure werkzeug logger
        werkzeug_logger = logging.getLogger('werkzeug')
        werkzeug_logger.setLevel(_log_level)
        
        # Configure SQLAlchemy logger
        sqlalchemy_logger = logging.getLogger('sqlalchemy')
        sqlalchemy_logger.setLevel(logging.WARNING)
        
        _logger_configured = True
    
    return logger
