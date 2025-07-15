"""
Tests for the ExcelManager class.

This module contains unit tests for the optimized ExcelManager
and related functionality.
"""

import pytest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# Add src to path for imports
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.excel_manager import ExcelManager, ExcelContextManager
from core.excel_service import ExcelService


class TestExcelManager:
    """Test cases for ExcelManager class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def test_excel_file(self, temp_dir):
        """Create a test Excel file."""
        file_path = os.path.join(temp_dir, "test.xlsx")
        return ExcelManager.create_excel_file(file_path, "TestSheet")
    
    def test_initialization(self, temp_dir):
        """Test ExcelManager initialization."""
        file_path = os.path.join(temp_dir, "test_init.xlsx")
        ExcelManager.create_excel_file(file_path, "Sheet1")
        
        manager = ExcelManager(file_path)
        assert manager.file_path == file_path
        assert manager.is_open is False
        assert manager._workbook is None
    
    def test_initialization_nonexistent_file(self, temp_dir):
        """Test initialization with non-existent file."""
        file_path = os.path.join(temp_dir, "nonexistent.xlsx")
        
        with pytest.raises(FileNotFoundError):
            ExcelManager(file_path)
    
    def test_lazy_loading(self, test_excel_file):
        """Test lazy loading of workbook."""
        manager = test_excel_file
        
        # Initially not loaded
        assert manager._workbook is None
        
        # Access triggers loading
        workbook = manager.workbook
        assert workbook is not None
        assert manager._workbook is not None
        assert manager.is_open is True
    
    def test_get_sheet_names(self, test_excel_file):
        """Test getting sheet names."""
        manager = test_excel_file
        
        sheet_names = manager.get_sheet_names()
        assert "TestSheet" in sheet_names
        assert len(sheet_names) >= 1
    
    def test_sheet_exists(self, test_excel_file):
        """Test sheet existence check."""
        manager = test_excel_file
        
        assert manager.sheet_exists("TestSheet") is True
        assert manager.sheet_exists("NonExistent") is False
    
    def test_get_sheet_by_name(self, test_excel_file):
        """Test getting sheet by name."""
        manager = test_excel_file
        
        sheet = manager.get_sheet_by_name("TestSheet")
        assert sheet is not None
        assert sheet.title == "TestSheet"
        
        non_existent = manager.get_sheet_by_name("NonExistent")
        assert non_existent is None
    
    def test_create_sheet(self, test_excel_file):
        """Test creating new sheets."""
        manager = test_excel_file
        
        # Create new sheet
        new_sheet = manager.create_sheet("NewSheet")
        assert new_sheet is not None
        assert "NewSheet" in manager.get_sheet_names()
    
    def test_remove_sheet(self, test_excel_file):
        """Test removing sheets."""
        manager = test_excel_file
        
        # Create a sheet to remove
        manager.create_sheet("SheetToRemove")
        assert "SheetToRemove" in manager.get_sheet_names()
        
        # Remove the sheet
        result = manager.remove_sheet("SheetToRemove")
        assert result is True
        assert "SheetToRemove" not in manager.get_sheet_names()
        
        # Try to remove non-existent sheet
        result = manager.remove_sheet("NonExistent")
        assert result is False
    
    def test_save(self, temp_dir):
        """Test saving workbook."""
        file_path = os.path.join(temp_dir, "test_save.xlsx")
        manager = ExcelManager.create_excel_file(file_path, "Sheet1")
        
        # Modify and save
        sheet = manager.active_sheet
        sheet['A1'] = "Test Save"
        manager.save()
        
        # Verify file exists and has content
        assert os.path.exists(file_path)
        
        # Reopen and verify content
        new_manager = ExcelManager(file_path)
        sheet = new_manager.active_sheet
        assert sheet['A1'].value == "Test Save"
        new_manager.close()
    
    def test_close(self, test_excel_file):
        """Test closing workbook."""
        manager = test_excel_file
        
        # Ensure workbook is loaded
        _ = manager.workbook
        assert manager.is_open is True
        
        # Close workbook
        manager.close()
        assert manager.is_open is False
        assert manager._workbook is None
    
    def test_context_manager(self, temp_dir):
        """Test context manager usage."""
        file_path = os.path.join(temp_dir, "test_context.xlsx")
        ExcelManager.create_excel_file(file_path, "TestSheet")
        
        with ExcelContextManager(file_path) as excel:
            assert excel.is_open is True
            sheet = excel.active_sheet
            sheet['A1'] = "Context Test"
        
        # Verify file is closed after context
        assert excel.is_open is False
    
    def test_get_file_info(self, test_excel_file):
        """Test getting file information."""
        manager = test_excel_file
        
        info = manager.get_file_info()
        
        assert 'file_path' in info
        assert 'file_size' in info
        assert 'sheet_count' in info
        assert 'sheet_names' in info
        assert info['file_path'] == manager.file_path
        assert info['sheet_count'] >= 1
    
    def test_create_excel_file(self, temp_dir):
        """Test creating new Excel files."""
        file_path = os.path.join(temp_dir, "test_create.xlsx")
        
        manager = ExcelManager.create_excel_file(file_path, "CustomSheet")
        
        assert os.path.exists(file_path)
        assert "CustomSheet" in manager.get_sheet_names()
        manager.close()


class TestExcelService:
    """Test cases for ExcelService class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def excel_service(self):
        """Create ExcelService instance."""
        return ExcelService()
    
    @pytest.fixture
    def test_file(self, temp_dir):
        """Create test Excel file."""
        file_path = os.path.join(temp_dir, "test_service.xlsx")
        ExcelManager.create_excel_file(file_path, "TestSheet")
        return file_path
    
    def test_open_workbook(self, excel_service, test_file):
        """Test opening workbooks."""
        manager = excel_service.open_workbook(test_file)
        
        assert manager is not None
        assert manager.file_path == test_file
        assert test_file in excel_service.current_managers
    
    def test_close_workbook(self, excel_service, test_file):
        """Test closing workbooks."""
        excel_service.open_workbook(test_file)
        assert test_file in excel_service.current_managers
        
        excel_service.close_workbook(test_file)
        assert test_file not in excel_service.current_managers
    
    def test_close_all_workbooks(self, excel_service, temp_dir):
        """Test closing all workbooks."""
        file1 = os.path.join(temp_dir, "test1.xlsx")
        file2 = os.path.join(temp_dir, "test2.xlsx")
        
        ExcelManager.create_excel_file(file1, "Sheet1")
        ExcelManager.create_excel_file(file2, "Sheet2")
        
        excel_service.open_workbook(file1)
        excel_service.open_workbook(file2)
        
        assert len(excel_service.current_managers) == 2
        
        excel_service.close_all_workbooks()
        assert len(excel_service.current_managers) == 0
    
    def test_clone_file(self, excel_service, test_file, temp_dir):
        """Test file cloning."""
        dest_path = os.path.join(temp_dir, "cloned.xlsx")
        
        result = excel_service.clone_file(test_file, dest_path)
        
        assert result is True
        assert os.path.exists(dest_path)
    
    def test_validate_excel_file(self, excel_service, test_file):
        """Test Excel file validation."""
        assert excel_service.validate_excel_file(test_file) is True
        assert excel_service.validate_excel_file("nonexistent.xlsx") is False
    
    def test_get_sheet_data(self, excel_service, test_file):
        """Test getting sheet data."""
        # Add some test data
        with ExcelContextManager(test_file) as excel:
            sheet = excel.active_sheet
            sheet['A1'] = "Test"
            sheet['B1'] = 123
            excel.save()
        
        data = excel_service.get_sheet_data(test_file, "TestSheet", max_rows=1)
        
        assert len(data) == 1
        assert data[0] == ["Test", 123]
    
    def test_update_sheet_data(self, excel_service, test_file):
        """Test updating sheet data."""
        new_data = [["Name", "Age"], ["Alice", 25], ["Bob", 30]]
        
        result = excel_service.update_sheet_data(
            test_file, "TestSheet", new_data
        )
        
        assert result is True
        
        # Verify data was written
        data = excel_service.get_sheet_data(test_file, "TestSheet")
        assert data == new_data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
