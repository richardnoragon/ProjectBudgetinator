"""
Backup management functionality.
"""
import os
import shutil
import json
from datetime import datetime
from pathlib import Path
from utils.config_utils import get_app_directory, load_json_config
from utils.dialog_utils import show_error, show_info
from utils.security_validator import SecurityValidator, InputSanitizer
import logging

logger = logging.getLogger(__name__)


def backup_file(filepath):
    """Create a backup of the specified file with security validation."""
    try:
        # Validate and sanitize file path
        safe_filepath = SecurityValidator.validate_file_path(filepath)
        logger.info(f"Creating backup for file: {safe_filepath}")
        
        # Validate file exists and is accessible
        if not os.path.exists(safe_filepath):
            show_error("Error", "File not found.")
            logger.warning(f"Backup failed: File not found - {safe_filepath}")
            return None

        # Validate it's actually an Excel file if it has Excel extension
        if safe_filepath.lower().endswith(('.xlsx', '.xls', '.xlsm', '.xlsb')):
            is_valid, error_msg = SecurityValidator.validate_excel_file(safe_filepath)
            if not is_valid:
                show_error("Security Error", f"Cannot backup file: {error_msg}")
                logger.warning(f"Backup failed: Security validation - {error_msg}")
                return None

        # Load backup config
        config = load_json_config("backup.config.json") or {
            "frequency": "daily",
            "keep_versions": 5
        }

        # Create backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = Path(safe_filepath).name
        
        # Sanitize filename components
        safe_filename = SecurityValidator.sanitize_filename(filename)
        backup_name = f"{Path(safe_filename).stem}_{timestamp}{Path(safe_filename).suffix}"
        
        # Validate backup directory
        backup_dir = SecurityValidator.validate_directory_path(
            os.path.join(get_app_directory(), "backups"),
            create_if_missing=True
        )

        # Create backup path and validate it
        backup_path = SecurityValidator.validate_file_path(
            os.path.join(backup_dir, backup_name)
        )

        # Create backup
        shutil.copy2(safe_filepath, backup_path)
        logger.info(f"Backup created successfully: {backup_path}")

        # Cleanup old backups if needed
        cleanup_old_backups(
            backup_dir,
            Path(safe_filename).stem,
            config["keep_versions"]
        )

        show_info("Backup", "File backup created successfully.")
        return backup_path
        
    except ValueError as e:
        show_error("Security Error", f"Invalid file path: {str(e)}")
        logger.error(f"Backup failed: Security validation error - {str(e)}")
        return None
    except Exception as e:
        show_error("Error", f"Failed to create backup: {str(e)}")
        logger.error(f"Backup failed: {str(e)}")
        return None


def restore_file(backup_path, restore_path=None):
    """Restore a file from backup with security validation."""
    try:
        # Validate and sanitize backup path
        safe_backup_path = SecurityValidator.validate_file_path(backup_path)
        logger.info(f"Restoring file from backup: {safe_backup_path}")
        
        if not os.path.exists(safe_backup_path):
            show_error("Error", "Backup file not found.")
            logger.warning(f"Restore failed: Backup file not found - {safe_backup_path}")
            return False

        # Validate backup file if it's an Excel file
        if safe_backup_path.lower().endswith(('.xlsx', '.xls', '.xlsm', '.xlsb')):
            is_valid, error_msg = SecurityValidator.validate_excel_file(safe_backup_path)
            if not is_valid:
                show_error("Security Error", f"Cannot restore file: {error_msg}")
                logger.warning(f"Restore failed: Security validation - {error_msg}")
                return False

        if not restore_path:
            # If no restore path specified, restore to original location
            backup_dir = os.path.dirname(safe_backup_path)
            backup_filename = Path(safe_backup_path).name
            
            # Extract original filename (remove timestamp)
            if '_' in backup_filename:
                original_name = backup_filename.rsplit('_', 2)[0]  # Remove timestamp and extension
                original_ext = Path(backup_filename).suffix
                restore_filename = f"{original_name}{original_ext}"
            else:
                restore_filename = backup_filename
            
            # Sanitize the restore filename
            safe_restore_filename = SecurityValidator.sanitize_filename(restore_filename)
            restore_path = os.path.join(backup_dir, safe_restore_filename)

        # Validate and sanitize restore path
        safe_restore_path = SecurityValidator.validate_file_path(restore_path)

        # Create backup of current file if it exists
        if os.path.exists(safe_restore_path):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            current_filename = Path(safe_restore_path).name
            safe_current_filename = SecurityValidator.sanitize_filename(current_filename)
            
            pre_restore_backup = (
                f"{Path(safe_current_filename).stem}_prerestore_{timestamp}"
                f"{Path(safe_current_filename).suffix}"
            )
            
            pre_restore_path = SecurityValidator.validate_file_path(
                os.path.join(os.path.dirname(safe_restore_path), pre_restore_backup)
            )
            
            shutil.copy2(safe_restore_path, pre_restore_path)
            logger.info(f"Created pre-restore backup: {pre_restore_path}")

        # Perform restore
        shutil.copy2(safe_backup_path, safe_restore_path)
        logger.info(f"File restored successfully: {safe_restore_path}")
        show_info("Restore", "File restored successfully.")
        return True
        
    except ValueError as e:
        show_error("Security Error", f"Invalid file path: {str(e)}")
        logger.error(f"Restore failed: Security validation error - {str(e)}")
        return False
    except Exception as e:
        show_error("Error", f"Failed to restore file: {str(e)}")
        logger.error(f"Restore failed: {str(e)}")
        return False


def cleanup_old_backups(backup_dir, file_stem, keep_versions):
    """Remove old backup files, keeping only the specified number of versions."""
    try:
        # Get list of backup files for this file
        backup_files = []
        for filename in os.listdir(backup_dir):
            if filename.startswith(file_stem + "_"):
                backup_path = os.path.join(backup_dir, filename)
                backup_files.append((
                    backup_path,
                    os.path.getmtime(backup_path)
                ))

        # Sort by modification time (newest first)
        backup_files.sort(key=lambda x: x[1], reverse=True)

        # Remove old backups
        for backup_path, _ in backup_files[keep_versions:]:
            os.remove(backup_path)
    except Exception as e:
        show_error("Error", f"Failed to clean up old backups: {str(e)}")


def list_backups(file_stem):
    """List available backups for a file."""
    backup_dir = os.path.join(get_app_directory(), "backups")
    try:
        backups = []
        for filename in os.listdir(backup_dir):
            if filename.startswith(file_stem + "_"):
                backup_path = os.path.join(backup_dir, filename)
                backup_time = datetime.fromtimestamp(
                    os.path.getmtime(backup_path)
                )
                backups.append({
                    'path': backup_path,
                    'filename': filename,
                    'timestamp': backup_time.strftime("%Y-%m-%d %H:%M:%S"),
                    'size': os.path.getsize(backup_path)
                })

        # Sort by timestamp (newest first)
        backups.sort(key=lambda x: x['timestamp'], reverse=True)
        return backups
    except Exception as e:
        show_error("Error", f"Failed to list backups: {str(e)}")
        return []
