# Resource Cleanup and Memory Management Guide

## Overview

This guide provides comprehensive documentation for the resource cleanup and memory management system implemented in ProjectBudgetinator. The system is designed to prevent memory leaks, manage Excel resources efficiently, and ensure proper cleanup of system resources.

## Architecture

The resource cleanup system consists of several key components:

1. **ExcelManager** - Enhanced with memory tracking and cleanup
2. **ResourceCleanupManager** - Centralized resource lifecycle management
3. **Context Managers** - Safe resource handling patterns
4. **Memory Monitor** - Real-time memory usage tracking
5. **ExcelResourceTracker** - File-level resource tracking

## Components

### 1. ExcelManager

The enhanced ExcelManager provides comprehensive memory management features:

#### Key Features
- **Memory Usage Tracking**: Real-time memory monitoring
- **Force Cleanup**: Immediate resource release
- **Context Manager Support**: Automatic cleanup with `with` statements
- **Lazy Loading**: Efficient resource loading
- **Read-Only Mode**: Memory optimization for large files

#### Usage Examples

```python
from utils.excel_manager import ExcelManager, excel_context

# Basic usage with memory tracking
excel = ExcelManager("file.xlsx")
memory_info = excel.get_memory_usage()
print(f"Memory usage: {memory_info['process_memory_mb']}MB")

# Force cleanup
excel.force_close()

# Context manager usage
with excel_context("file.xlsx") as wb:
    sheet = wb.active
    sheet['A1'] = "Data"
# Workbook automatically closed
```

### 2. ResourceCleanupManager

Centralized system for managing resource lifecycle:

#### Key Features
- **Resource Registration**: Track resources for cleanup
- **Callback System**: Custom cleanup functions
- **Exception Handling**: Graceful cleanup on errors
- **Automatic Registration**: Integration with ExcelManager

#### Usage Examples

```python
from utils.resource_cleanup import cleanup_manager

# Register custom cleanup
def custom_cleanup():
    print("Cleaning up custom resources")

cleanup_manager.add_cleanup_callback(custom_cleanup)

# Register resource for cleanup
excel = ExcelManager("file.xlsx")
cleanup_manager.register_resource(
    "file.xlsx",
    lambda: excel.force_close()
)
```

### 3. Context Managers

Safe resource handling with automatic cleanup:

#### Available Context Managers

1. **excel_context**: Basic Excel file handling
2. **safe_excel_context**: Enhanced with error handling
3. **memory_safe_bulk_context**: Multiple file handling
4. **memory_monitored_context**: With memory monitoring

#### Usage Examples

```python
from utils.excel_manager import (
    excel_context, 
    memory_safe_bulk_context,
    memory_monitored_context
)

# Single file context
with excel_context("file.xlsx") as wb:
    # Process file
    pass

# Bulk file context
files = ["file1.xlsx", "file2.xlsx", "file3.xlsx"]
with memory_safe_bulk_context(files) as workbooks:
    for file_path, wb in workbooks.items():
        # Process each file
        pass

# Memory monitored context
with memory_monitored_context("operation_name"):
    # Memory usage will be tracked
    pass
```

### 4. Memory Monitor

Real-time memory usage tracking:

#### Key Features
- **System Memory Info**: Total, used, available memory
- **Process Memory**: Current process memory usage
- **Operation Monitoring**: Track memory usage per operation
- **Memory Leak Detection**: Identify potential leaks

#### Usage Examples

```python
from utils.resource_cleanup import (
    get_system_memory_info, 
    memory_monitor,
    force_system_cleanup
)

# Get system memory info
memory_info = get_system_memory_info()
print(f"System memory: {memory_info['used_memory_gb']:.2f}GB")

# Monitor operation
@memory_monitor.monitor_operation("data_processing")
def process_data():
    # Your processing code
    pass

# Force system cleanup
force_system_cleanup()
```

### 5. Resource Manager

Centralized resource management with caching:

#### Key Features
- **Resource Caching**: Reuse existing resources
- **Automatic Cleanup**: On application exit
- **Resource Statistics**: Track resource usage
- **Thread-Safe**: Safe for concurrent use

#### Usage Examples

```python
from utils.resource_cleanup import resource_manager

# Get resource manager
manager = resource_manager.get_manager("file.xlsx")

# Get resource statistics
stats = resource_manager.get_resource_stats()
print(f"Active resources: {stats['total_resources']}")

# Release specific resource
resource_manager.release_manager("file.xlsx")
```

