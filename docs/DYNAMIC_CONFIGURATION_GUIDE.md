# Dynamic Configuration System Documentation

## Overview

The ProjectBudgetinator dynamic configuration system provides a robust, type-safe, and migration-friendly approach to application configuration management. This system replaces the previous JSON-based preferences with a modern Pydantic-based solution that offers validation, environment variable support, and automatic migration capabilities.

## Features

### ✅ **Type Safety & Validation**
- Pydantic models ensure configuration data integrity
- Automatic type conversion and validation
- Detailed error messages for invalid configurations

### ✅ **Migration System**
- Automatic migration from old configuration formats
- Version-based migration rules
- Backup creation before migration
- Rollback capabilities

### ✅ **Environment Variable Support**
- Override configuration with environment variables
- Support for `.env` files
- Hierarchical configuration precedence

### ✅ **Enhanced User Interface**
- Modern tabbed preferences dialog
- Real-time validation with error highlighting
- Import/export functionality
- Configuration comparison tools

### ✅ **JSON Schema Validation**
- Comprehensive JSON schema for configuration files
- External validation support
- Documentation generation capabilities

## Architecture

```
src/config/
├── dynamic_config.py          # Core configuration models and managers
├── config_integration.py      # Application integration layer
└── enhanced_preferences.py    # Enhanced UI components

config/
└── user-config-schema.json    # JSON schema definition

src/utils/
└── config_migration.py        # Migration utilities
```

## Configuration Structure

The configuration is organized into logical sections:

### Display Settings
```python
display:
  theme: "light" | "dark" | "auto"
  language: str
  font_size: int (8-20)
  window_maximized: bool
```

### Diagnostics Settings
```python
diagnostics:
  level: "DEBUG" | "INFO" | "WARNING" | "ERROR"
  enabled: bool
  file_enabled: bool
  detailed_errors: bool
```

### File Locations
```python
file_locations:
  last_excel_dir: str
  last_export_dir: str
  backup_dir: str
  template_dir: str
```

### Performance Settings
```python
performance:
  cache_enabled: bool
  cache_size_mb: int (10-1000)
  batch_size: int (100-10000)
  timeout_seconds: int (10-300)
  max_memory_mb: int (256-8192)
```

### Advanced Settings
```python
advanced:
  auto_backup: bool
  backup_count: int (1-50)
  check_updates: bool
  beta_features: bool
```

### Environment Variables
```python
environment:
  env_file_path: str
  override_from_env: bool
  env_prefix: str
```

## Usage Examples

### Basic Configuration Access

```python
from config.config_integration import get_config, update_config, is_feature_enabled

# Get current configuration
config = get_config()
print(f"Current theme: {config.display.theme}")
print(f"Cache enabled: {config.performance.cache_enabled}")

# Check if features are enabled
if is_feature_enabled("auto_backup"):
    print("Auto backup is enabled")

# Update configuration
update_config({
    "display.theme": "dark",
    "performance.cache_enabled": True
})
```

### Using the Configuration Manager Directly

```python
from config.dynamic_config import ConfigurationManager

# Initialize manager
config_manager = ConfigurationManager("./config")

# Load configuration
config = config_manager.load_config()

# Validate configuration
is_valid = config_manager.validate_config(config.model_dump())

# Save configuration
config_manager.save_config(config)
```

### Environment Variable Integration

```python
# Set environment variables
import os
os.environ["PROJECTBUDGETINATOR_THEME"] = "dark"
os.environ["PROJECTBUDGETINATOR_CACHE_ENABLED"] = "true"

# Configuration will automatically use these values
config = get_config()
print(config.display.theme)  # "dark"
print(config.performance.cache_enabled)  # True
```

### Migration Usage

```python
from utils.config_migration import PreferencesMigrationTool

# Check if migration is needed
migration_tool = PreferencesMigrationTool()
if migration_tool.needs_migration():
    print("Migration required")
    
    # Perform migration
    if migration_tool.migrate_preferences():
        print("Migration successful")
    else:
        print("Migration failed")
```

### Enhanced Preferences Dialog

```python
from gui.enhanced_preferences import EnhancedPreferencesDialog
from tkinter import Tk

# Create and show preferences dialog
root = Tk()
dialog = EnhancedPreferencesDialog(root)
root.mainloop()
```

## Environment Variables

The system supports environment variable overrides with the prefix `PROJECTBUDGETINATOR_`:

```bash
# Theme setting
PROJECTBUDGETINATOR_THEME=dark

# Performance settings
PROJECTBUDGETINATOR_CACHE_ENABLED=true
PROJECTBUDGETINATOR_CACHE_SIZE_MB=512

# Diagnostics
PROJECTBUDGETINATOR_DIAGNOSTICS_LEVEL=DEBUG
PROJECTBUDGETINATOR_DIAGNOSTICS_ENABLED=true

# File locations
PROJECTBUDGETINATOR_LAST_EXCEL_DIR=/path/to/excel/files
PROJECTBUDGETINATOR_BACKUP_DIR=/path/to/backups
```

## Configuration File Format

The configuration is stored in JSON format with full validation:

