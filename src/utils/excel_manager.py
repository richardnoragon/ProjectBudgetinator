"""
Excel file management utilities with performance optimizations and memory management.

This module provides optimized Excel file handling with lazy loading,
memory management, and comprehensive resource cleanup.
"""

import os
import gc
import psutil
import logging
from typing import Optional, List, Dict, Any, Iterator
from contextlib import contextmanager
from pathlib import Path
from openpyxl import load_workbook
from openpyxl.workbook.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet

# Import performance monitoring
from utils.performance_monitor import monitor_file_operation
from utils.security_validator import SecurityValidator

logger = logging.getLogger(__name__)


class ExcelMemoryTracker:
    """Track and manage Excel-related memory usage."""
    
    def __init__(self):
        self.open_workbooks = set()
        self.total_memory_used = 0
    
    def track_workbook(self, file_path: str, workbook: Workbook):
        """Track an opened workbook."""
        self.open_workbooks.add(file_path)
        memory = self._get_memory_usage()
        logger.debug(f"Opened workbook: {file_path}, Memory: {memory:.2f}MB")
    
    def untrack_workbook(self, file_path: str):
        """Untrack a closed workbook."""
        if file_path in self.open_workbooks:
            self.open_workbooks.remove(file_path)
            memory = self._get_memory_usage()
            logger.debug(f"Closed workbook: {file_path}, Memory: {memory:.2f}MB")
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            process = psutil.Process()
            return process.memory_info().rss / (1024 * 1024)
        except:
            return 0.0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory tracking statistics."""
        return {
            'open_workbooks': len(self.open_workbooks),
            'open_files': list(self.open_workbooks),
            'memory_usage_mb': self._get_memory_usage()
        }


# Global memory tracker
memory_tracker = ExcelMemoryTracker()


class ExcelManager:
    """
    Optimized Excel file manager with lazy loading and comprehensive memory management.
    
    Features:
    - Lazy loading of workbooks to reduce memory usage
    - Read-only mode for large files
    - Automatic resource cleanup with context managers
    - Memory usage tracking and monitoring
    - Force garbage collection on close
    """
    
    def __init__(self, file_path: str):
        """
        Initialize ExcelManager with file path.
        
        Args:
            file_path: Path to the Excel file
        """
        # Validate file path
        try:
            self.file_path = SecurityValidator.validate_file_path(file_path)
        except ValueError as e:
            raise ValueError(f"Invalid file path: {str(e)}")
        
        self._workbook: Optional[Workbook] = None
        self._active_sheet: Optional[Worksheet] = None
        self._is_open = False
        self._memory_usage = 0
        
        # Validate Excel file
        is_valid, error_msg = SecurityValidator.validate_excel_file(self.file_path)
        if not is_valid:
            raise ValueError(f"Invalid Excel file: {error_msg}")
    
    @property
    def workbook(self) -> Workbook:
        """
        Lazy-loaded workbook property with memory tracking.
        
        Returns:
            Workbook: The Excel workbook instance
        """
        if self._workbook is None:
            self._load_workbook()
        return self._workbook
    
    @property
    def active_sheet(self) -> Optional[Worksheet]:
        """
        Get the active worksheet.
        
        Returns:
            Worksheet: The active worksheet or None if not available
        """
        if self._active_sheet is None and self.workbook:
            self._active_sheet = self.workbook.active
        return self._active_sheet
    
    def _load_workbook(self) -> None:
        """
        Load workbook with optimized settings and memory tracking.
        
        Uses read-only mode for large files and data_only to load
        values instead of formulas for better performance.
        """
        try:
            logger.info(f"Loading Excel file: {self.file_path}")
            
            # Get file size to determine loading strategy
            file_size = os.path.getsize(self.file_path)
            
            # Use read-only mode for files larger than 10MB
            use_read_only = file_size > 10 * 1024 * 1024
            
            self._workbook = load_workbook(
                self.file_path,
                read_only=use_read_only,
                data_only=True,  # Load values instead of formulas
                keep_links=False  # Don't load external links
            )
            
            self._is_open = True
            memory_tracker.track_workbook(self.file_path, self._workbook)
            
            logger.info(f"Successfully loaded workbook: {self.file_path}")
            
        except Exception as e:
            logger.error(f"Failed to load Excel file {self.file_path}: {str(e)}")
            raise
    
    def close(self) -> None:
        """
        Close the workbook and release resources with memory cleanup.
        
        This method ensures proper cleanup of Excel resources to prevent
        memory leaks, including garbage collection and memory tracking.
        """
        if self._workbook is not None:
            try:
                # Close the workbook
                self._workbook.close()
                memory_tracker.untrack_workbook(self.file_path)
                
                # Force garbage collection
                gc.collect()
                
                logger.info(f"Closed workbook: {self.file_path}")
                
            except Exception as e:
                logger.warning(f"Error closing workbook: {str(e)}")
            finally:
                self._workbook = None
                self._active_sheet = None
                self._is_open = False
                
                # Additional cleanup
                gc.collect()
    
    def force_close(self) -> None:
        """
        Force close workbook and perform aggressive memory cleanup.
        
        Use this method when you need to ensure complete cleanup,
        such as before processing large files or when memory is constrained.
        """
        self.close()
        
        # Additional memory cleanup
        gc.collect()
        
        # Log memory usage
        memory = memory_tracker._get_memory_usage()
        logger.info(f"Memory after force close: {memory:.2f}MB")
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """
        Get current memory usage information.
        
        Returns:
            Dict[str, Any]: Memory usage statistics
        """
        return {
            'file_path': self.file_path,
            'is_open': self._is_open,
            'memory_tracker': memory_tracker.get_stats()
        }


@contextmanager
def excel_context(file_path: str, **kwargs) -> Iterator[Workbook]:
    """
    Context manager for safe Excel file handling with automatic cleanup.
    
    Args:
        file_path: Path to the Excel file
        **kwargs: Additional arguments for load_workbook
    
    Yields:
        Workbook: The Excel workbook instance
    
    Example:
        >>> with excel_context('file.xlsx') as wb:
        ...     sheet = wb.active
        ...     # Process workbook
        ...     # Auto-cleanup on exit
    """
    workbook = None
    try:
        # Apply optimized settings
        kwargs.setdefault('data_only', True)
        kwargs.setdefault('keep_links', False)
        
        # Use read-only for large files
        file_size = os.path.getsize(file_path)
        if file_size > 10 * 1024 * 1024:
            kwargs.setdefault('read_only', True)
        
        # Monitor file operation
        with monitor_file_operation('open', file_path):
            workbook = load_workbook(file_path, **kwargs)
            memory_tracker.track_workbook(file_path, workbook)
        
        logger.debug(f"Opened workbook in context: {file_path}")
        yield workbook
        
    except Exception as e:
        logger.error(f"Error in excel_context: {str(e)}")
        raise
    finally:
        if workbook:
            try:
                with monitor_file_operation('close', file_path):
                    workbook.close()
                    memory_tracker.untrack_workbook(file_path)
                    gc.collect()
                logger.debug(f"Closed workbook in context: {file_path}")
            except Exception as e:
                logger.warning(f"Error closing workbook in context: {str(e)}")


@contextmanager
def excel_safe_context(file_path: str, **kwargs) -> Iterator[ExcelManager]:
    """
    Context manager for safe ExcelManager usage with full cleanup.
    
    Args:
        file_path: Path to the Excel file
        **kwargs: Additional arguments for ExcelManager
    
    Yields:
        ExcelManager: The Excel manager instance
    
    Example:
        >>> with excel_safe_context('file.xlsx') as excel:
        ...     sheet = excel.active_sheet
        ...     # Process using ExcelManager
        ...     # Full cleanup on exit
    """
    excel_manager = None
    try:
        excel_manager = ExcelManager(file_path)
        yield excel_manager
    except Exception as e:
        logger.error(f"Error in excel_safe_context: {str(e)}")
        raise
    finally:
        if excel_manager:
            excel_manager.force_close()


class ResourceManager:
    """
    Centralized resource management for Excel operations.
    
    Tracks and manages all Excel resources to prevent memory leaks.
    """
    
    def __init__(self):
        self.active_managers: Dict[str, ExcelManager] = {}
        self.cleanup_callbacks = []
    
    def get_manager(self, file_path: str) -> ExcelManager:
        """Get or create ExcelManager for file."""
        if file_path not in self.active_managers:
            self.active_managers[file_path] = ExcelManager(file_path)
        return self.active_managers[file_path]
    
    def release_manager(self, file_path: str) -> None:
        """Release and cleanup ExcelManager for file."""
        if file_path in self.active_managers:
            self.active_managers[file_path].force_close()
            del self.active_managers[file_path]
    
    def cleanup_all(self) -> None:
        """Force cleanup of all managed resources."""
        for file_path in list(self.active_managers.keys()):
            self.release_manager(file_path)
        
        # Force garbage collection
        gc.collect()
        
        # Log final memory state
        memory = memory_tracker._get_memory_usage()
        logger.info(f"Final memory after cleanup: {memory:.2f}MB")
    
    def register_cleanup_callback(self, callback):
        """Register callback for cleanup events."""
        self.cleanup_callbacks.append(callback)
    
    def get_resource_stats(self) -> Dict[str, Any]:
        """Get resource management statistics."""
        return {
            'active_managers': len(self.active_managers),
            'active_files': list(self.active_managers.keys()),
            'memory_tracker': memory_tracker.get_stats()
        }


# Global resource manager
resource_manager = ResourceManager()


# Enhanced context managers for specific use cases

@contextmanager
def read_only_excel_context(file_path: str) -> Iterator[Workbook]:
    """Context manager for read-only Excel access."""
    with excel_context(file_path, read_only=True, data_only=True) as wb:
        yield wb


@contextmanager
def write_excel_context(file_path: str) -> Iterator[Workbook]:
    """Context manager for write operations with full features."""
    with excel_context(file_path, read_only=False, data_only=False) as wb:
        yield wb


@contextmanager
def memory_safe_bulk_operation(file_paths: List[str]) -> Iterator[Dict[str, Workbook]]:
    """
    Context manager for bulk Excel operations with memory management.
    
    Args:
        file_paths: List of Excel file paths to process
    
    Yields:
        Dict[str, Workbook]: Dictionary mapping file paths to workbooks
    
    Example:
        >>> files = ['file1.xlsx', 'file2.xlsx']
        >>> with memory_safe_bulk_operation(files) as workbooks:
        ...     for path, wb in workbooks.items():
        ...         # Process each workbook
        ...         # Auto-cleanup all workbooks on exit
    """
    workbooks = {}
    try:
        for file_path in file_paths:
            if os.path.exists(file_path):
                wb = load_workbook(file_path, read_only=True, data_only=True)
                workbooks[file_path] = wb
                memory_tracker.track_workbook(file_path, wb)
        
        logger.info(f"Opened {len(workbooks)} workbooks for bulk operation")
        yield workbooks
        
    except Exception as e:
        logger.error(f"Error in bulk operation: {str(e)}")
        raise
    finally:
        # Close all workbooks
        for file_path, wb in workbooks.items():
            try:
                wb.close()
                memory_tracker.untrack_workbook(file_path)
            except Exception as e:
                logger.warning(f"Error closing {file_path}: {str(e)}")
        
        # Force garbage collection
        gc.collect()
        logger.info("Completed bulk operation cleanup")


# Utility functions for memory management

def get_memory_usage() -> Dict[str, float]:
    """Get comprehensive memory usage information."""
    try:
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            'rss_mb': memory_info.rss / (1024 * 1024),
            'vms_mb': memory_info.vms / (1024 * 1024),
            'percent': process.memory_percent(),
            'open_workbooks': len(memory_tracker.open_workbooks)
        }
    except Exception as e:
        logger.error(f"Error getting memory usage: {str(e)}")
        return {'rss_mb': 0, 'vms_mb': 0, 'percent': 0, 'open_workbooks': 0}


def force_memory_cleanup() -> None:
    """Force comprehensive memory cleanup."""
    logger.info("Starting comprehensive memory cleanup...")
    
    # Close all managed resources
    resource_manager.cleanup_all()
    
    # Force garbage collection multiple times
    for i in range(3):
        collected = gc.collect()
        logger.debug(f"GC cycle {i+1}: collected {collected} objects")
    
    # Log final state
    memory = get_memory_usage()
    logger.info(f"Memory cleanup completed: {memory['rss_mb']:.2f}MB used")


def monitor_memory_usage(func):
    """Decorator to monitor memory usage of Excel operations."""
    def wrapper(*args, **kwargs):
        start_memory = get_memory_usage()
        logger.info(f"Memory before {func.__name__}: {start_memory['rss_mb']:.2f}MB")
        
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            end_memory = get_memory_usage()
            delta = end_memory['rss_mb'] - start_memory['rss_mb']
            logger.info(f"Memory after {func.__name__}: {end_memory['rss_mb']:.2f}MB (Δ{delta:+.2f}MB)")
    
    return wrapper
