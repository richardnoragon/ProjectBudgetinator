"""
Caching utilities for ProjectBudgetinator.

This module provides intelligent caching for Excel operations, file validation,
and frequently accessed data to improve application performance.
"""

import os
import hashlib
import json
import time
from functools import lru_cache, wraps
from typing import Dict, List, Any, Optional, Tuple
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Centralized caching system for ProjectBudgetinator.
    
    Provides caching for:
    - Excel file hashes and change detection
    - Partner data extraction
    - Workpackage lookups
    - Validation results
    - File metadata
    """
    
    def __init__(self, cache_dir: str = None):
        """
        Initialize CacheManager.
        
        Args:
            cache_dir: Directory for persistent cache storage
        """
        self.cache_dir = cache_dir or os.path.join(
            str(Path.home()), "ProjectBudgetinator", "cache"
        )
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Cache statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0
        }
    
    @staticmethod
    @lru_cache(maxsize=128)
    def get_file_hash(file_path: str) -> str:
        """
        Get MD5 hash of file for change detection.
        
        Args:
            file_path: Path to the file
            
        Returns:
            str: MD5 hash of file content
        """
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except (IOError, OSError):
            return ""
    
    @staticmethod
    @lru_cache(maxsize=64)
    def get_file_metadata(file_path: str) -> Dict[str, Any]:
        """
        Cache file metadata for quick access.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dict[str, Any]: File metadata including size, mtime, etc.
        """
        try:
            stat = os.stat(file_path)
            return {
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'created': stat.st_ctime,
                'hash': CacheManager.get_file_hash(file_path)
            }
        except (IOError, OSError):
            return {}
    
    @lru_cache(maxsize=32)
    def is_file_modified(self, file_path: str, last_known_hash: str) -> bool:
        """
        Check if file has been modified since last known hash.
        
        Args:
            file_path: Path to check
            last_known_hash: Previously cached hash
            
        Returns:
            bool: True if file has been modified
        """
        current_hash = self.get_file_hash(file_path)
        return current_hash != last_known_hash
    
    @lru_cache(maxsize=256)
    def validate_excel_file(self, file_path: str) -> Tuple[bool, str]:
        """
        Cache Excel file validation results.
        
        Args:
            file_path: Path to validate
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        try:
            if not os.path.exists(file_path):
                return False, "File does not exist"
            
            if not file_path.lower().endswith(('.xlsx', '.xls')):
                return False, "Invalid file extension"
            
            # Check file size (max 100MB)
            file_size = os.path.getsize(file_path)
            if file_size > 100 * 1024 * 1024:
                return False, "File too large (>100MB)"
            
            # Try to open with openpyxl
            from openpyxl import load_workbook
            load_workbook(file_path, read_only=True, data_only=True).close()
            
            return True, ""
            
        except Exception as e:
            return False, str(e)
    
    @lru_cache(maxsize=128)
    def get_excel_sheet_names(self, file_path: str) -> List[str]:
        """
        Cache Excel sheet names for quick access.
        
        Args:
            file_path: Path to Excel file
            
        Returns:
            List[str]: List of sheet names
        """
        try:
            from openpyxl import load_workbook
            with load_workbook(file_path, read_only=True) as wb:
                return wb.sheetnames
        except Exception:
            return []
    
    @lru_cache(maxsize=64)
    def get_partner_data(self, file_path: str, partner_number: str) -> Dict[str, Any]:
        """
        Cache partner data extraction from Excel files.
        
        Args:
            file_path: Path to Excel file
            partner_number: Partner identifier
            
        Returns:
            Dict[str, Any]: Partner data
        """
        try:
            from openpyxl import load_workbook
            with load_workbook(file_path, read_only=True, data_only=True) as wb:
                sheet_name = f"P{partner_number}"
                if sheet_name not in wb.sheetnames:
                    return {}
                
                sheet = wb[sheet_name]
                
                # Extract basic partner info
                data = {
                    'partner_number': partner_number,
                    'sheet_name': sheet_name,
                    'exists': True,
                    'data_extracted': False
                }
                
                # Try to extract common fields
                try:
                    data.update({
                        'partner_id': sheet['D4'].value,
                        'beneficiary_name': sheet['D5'].value,
                        'country': sheet['D6'].value,
                        'role': sheet['D7'].value,
                        'data_extracted': True
                    })
                except (KeyError, AttributeError):
                    pass
                
                return data
                
        except Exception as e:
            logger.error(f"Error extracting partner data: {e}")
            return {}
    
    @lru_cache(maxsize=64)
    def get_workpackage_data(self, file_path: str, workpackage_id: str) -> Dict[str, Any]:
        """
        Cache workpackage data extraction.
        
        Args:
            file_path: Path to Excel file
            workpackage_id: Workpackage identifier
            
        Returns:
            Dict[str, Any]: Workpackage data
        """
        try:
            from openpyxl import load_workbook
            with load_workbook(file_path, read_only=True, data_only=True) as wb:
                if "PM Summary" not in wb.sheetnames:
                    return {}
                
                sheet = wb["PM Summary"]
                
                # Find workpackage row (simplified logic)
                data = {
                    'workpackage_id': workpackage_id,
                    'exists': False,
                    'row_data': None
                }
                
                # Scan for workpackage ID in column A
                for row in range(2, sheet.max_row + 1):
                    cell_value = sheet.cell(row=row, column=1).value
                    if str(cell_value) == str(workpackage_id):
                        data.update({
                            'exists': True,
                            'row': row,
                            'row_data': [
                                sheet.cell(row=row, column=col).value
                                for col in range(1, min(sheet.max_column + 1, 10))
                            ]
                        })
                        break
                
                return data
                
        except Exception as e:
            logger.error(f"Error extracting workpackage data: {e}")
            return {}
    
    def cache_with_ttl(self, key: str, data: Any, ttl_seconds: int = 300) -> None:
        """
        Cache data with time-to-live.
        
        Args:
            key: Cache key
            data: Data to cache
            ttl_seconds: Time to live in seconds
        """
        cache_file = os.path.join(self.cache_dir, f"{key}.json")
        cache_data = {
            'data': data,
            'timestamp': time.time(),
            'ttl': ttl_seconds
        }
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, default=str)
        except Exception as e:
            logger.error(f"Failed to cache data: {e}")
    
    def get_cached_with_ttl(self, key: str) -> Optional[Any]:
        """
        Get cached data with TTL check.
        
        Args:
            key: Cache key
            
        Returns:
            Optional[Any]: Cached data or None if expired/missing
        """
        cache_file = os.path.join(self.cache_dir, f"{key}.json")
        
        try:
            if not os.path.exists(cache_file):
                return None
            
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
            
            # Check if cache is expired
            if time.time() - cache_data['timestamp'] > cache_data['ttl']:
                os.remove(cache_file)
                return None
            
            return cache_data['data']
            
        except Exception as e:
            logger.error(f"Failed to get cached data: {e}")
            return None
    
    def clear_cache(self, pattern: str = "*") -> int:
        """
        Clear cache files matching pattern.
        
        Args:
            pattern: File pattern to match (default: all)
            
        Returns:
            int: Number of files removed
        """
        import glob
        
        removed_count = 0
        cache_pattern = os.path.join(self.cache_dir, pattern)
        
        try:
            for cache_file in glob.glob(cache_pattern):
                if cache_file.endswith('.json'):
                    os.remove(cache_file)
                    removed_count += 1
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
        
        return removed_count
    
    def get_cache_stats(self) -> Dict[str, int]:
        """
        Get cache statistics.
        
        Returns:
            Dict[str, int]: Cache statistics
        """
        return {
            'file_hash_cache_size': self.get_file_hash.cache_info().currsize,
            'file_hash_cache_max': self.get_file_hash.cache_info().maxsize,
            'metadata_cache_size': self.get_file_metadata.cache_info().currsize,
            'metadata_cache_max': self.get_file_metadata.cache_info().maxsize,
            'sheet_names_cache_size': self.get_excel_sheet_names.cache_info().currsize,
            'sheet_names_cache_max': self.get_excel_sheet_names.cache_info().maxsize,
            'partner_data_cache_size': self.get_partner_data.cache_info().currsize,
            'partner_data_cache_max': self.get_partner_data.cache_info().maxsize,
            'workpackage_data_cache_size': self.get_workpackage_data.cache_info().currsize,
            'workpackage_data_cache_max': self.get_workpackage_data.cache_info().maxsize,
            'validation_cache_size': self.validate_excel_file.cache_info().currsize,
            'validation_cache_max': self.validate_excel_file.cache_info().maxsize,
        }
    
    def invalidate_cache_for_file(self, file_path: str) -> None:
        """
        Invalidate all cached data for a specific file.
        
        Args:
            file_path: Path to invalidate cache for
        """
        # Clear LRU cache entries for this file
        self.get_file_hash.cache_clear()
        self.get_file_metadata.cache_clear()
        self.get_excel_sheet_names.cache_clear()
        self.validate_excel_file.cache_clear()
        self.get_partner_data.cache_clear()
        self.get_workpackage_data.cache_clear()
        
        logger.info(f"Invalidated cache for file: {file_path}")


