"""ProjectBudgetinator Structured Logging Module.

This module provides a comprehensive structured logging system for ProjectBudgetinator
with context-aware logging capabilities, JSON formatting, and multi-level file output.

The logging system supports:
    - Structured logging with context variables (operation_id, session_id, user_context)
    - JSON-formatted file logs for machine parsing
    - Human-readable console logs
    - Thread-safe logging with thread identification
    - Automatic log file rotation and cleanup
    - Context managers for operation tracking
    - Performance monitoring integration

Classes:
    StructuredFormatter: Custom formatter for structured logging with context
    StructuredLogger: Enhanced logger with structured logging capabilities
    LogContext: Context manager for structured logging context

Functions:
    setup_logging: Initialize the logging system with structured support
    get_structured_logger: Factory function for structured logger instances
    set_session_id: Set session ID for current context
    set_operation_context: Set operation context and return operation ID
    set_user_context: Set user context for current thread

Constants:
    LOG_DIR_NAME: Directory name for log files
    LOG_BASE_DIR: Base directory path for all log files
    LOG_LEVELS: Supported logging levels
    MAX_LOG_FILES: Maximum number of log files to retain

Example:
    Basic usage with context:
    
        setup_logging()
        logger = get_structured_logger("my_module")
        
        with LogContext("user_login", user_id="user123"):
            logger.info("User login attempt", ip_address="192.168.1.1")

Note:
    The logging system automatically creates log files for each level and manages
    file rotation. Context variables are thread-local and operation-specific.
"""

import logging
import os
import uuid
import threading
import json
from datetime import datetime
from pathlib import Path
from contextvars import ContextVar
from typing import Any, Dict, Optional

LOG_DIR_NAME = "Log Files"
LOG_BASE_DIR = os.path.join(str(Path.home()), "ProjectBudgetinator", LOG_DIR_NAME)
LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
MAX_LOG_FILES = 10

# Context variables for structured logging
operation_id: ContextVar[Optional[str]] = ContextVar('operation_id', default=None)
user_context: ContextVar[Optional[str]] = ContextVar('user_context', default=None)
session_id: ContextVar[Optional[str]] = ContextVar('session_id', default=None)

# Ensure log directory exists
os.makedirs(LOG_BASE_DIR, exist_ok=True)

