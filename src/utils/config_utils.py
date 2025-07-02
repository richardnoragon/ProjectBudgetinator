"""
Configuration and directory management utilities.
"""
import os
import json
from pathlib import Path
from ..utils.dialog_utils import show_error, show_info


def get_app_directory():
    """Get the application's base directory."""
    return os.path.join(str(Path.home()), "ProjectBudgetinator")


def ensure_directory_exists(path):
    """Create a directory if it doesn't exist and return True if successful."""
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        show_error("Error", f"Failed to create directory: {str(e)}")
        return False


def create_directory_structure():
    """Create the necessary directory structure and default config files."""
    base_dir = get_app_directory()
    
    directories = [
        os.path.join(base_dir, "workbooks"),
        os.path.join(base_dir, "logs", "system"),
        os.path.join(base_dir, "logs", "user_actions"),
        os.path.join(base_dir, "logs", "comparisons", "snapshots"),
        os.path.join(base_dir, "config"),
        os.path.join(base_dir, "backups"),
        os.path.join(base_dir, "templates")
    ]

    for directory in directories:
        ensure_directory_exists(directory)

    # Create default configuration files
    config_files = {
        "user.config.json": {
            "theme": "light",
            "welcome_screen": True,
            "startup_diagnostic": "verbose"
        },
        "backup.config.json": {
            "frequency": "daily",
            "keep_versions": 5
        },
        "diagnostic.config.json": {
            "debug_mode": False,
            "log_level": "INFO"
        }
    }

    config_dir = os.path.join(base_dir, "config")
    for filename, default_content in config_files.items():
        filepath = os.path.join(config_dir, filename)
        if not os.path.exists(filepath):
            try:
                with open(filepath, "w") as f:
                    json.dump(default_content, f, indent=4)
            except Exception as e:
                show_error(
                    "Error",
                    f"Failed to create config file {filename}: {str(e)}"
                )


def load_json_config(filename):
    """Load and return a JSON configuration file."""
    filepath = os.path.join(get_app_directory(), "config", filename)
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except Exception as e:
        show_error("Error", f"Failed to load {filename}: {str(e)}")
        return {}


def save_json_config(filename, config_data):
    """Save configuration data to a JSON file."""
    filepath = os.path.join(get_app_directory(), "config", filename)
    try:
        with open(filepath, "w") as f:
            json.dump(config_data, f, indent=4)
        return True
    except Exception as e:
        show_error("Error", f"Failed to save {filename}: {str(e)}")
        return False
