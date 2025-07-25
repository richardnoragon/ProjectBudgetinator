"""Performance optimization utilities for ProjectBudgetinator.

This module provides performance optimization utilities including caching mechanisms,
loop optimizations, and performance monitoring integration for the ProjectBudgetinator
application.

Classes:
    WorkbookCache: Caching mechanism for workbook-related calculations
    PerformanceOptimizer: Main performance optimization coordinator

Functions:
    optimize_partner_calculations: Optimize partner-related calculations
    optimize_workpackage_loops: Optimize workpackage processing loops
    monitor_operation: Decorator for performance monitoring
    batch_process_sheets: Batch processing for multiple sheets

Constants:
    CACHE_TTL_SECONDS: Default cache time-to-live in seconds
    MAX_CACHE_SIZE: Maximum number of cached items
    PERFORMANCE_THRESHOLD_MS: Performance warning threshold in milliseconds

Example:
    Basic usage of performance optimizations:
    
        from utils.performance_optimizations import PerformanceOptimizer
        
        optimizer = PerformanceOptimizer()
        cached_sheets = optimizer.get_cached_partner_sheets(workbook)
        
        @monitor_operation("partner_processing")
        def process_partners(sheets):
            return batch_process_sheets(sheets)

Note:
    This module integrates with the existing performance monitoring system
    and provides caching mechanisms to reduce repeated calculations.
"""

import time
import functools
from typing import Dict, List, Any, Optional, Tuple, Callable
from collections import OrderedDict
import logging
from utils.performance_monitor import get_performance_monitor, monitor_performance

# Performance optimization constants
CACHE_TTL_SECONDS = 300  # 5 minutes cache TTL
MAX_CACHE_SIZE = 100     # Maximum cached items
PERFORMANCE_THRESHOLD_MS = 100  # Warning threshold in milliseconds

# Set up logger
logger = logging.getLogger(__name__)


class WorkbookCache:
    """Caching mechanism for workbook-related calculations.
    
    This class provides a time-based cache for expensive workbook operations
    such as partner sheet enumeration, workpackage calculations, and formula
    evaluations.
    
    Attributes:
        _cache (OrderedDict): Internal cache storage with LRU eviction
        _timestamps (Dict): Cache entry timestamps for TTL management
        max_size (int): Maximum number of cached items
        ttl_seconds (int): Time-to-live for cache entries in seconds
    
    Example:
        Basic cache usage:
        
            cache = WorkbookCache()
            
            # Cache partner sheets
            sheets = cache.get_or_compute(
                "partner_sheets_wb123",
                lambda: expensive_partner_calculation(workbook)
            )
    """
    
    def __init__(self, max_size: int = MAX_CACHE_SIZE, ttl_seconds: int = CACHE_TTL_SECONDS):
        """Initialize the workbook cache.
        
        Args:
            max_size: Maximum number of items to cache
            ttl_seconds: Time-to-live for cache entries in seconds
        """
        self._cache = OrderedDict()
        self._timestamps = {}
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
    
    def get_or_compute(self, key: str, compute_func: Callable[[], Any]) -> Any:
        """Get cached value or compute and cache it.
        
        Args:
            key: Cache key identifier
            compute_func: Function to compute value if not cached
            
        Returns:
            Cached or computed value
        """
        # Check if key exists and is not expired
        if key in self._cache:
            if self._is_valid(key):
                # Move to end (LRU)
                self._cache.move_to_end(key)
                logger.debug(f"Cache hit for key: {key}")
                return self._cache[key]
            else:
                # Remove expired entry
                self._remove_key(key)
        
        # Compute new value
        logger.debug(f"Cache miss for key: {key}, computing value")
        start_time = time.time()
        value = compute_func()
        compute_time = (time.time() - start_time) * 1000
        
        # Cache the computed value
        self._cache[key] = value
        self._timestamps[key] = time.time()
        
        # Enforce size limit
        while len(self._cache) > self.max_size:
            oldest_key = next(iter(self._cache))
            self._remove_key(oldest_key)
        
        logger.debug(f"Cached value for key: {key} (computed in {compute_time:.2f}ms)")
        return value
    
    def invalidate(self, key: str) -> None:
        """Invalidate a specific cache entry.
        
        Args:
            key: Cache key to invalidate
        """
        if key in self._cache:
            self._remove_key(key)
            logger.debug(f"Invalidated cache key: {key}")
    
    def invalidate_pattern(self, pattern: str) -> None:
        """Invalidate all cache entries matching a pattern.
        
        Args:
            pattern: Pattern to match against cache keys
        """
        keys_to_remove = [key for key in self._cache.keys() if pattern in key]
        for key in keys_to_remove:
            self._remove_key(key)
        logger.debug(f"Invalidated {len(keys_to_remove)} cache entries matching pattern: {pattern}")
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
        self._timestamps.clear()
        logger.debug("Cache cleared")
    
    def _is_valid(self, key: str) -> bool:
        """Check if cache entry is still valid (not expired).
        
        Args:
            key: Cache key to check
            
        Returns:
            True if entry is valid, False if expired
        """
        if key not in self._timestamps:
            return False
        
        age = time.time() - self._timestamps[key]
        return age < self.ttl_seconds
    
    def _remove_key(self, key: str) -> None:
        """Remove a key from both cache and timestamps.
        
        Args:
            key: Cache key to remove
        """
        self._cache.pop(key, None)
        self._timestamps.pop(key, None)