def get_log_filename(level):
    today = datetime.now().strftime("%d-%m-%Y")
    return os.path.join(LOG_BASE_DIR, f"{today}-{level}.log")


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging with context information.
    
    This formatter enhances standard Python logging by adding structured context
    information including operation IDs, session IDs, user context, and thread
    information. It supports both JSON and human-readable output formats.
    
    Args:
        use_json (bool): If True, format logs as JSON; if False, use human-readable format.
        *args: Additional arguments passed to logging.Formatter.
        **kwargs: Additional keyword arguments passed to logging.Formatter.
    
    Attributes:
        use_json (bool): Flag indicating the output format type.
    
    Example:
        Creating formatters for different outputs:
        
            # JSON formatter for file logs
            json_formatter = StructuredFormatter(use_json=True)
            
            # Human-readable formatter for console
            console_formatter = StructuredFormatter(use_json=False)
    
    Note:
        The formatter automatically includes context variables from the current
        thread context, including operation_id, session_id, and user_context.
    """
    
    def __init__(self, use_json: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.use_json = use_json
    
    def format(self, record):
        # Create base log record
        log_entry = {
            'timestamp': self.formatTime(record, self.datefmt),
            'level': record.levelname,
            'module': record.module,
            'function': getattr(record, 'funcName', 'unknown'),
            'line': getattr(record, 'lineno', 0),
            'message': record.getMessage(),
        }
        
        # Add context information
        log_entry['operation_id'] = operation_id.get()
        log_entry['session_id'] = session_id.get()
        log_entry['user_context'] = user_context.get()
        log_entry['thread_id'] = threading.current_thread().ident
        log_entry['thread_name'] = threading.current_thread().name
        
        # Add any extra context from the log record
        if hasattr(record, 'extra_context'):
            log_entry.update(record.extra_context)
        
        # Format as JSON for structured logs, or traditional format for console
        if self.use_json:
            return json.dumps(log_entry, default=str, ensure_ascii=False)
        else:
            # Traditional format with context
            context_parts = []
            if log_entry['operation_id']:
                context_parts.append(f"op:{log_entry['operation_id']}")
            if log_entry['session_id']:
                context_parts.append(f"session:{log_entry['session_id']}")
            if log_entry['user_context']:
                context_parts.append(f"user:{log_entry['user_context']}")
            
            context_str = (f"[{', '.join(context_parts)}]" 
                          if context_parts else "")
            
            return (f"{log_entry['timestamp']} | {log_entry['level']} | "
                   f"{log_entry['module']} | {context_str} | "
                   f"{log_entry['message']}")


class StructuredLogger:
    """Enhanced logger with structured logging capabilities and context management.
    
    This class provides an enhanced logging interface that automatically includes
    structured context information such as operation IDs, session IDs, user context,
    and thread information in all log messages. It wraps the standard Python logger
    with additional functionality for better observability and debugging.
    
    Args:
        name (str): The name of the logger, typically the module or component name.
    
    Attributes:
        logger (logging.Logger): The underlying Python logger instance.
        name (str): The name of this logger instance.
    
    Methods:
        debug: Log debug messages with context
        info: Log info messages with context
        warning: Log warning messages with context
        error: Log error messages with context
        critical: Log critical messages with context
        exception: Log exceptions with context and traceback
    
    Example:
        Using structured logging with context:
        
            logger = StructuredLogger("my_module")
            logger.info("User action", user_id="123", action="login")
            
            # With context manager
            with LogContext("user_login", user_id="123"):
                logger.info("Login attempt started")
    
    Note:
        All log methods accept additional keyword arguments that will be included
        in the structured log output for enhanced debugging and monitoring.
    """
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.name = name
    
    def _log_with_context(self, level: str, msg: str, **kwargs):
        """Log message with context information."""
        extra_context = {
            'operation_id': operation_id.get(),
            'session_id': session_id.get(),
            'user_context': user_context.get(),
            'thread_id': threading.current_thread().ident,
            'thread_name': threading.current_thread().name,
            **kwargs
        }
        
        # Create extra record with context
        extra = {'extra_context': extra_context}
        
        # Log the message
        log_method = getattr(self.logger, level.lower())
        log_method(msg, extra=extra)
    
    def debug(self, msg: str, **kwargs):
        """Log debug message with context."""
        self._log_with_context('DEBUG', msg, **kwargs)
    
    def info(self, msg: str, **kwargs):
        """Log info message with context."""
        self._log_with_context('INFO', msg, **kwargs)
    
    def warning(self, msg: str, **kwargs):
        """Log warning message with context."""
        self._log_with_context('WARNING', msg, **kwargs)
    
    def error(self, msg: str, **kwargs):
        """Log error message with context."""
        self._log_with_context('ERROR', msg, **kwargs)
    
    def critical(self, msg: str, **kwargs):
        """Log critical message with context."""
        self._log_with_context('CRITICAL', msg, **kwargs)
    
    def exception(self, msg: str, **kwargs):
        """Log exception with context and traceback."""
        extra_context = {
            'operation_id': operation_id.get(),
            'session_id': session_id.get(),
            'user_context': user_context.get(),
            'thread_id': threading.current_thread().ident,
            'thread_name': threading.current_thread().name,
            **kwargs
        }
        
        extra = {'extra_context': extra_context}
        self.logger.exception(msg, extra=extra)


class LogContext:
    """Context manager for structured logging context management.
    
    This context manager allows setting operation-specific and user-specific
    context that will be automatically included in all log messages within
    the context block. It uses Python's contextvars for thread-safe context
    management and automatically cleans up context when exiting.
    
    Args:
        operation_name (Optional[str]): Name of the operation for context tracking.
            If provided, generates a unique operation ID.
        user_id (Optional[str]): User identifier for the current operation.
        **additional_context: Additional context key-value pairs (currently unused
            but available for future extension).
    
    Attributes:
        operation_name (Optional[str]): The operation name for this context.
        user_id (Optional[str]): The user ID for this context.
        additional_context (dict): Additional context information.
        operation_token: Context variable token for operation ID.
        user_token: Context variable token for user context.
    
    Example:
        Using context manager for operation tracking:
        
            with LogContext("user_login", user_id="user123"):
                logger.info("Login attempt started")
                # All logs within this block will include operation and user context
                logger.info("Authentication successful")
        
        Nested contexts:
        
            with LogContext("batch_operation"):
                with LogContext("individual_task", user_id="user456"):
                    logger.info("Processing individual task")
    
    Note:
        Context variables are thread-local and will not interfere with other
        threads. The context is automatically cleaned up when exiting the block.
    """
    
    def __init__(self, operation_name: Optional[str] = None,
                 user_id: Optional[str] = None, **additional_context):
        self.operation_name = operation_name
        self.user_id = user_id
        self.additional_context = additional_context
        self.operation_token = None
        self.user_token = None
    
    def __enter__(self):
        # Set operation ID
        if self.operation_name:
            op_id = f"{self.operation_name}_{uuid.uuid4().hex[:8]}"
            self.operation_token = operation_id.set(op_id)
        
        # Set user context
        if self.user_id:
            self.user_token = user_context.set(self.user_id)
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Reset context variables
        if self.operation_token:
            operation_id.reset(self.operation_token)
        if self.user_token:
            user_context.reset(self.user_token)


def set_session_id(session_id_value: str):
    """Set the session ID for the current context."""
    session_id.set(session_id_value)


def get_session_id() -> Optional[str]:
    """Get the current session ID."""
    return session_id.get()


def set_operation_context(operation_name: str) -> str:
    """Set operation context and return operation ID."""
    op_id = f"{operation_name}_{uuid.uuid4().hex[:8]}"
    operation_id.set(op_id)
    return op_id


def clear_operation_context():
    """Clear the current operation context."""
    operation_id.set(None)


def set_user_context(user_id: str):
    """Set user context for current thread."""
    user_context.set(user_id)

def setup_logging():
    """Initialize the comprehensive structured logging system for ProjectBudgetinator.
    
    This function sets up a multi-level logging system with structured context support,
    JSON formatting for machine parsing, and automatic log file management. It creates
    separate log files for each logging level and includes console output.
    
    The logging system provides:
        - Structured logging with context variables (operation_id, session_id, user_context)
        - JSON-formatted file logs for each level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        - Human-readable console output for development
        - Automatic log file rotation and cleanup
        - Thread-safe logging with thread identification
        - Session tracking with unique session IDs
    
    Returns:
        logging.Logger: The configured root logger instance.
    
    Raises:
        Exception: May raise exceptions during file system operations, but continues
            with degraded functionality if log directory creation fails.
    
    Examples:
        Initialize logging at application startup:
        
            # Set up logging system
            logger = setup_logging()
            
            # Get structured logger for module
            module_logger = get_structured_logger("my_module")
            
            # Use with context
            with LogContext("user_operation", user_id="123"):
                module_logger.info("Operation started")
    
    File Structure:
        Creates log files in LOG_BASE_DIR with format: DD-MM-YYYY-LEVEL.log
        - 25-01-2025-DEBUG.log
        - 25-01-2025-INFO.log
        - 25-01-2025-WARNING.log
        - 25-01-2025-ERROR.log
        - 25-01-2025-CRITICAL.log
    
    Note:
        This function should be called once at application startup. It automatically
        manages log file cleanup, keeping only the most recent MAX_LOG_FILES files.
        The session ID is automatically generated and set for the current context.
    """
    # Remove old log files if more than MAX_LOG_FILES exist
    log_files = sorted([f for f in os.listdir(LOG_BASE_DIR) 
                       if f.endswith('.log')])
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
    
    # Add a structured file handler for each log level
    for level in LOG_LEVELS:
        handler = logging.FileHandler(get_log_filename(level))
        handler.setLevel(getattr(logging, level))
        
        # Use structured formatter for file logs
        formatter = StructuredFormatter(use_json=True, 
                                       datefmt='%Y-%m-%d %H:%M:%S')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    # Add console handler with traditional format
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console_formatter = StructuredFormatter(use_json=False)
    console.setFormatter(console_formatter)
    logger.addHandler(console)
    
    # Initialize session ID
    session_id_value = f"session_{uuid.uuid4().hex[:8]}"
    set_session_id(session_id_value)
    
    # Log startup
    startup_logger = StructuredLogger("system.startup")
    startup_logger.info("Logging system initialized", 
                       session_id=session_id_value,
                       log_directory=LOG_BASE_DIR)
    
    return logger


def get_structured_logger(name: str) -> StructuredLogger:
    """Get a structured logger instance with enhanced context capabilities.
    
    This factory function creates and returns a StructuredLogger instance that
    automatically includes context information in all log messages. The logger
    integrates with the global logging system and context variables.
    
    Args:
        name (str): The name for the logger, typically the module or component name.
            This name appears in log messages and helps identify the source.
    
    Returns:
        StructuredLogger: A configured structured logger instance with context support.
    
    Examples:
        Creating and using structured loggers:
        
            # Create logger for a module
            logger = get_structured_logger("user_management")
            
            # Log with additional context
            logger.info("User login attempt",
                       user_id="123",
                       ip_address="192.168.1.1")
            
            # Use with context manager
            with LogContext("password_change", user_id="123"):
                logger.info("Password change initiated")
                logger.info("Password validation completed")
    
    Note:
        The returned logger automatically includes operation_id, session_id,
        user_context, and thread information in all log messages when available.
        Call setup_logging() before using this function to ensure proper configuration.
    """
    return StructuredLogger(name)

# Usage: import and call setup_logging() at app startup
# Then use logging.debug/info/warning/error/critical as needed
