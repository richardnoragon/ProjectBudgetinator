"""
Resource cleanup utilities for ProjectBudgetinator.

This module provides comprehensive resource management including:
- Excel workbook lifecycle management
- Memory leak prevention
- Automatic cleanup on application exit
- Memory usage monitoring
"""

import os
import gc
import atexit
import weakref
import threading
from typing import Dict, List, Any, Optional, Iterator
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)


class ResourceCleanupManager:
    """
    Centralized resource cleanup manager for Excel operations.
    
    Ensures proper cleanup of Excel resources, prevents memory leaks,
    and provides monitoring capabilities.
    """
    
    def __init__(self):
        self._open_resources = {}
        self._cleanup_callbacks = []
        self._lock = threading.Lock()
        self._setup_cleanup_handlers()
    
    def _setup_cleanup_handlers(self):
        """Setup automatic cleanup handlers."""
        # Register cleanup on application exit
        atexit.register(self._cleanup_all_resources)
        
        # Register cleanup callbacks
        self._register_cleanup_callbacks()
    
    def register_resource(self, resource_id: str, resource, cleanup_func):
        """Register a resource for automatic cleanup."""
        with self._lock:
            self._open_resources[resource_id] = {
                'resource': resource,
                'cleanup_func': cleanup_func,
                'created_at': threading.current_thread().ident
            }
    
    def unregister_resource(self, resource_id: str):
        """Unregister a resource from cleanup tracking."""
        with self._lock:
            if resource_id in self._open_resources:
                del self._open_resources[resource_id]
    
    def cleanup_resource(self, resource_id: str) -> bool:
        """Cleanup a specific resource."""
        with self._lock:
            if resource_id in self._open_resources:
                try:
                    resource_info = self._open_resources[resource_id]
                    resource_info['cleanup_func'](resource_info['resource'])
                    del self._open_resources[resource_id]
                    logger.debug(f"Cleaned up resource: {resource_id}")
                    return True
                except Exception as e:
                    logger.error(f"Error cleaning up resource {resource_id}: {e}")
                    return False
        return False
    
    def _cleanup_all_resources(self):
        """Cleanup all registered resources."""
        logger.info("Starting comprehensive resource cleanup...")
        
        with self._lock:
            resources_to_cleanup = list(self._open_resources.items())
            
            for resource_id, resource_info in resources_to_cleanup:
                try:
                    resource_info['cleanup_func'](resource_info['resource'])
                    logger.debug(f"Auto-cleanup: {resource_id}")
                except Exception as e:
                    logger.error(f"Auto-cleanup error for {resource_id}: {e}")
            
            self._open_resources.clear()
        
        # Run garbage collection
        gc.collect()
        logger.info("Resource cleanup completed")
    
    def get_resource_stats(self) -> Dict[str, Any]:
        """Get resource management statistics."""
        with self._lock:
            return {
                'active_resources': len(self._open_resources),
                'resource_ids': list(self._open_resources.keys()),
                'cleanup_callbacks': len(self._cleanup_callbacks)
            }
    
    def _register_cleanup_callbacks(self):
        """Register various cleanup callbacks."""
        # Excel workbook cleanup
        self.add_cleanup_callback(self._cleanup_excel_resources)
        
        # Temporary file cleanup
        self.add_cleanup_callback(self._cleanup_temp_files)
        
        # Memory cleanup
        self.add_cleanup_callback(self._cleanup_memory)
    
    def _cleanup_excel_resources(self):
        """Cleanup Excel-specific resources."""
        try:
            import openpyxl
            # Force close any remaining workbooks
            gc.collect()
        except ImportError:
            pass
    
    def _cleanup_temp_files(self):
        """Cleanup temporary files."""
        try:
            temp_dir = os.path.join(os.path.expanduser("~"), "ProjectBudgetinator", "temp")
            if os.path.exists(temp_dir):
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception as e:
            logger.warning(f"Error cleaning temp files: {e}")
    
    def _cleanup_memory(self):
        """Force memory cleanup."""
        try:
            gc.collect()
            logger.debug("Forced garbage collection")
        except Exception as e:
            logger.warning(f"Error during memory cleanup: {e}")
    
    def add_cleanup_callback(self, callback):
        """Add a custom cleanup callback."""
        self._cleanup_callbacks.append(callback)


# Global resource cleanup manager
cleanup_manager = ResourceCleanupManager()