class PerformanceOptimizer:
    """Main performance optimization coordinator.
    
    This class coordinates various performance optimizations including caching,
    batch processing, and monitoring integration for the ProjectBudgetinator
    application.
    
    Attributes:
        cache (WorkbookCache): Workbook-specific cache instance
        performance_monitor: Performance monitoring instance
        
    Example:
        Using the performance optimizer:
        
            optimizer = PerformanceOptimizer()
            
            # Get cached partner sheets
            sheets = optimizer.get_cached_partner_sheets(workbook)
            
            # Batch process with monitoring
            results = optimizer.batch_process_partners(workbook, operation_func)
    """
    
    def __init__(self):
        """Initialize the performance optimizer."""
        self.cache = WorkbookCache()
        self.performance_monitor = get_performance_monitor()
        logger.info("Performance optimizer initialized")
    
    def get_cached_partner_sheets(self, workbook, sheet_validator_func: Callable[[str], bool]) -> List[str]:
        """Get cached list of partner sheets for a workbook.
        
        Args:
            workbook: Excel workbook object
            sheet_validator_func: Function to validate if sheet is a partner sheet
            
        Returns:
            List of partner sheet names
        """
        if workbook is None:
            return []
        
        # Generate cache key based on workbook sheets
        try:
            sheet_names = tuple(sorted(workbook.sheetnames))
            cache_key = f"partner_sheets_{hash(sheet_names)}"
        except Exception:
            # Fallback if workbook access fails
            return []
        
        def compute_partner_sheets():
            """Compute partner sheets list."""
            partner_sheets = []
            try:
                for sheet_name in workbook.sheetnames:
                    if sheet_validator_func(sheet_name):
                        partner_sheets.append(sheet_name)
            except Exception as e:
                logger.warning(f"Error computing partner sheets: {e}")
            return partner_sheets
        
        return self.cache.get_or_compute(cache_key, compute_partner_sheets)
    
    def invalidate_workbook_cache(self, workbook) -> None:
        """Invalidate all cache entries for a specific workbook.
        
        Args:
            workbook: Excel workbook object
        """
        if workbook is None:
            return
        
        try:
            sheet_names = tuple(sorted(workbook.sheetnames))
            cache_pattern = f"_{hash(sheet_names)}"
            self.cache.invalidate_pattern(cache_pattern)
        except Exception as e:
            logger.warning(f"Error invalidating workbook cache: {e}")
    
    @monitor_performance(include_memory=True, log_level='DEBUG')
    def batch_process_partners(self, workbook, operation_func: Callable[[str], Any]) -> List[Tuple[str, Any]]:
        """Batch process partner sheets with performance monitoring.
        
        Args:
            workbook: Excel workbook object
            operation_func: Function to apply to each partner sheet
            
        Returns:
            List of tuples containing (sheet_name, operation_result)
        """
        from utils.workbook_utils import is_partner_worksheet
        
        partner_sheets = self.get_cached_partner_sheets(workbook, is_partner_worksheet)
        results = []
        
        logger.info(f"Batch processing {len(partner_sheets)} partner sheets")
        
        for sheet_name in partner_sheets:
            try:
                start_time = time.time()
                result = operation_func(sheet_name)
                process_time = (time.time() - start_time) * 1000
                
                results.append((sheet_name, result))
                
                if process_time > PERFORMANCE_THRESHOLD_MS:
                    logger.warning(f"Slow operation on sheet {sheet_name}: {process_time:.2f}ms")
                    
            except Exception as e:
                logger.error(f"Error processing sheet {sheet_name}: {e}")
                results.append((sheet_name, None))
        
        logger.info(f"Batch processing completed: {len(results)} results")
        return results


