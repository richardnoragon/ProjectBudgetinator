"""
Resource cleanup and memory management usage examples.

This module demonstrates how to use the comprehensive resource cleanup
system to prevent memory leaks and manage Excel resources efficiently.
"""

import sys
import os
import tempfile
import shutil
import logging

from utils.excel_manager import ExcelManager, excel_context, memory_tracker
from utils.resource_cleanup import (
    resource_manager, cleanup_manager,
    get_system_memory_info, force_system_cleanup, memory_monitor
)

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Set up logging
logging.basicConfig(level=logging.INFO)


def example_basic_context_manager():
    """Basic context manager usage for resource cleanup."""
    print("=== Basic Context Manager Usage ===")
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Create test file
        test_file = os.path.join(temp_dir, "test_context.xlsx")
        
        # Use context manager for automatic cleanup
        with excel_context(test_file) as wb:
            print(f"Opened workbook: {test_file}")
            sheet = wb.active
            sheet['A1'] = "Context Manager Test"
            print("Data written to sheet")
        
        print("Workbook automatically closed")
        
        # Verify cleanup
        stats = memory_tracker.get_stats()
        print(f"Memory stats: {stats}")
        
    finally:
        shutil.rmtree(temp_dir)


def example_safe_excel_manager():
    """Safe ExcelManager usage with memory tracking."""
    print("\n=== Safe ExcelManager Usage ===")
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        test_file = os.path.join(temp_dir, "safe_manager.xlsx")
        
        # Create file
        excel = ExcelManager.create_excel_file(test_file, "TestSheet")
        excel.save()
        excel.close()
        
        # Use ExcelManager with memory tracking
        excel = ExcelManager(test_file)
        
        # Get memory usage
        memory_info = excel.get_memory_usage()
        print(f"Memory info: {memory_info}")
        
        # Process data
        sheet = excel.active_sheet
        sheet['A1'] = "Memory Test"
        sheet['B1'] = 42
        
        # Force cleanup
        excel.force_close()
        
        # Check final state
        final_stats = memory_tracker.get_stats()
        print(f"Final stats: {final_stats}")
        
    finally:
        shutil.rmtree(temp_dir)


def example_bulk_operation_cleanup():
    """Bulk operation with automatic cleanup."""
    print("\n=== Bulk Operation Cleanup ===")
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Create multiple test files
        files = []
        for i in range(3):
            file_path = os.path.join(temp_dir, f"bulk_{i}.xlsx")
            excel = ExcelManager.create_excel_file(file_path, f"Sheet{i}")
            excel.save()
            excel.close()
            files.append(file_path)
        
        # Use bulk operation context manager
        from utils.excel_manager import memory_safe_bulk_context
        
        with memory_safe_bulk_context(files) as workbooks:
            print(f"Opened {len(workbooks)} workbooks")
            
            for file_path, wb in workbooks.items():
                sheet = wb.active
                sheet['A1'] = f"Bulk {os.path.basename(file_path)}"
                print(f"Processed {file_path}")
        
        print("All workbooks automatically closed")
        
    finally:
        shutil.rmtree(temp_dir)


def example_memory_monitoring():
    """Memory monitoring during Excel operations."""
    print("\n=== Memory Monitoring ===")
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        test_file = os.path.join(temp_dir, "memory_monitor.xlsx")
        
        # Get initial memory
        initial_memory = get_system_memory_info()
        print(f"Initial memory: {initial_memory['used_memory_gb']:.2f}GB")
        
        # Monitor with decorator
        @memory_monitor.monitor_operation("excel_processing")
        def process_excel():
            excel = ExcelManager.create_excel_file(test_file, "Monitor")
            
            # Add lots of data to test memory usage
            sheet = excel.active_sheet
            for i in range(1, 1000):
                sheet[f'A{i}'] = f"Data {i}"
                sheet[f'B{i}'] = i * 2
            
            excel.save()
            excel.close()
            return "completed"
        
        result = process_excel()
        print(f"Processing result: {result}")
        
        # Check memory stats
        stats = memory_monitor.get_stats()
        print(f"Memory stats: {stats}")
        
    finally:
        shutil.rmtree(temp_dir)


