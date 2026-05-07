"""
Simple logging utility for the hand detection application.
"""

import sys
import traceback
from datetime import datetime
from app.config.settings import LOG_LEVEL


class Logger:
    """Lightweight console logger with timestamp and level indicators."""
    
    LEVELS = {
        'DEBUG': (0, '[DEBUG]', '\033[36m'),    # Cyan
        'INFO': (1, '[INFO]', '\033[32m'),      # Green
        'WARNING': (2, '[WARNING]', '\033[33m'),  # Yellow
        'ERROR': (3, '[ERROR]', '\033[31m'),    # Red
    }
    
    RESET = '\033[0m'
    
    def __init__(self, level=LOG_LEVEL):
        """Initialize logger with minimum level."""
        self.level = level
        self.min_level = self.LEVELS[level][0]
    
    def _log(self, level, message):
        """Internal logging method."""
        if self.LEVELS[level][0] < self.min_level:
            return
        
        timestamp = datetime.now().strftime('%H:%M:%S')
        color = self.LEVELS[level][2]
        tag = self.LEVELS[level][1]
        
        log_message = f"{color}{tag} {timestamp} | {message}{self.RESET}"
        print(log_message, file=sys.stdout)
    
    def debug(self, message):
        """Log debug message."""
        self._log('DEBUG', message)
    
    def info(self, message):
        """Log info message."""
        self._log('INFO', message)
    
    def warning(self, message):
        """Log warning message."""
        self._log('WARNING', message)
    
    def error(self, message, **kwargs):
        """Log error message."""
        if kwargs.get('exc_info'):
            message = f"{message}\n{traceback.format_exc().rstrip()}"
        self._log('ERROR', message)


# Global logger instance
logger = Logger()
