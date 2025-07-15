"""
Dynamic Configuration Management System

This module provides enhanced configuration management with:
- Pydantic-based validation
- JSON Schema validation
- Configuration migration
- Environment variable support
- Type safety and validation
"""

import os
import json
import logging
from enum import Enum
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import hashlib

from pydantic import BaseModel, Field, validator, ValidationError
from pydantic.env_settings import BaseSettings
import jsonschema
from dotenv import load_dotenv


class ThemeType(str, Enum):
    """Available theme options"""
    LIGHT = "light"
    DARK = "dark"


class DiagnosticLevel(str, Enum):
    """Available diagnostic levels"""
    SILENT = "silent"
    MINIMAL = "minimal"
    VERBOSE = "verbose"
    DEBUG = "debug"


class UserConfig(BaseModel):
    """
    User configuration model with validation.
    
    This model defines the structure and validation rules for user preferences.
    """
    
    # Display settings
    theme: ThemeType = Field(default=ThemeType.LIGHT, description="Application theme")
    welcome_screen: bool = Field(default=True, description="Show welcome screen on startup")
    
    # Diagnostic settings
    startup_diagnostic: DiagnosticLevel = Field(
        default=DiagnosticLevel.VERBOSE, 
        description="Level of startup diagnostics"
    )
    
    # File handling settings
    default_file_location: str = Field(
        default_factory=lambda: str(Path.home()),
        description="Default directory for file operations"
    )
    remember_last_location: bool = Field(
        default=False, 
        description="Remember last used directory"
    )
    save_location: str = Field(
        default_factory=lambda: str(Path.home()),
        description="Default directory for saving files"
    )
    
    # Advanced settings
    auto_backup: bool = Field(default=True, description="Enable automatic backups")
    backup_count: int = Field(default=5, ge=1, le=50, description="Number of backups to keep")
    max_recent_files: int = Field(default=10, ge=1, le=50, description="Number of recent files to remember")
    
    # Performance settings
    enable_caching: bool = Field(default=True, description="Enable file caching")
    cache_size_mb: int = Field(default=100, ge=10, le=1000, description="Cache size in MB")
    
    # Version for migration
    config_version: str = Field(default="2.0", description="Configuration schema version")
    last_updated: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    
    @validator('default_file_location', 'save_location')
    def validate_paths(cls, v):
        """Validate that paths exist or can be created"""
        if v and not os.path.exists(v):
            try:
                Path(v).mkdir(parents=True, exist_ok=True)
            except (OSError, PermissionError):
                # Fall back to home directory if path creation fails
                return str(Path.home())
        return v
    
    @validator('config_version')
    def validate_version(cls, v):
        """Validate version format"""
        if not v or len(v.split('.')) != 2:
            raise ValueError('Version must be in format "major.minor"')
        return v
    
    class Config:
        # Allow environment variable override
        env_prefix = 'BUDGETINATOR_'
        # Enable validation on assignment
        validate_assignment = True
        # Use enum values in JSON
        use_enum_values = True