def example_resource_manager():
    """Resource manager usage for centralized cleanup."""
    print("\n=== Resource Manager Usage ===")
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        test_file = os.path.join(temp_dir, "resource_manager.xlsx")
        
        # Use resource manager
        manager = resource_manager.get_manager(test_file)
        
        # Process data
        sheet = manager.active_sheet
        sheet['A1'] = "Resource Manager Test"
        
        # Get resource stats
        stats = resource_manager.get_resource_stats()
        print(f"Resource stats: {stats}")
        
        # Manual cleanup
        resource_manager.release_manager(test_file)
        
        # Final stats
        final_stats = resource_manager.get_resource_stats()
        print(f"Final stats: {final_stats}")
        
    finally:
        shutil.rmtree(temp_dir)


def example_exception_handling():
    """Exception handling with automatic cleanup."""
    print("\n=== Exception Handling ===")
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        test_file = os.path.join(temp_dir, "exception_test.xlsx")
        
        # Simulate exception with cleanup
        try:
            with excel_context(test_file) as wb:
                # This will raise an exception
                _ = wb  # Use the variable to avoid unused variable warning
                raise ValueError("Simulated error")
        except ValueError as e:
            print(f"Caught exception: {e}")
            print("Workbook was automatically closed")
        
        # Verify cleanup
        stats = memory_tracker.get_stats()
        print(f"Memory after exception: {stats}")
        
    finally:
        shutil.rmtree(temp_dir)


def example_force_cleanup():
    """Force system-wide cleanup."""
    print("\n=== Force System Cleanup ===")
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Create multiple files
        files = []
        for i in range(5):
            file_path = os.path.join(temp_dir, f"cleanup_{i}.xlsx")
            excel = ExcelManager.create_excel_file(file_path, f"Sheet{i}")
            excel.save()
            excel.close()
            files.append(file_path)
        
        # Process files
        managers = []
        for file_path in files:
            manager = ExcelManager(file_path)
            managers.append(manager)
        
        # Check initial state
        initial_stats = memory_tracker.get_stats()
        print(f"Initial: {initial_stats}")
        
        # Force cleanup
        force_system_cleanup()
        
        # Check final state
        final_stats = memory_tracker.get_stats()
        print(f"Final: {final_stats}")
        
    finally:
        shutil.rmtree(temp_dir)


def example_memory_leak_detection():
    """Memory leak detection example."""
    print("\n=== Memory Leak Detection ===")
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        test_file = os.path.join(temp_dir, "leak_detection.xlsx")
        
        # Simulate memory leak scenario
        print("Creating potential memory leak scenario...")
        
        # Create many managers without proper cleanup
        managers = []
        for i in range(10):
            manager = ExcelManager(test_file)
            managers.append(manager)
            
            if i % 3 == 0:
                # Proper cleanup every 3rd iteration
                manager.force_close()
                managers.clear()
        
        # Force cleanup
        force_system_cleanup()
        
        # Check memory
        memory_info = get_system_memory_info()
        print(f"System memory after cleanup: {memory_info['used_memory_gb']:.2f}GB")
        
    finally:
        shutil.rmtree(temp_dir)


def example_cleanup_callbacks():
    """Custom cleanup callbacks."""
    print("\n=== Cleanup Callbacks ===")
    
    def custom_cleanup():
        print("Custom cleanup callback executed")
    
    # Register custom cleanup
    cleanup_manager.add_cleanup_callback(custom_cleanup)
    
    # Simulate application exit
    print("Simulating application exit...")
    cleanup_manager._cleanup_all_resources()


if __name__ == "__main__":
    print("Resource Cleanup and Memory Management Examples")
    print("=" * 60)
    
    try:
        # Get initial system memory
        initial_memory = get_system_memory_info()
        print(f"Initial system memory: {initial_memory['used_memory_gb']:.2f}GB")
        
        # Run examples
        example_basic_context_manager()
        example_safe_excel_manager()
        example_bulk_operation_cleanup()
        example_memory_monitoring()
        example_resource_manager()
        example_exception_handling()
        example_force_cleanup()
        example_memory_leak_detection()
        example_cleanup_callbacks()
        
        # Final system memory
        final_memory = get_system_memory_info()
        print(f"\nFinal system memory: {final_memory['used_memory_gb']:.2f}GB")
        
        print("\n" + "=" * 60)
        print("All resource cleanup examples completed successfully!")
        
    except Exception as e:
        print(f"Example execution failed: {e}")
        import traceback
        traceback.print_exc()
        
        # Ensure cleanup on error
        force_system_cleanup()
