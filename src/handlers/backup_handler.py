"""
Backup management functionality.
"""
import os
import shutil
import json
from datetime import datetime
from pathlib import Path
from ..utils.config_utils import get_app_directory, load_json_config
from ..utils.dialog_utils import show_error, show_info


def backup_file(filepath):
    """Create a backup of the specified file."""
    if not os.path.exists(filepath):
        show_error("Error", "File not found.")
        return None

    # Load backup config
    config = load_json_config("backup.config.json") or {
        "frequency": "daily",
        "keep_versions": 5
    }

    # Create backup filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = Path(filepath).name
    backup_name = f"{Path(filename).stem}_{timestamp}{Path(filename).suffix}"
    backup_dir = os.path.join(get_app_directory(), "backups")

    try:
        # Ensure backup directory exists
        os.makedirs(backup_dir, exist_ok=True)

        # Create backup
        backup_path = os.path.join(backup_dir, backup_name)
        shutil.copy2(filepath, backup_path)

        # Cleanup old backups if needed
        cleanup_old_backups(
            backup_dir,
            Path(filename).stem,
            config["keep_versions"]
        )

        show_info("Backup", "File backup created successfully.")
        return backup_path
    except Exception as e:
        show_error("Error", f"Failed to create backup: {str(e)}")
        return None


def restore_file(backup_path, restore_path=None):
    """Restore a file from backup."""
    if not os.path.exists(backup_path):
        show_error("Error", "Backup file not found.")
        return False

    try:
        if not restore_path:
            # If no restore path specified, restore to original location
            restore_path = os.path.join(
                os.path.dirname(backup_path),
                Path(backup_path).stem.rsplit('_', 1)[0] +
                Path(backup_path).suffix
            )

        # Create backup of current file if it exists
        if os.path.exists(restore_path):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pre_restore_backup = (
                f"{Path(restore_path).stem}_prerestore_{timestamp}"
                f"{Path(restore_path).suffix}"
            )
            pre_restore_path = os.path.join(
                os.path.dirname(restore_path),
                pre_restore_backup
            )
            shutil.copy2(restore_path, pre_restore_path)

        # Perform restore
        shutil.copy2(backup_path, restore_path)
        show_info("Restore", "File restored successfully.")
        return True
    except Exception as e:
        show_error("Error", f"Failed to restore file: {str(e)}")
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