class ConfigMigrator:
    """Handles configuration migration between versions"""
    
    MIGRATION_RULES = {
        "1.0": {
            "target_version": "2.0",
            "migrations": [
                {
                    "action": "rename_key",
                    "old_key": "startup_diagnostics",
                    "new_key": "startup_diagnostic"
                },
                {
                    "action": "add_default",
                    "key": "auto_backup",
                    "value": True
                },
                {
                    "action": "add_default",
                    "key": "backup_count",
                    "value": 5
                },
                {
                    "action": "add_default",
                    "key": "max_recent_files",
                    "value": 10
                },
                {
                    "action": "add_default",
                    "key": "enable_caching",
                    "value": True
                },
                {
                    "action": "add_default",
                    "key": "cache_size_mb",
                    "value": 100
                }
            ]
        }
    }
    
    @classmethod
    def migrate_config(cls, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Migrate configuration data to the latest version.
        
        Args:
            config_data: Raw configuration dictionary
            
        Returns:
            Migrated configuration dictionary
        """
        current_version = config_data.get("config_version", "1.0")
        
        while current_version in cls.MIGRATION_RULES:
            migration = cls.MIGRATION_RULES[current_version]
            
            # Apply migrations
            for rule in migration["migrations"]:
                if rule["action"] == "rename_key":
                    if rule["old_key"] in config_data:
                        config_data[rule["new_key"]] = config_data.pop(rule["old_key"])
                
                elif rule["action"] == "add_default":
                    if rule["key"] not in config_data:
                        config_data[rule["key"]] = rule["value"]
                
                elif rule["action"] == "remove_key":
                    config_data.pop(rule["key"], None)
            
            # Update version
            config_data["config_version"] = migration["target_version"]
            config_data["last_updated"] = datetime.now().isoformat()
            current_version = migration["target_version"]
        
        return config_data


class ConfigurationManager:
    """
    Enhanced configuration manager with validation, migration, and environment support.
    """
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_dir: Custom configuration directory path
        """
        # Load environment variables from .env file if it exists
        load_dotenv()
        
        # Setup paths
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            self.app_dir = Path.home() / "ProjectBudgetinator"
            self.config_dir = self.app_dir / "config"
        
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Current configuration
        self._config: Optional[UserConfig] = None
        self._config_file_path: Optional[Path] = None
        
    def get_config_schema(self) -> Dict[str, Any]:
        """Get JSON schema for configuration validation"""
        return UserConfig.schema()
    
    def validate_config_data(self, config_data: Dict[str, Any]) -> List[str]:
        """
        Validate configuration data against schema.
        
        Args:
            config_data: Configuration dictionary to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        try:
            schema = self.get_config_schema()
            jsonschema.validate(config_data, schema)
        except jsonschema.ValidationError as e:
            errors.append(f"Schema validation error: {e.message}")
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
        
        return errors
    
    def load_config(self, config_name: str = "user.config.json") -> UserConfig:
        """
        Load and validate configuration from file.
        
        Args:
            config_name: Configuration file name
            
        Returns:
            Validated UserConfig instance
        """
        config_path = self.config_dir / config_name
        self._config_file_path = config_path
        
        try:
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    raw_config = json.load(f)
                
                # Create backup before migration
                self._backup_config(config_path)
                
                # Migrate if needed
                migrated_config = ConfigMigrator.migrate_config(raw_config)
                
                # Validate with schema
                validation_errors = self.validate_config_data(migrated_config)
                if validation_errors:
                    self.logger.warning(f"Config validation errors: {validation_errors}")
                
                # Create Pydantic model (this will also validate and apply defaults)
                self._config = UserConfig(**migrated_config)
                
                # Save if migration occurred
                if migrated_config != raw_config:
                    self.save_config()
                    self.logger.info(f"Configuration migrated and saved to {config_path}")
                
            else:
                # Create default config
                self._config = UserConfig()
                self.save_config()
                self.logger.info(f"Created default configuration at {config_path}")
                
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            # Fall back to default configuration
            self._config = UserConfig()
            self._backup_corrupted_config(config_path)
        
        return self._config
    
    def save_config(self, config: Optional[UserConfig] = None) -> bool:
        """
        Save configuration to file.
        
        Args:
            config: Configuration to save (uses current if None)
            
        Returns:
            True if successful, False otherwise
        """
        if config:
            self._config = config
        
        if not self._config or not self._config_file_path:
            self.logger.error("No configuration to save")
            return False
        
        try:
            # Update timestamp
            self._config.last_updated = datetime.now()
            
            # Convert to dict and save
            config_dict = self._config.dict()
            
            with open(self._config_file_path, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=4, default=str)
            
            self.logger.info(f"Configuration saved to {self._config_file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")
            return False
    
    def get_config(self) -> UserConfig:
        """Get current configuration"""
        if not self._config:
            return self.load_config()
        return self._config
    
    def update_config(self, **kwargs) -> bool:
        """
        Update configuration with new values.
        
        Args:
            **kwargs: Configuration values to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self._config:
                self.load_config()
            
            # Create updated config
            current_dict = self._config.dict()
            current_dict.update(kwargs)
            
            # Validate new configuration
            updated_config = UserConfig(**current_dict)
            
            # Save if validation successful
            return self.save_config(updated_config)
            
        except ValidationError as e:
            self.logger.error(f"Configuration validation failed: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error updating config: {e}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """Reset configuration to default values"""
        try:
            self._config = UserConfig()
            return self.save_config()
        except Exception as e:
            self.logger.error(f"Error resetting config: {e}")
            return False
    
    def export_config(self, export_path: str) -> bool:
        """
        Export configuration to specified path.
        
        Args:
            export_path: Path to export configuration
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self._config:
                self.load_config()
            
            export_file = Path(export_path)
            export_file.parent.mkdir(parents=True, exist_ok=True)
            
            config_dict = self._config.dict()
            
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=4, default=str)
            
            self.logger.info(f"Configuration exported to {export_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting config: {e}")
            return False
    
    def import_config(self, import_path: str) -> bool:
        """
        Import configuration from specified path.
        
        Args:
            import_path: Path to import configuration from
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import_file = Path(import_path)
            if not import_file.exists():
                self.logger.error(f"Import file does not exist: {import_file}")
                return False
            
            with open(import_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Migrate and validate
            migrated_config = ConfigMigrator.migrate_config(config_data)
            imported_config = UserConfig(**migrated_config)
            
            return self.save_config(imported_config)
            
        except Exception as e:
            self.logger.error(f"Error importing config: {e}")
            return False
    
    def get_config_hash(self) -> str:
        """Get hash of current configuration for change detection"""
        if not self._config:
            return ""
        
        config_str = json.dumps(self._config.dict(), sort_keys=True, default=str)
        return hashlib.sha256(config_str.encode()).hexdigest()
    
    def _backup_config(self, config_path: Path) -> None:
        """Create backup of configuration file"""
        try:
            backup_dir = self.config_dir / "backups"
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{config_path.stem}_{timestamp}.bak"
            backup_path = backup_dir / backup_name
            
            if config_path.exists():
                import shutil
                shutil.copy2(config_path, backup_path)
                self.logger.info(f"Configuration backed up to {backup_path}")
                
                # Clean old backups (keep last 10)
                self._cleanup_old_backups(backup_dir, config_path.stem)
                
        except Exception as e:
            self.logger.warning(f"Could not backup config: {e}")
    
    def _backup_corrupted_config(self, config_path: Path) -> None:
        """Backup corrupted configuration file"""
        try:
            if config_path.exists():
                corrupted_dir = self.config_dir / "corrupted"
                corrupted_dir.mkdir(exist_ok=True)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                corrupted_name = f"{config_path.stem}_corrupted_{timestamp}.json"
                corrupted_path = corrupted_dir / corrupted_name
                
                import shutil
                shutil.move(str(config_path), str(corrupted_path))
                self.logger.warning(f"Corrupted config moved to {corrupted_path}")
                
        except Exception as e:
            self.logger.error(f"Could not backup corrupted config: {e}")
    
    def _cleanup_old_backups(self, backup_dir: Path, config_name: str, keep_count: int = 10) -> None:
        """Clean up old backup files"""
        try:
            pattern = f"{config_name}_*.bak"
            backup_files = list(backup_dir.glob(pattern))
            
            if len(backup_files) > keep_count:
                # Sort by modification time and remove oldest
                backup_files.sort(key=lambda x: x.stat().st_mtime)
                for old_backup in backup_files[:-keep_count]:
                    old_backup.unlink()
                    self.logger.debug(f"Removed old backup: {old_backup}")
                    
        except Exception as e:
            self.logger.warning(f"Could not cleanup old backups: {e}")


# Global configuration manager instance
_config_manager: Optional[ConfigurationManager] = None


def get_config_manager() -> ConfigurationManager:
    """Get global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigurationManager()
    return _config_manager


def get_user_config() -> UserConfig:
    """Get current user configuration"""
    return get_config_manager().get_config()


def update_user_config(**kwargs) -> bool:
    """Update user configuration with new values"""
    return get_config_manager().update_config(**kwargs)


# Environment variable utilities
def get_env_config_override() -> Dict[str, Any]:
    """
    Get configuration overrides from environment variables.
    
    Environment variables should be prefixed with BUDGETINATOR_
    Example: BUDGETINATOR_THEME=dark
    """
    overrides = {}
    prefix = "BUDGETINATOR_"
    
    for key, value in os.environ.items():
        if key.startswith(prefix):
            config_key = key[len(prefix):].lower()
            
            # Type conversion based on known fields
            if config_key in ['welcome_screen', 'remember_last_location', 'auto_backup', 'enable_caching']:
                overrides[config_key] = value.lower() in ('true', '1', 'yes', 'on')
            elif config_key in ['backup_count', 'max_recent_files', 'cache_size_mb']:
                try:
                    overrides[config_key] = int(value)
                except ValueError:
                    pass
            else:
                overrides[config_key] = value
    
    return overrides


if __name__ == "__main__":
    # Example usage and testing
    print("Dynamic Configuration System")
    print("=" * 40)
    
    # Create configuration manager
    config_mgr = ConfigurationManager()
    
    # Load configuration
    config = config_mgr.load_config()
    print(f"Loaded configuration: {config.dict()}")
    
    # Show JSON schema
    schema = config_mgr.get_config_schema()
    print(f"\nConfiguration schema: {json.dumps(schema, indent=2)}")
    
    # Test environment overrides
    env_overrides = get_env_config_override()
    if env_overrides:
        print(f"\nEnvironment overrides: {env_overrides}")