## Best Practices

### 1. Always Use Context Managers

```python
# Good
with excel_context("file.xlsx") as wb:
    sheet = wb.active
    sheet['A1'] = "Data"

# Avoid
excel = ExcelManager("file.xlsx")
sheet = excel.active_sheet
sheet['A1'] = "Data"
# Manual cleanup required
```

### 2. Monitor Memory Usage

```python
# Monitor large operations
@memory_monitor.monitor_operation("large_import")
def import_large_dataset():
    # Your import code
    pass

# Check memory before/after
before = get_system_memory_info()
import_large_dataset()
after = get_system_memory_info()
print(f"Memory used: {after['used_memory_gb'] - before['used_memory_gb']:.2f}GB")
```

### 3. Use Bulk Operations for Multiple Files

```python
# Good - bulk context
files = ["file1.xlsx", "file2.xlsx", "file3.xlsx"]
with memory_safe_bulk_context(files) as workbooks:
    for file_path, wb in workbooks.items():
        # Process file
        pass

# Avoid - individual contexts
for file in files:
    with excel_context(file) as wb:
        # Process file
        pass
```

### 4. Register Custom Cleanup

```python
# Register application-specific cleanup
def cleanup_temp_files():
    import shutil
    import tempfile
    temp_dir = tempfile.gettempdir()
    # Clean up temp files
    pass

cleanup_manager.add_cleanup_callback(cleanup_temp_files)
```

### 5. Handle Exceptions Gracefully

```python
# Good - exception-safe
try:
    with excel_context("file.xlsx") as wb:
        # Process file
        pass
except Exception as e:
    logger.error(f"Error processing file: {e}")
    # Context manager ensures cleanup

# Avoid - manual cleanup on exception
excel = None
try:
    excel = ExcelManager("file.xlsx")
    # Process file
except Exception as e:
    logger.error(f"Error: {e}")
finally:
    if excel:
        excel.close()
```

## Memory Leak Prevention

### Common Memory Leak Patterns

1. **Unclosed Workbooks**
   ```python
   # Leak
   excel = ExcelManager("file.xlsx")
   # Missing excel.close()
   
   # Fix
   with excel_context("file.xlsx") as wb:
       # Use workbook
       pass
   ```

2. **Circular References**
   ```python
   # Leak
   class DataProcessor:
       def __init__(self, excel):
           self.excel = excel
           excel.processor = self  # Circular reference
   
   # Fix
   import weakref
   class DataProcessor:
       def __init__(self, excel):
           self.excel = weakref.ref(excel)
   ```

3. **Large Data Retention**
   ```python
   # Leak
   data = []
   for file in files:
       excel = ExcelManager(file)
       data.extend(excel.get_all_data())  # Keeps all in memory
   
   # Fix
   def process_file(file):
       with excel_context(file) as wb:
           return process_data(wb)
   
   results = [process_file(f) for f in files]
   ```

### Memory Monitoring

```python
from utils.resource_cleanup import memory_monitor

# Set up monitoring
memory_monitor.start_monitoring()

# Your application code
process_files()

# Check for leaks
stats = memory_monitor.get_stats()
if stats['potential_leaks'] > 0:
    logger.warning(f"Detected {stats['potential_leaks']} potential memory leaks")
```

## Performance Optimization

### 1. Lazy Loading

```python
# Use lazy loading for large files
excel = ExcelManager("large_file.xlsx", read_only=True)
# Only loads data when accessed
```

### 2. Resource Pooling

```python
# Use resource manager for pooling
manager = resource_manager.get_manager("file.xlsx")
# Reuses existing instance if available
```

### 3. Batch Processing

```python
# Process multiple files efficiently
files = get_files_to_process()
with memory_safe_bulk_context(files) as workbooks:
    for file_path, wb in workbooks.items():
        process_workbook(wb)
```

## Debugging Memory Issues

### 1. Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable memory debug logging
memory_monitor.set_debug_mode(True)
```

### 2. Memory Profiling

```python
from utils.resource_cleanup import memory_monitor

# Profile specific operation
@memory_monitor.profile_operation("critical_operation")
def critical_operation():
    # Your critical code
    pass