def monitor_operation(operation_name: str):
    """Decorator for monitoring operation performance.
    
    Args:
        operation_name: Name of the operation for logging
        
    Returns:
        Decorated function with performance monitoring
        
    Example:
        @monitor_operation("partner_calculation")
        def calculate_partner_totals(sheets):
            # Expensive calculation
            return results
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000
                
                if execution_time > PERFORMANCE_THRESHOLD_MS:
                    logger.warning(f"Slow {operation_name}: {execution_time:.2f}ms")
                else:
                    logger.debug(f"{operation_name} completed in {execution_time:.2f}ms")
                
                return result
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                logger.error(f"{operation_name} failed after {execution_time:.2f}ms: {e}")
                raise
        return wrapper
    return decorator


def optimize_partner_calculations(workbook, calculation_func: Callable[[List[str]], Any]) -> Any:
    """Optimize partner-related calculations using caching and batch processing.
    
    Args:
        workbook: Excel workbook object
        calculation_func: Function that performs calculations on partner sheets
        
    Returns:
        Result of the calculation function
        
    Example:
        def calculate_totals(partner_sheets):
            return sum(get_sheet_total(sheet) for sheet in partner_sheets)
        
        result = optimize_partner_calculations(workbook, calculate_totals)
    """
    optimizer = PerformanceOptimizer()
    from utils.workbook_utils import is_partner_worksheet
    
    partner_sheets = optimizer.get_cached_partner_sheets(workbook, is_partner_worksheet)
    
    @monitor_operation("partner_calculation")
    def monitored_calculation():
        return calculation_func(partner_sheets)
    
    return monitored_calculation()


def batch_process_sheets(sheets: List[str], operation_func: Callable[[str], Any], 
                        batch_size: int = 10) -> List[Tuple[str, Any]]:
    """Batch process sheets with configurable batch size.
    
    Args:
        sheets: List of sheet names to process
        operation_func: Function to apply to each sheet
        batch_size: Number of sheets to process in each batch
        
    Returns:
        List of tuples containing (sheet_name, operation_result)
        
    Example:
        def process_sheet(sheet_name):
            return expensive_sheet_operation(sheet_name)
        
        results = batch_process_sheets(partner_sheets, process_sheet, batch_size=5)
    """
    results = []
    total_sheets = len(sheets)
    
    logger.info(f"Batch processing {total_sheets} sheets in batches of {batch_size}")
    
    for i in range(0, total_sheets, batch_size):
        batch = sheets[i:i + batch_size]
        batch_start_time = time.time()
        
        logger.debug(f"Processing batch {i//batch_size + 1}: sheets {i+1}-{min(i+batch_size, total_sheets)}")
        
        for sheet_name in batch:
            try:
                start_time = time.time()
                result = operation_func(sheet_name)
                process_time = (time.time() - start_time) * 1000
                
                results.append((sheet_name, result))
                
                if process_time > PERFORMANCE_THRESHOLD_MS:
                    logger.warning(f"Slow operation on sheet {sheet_name}: {process_time:.2f}ms")
                    
            except Exception as e:
                logger.error(f"Error processing sheet {sheet_name}: {e}")
                results.append((sheet_name, None))
        
        batch_time = (time.time() - batch_start_time) * 1000
        logger.debug(f"Batch completed in {batch_time:.2f}ms")
    
    logger.info(f"Batch processing completed: {len(results)} total results")
    return results


# Global performance optimizer instance
_global_optimizer = None


def get_performance_optimizer() -> PerformanceOptimizer:
    """Get the global performance optimizer instance.
    
    Returns:
        Global PerformanceOptimizer instance
    """
    global _global_optimizer
    if _global_optimizer is None:
        _global_optimizer = PerformanceOptimizer()
    return _global_optimizer