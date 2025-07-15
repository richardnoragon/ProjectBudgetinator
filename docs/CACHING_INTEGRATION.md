# Caching System Integration Guide

## Overview

The caching system has been implemented to significantly reduce repeated Excel file reads and improve application performance. This guide explains how to integrate the caching system into existing code.

## Key Components

### 1. CacheManager
Centralized caching system for:
- File hashes and change detection
- Excel file validation results
- Sheet names and metadata
- Partner and workpackage data extraction
- TTL-based caching with automatic cleanup

### 2. CacheAwareExcelManager
Wrapper around Excel operations with built-in caching.

### 3. ExcelService
Service layer that combines ExcelManager with caching for optimal performance.

## Quick Integration Examples

### Basic Usage

```python
from utils.cache_manager import cache_manager
from core.excel_service import ExcelService

# Use global cache manager
is_valid, error = cache_manager.validate_excel_file('file.xlsx')
sheet_names = cache_manager.get_excel_sheet_names('file.xlsx')

# Use ExcelService with caching
service = ExcelService()
partners = service.get_partner_list('file.xlsx')
workpackages = service.get_workpackage_list('file.xlsx')
```

### File Operations with Caching

```python
from core.excel_service import ExcelService

service = ExcelService()

# All operations are automatically cached
file_info = service.get_file_info('project.xlsx')
partners = service.get_partner_list('project.xlsx')
workpackages = service.get_workpackage_list('project.xlsx')

# Cache is automatically invalidated on file modifications
service.update_sheet_data('project.xlsx', 'P2 Partner', new_data)
```

### Custom Caching with Decorator

```python
from utils.cache_manager import cached_with_invalidation, CacheManager

custom_cache = CacheManager()

@cached_with_invalidation(custom_cache, ttl=300)  # 5 minutes TTL
def expensive_operation(file_path, param):
    # This will be cached for 5 minutes
    return perform_expensive_calculation(file_path, param)
```

## Performance Improvements

### Before (Without Caching)
```python
# Each call reads the entire file
for file in files:
    wb = load_workbook(file)
    sheets = wb.sheetnames
    # Process sheets...
    wb.close()
```

### After (With Caching)
```python
# First call reads file, subsequent calls use cache
for file in files:
    sheets = cache_manager.get_excel_sheet_names(file)  # Cached!
    # Process sheets...
```

## Cache Statistics

Monitor cache performance:

```python
# Get cache statistics
stats = cache_manager.get_cache_stats()
print(f"Cache hits: {stats}")

# ExcelService provides combined stats
service = ExcelService()
combined_stats = service.get_cache_stats()
```

## Cache Invalidation

### Automatic Invalidation
- File modifications are automatically detected
- Cache is invalidated when files are updated
- TTL-based expiration for temporary data

### Manual Invalidation

```python
# Invalidate cache for specific file
cache_manager.invalidate_cache_for_file('project.xlsx')

# Clear all caches
cleared = cache_manager.clear_cache()
print(f"Cleared {cleared} cache entries")

# Clear specific cache types
cache_manager.get_file_hash.cache_clear()
cache_manager.validate_excel_file.cache_clear()
```

## Integration with Existing Handlers

### Updated Partner Handler
```python
from core.excel_service import ExcelService

class PartnerHandler:
    def __init__(self):
        self.excel_service = ExcelService()
    
    def get_partners(self, file_path):
        # Uses caching automatically
        return self.excel_service.get_partner_list(file_path)
    
    def get_partner_data(self, file_path, partner_number):
        # Uses caching automatically
        return self.excel_service.get_partner_data(file_path, partner_number)
```

### Updated Workpackage Handler
```python
from core.excel_service import ExcelService

class WorkpackageHandler:
    def __init__(self):
        self.excel_service = ExcelService()
    
    def get_workpackages(self, file_path):
        # Uses caching automatically
        return self.excel_service.get_workpackage_list(file_path)
```

## Memory Management

### Automatic Cleanup
```python
# Context manager ensures proper cleanup
with ExcelService() as service:
    partners = service.get_partner_list('file.xlsx')
    # Cache is automatically managed
# Resources are cleaned up
```

### Manual Cleanup
```python
service = ExcelService()
try:
    # Use service...
    pass
finally:
    service.close_all_workbooks()
    service.clear_all_caches()
```

## Configuration

### Cache Directory
```python
# Custom cache directory
custom_cache = CacheManager(cache_dir="/path/to/cache")

# Use global cache manager (default)
# Cache directory: ~/ProjectBudgetinator/cache/
```

### TTL Configuration
```python
# Different TTL for different operations
@cached_with_invalidation(cache_manager, ttl=60)  # 1 minute
@cached_with_invalidation(cache_manager, ttl=300)  # 5 minutes
@cached_with_invalidation(cache_manager, ttl=3600)  # 1 hour
```

## Performance Monitoring

### Built-in Statistics
```python
# Monitor cache performance
stats = cache_manager.get_cache_stats()
print(f"File hash cache: {stats['file_hash_cache_size']}/{stats['file_hash_cache_max']}")
print(f"Validation cache: {stats['validation_cache_size']}/{stats['validation_cache_max']}")

# Monitor ExcelService performance
service = ExcelService()
stats = service.get_cache_stats()
print(f"Open workbooks: {stats['open_workbooks']}")
```

## Migration Guide

### Step 1: Replace Direct Excel Operations
```python
# Before
wb = load_workbook(file_path)
sheets = wb.sheetnames
wb.close()

# After
sheets = cache_manager.get_excel_sheet_names(file_path)
```

### Step 2: Use ExcelService for Complex Operations
```python
# Before
wb = load_workbook(file_path)
partners = []
for sheet in wb.sheetnames:
    if sheet.startswith('P'):
        # Extract partner data...
wb.close()

# After
service = ExcelService()
partners = service.get_partner_list(file_path)
```

### Step 3: Add Cache Invalidation
```python
# After file modifications
service.update_sheet_data(file_path, sheet_name, new_data)
# Cache is automatically invalidated
```

## Expected Performance Gains

| Operation | Without Caching | With Caching | Improvement |
|-----------|-----------------|--------------|-------------|
| File validation | 100-500ms | 1-5ms | 95-99% |
| Sheet names | 50-200ms | 1-2ms | 95-99% |
| Partner list | 200-1000ms | 5-20ms | 90-98% |
| Workpackage list | 300-1500ms | 10-50ms | 90-97% |

## Troubleshooting

### Common Issues

1. **Cache not updating**: Ensure file modification detection is working
2. **Memory usage**: Monitor cache sizes and clear periodically
3. **Stale data**: Use TTL-based caching for frequently changing data

### Debug Commands

```python
# Check cache status
print(cache_manager.get_cache_stats())

# Clear specific caches
cache_manager.clear_cache("*.json")

# Monitor file changes
print(cache_manager.is_file_modified('file.xlsx', old_hash))
```

## Best Practices

1. **Use ExcelService** for all Excel operations
2. **Set appropriate TTL** for different data types
3. **Monitor cache statistics** regularly
4. **Invalidate caches** after file modifications
5. **Use context managers** for resource cleanup
6. **Test cache behavior** in your specific use case

## Integration Checklist

- [ ] Replace direct `load_workbook` calls with cached methods
- [ ] Update handlers to use ExcelService
- [ ] Add cache invalidation after file modifications
- [ ] Monitor cache performance
- [ ] Test with large files
- [ ] Verify memory usage improvements
