"""
Configuration Migration Utility

This script helps migrate from the old preferences system to the new dynamic configuration system.
It can be run standalone or integrated into the application startup process.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import shutil
from datetime import datetime

from config.dynamic_config import ConfigurationManager, ConfigMigrator


class PreferencesMigrationTool:
    """Tool for migrating old preferences to new dynamic configuration system"""
    
    def __init__(self, app_dir: Optional[str] = None):
        """
        Initialize migration tool.
        
        Args:
            app_dir: Application directory path (uses default if None)
        """
        if app_dir:
            self.app_dir = Path(app_dir)
        else:
            self.app_dir = Path.home() / "ProjectBudgetinator"
        
        self.config_dir = self.app_dir / "config"
        self.old_preferences_file = self.config_dir / "user.config.json"
        self.new_preferences_file = self.config_dir / "user.config.json"
        self.backup_dir = self.config_dir / "migration_backups"
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Migration status
        self.migration_performed = False
        self.backup_created = False
    
    def needs_migration(self) -> bool:
        """
        Check if migration is needed.
        
        Returns:
            True if migration is needed, False otherwise
        """
        if not self.old_preferences_file.exists():
            return False
        
        try:
            with open(self.old_preferences_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Check if it's already migrated (has config_version 2.0+)
            version = config.get('config_version', '1.0')
            if version and version >= '2.0':
                return False
            
            # Check for old format indicators
            old_indicators = [
                'startup_diagnostics',  # Old key name
                not config.get('config_version'),  # Missing version
                not config.get('last_updated')  # Missing timestamp
            ]
            
            return any(old_indicators)
            
        except (json.JSONDecodeError, OSError) as e:
            self.logger.warning(f"Could not check migration status: {e}")
            return False
    
    def create_backup(self) -> bool:
        """
        Create backup of current configuration.
        
        Returns:
            True if backup successful, False otherwise
        """
        try:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            if self.old_preferences_file.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = self.backup_dir / f"user.config_pre_migration_{timestamp}.json"
                
                shutil.copy2(self.old_preferences_file, backup_file)
                self.backup_created = True
                self.logger.info(f"Backup created: {backup_file}")
                return True
            
            return True  # No file to backup is OK
            
        except Exception as e:
            self.logger.error(f"Failed to create backup: {e}")
            return False
    
    def migrate_preferences(self) -> bool:
        """
        Perform the migration from old to new format.
        
        Returns:
            True if migration successful, False otherwise
        """
        try:
            # Check if migration is needed
            if not self.needs_migration():
                self.logger.info("No migration needed")
                return True
            
            # Create backup first
            if not self.create_backup():
                self.logger.error("Failed to create backup, aborting migration")
                return False
            
            # Load old configuration
            with open(self.old_preferences_file, 'r', encoding='utf-8') as f:
                old_config = json.load(f)
            
            self.logger.info(f"Migrating configuration from version {old_config.get('config_version', '1.0')}")
            
            # Apply migration rules
            migrated_config = ConfigMigrator.migrate_config(old_config.copy())
            
            # Create configuration manager to validate and save
            config_manager = ConfigurationManager(str(self.config_dir))
            
            # Import the migrated configuration
            temp_file = self.config_dir / "temp_migration.json"
            try:
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(migrated_config, f, indent=4, default=str)
                
                success = config_manager.import_config(str(temp_file))
                
                # Clean up temp file
                if temp_file.exists():
                    temp_file.unlink()
                
                if success:
                    self.migration_performed = True
                    self.logger.info("Migration completed successfully")
                    return True
                else:
                    self.logger.error("Migration validation failed")
                    return False
                    
            except Exception as e:
                # Clean up temp file on error
                if temp_file.exists():
                    temp_file.unlink()
                raise e
                
        except Exception as e:
            self.logger.error(f"Migration failed: {e}")
            return False
    
    def rollback_migration(self) -> bool:
        """
        Rollback migration by restoring from backup.
        
        Returns:
            True if rollback successful, False otherwise
        """
        try:
            if not self.backup_created:
                self.logger.error("No backup available for rollback")
                return False
            
            # Find most recent backup
            backup_files = list(self.backup_dir.glob("user.config_pre_migration_*.json"))
            if not backup_files:
                self.logger.error("No backup files found")
                return False
            
            # Use most recent backup
            latest_backup = max(backup_files, key=lambda x: x.stat().st_mtime)
            
            # Restore backup
            shutil.copy2(latest_backup, self.old_preferences_file)
            
            self.logger.info(f"Migration rolled back from backup: {latest_backup}")
            return True
            
        except Exception as e:
            self.logger.error(f"Rollback failed: {e}")
            return False
    
    def get_migration_report(self) -> Dict[str, Any]:
        """
        Get detailed migration report.
        
        Returns:
            Dictionary with migration status and details
        """
        report = {
            "migration_needed": self.needs_migration(),
            "migration_performed": self.migration_performed,
            "backup_created": self.backup_created,
            "old_file_exists": self.old_preferences_file.exists(),
            "new_file_exists": self.new_preferences_file.exists(),
            "backup_dir": str(self.backup_dir),
            "backup_files": []
        }
        
        # List backup files
        if self.backup_dir.exists():
            backup_files = list(self.backup_dir.glob("*.json"))
            report["backup_files"] = [str(f) for f in backup_files]
        
        # Get configuration versions
        try:
            if self.old_preferences_file.exists():
                with open(self.old_preferences_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                report["current_version"] = config.get("config_version", "unknown")
        except Exception:
            report["current_version"] = "error_reading"
        
        return report
    
    def cleanup_old_backups(self, keep_count: int = 5) -> bool:
        """
        Clean up old backup files, keeping only the most recent ones.
        
        Args:
            keep_count: Number of backup files to keep
            
        Returns:
            True if cleanup successful, False otherwise
        """
        try:
            if not self.backup_dir.exists():
                return True
            
            # Get all backup files
            backup_files = list(self.backup_dir.glob("user.config_pre_migration_*.json"))
            
            if len(backup_files) <= keep_count:
                return True
            
            # Sort by modification time (newest first)
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Remove old files
            for old_file in backup_files[keep_count:]:
                old_file.unlink()
                self.logger.info(f"Removed old backup: {old_file}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Backup cleanup failed: {e}")
            return False


def run_migration_check() -> Dict[str, Any]:
    """
    Run migration check and return status report.
    
    Returns:
        Migration status report
    """
    migration_tool = PreferencesMigrationTool()
    
    report = migration_tool.get_migration_report()
    
    if report["migration_needed"]:
        print("🔄 Configuration migration needed")
        print(f"Current version: {report.get('current_version', 'unknown')}")
        
        # Perform migration
        if migration_tool.migrate_preferences():
            print("✅ Migration completed successfully")
            report["migration_result"] = "success"
        else:
            print("❌ Migration failed")
            report["migration_result"] = "failed"
    else:
        print("✅ No migration needed - configuration is up to date")
        report["migration_result"] = "not_needed"
    
    return report


def run_interactive_migration():
    """Run interactive migration with user prompts"""
    print("ProjectBudgetinator Configuration Migration Tool")
    print("=" * 50)
    
    migration_tool = PreferencesMigrationTool()
    report = migration_tool.get_migration_report()
    
    print(f"Configuration Status:")
    print(f"  Migration needed: {report['migration_needed']}")
    print(f"  Current version: {report.get('current_version', 'unknown')}")
    print(f"  Backup files: {len(report['backup_files'])}")
    
    if not report["migration_needed"]:
        print("\n✅ Configuration is already up to date!")
        return
    
    print(f"\n🔄 Migration is needed to update your configuration.")
    print(f"This will:")
    print(f"  • Create a backup of your current settings")
    print(f"  • Update configuration format to version 2.0")
    print(f"  • Add new configuration options with defaults")
    print(f"  • Preserve all your existing preferences")
    
    response = input("\nProceed with migration? (y/n): ").lower().strip()
    
    if response not in ['y', 'yes']:
        print("Migration cancelled.")
        return
    
    print("\n🔄 Starting migration...")
    
    if migration_tool.migrate_preferences():
        print("✅ Migration completed successfully!")
        
        # Show updated report
        updated_report = migration_tool.get_migration_report()
        print(f"New version: {updated_report.get('current_version', 'unknown')}")
        
        # Cleanup old backups
        if input("\nCleanup old backup files? (y/n): ").lower().strip() in ['y', 'yes']:
            migration_tool.cleanup_old_backups()
            print("🧹 Old backups cleaned up")
        
    else:
        print("❌ Migration failed!")
        
        if input("\nWould you like to see the error log? (y/n): ").lower().strip() in ['y', 'yes']:
            # This would show log details in a real implementation
            print("Check the application logs for detailed error information.")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        run_interactive_migration()
    else:
        # Run automatic migration check
        result = run_migration_check()
        
        # Exit with appropriate code
        if result.get("migration_result") == "failed":
            sys.exit(1)
        else:
            sys.exit(0)
