"""
Centralized logging configuration with colorized output.

This module provides a unified logging configuration for the entire application
with colored console output for better readability and debugging.
"""

import logging
import os
import sys
from typing import Optional

# Import colorama for cross-platform color support
try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)  # Automatically reset colors after each print
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colored output for different log levels."""
    
    if COLORAMA_AVAILABLE:
        # Use colorama colors for better cross-platform support
        COLORS = {
            'DEBUG': Fore.CYAN + Style.BRIGHT,           # Bright Cyan
            'INFO': Fore.GREEN + Style.BRIGHT,           # Bright Green  
            'WARNING': Fore.YELLOW + Style.BRIGHT,       # Bright Yellow
            'ERROR': Fore.RED + Style.BRIGHT,            # Bright Red
            'CRITICAL': Fore.MAGENTA + Style.BRIGHT,     # Bright Magenta
            'RESET': Style.RESET_ALL,                    # Reset all formatting
        }
    else:
        # Fallback ANSI color codes
        COLORS = {
            'DEBUG': '\033[96m',      # Cyan
            'INFO': '\033[92m',       # Green  
            'WARNING': '\033[93m',    # Yellow
            'ERROR': '\033[91m',      # Red
            'CRITICAL': '\033[95m',   # Magenta
            'RESET': '\033[0m',       # Reset
        }
    
    def __init__(self, fmt: str = None, datefmt: str = None, use_colors: bool = True):
        """
        Initialize the colored formatter.
        
        Args:
            fmt: Log format string
            datefmt: Date format string
            use_colors: Whether to use colored output
        """
        super().__init__(fmt, datefmt)
        self.use_colors = use_colors and self._supports_color()
    
    def _supports_color(self) -> bool:
        """Check if the terminal supports color output."""
        # If colorama is available, it handles cross-platform color support
        if COLORAMA_AVAILABLE:
            return True
            
        # Check for Windows
        if os.name == 'nt':
            # Enable ANSI color support on Windows 10+
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
                return True
            except:
                return False
        
        # Check for Unix-like systems
        return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    
    def format(self, record: logging.LogRecord) -> str:
        """Format the log record with colors."""
        if not self.use_colors:
            return super().format(record)
        
        # Get the base formatted message
        log_message = super().format(record)
        
        # Get color for the log level
        level_color = self.COLORS.get(record.levelname, '')
        reset_color = self.COLORS.get('RESET', '')
        
        # Add color to the level name only
        if level_color:
            colored_level = f"{level_color}{record.levelname}{reset_color}"
            log_message = log_message.replace(record.levelname, colored_level, 1)
        
        return log_message


def setup_logger(
    name: str,
    level: Optional[str] = None,
    format_string: Optional[str] = None,
    use_colors: bool = True
) -> logging.Logger:
    """
    Set up a logger with the standardized configuration.
    
    Args:
        name: Logger name (usually __name__)
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Custom format string
        use_colors: Whether to use colored output
    
    Returns:
        Configured logger instance
    """
    # Get log level from environment or use provided level or default to DEBUG
    if level is None:
        level = os.getenv('LOG_LEVEL', 'DEBUG').upper()
    
    # Default format string
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Create logger
    logger = logging.getLogger(name)
    
    # Avoid adding multiple handlers to the same logger
    if logger.handlers:
        return logger
    
    # Set log level
    logger.setLevel(getattr(logging, level, logging.DEBUG))
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level, logging.DEBUG))
    
    # Create formatter
    formatter = ColoredFormatter(
        fmt=format_string,
        datefmt='%Y-%m-%d %H:%M:%S',
        use_colors=use_colors
    )
    
    # Add formatter to handler
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    # Prevent propagation to avoid duplicate logs
    logger.propagate = False
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the standard configuration.
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        Configured logger instance
    """
    return setup_logger(name)


# Configure root logger for the application
def configure_root_logger():
    """Configure the root logger for the entire application."""
    root_logger = logging.getLogger()
    
    # Clear any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Set up the root logger with our configuration
    setup_logger('root')


# Auto-configure when module is imported
if not logging.getLogger().handlers:
    configure_root_logger()