```json
{
  "config_version": "2.0",
  "last_updated": "2024-01-15T10:30:00",
  "display": {
    "theme": "dark",
    "language": "en",
    "font_size": 12,
    "window_maximized": false
  },
  "diagnostics": {
    "level": "INFO",
    "enabled": true,
    "file_enabled": true,
    "detailed_errors": false
  },
  "file_locations": {
    "last_excel_dir": "C:\\Users\\User\\Documents\\Excel",
    "last_export_dir": "C:\\Users\\User\\Documents\\Exports",
    "backup_dir": "C:\\Users\\User\\AppData\\Local\\ProjectBudgetinator\\backups",
    "template_dir": "C:\\Users\\User\\AppData\\Local\\ProjectBudgetinator\\templates"
  },
  "performance": {
    "cache_enabled": true,
    "cache_size_mb": 256,
    "batch_size": 1000,
    "timeout_seconds": 30,
    "max_memory_mb": 2048
  },
  "advanced": {
    "auto_backup": true,
    "backup_count": 10,
    "check_updates": true,
    "beta_features": false
  },
  "environment": {
    "env_file_path": "",
    "override_from_env": true,
    "env_prefix": "PROJECTBUDGETINATOR"
  }
}
```

## Migration from Legacy System

### Automatic Migration

The system automatically detects old configuration formats and migrates them:

1. **Detection**: Checks for old format indicators
2. **Backup**: Creates timestamped backup of current configuration
3. **Migration**: Applies migration rules to convert old format
4. **Validation**: Ensures migrated configuration is valid
5. **Save**: Saves new configuration with updated version

### Manual Migration

```python
from utils.config_migration import run_interactive_migration

# Run interactive migration
run_interactive_migration()
```

### Migration Rules

The migration system applies these transformations:

- `startup_diagnostics` → `diagnostics.enabled`
- Version upgrade: `1.0` → `2.0`
- Add missing fields with defaults
- Normalize file paths
- Update timestamp format

## Legacy Compatibility

For existing code that uses the old preferences system:

```python
from config.config_integration import legacy_config

# Old style access
theme = legacy_config.get_preference("theme", "light")
legacy_config.set_preference("theme", "dark")

# This automatically maps to new configuration structure
```

## Error Handling

The system provides comprehensive error handling:

### Configuration Validation Errors
```python
try:
    config = load_config()
except ValidationError as e:
    print(f"Configuration validation failed: {e}")
    # Use default configuration
    config = UserConfig()
```

### File I/O Errors
```python
try:
    config_manager.save_config(config)
except OSError as e:
    print(f"Failed to save configuration: {e}")
```

### Migration Errors
```python
migration_tool = PreferencesMigrationTool()
if not migration_tool.migrate_preferences():
    # Handle migration failure
    print("Migration failed, using defaults")
```

## Performance Considerations

### Lazy Loading
- Configuration is loaded only when first accessed
- Changes are saved immediately to prevent data loss

### Caching
- Configuration values are cached in memory
- File system access is minimized

### Validation
- Validation occurs only when configuration changes
- Schema validation is optimized for performance

## Security Considerations

### Input Validation
- All configuration values are validated against schema
- Type checking prevents injection attacks
- Path validation prevents directory traversal

### Environment Variables
- Environment variables are sanitized
- Only allowed prefixes are processed
- No sensitive data in configuration files

### File Permissions
- Configuration files use restrictive permissions
- Backup files are protected
- Temporary files are cleaned up

## Testing

### Unit Tests
```python
# Test configuration loading
def test_config_loading():
    config = UserConfig()
    assert config.display.theme == "light"
    assert config.performance.cache_enabled == True

# Test migration
def test_migration():
    migration_tool = PreferencesMigrationTool()
    assert migration_tool.needs_migration() == False
```

### Integration Tests
```python
# Test full configuration cycle
def test_config_cycle():
    # Load, modify, save, reload
    config = get_config()
    original_theme = config.display.theme
    
    update_config({"display.theme": "dark"})
    
    new_config = get_config()
    assert new_config.display.theme == "dark"
```

## Troubleshooting

### Common Issues

#### Configuration Not Loading
1. Check file permissions
2. Verify JSON syntax
3. Check migration status
4. Review error logs

#### Migration Failures
1. Ensure backup directory is writable
2. Check old configuration file format
3. Verify disk space
4. Review migration logs

#### Validation Errors
1. Check configuration against schema
2. Verify data types
3. Check value ranges
4. Review validation messages

### Debug Mode

Enable debug logging to troubleshoot issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now all configuration operations will log detailed information
```

### Configuration Diagnostics

```python
from config.config_integration import ConfigurationIntegration

integration = ConfigurationIntegration.get_instance()

# Check configuration status
if integration.validate_config():
    print("Configuration is valid")
else:
    print("Configuration has issues")

# Get diagnostic information
print(f"Config file exists: {integration.config_dir.exists()}")
print(f"Migration needed: {migration_tool.needs_migration()}")
```

## Best Practices

### Configuration Management
1. **Always validate** configuration before use
2. **Use type hints** for configuration access
3. **Handle errors gracefully** with fallback defaults
4. **Save changes immediately** to prevent data loss

### Development
1. **Use environment variables** for development settings
2. **Test migration paths** thoroughly
3. **Validate schema changes** carefully
4. **Document configuration options** clearly

### Deployment
1. **Review environment variables** before deployment
2. **Test configuration loading** in target environment
3. **Backup configuration files** before updates
4. **Monitor configuration validation** errors

## Future Enhancements

### Planned Features
- Remote configuration support
- Configuration templates
- Advanced validation rules
- Configuration diffing tools
- Cloud synchronization
- Multi-user configuration profiles

### API Extensions
- REST API for configuration management
- Configuration change notifications
- Plugin-based configuration extensions
- Advanced environment variable patterns

## Support

For issues or questions about the dynamic configuration system:

1. Check this documentation first
2. Review error logs for detailed messages
3. Use debug mode for troubleshooting
4. Check the migration status and backups
5. Refer to the JSON schema for validation details

The dynamic configuration system is designed to be robust and user-friendly. With proper usage, it should provide a seamless experience for managing application preferences and settings.