class ExcelResourceTracker:
    """
    Track and manage Excel resources with automatic cleanup.
    """
    
    def __init__(self):
        self._workbooks = {}
        self._temp_files = set()
    
    def track_workbook(self, file_path: str, workbook):
        """Track an Excel workbook for cleanup."""
        def cleanup_func(wb):
            try:
                wb.close()
                logger.debug(f"Closed workbook: {file_path}")
            except Exception as e:
                logger.error(f"Error closing workbook {file_path}: {e}")
        
        cleanup_manager.register_resource(f"workbook_{file_path}", workbook, cleanup_func)
        self._workbooks[file_path] = workbook
    
    def untrack_workbook(self, file_path: str):
        """Untrack an Excel workbook."""
        cleanup_manager.unregister_resource(f"workbook_{file_path}")
        if file_path in self._workbooks:
            del self._workbooks[file_path]
    
    def track_temp_file(self, file_path: str):
        """Track a temporary file for cleanup."""
        self._temp_files.add(file_path)
    
    def cleanup_temp_files(self):
        """Cleanup tracked temporary files."""
        for file_path in list(self._temp_files):
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.debug(f"Removed temp file: {file_path}")
                self._temp_files.discard(file_path)
            except Exception as e:
                logger.error(f"Error removing temp file {file_path}: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get resource tracking statistics."""
        return {
            'tracked_workbooks': len(self._workbooks),
            'tracked_temp_files': len(self._temp_files),
            'active_files': list(self._workbooks.keys())
        }


# Global Excel resource tracker
excel_tracker = ExcelResourceTracker()


@contextmanager
def safe_excel_context(file_path: str, **kwargs) -> Iterator:
    """
    Enhanced context manager for safe Excel file handling with resource tracking.
    
    Args:
        file_path: Path to the Excel file
        **kwargs: Additional arguments for load_workbook
    
    Yields:
        Workbook: The Excel workbook instance
    """
    from openpyxl import load_workbook
    
    workbook = None
    try:
        # Apply optimized settings
        kwargs.setdefault('data_only', True)
        kwargs.setdefault('keep_links', False)
        
        # Use read-only for large files
        file_size = os.path.getsize(file_path)
        if file_size > 10 * 1024 * 1024:
            kwargs.setdefault('read_only', True)
        
        workbook = load_workbook(file_path, **kwargs)
        excel_tracker.track_workbook(file_path, workbook)
        
        logger.debug(f"Opened workbook with tracking: {file_path}")
        yield workbook
        
    except Exception as e:
        logger.error(f"Error in safe_excel_context: {str(e)}")
        raise
    finally:
        if workbook:
            try:
                workbook.close()
                excel_tracker.untrack_workbook(file_path)
                gc.collect()
                logger.debug(f"Closed workbook with tracking: {file_path}")
            except Exception as e:
                logger.warning(f"Error closing workbook: {str(e)}")


@contextmanager
def memory_monitored_context(file_path: str, **kwargs) -> Iterator:
    """
    Context manager with memory monitoring for Excel operations.
    
    Args:
        file_path: Path to the Excel file
        **kwargs: Additional arguments for load_workbook
    
    Yields:
        Workbook: The Excel workbook instance
    """
    from openpyxl import load_workbook
    
    # Get initial memory usage
    import psutil
    process = psutil.Process()
    initial_memory = process.memory_info().rss / (1024 * 1024)
    
    workbook = None
    try:
        workbook = load_workbook(file_path, **kwargs)
        
        current_memory = process.memory_info().rss / (1024 * 1024)
        logger.info(f"Memory after loading {file_path}: {current_memory:.2f}MB "
                   f"(Δ{current_memory - initial_memory:+.2f}MB)")
        
        yield workbook
        
    finally:
        if workbook:
            try:
                workbook.close()
                gc.collect()
                
                final_memory = process.memory_info().rss / (1024 * 1024)
                logger.info(f"Memory after closing {file_path}: {final_memory:.2f}MB "
                           f"(Δ{final_memory - initial_memory:+.2f}MB)")
            except Exception as e:
                logger.warning(f"Error during memory cleanup: {str(e)}")


class MemoryMonitor:
    """
    Monitor and report memory usage for Excel operations.
    """
    
    def __init__(self):
        self.operation_stats = {}
    
    def monitor_operation(self, operation_name: str):
        """Decorator to monitor memory usage of operations."""
        def decorator(func):
            def wrapper(*args, **kwargs):
                import psutil
                process = psutil.Process()
                
                start_memory = process.memory_info().rss / (1024 * 1024)
                start_time = time.time()
                
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    end_memory = process.memory_info().rss / (1024 * 1024)
                    duration = time.time() - start_time
                    
                    self.operation_stats[operation_name] = {
                        'memory_delta_mb': end_memory - start_memory,
                        'duration_seconds': duration,
                        'peak_memory_mb': max(start_memory, end_memory)
                    }
                    
                    logger.info(f"Operation {operation_name}: "
                               f"{duration:.2f}s, "
                               f"Δ{end_memory - start_memory:+.2f}MB")
            
            return wrapper
        return decorator
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory monitoring statistics."""
        return {
            'operations': self.operation_stats,
            'total_operations': len(self.operation_stats)
        }


# Global memory monitor
memory_monitor = MemoryMonitor()


def cleanup_on_exception(func):
    """Decorator to ensure cleanup on exceptions."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Exception in {func.__name__}: {str(e)}")
            # Force cleanup on exception
            gc.collect()
            raise
    return wrapper


def get_system_memory_info() -> Dict[str, Any]:
    """Get comprehensive system memory information."""
    try:
        import psutil
        
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            'total_memory_gb': memory.total / (1024**3),
            'available_memory_gb': memory.available / (1024**3),
            'used_memory_gb': memory.used / (1024**3),
            'memory_percent': memory.percent,
            'swap_total_gb': swap.total / (1024**3),
            'swap_used_gb': swap.used / (1024**3),
            'swap_percent': swap.percent
        }
    except ImportError:
        return {'error': 'psutil not available'}


def force_system_cleanup():
    """Force comprehensive system cleanup."""
    logger.info("Starting system-wide resource cleanup...")
    
    # Cleanup all managed resources
    cleanup_manager._cleanup_all_resources()
    
    # Cleanup temporary files
    excel_tracker.cleanup_temp_files()
    
    # Force garbage collection
    gc.collect()
    
    # Log final state
    memory_info = get_system_memory_info()
    logger.info(f"System cleanup completed: {memory_info}")


# Register cleanup on module import
atexit.register(force_system_cleanup)
