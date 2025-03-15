import os
import sys
import logging
from pathlib import Path
import colorlog
from datetime import datetime
from typing import Dict, Any

from app.core.config import settings


class AppLogger:
    """Application logger with support for colorful terminal and file logging"""
    
    # ANSI color codes for terminal output
    COLORS = {
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }
    
    def __init__(self, name: str = "app"):
        """Initialize the logger with the given name"""
        self.name = name
        self.log_dir = Path(settings.LOG_DIR)
        self.log_level = getattr(logging, settings.LOG_LEVEL.upper())
        
        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.log_level)
        self.logger.propagate = False
        
        # Remove existing handlers to avoid duplicates
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # Ensure log directory exists
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Add handlers
        self.setup_console_handler()
        self.setup_file_handler()
        
    def setup_console_handler(self):
        """Setup colorful console handler"""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)
        
        # Create colorful formatter
        formatter = colorlog.ColoredFormatter(
            fmt="%(log_color)s[%(asctime)s] %(levelname)-8s %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors=self.COLORS
        )
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
    def setup_file_handler(self):
        """Setup file handler with rotating log files by date"""
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.log_dir / f"{today}.log"
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(self.log_level)
        
        # Define file format (without colors)
        formatter = logging.Formatter(
            fmt="[%(asctime)s] %(levelname)-8s %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
    
    def get_logger(self) -> logging.Logger:
        """Get the configured logger"""
        return self.logger


def get_logger(name: str = "app") -> logging.Logger:
    """Get a configured logger with the given name"""
    return AppLogger(name).get_logger()


def log_request_info(request_data: Dict[str, Any]) -> None:
    """Log information about the incoming request"""
    logger = get_logger("request")
    method = request_data.get("method", "UNKNOWN")
    path = request_data.get("path", "UNKNOWN")
    client = request_data.get("client", "UNKNOWN")
    logger.info(f"{method} {path} from {client}")


def log_response_info(response_data: Dict[str, Any]) -> None:
    """Log information about the outgoing response"""
    logger = get_logger("response")
    status_code = response_data.get("status_code", "UNKNOWN")
    path = response_data.get("path", "UNKNOWN")
    logger.info(f"{status_code} for {path}") 