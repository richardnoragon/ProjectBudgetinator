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
    """Custom formatter for structured logging with context."""
    
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
    """Enhanced logger with structured logging capabilities."""
    
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
    """Context manager for structured logging context."""
    
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
    """Setup logging with structured logging support."""
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
    """Get a structured logger instance for the given name."""
    return StructuredLogger(name)

# Usage: import and call setup_logging() at app startup
# Then use logging.debug/info/warning/error/critical as needed