def cached_with_invalidation(cache_manager: CacheManager, ttl: int = 300):
    """
    Decorator for caching function results with TTL and invalidation.
    
    Args:
        cache_manager: CacheManager instance
        ttl: Time to live in seconds
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            key_parts = [func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
            key = "_".join(key_parts)
            
            # Try to get from cache
            cached = cache_manager.get_cached_with_ttl(key)
            if cached is not None:
                logger.debug(f"Cache hit for {key}")
                return cached
            
            # Compute and cache
            result = func(*args, **kwargs)
            cache_manager.cache_with_ttl(key, result, ttl)
            logger.debug(f"Cache miss for {key}, cached result")
            
            return result
        return wrapper
    return decorator


class CacheAwareExcelManager:
    """
    ExcelManager wrapper with caching capabilities.
    
    Provides caching layer on top of Excel operations to avoid
    repeated expensive operations.
    """
    
    def __init__(self, cache_manager: CacheManager):
        """Initialize with cache manager."""
        self.cache = cache_manager
    
    def get_cached_sheet_names(self, file_path: str) -> List[str]:
        """Get sheet names with caching."""
        return self.cache.get_excel_sheet_names(file_path)
    
    def get_cached_partner_data(self, file_path: str, partner_number: str) -> Dict[str, Any]:
        """Get partner data with caching."""
        return self.cache.get_partner_data(file_path, partner_number)
    
    def get_cached_workpackage_data(self, file_path: str, workpackage_id: str) -> Dict[str, Any]:
        """Get workpackage data with caching."""
        return self.cache.get_workpackage_data(file_path, workpackage_id)
    
    def is_file_valid(self, file_path: str) -> Tuple[bool, str]:
        """Check file validity with caching."""
        return self.cache.validate_excel_file(file_path)
    
    def has_file_changed(self, file_path: str, last_hash: str) -> bool:
        """Check if file has changed since last known hash."""
        return self.cache.is_file_modified(file_path, last_hash)


# Global cache manager instance
cache_manager = CacheManager()
