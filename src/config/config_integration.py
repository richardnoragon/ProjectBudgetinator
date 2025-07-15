"""
Dynamic Configuration Integration Module

This module provides integration points for the new dynamic configuration system
with the existing ProjectBudgetinator application.
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any, Union
import atexit

from config.dynamic_config import ConfigurationManager, UserConfig
from utils.config_migration import PreferencesMigrationTool


class ConfigurationIntegration:
    """
    Main integration class for dynamic configuration system.
    
    This class serves as the primary interface between the application
    and the new configuration system.
    """
    
    _instance: Optional['ConfigurationIntegration'] = None
    _config_manager: Optional[ConfigurationManager] = None
    _config: Optional[UserConfig] = None
    
    def __init__(self, app_dir: Optional[str] = None):
        """
        Initialize configuration integration.
        
        Args:
            app_dir: Application directory path
        """
        self.app_dir = Path(app_dir) if app_dir else Path.home() / "ProjectBudgetinator"
        self.config_dir = self.app_dir / "config"
        self.logger = logging.getLogger(__name__)
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize configuration manager
        self._config_manager = ConfigurationManager(str(self.config_dir))
        
        # Run migration if needed
        self._run_migration_if_needed()
        
        # Load configuration
        self._load_configuration()
        
        # Register cleanup
        atexit.register(self.cleanup)
    
    @classmethod
    def get_instance(cls, app_dir: Optional[str] = None) -> 'ConfigurationIntegration':
        """
        Get singleton instance of configuration integration.
        
        Args:
            app_dir: Application directory path (only used on first call)
            
        Returns:
            ConfigurationIntegration instance
        """
        if cls._instance is None:
            cls._instance = cls(app_dir)
        return cls._instance
    
    def _run_migration_if_needed(self) -> bool:
        """
        Run configuration migration if needed.
        
        Returns:
            True if migration successful or not needed, False otherwise
        """
        try:
            migration_tool = PreferencesMigrationTool(str(self.app_dir))
            
            if migration_tool.needs_migration():
                self.logger.info("Running configuration migration...")
                
                if migration_tool.migrate_preferences():
                    self.logger.info("Configuration migration completed successfully")
                    return True
                else:
                    self.logger.error("Configuration migration failed")
                    return False
            else:
                self.logger.debug("No configuration migration needed")
                return True
                
        except Exception as e:
            self.logger.error(f"Migration check failed: {e}")
            return False
    
    def _load_configuration(self) -> bool:
        """
        Load configuration from file.
        
        Returns:
            True if load successful, False otherwise
        """
        try:
            self._config = self._config_manager.load_config()
            
            if self._config:
                self.logger.info("Configuration loaded successfully")
                return True
            else:
                self.logger.warning("Failed to load configuration, using defaults")
                self._config = UserConfig()  # Use defaults
                return False
                
        except Exception as e:
            self.logger.error(f"Configuration load failed: {e}")
            self._config = UserConfig()  # Use defaults
            return False
    
    def get_config(self) -> UserConfig:
        """
        Get current configuration.
        
        Returns:
            UserConfig instance
        """
        if self._config is None:
            self._load_configuration()
        return self._config
    
    def save_config(self) -> bool:
        """
        Save current configuration to file.
        
        Returns:
            True if save successful, False otherwise
        """
        try:
            if self._config and self._config_manager:
                return self._config_manager.save_config(self._config)
            return False
            
        except Exception as e:
            self.logger.error(f"Configuration save failed: {e}")
            return False
    
    def update_config(self, updates: Dict[str, Any]) -> bool:
        """
        Update configuration with new values.
        
        Args:
            updates: Dictionary of configuration updates
            
        Returns:
            True if update successful, False otherwise
        """
        try:
            if self._config is None:
                self._load_configuration()
            
            # Apply updates
            for key, value in updates.items():
                if hasattr(self._config, key):
                    setattr(self._config, key, value)
                else:
                    self.logger.warning(f"Unknown configuration key: {key}")
            
            # Save updated configuration
            return self.save_config()
            
        except Exception as e:
            self.logger.error(f"Configuration update failed: {e}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """
        Reset configuration to default values.
        
        Returns:
            True if reset successful, False otherwise
        """
        try:
            self._config = UserConfig()
            return self.save_config()
            
        except Exception as e:
            self.logger.error(f"Configuration reset failed: {e}")
            return False
    
    def import_config_file(self, file_path: str) -> bool:
        """
        Import configuration from file.
        
        Args:
            file_path: Path to configuration file
            
        Returns:
            True if import successful, False otherwise
        """
        try:
            if self._config_manager.import_config(file_path):
                self._load_configuration()  # Reload after import
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Configuration import failed: {e}")
            return False
    
    def export_config_file(self, file_path: str) -> bool:
        """
        Export configuration to file.
        
        Args:
            file_path: Path to export file
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            if self._config_manager:
                return self._config_manager.export_config(file_path)
            return False
            
        except Exception as e:
            self.logger.error(f"Configuration export failed: {e}")
            return False
    
    def validate_config(self) -> bool:
        """
        Validate current configuration.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        try:
            if self._config_manager and self._config:
                return self._config_manager.validate_config(self._config.model_dump())
            return False
            
        except Exception as e:
            self.logger.error(f"Configuration validation failed: {e}")
            return False
    
    def get_diagnostics_config(self) -> Dict[str, Any]:
        """
        Get diagnostics-related configuration.
        
        Returns:
            Dictionary with diagnostics configuration
        """
        config = self.get_config()
        return {
            "level": config.diagnostics.level,
            "enabled": config.diagnostics.enabled,
            "file_enabled": config.diagnostics.file_enabled,
            "detailed_errors": config.diagnostics.detailed_errors
        }
    
    def get_performance_config(self) -> Dict[str, Any]:
        """
        Get performance-related configuration.
        
        Returns:
            Dictionary with performance configuration
        """
        config = self.get_config()
        return {
            "cache_enabled": config.performance.cache_enabled,
            "cache_size_mb": config.performance.cache_size_mb,
            "batch_size": config.performance.batch_size,
            "timeout_seconds": config.performance.timeout_seconds,
            "max_memory_mb": config.performance.max_memory_mb
        }
    
    def get_file_locations_config(self) -> Dict[str, Any]:
        """
        Get file locations configuration.
        
        Returns:
            Dictionary with file locations
        """
        config = self.get_config()
        return {
            "last_excel_dir": config.file_locations.last_excel_dir,
            "last_export_dir": config.file_locations.last_export_dir,
            "backup_dir": config.file_locations.backup_dir,
            "template_dir": config.file_locations.template_dir
        }
    
    def update_last_excel_dir(self, directory: str) -> bool:
        """
        Update last Excel directory.
        
        Args:
            directory: Directory path
            
        Returns:
            True if update successful, False otherwise
        """
        return self.update_config({"file_locations.last_excel_dir": directory})
    
    def update_last_export_dir(self, directory: str) -> bool:
        """
        Update last export directory.
        
        Args:
            directory: Directory path
            
        Returns:
            True if update successful, False otherwise
        """
        return self.update_config({"file_locations.last_export_dir": directory})
    
    def is_feature_enabled(self, feature_name: str) -> bool:
        """
        Check if a specific feature is enabled.
        
        Args:
            feature_name: Name of the feature to check
            
        Returns:
            True if feature is enabled, False otherwise
        """
        config = self.get_config()
        
        feature_map = {
            "auto_backup": config.advanced.auto_backup,
            "startup_diagnostics": config.diagnostics.enabled,
            "caching": config.performance.cache_enabled,
            "detailed_errors": config.diagnostics.detailed_errors,
            "file_logging": config.diagnostics.file_enabled
        }
        
        return feature_map.get(feature_name, False)
    
    def get_theme(self) -> str:
        """
        Get current theme setting.
        
        Returns:
            Theme name
        """
        config = self.get_config()
        return config.display.theme.value
    
    def set_theme(self, theme: str) -> bool:
        """
        Set theme.
        
        Args:
            theme: Theme name (light, dark, auto)
            
        Returns:
            True if set successful, False otherwise
        """
        valid_themes = ["light", "dark", "auto"]
        if theme not in valid_themes:
            self.logger.error(f"Invalid theme: {theme}. Valid themes: {valid_themes}")
            return False
        
        return self.update_config({"display.theme": theme})
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            if self._config:
                self.save_config()
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")


# Convenience functions for easy integration
def get_config() -> UserConfig:
    """Get current configuration"""
    return ConfigurationIntegration.get_instance().get_config()


def save_config() -> bool:
    """Save current configuration"""
    return ConfigurationIntegration.get_instance().save_config()


def update_config(updates: Dict[str, Any]) -> bool:
    """Update configuration with new values"""
    return ConfigurationIntegration.get_instance().update_config(updates)


def is_feature_enabled(feature_name: str) -> bool:
    """Check if a feature is enabled"""
    return ConfigurationIntegration.get_instance().is_feature_enabled(feature_name)


def get_diagnostics_config() -> Dict[str, Any]:
    """Get diagnostics configuration"""
    return ConfigurationIntegration.get_instance().get_diagnostics_config()


def get_performance_config() -> Dict[str, Any]:
    """Get performance configuration"""
    return ConfigurationIntegration.get_instance().get_performance_config()


def get_file_locations_config() -> Dict[str, Any]:
    """Get file locations configuration"""
    return ConfigurationIntegration.get_instance().get_file_locations_config()


# Migration utilities for existing code
class LegacyConfigAdapter:
    """
    Adapter to help existing code work with new configuration system.
    
    This provides compatibility methods that match the old preferences interface.
    """
    
    def __init__(self):
        self.config_integration = ConfigurationIntegration.get_instance()
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """
        Get preference value using legacy key format.
        
        Args:
            key: Preference key in old format
            default: Default value if not found
            
        Returns:
            Preference value
        """
        config = self.config_integration.get_config()
        
        # Map old keys to new structure
        key_mapping = {
            "theme": config.display.theme.value,
            "startup_diagnostics": config.diagnostics.enabled,
            "cache_enabled": config.performance.cache_enabled,
            "last_excel_directory": config.file_locations.last_excel_dir,
            "last_export_directory": config.file_locations.last_export_dir,
            "auto_backup": config.advanced.auto_backup,
            "backup_count": config.advanced.backup_count,
            "detailed_errors": config.diagnostics.detailed_errors
        }
        
        return key_mapping.get(key, default)
    
    def set_preference(self, key: str, value: Any) -> bool:
        """
        Set preference value using legacy key format.
        
        Args:
            key: Preference key in old format
            value: Value to set
            
        Returns:
            True if set successful, False otherwise
        """
        # Map old keys to new structure
        new_key_mapping = {
            "theme": "display.theme",
            "startup_diagnostics": "diagnostics.enabled",
            "cache_enabled": "performance.cache_enabled",
            "last_excel_directory": "file_locations.last_excel_dir",
            "last_export_directory": "file_locations.last_export_dir",
            "auto_backup": "advanced.auto_backup",
            "backup_count": "advanced.backup_count",
            "detailed_errors": "diagnostics.detailed_errors"
        }
        
        new_key = new_key_mapping.get(key)
        if new_key:
            return self.config_integration.update_config({new_key: value})
        
        return False


# Global instance for legacy compatibility
legacy_config = LegacyConfigAdapter()
