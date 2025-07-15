"""
Excel service layer for optimized Excel operations.

This module provides a service layer that uses the optimized ExcelManager
and caching for all Excel-related operations in the application.
"""

import os
from typing import Optional, List, Dict, Any, Tuple
from utils.excel_manager import ExcelManager, ExcelContextManager
from utils.cache_manager import cache_manager, CacheAwareExcelManager
import logging

logger = logging.getLogger(__name__)


class ExcelService:
    """
    Service layer for Excel operations using optimized ExcelManager and caching.
    
    This service provides a clean interface for all Excel operations
    while leveraging performance optimizations and caching.
    """
    
    def __init__(self):
        """Initialize Excel service with caching."""
        self.current_managers: Dict[str, ExcelManager] = {}
        self.cache_aware = CacheAwareExcelManager(cache_manager)
    
    def open_workbook(self, file_path: str) -> ExcelManager:
        """
        Open an Excel workbook with optimized settings and caching.
        
        Args:
            file_path: Path to the Excel file
            
        Returns:
            ExcelManager: Optimized Excel manager instance
        """
        if file_path in self.current_managers:
            logger.info(f"Reusing existing manager for: {file_path}")
            return self.current_managers[file_path]
        
        try:
            # Validate file first (cached)
            is_valid, error_msg = self.validate_excel_file(file_path)
            if not is_valid:
                raise ValueError(f"Invalid Excel file: {error_msg}")
            
            manager = ExcelManager(file_path)
            self.current_managers[file_path] = manager
            logger.info(f"Opened workbook: {file_path}")
            return manager
        except Exception as e:
            logger.error(f"Failed to open workbook {file_path}: {str(e)}")
            raise
    
    def close_workbook(self, file_path: str) -> None:
        """
        Close a workbook and clean up resources.
        
        Args:
            file_path: Path of the workbook to close
        """
        if file_path in self.current_managers:
            manager = self.current_managers[file_path]
            manager.close()
            
            # Invalidate cache for this file
            cache_manager.invalidate_cache_for_file(file_path)
            
            del self.current_managers[file_path]
            logger.info(f"Closed workbook: {file_path}")
    
    def close_all_workbooks(self) -> None:
        """Close all open workbooks."""
        for file_path in list(self.current_managers.keys()):
            self.close_workbook(file_path)
    
    def clone_file(self, source_path: str, dest_path: str) -> bool:
        """
        Clone an Excel file using optimized methods.
        
        Args:
            source_path: Source file path
            dest_path: Destination file path
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Validate source file (cached)
            is_valid, error_msg = self.validate_excel_file(source_path)
            if not is_valid:
                logger.error(f"Cannot clone invalid file: {error_msg}")
                return False
            
            with ExcelContextManager(source_path) as source_excel:
                # Create new file with same content
                source_excel.save(dest_path)
                
                # Invalidate cache for new file
                cache_manager.invalidate_cache_for_file(dest_path)
                
                logger.info(f"Cloned file from {source_path} to {dest_path}")
                return True
        except Exception as e:
            logger.error(f"Failed to clone file: {str(e)}")
            return False
    
    def create_from_template(self, template_path: str, dest_path: str) -> bool:
        """
        Create a new file from template using optimized methods.
        
        Args:
            template_path: Path to template file
            dest_path: Path for new file
            
        Returns:
            bool: True if successful, False otherwise
        """
        return self.clone_file(template_path, dest_path)
    
    def create_from_scratch(self, file_path: str, 
                          sheet_name: str = "Sheet1") -> bool:
        """
        Create a new Excel file from scratch.
        
        Args:
            file_path: Path for the new file
            sheet_name: Name for the initial sheet
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            result = ExcelManager.create_excel_file(file_path, sheet_name)
            
            # Invalidate cache for new file
            cache_manager.invalidate_cache_for_file(file_path)
            
            logger.info(f"Created new Excel file: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to create file: {str(e)}")
            return False
    
    def validate_excel_file(self, file_path: str) -> Tuple[bool, str]:
        """
        Validate Excel file with caching.
        
        Args:
            file_path: Path to validate
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        return self.cache_aware.is_file_valid(file_path)
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get comprehensive file information with caching.
        
        Args:
            file_path: Path to the Excel file
            
        Returns:
            Dict[str, Any]: File information
        """
        try:
            # Get cached metadata
            metadata = cache_manager.get_file_metadata(file_path)
            
            # Get cached sheet names
            sheet_names = self.cache_aware.get_cached_sheet_names(file_path)
            
            # Combine information
            info = {
                'file_path': file_path,
                'file_size': metadata.get('size', 0),
                'file_size_mb': round(metadata.get('size', 0) / (1024 * 1024), 2),
                'sheet_count': len(sheet_names),
                'sheet_names': sheet_names,
                'last_modified': metadata.get('modified', 0),
                'file_hash': metadata.get('hash', ''),
                'is_valid': self.validate_excel_file(file_path)[0]
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Failed to get file info: {str(e)}")
            return {}
    
    def get_sheet_data(self, file_path: str, sheet_name: str,
                      max_rows: Optional[int] = None) -> List[List[Any]]:
        """
        Get data from a specific sheet with caching considerations.
        
        Args:
            file_path: Path to Excel file
            sheet_name: Name of the sheet
            max_rows: Maximum rows to read (None for all)
            
        Returns:
            List[List[Any]]: 2D array of cell values
        """
        # Check if sheet exists (cached)
        sheet_names = self.cache_aware.get_cached_sheet_names(file_path)
        if sheet_name not in sheet_names:
            return []
        
        try:
            with ExcelContextManager(file_path) as excel:
                sheet = excel.get_sheet_by_name(sheet_name)
                if not sheet:
                    return []
                
                data = []
                for i, row in enumerate(sheet.iter_rows(values_only=True), 1):
                    if max_rows and i > max_rows:
                        break
                    # Filter out None values and empty rows
                    if any(cell is not None for cell in row):
                        data.append(list(row))
                
                return data
        except Exception as e:
            logger.error(f"Failed to get sheet data: {str(e)}")
            return []
    
    def get_partner_list(self, file_path: str) -> List[Dict[str, str]]:
        """
        Get list of all partners with caching.
        
        Args:
            file_path: Path to Excel file
            
        Returns:
            List[Dict[str, str]]: List of partner information
        """
        try:
            sheet_names = self.cache_aware.get_cached_sheet_names(file_path)
            partners = []
            
            for sheet_name in sheet_names:
                if sheet_name.startswith('P') and len(sheet_name) > 1:
                    # Extract partner number and name
                    parts = sheet_name[1:].split()
                    partner_number = parts[0] if parts else ''
                    partner_name = ' '.join(parts[1:]) if len(parts) > 1 else ''
                    
                    # Get cached partner data
                    partner_data = self.cache_aware.get_cached_partner_data(
                        file_path, partner_number
                    )
                    
                    partners.append({
                        'sheet_name': sheet_name,
                        'partner_number': partner_number,
                        'partner_name': partner_name,
                        'has_data': partner_data.get('data_extracted', False)
                    })
            
            return partners
            
        except Exception as e:
            logger.error(f"Failed to get partner list: {str(e)}")
            return []
    
    def get_workpackage_list(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Get list of all workpackages with caching.
        
        Args:
            file_path: Path to Excel file
            
        Returns:
            List[Dict[str, Any]]: List of workpackage information
        """
        try:
            # Check if PM Summary exists
            sheet_names = self.cache_aware.get_cached_sheet_names(file_path)
            if "PM Summary" not in sheet_names:
                return []
            
            workpackages = []
            
            # Get workpackage data for common IDs
            for wp_id in range(1, 16):  # WP1 to WP15
                wp_data = self.cache_aware.get_cached_workpackage_data(
                    file_path, str(wp_id)
                )
                if wp_data.get('exists'):
                    workpackages.append(wp_data)
            
            return workpackages
            
        except Exception as e:
            logger.error(f"Failed to get workpackage list: {str(e)}")
            return []
    
    def update_sheet_data(self, file_path: str, sheet_name: str,
                         data: List[List[Any]], start_row: int = 1,
                         start_col: int = 1) -> bool:
        """
        Update sheet data and invalidate relevant caches.
        
        Args:
            file_path: Path to Excel file
            sheet_name: Name of the sheet to update
            data: 2D array of values to write
            start_row: Starting row (1-based)
            start_col: Starting column (1-based)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with ExcelContextManager(file_path) as excel:
                sheet = excel.get_sheet_by_name(sheet_name)
                if not sheet:
                    return False
                
                for row_idx, row_data in enumerate(data, start_row):
                    for col_idx, value in enumerate(row_data, start_col):
                        cell = sheet.cell(row=row_idx, column=col_idx)
                        cell.value = value
                
                excel.save()
                
                # Invalidate caches for this file
                cache_manager.invalidate_cache_for_file(file_path)
                
                return True
        except Exception as e:
            logger.error(f"Failed to update sheet data: {str(e)}")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive cache statistics.
        
        Returns:
            Dict[str, Any]: Cache statistics
        """
        return {
            'cache_manager_stats': cache_manager.get_cache_stats(),
            'open_workbooks': len(self.current_managers),
            'cached_files': len([
                f for f in cache_manager.get_excel_sheet_names.cache_info()
                .currsize > 0
            ])
        }
    
    def clear_all_caches(self) -> int:
        """
        Clear all caches and reset statistics.
        
        Returns:
            int: Number of cache entries cleared
        """
        cleared = cache_manager.clear_cache()
        
        # Clear LRU caches
        cache_manager.get_file_hash.cache_clear()
        cache_manager.get_file_metadata.cache_clear()
        cache_manager.validate_excel_file.cache_clear()
        cache_manager.get_excel_sheet_names.cache_clear()
        cache_manager.get_partner_data.cache_clear()
        cache_manager.get_workpackage_data.cache_clear()
        
        logger.info(f"Cleared all caches, removed {cleared} files")
        return cleared