# Get detailed profile
profile = memory_monitor.get_profile("critical_operation")
print(f"Peak memory: {profile['peak_memory_mb']}MB")
```

### 3. Memory Dump Analysis

```python
# Dump memory state
memory_monitor.dump_memory_state("before_operation")

# Perform operation
process_data()

# Dump memory state after
memory_monitor.dump_memory_state("after_operation")

# Compare states
comparison = memory_monitor.compare_states("before_operation", "after_operation")
print(f"Memory delta: {comparison['memory_delta_mb']}MB")
```

## Integration with Existing Code

### 1. Retrofitting Existing Handlers

```python
# Before
class OldHandler:
    def process_file(self, file_path):
        excel = ExcelManager(file_path)
        # Process file
        # Missing cleanup

# After
class NewHandler:
    def process_file(self, file_path):
        with excel_context(file_path) as wb:
            # Process file
            # Automatic cleanup
```

### 2. GUI Integration

```python
from utils.resource_cleanup import cleanup_manager

class MainWindow:
    def __init__(self):
        # Register cleanup on window close
        cleanup_manager.add_cleanup_callback(self.cleanup_gui)
    
    def cleanup_gui(self):
        # Close all open dialogs
        for dialog in self.open_dialogs:
            dialog.close()
        
        # Force cleanup of Excel resources
        force_system_cleanup()
```

## Testing

### Unit Tests

```python
import unittest
from tests.test_resource_cleanup import TestExcelManagerMemoryManagement

class TestMyIntegration(unittest.TestCase):
    def test_memory_cleanup(self):
        # Test your integration
        pass

if __name__ == '__main__':
    unittest.main()
```

### Memory Leak Tests

```python
def test_memory_leak():
    import gc
    import psutil
    
    process = psutil.Process()
    initial_memory = process.memory_info().rss
    
    # Run your operation multiple times
    for i in range(100):
        with excel_context("test.xlsx") as wb:
            # Your operation
            pass
    
    # Force garbage collection
    gc.collect()
    
    final_memory = process.memory_info().rss
    memory_increase = final_memory - initial_memory
    
    # Should be minimal increase
    assert memory_increase < 10 * 1024 * 1024  # 10MB threshold
```

## Configuration

### Environment Variables

```bash
# Enable debug mode
export MEMORY_DEBUG=1

# Set memory threshold (MB)
export MEMORY_THRESHOLD=100

# Enable automatic cleanup
export AUTO_CLEANUP=1
```

### Configuration File

```json
{
  "memory_management": {
    "debug_mode": true,
    "memory_threshold_mb": 100,
    "auto_cleanup": true,
    "cleanup_interval_seconds": 300
  }
}
```

## Troubleshooting

### Common Issues

1. **"Out of memory" errors**
   - Check system memory usage
   - Reduce batch sizes
   - Use streaming for large files

2. **"File in use" errors**
   - Ensure all contexts are properly closed
   - Use force_cleanup() if needed
   - Check for zombie processes

3. **Slow performance**
   - Enable resource pooling
   - Use lazy loading
   - Reduce memory monitoring overhead

### Debug Commands

```python
# Check current memory usage
from utils.resource_cleanup import get_system_memory_info
print(get_system_memory_info())

# List open resources
from utils.resource_cleanup import resource_manager
print(resource_manager.get_resource_stats())

# Force cleanup
from utils.resource_cleanup import force_system_cleanup
force_system_cleanup()
```

## API Reference

### ExcelManager

```python
class ExcelManager:
    def get_memory_usage(self) -> dict
    def force_close(self) -> None
    def get_memory_info(self) -> dict
```

### ResourceCleanupManager

```python
class ResourceCleanupManager:
    def add_cleanup_callback(self, callback: Callable) -> None
    def register_resource(self, resource_id: str, cleanup_func: Callable) -> None
    def _cleanup_all_resources(self) -> None
```

### Memory Monitor

```python
class MemoryMonitor:
    def monitor_operation(self, operation_name: str)
    def get_stats(self) -> dict
    def get_system_memory_info(self) -> dict
```

### Context Managers

```python
@contextmanager
def excel_context(file_path: str, **kwargs)
@contextmanager
def memory_safe_bulk_context(file_paths: List[str])
@contextmanager
def memory_monitored_context(operation_name: str)
```

This comprehensive guide provides everything needed to effectively use the resource cleanup system in ProjectBudgetinator. The system is designed to be easy to integrate while providing robust memory management and leak prevention.
