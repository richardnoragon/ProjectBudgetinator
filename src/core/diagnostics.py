"""
Diagnostic system for checking application state and configuration.
"""
import os
from pathlib import Path
import json
from utils.config_utils import get_app_directory
from utils.dialog_utils import show_error
from version import full_version_string


def run_directory_check():
    """Check required directories and their status."""
    base_dir = get_app_directory()
    
    directories = {
        "workbooks": os.path.join(base_dir, "workbooks"),
        "logs/system": os.path.join(base_dir, "logs", "system"),
        "logs/user_actions": os.path.join(base_dir, "logs", "user_actions"),
        "logs/comparisons/snapshots": os.path.join(
            base_dir, "logs", "comparisons", "snapshots"
        ),
        "config": os.path.join(base_dir, "config"),
        "backups": os.path.join(base_dir, "backups"),
        "templates": os.path.join(base_dir, "templates")
    }
    
    results = {}
    for name, path in directories.items():
        exists = os.path.exists(path)
        writable = exists and os.access(path, os.W_OK)
        results[name] = {
            "exists": exists,
            "writable": writable,
            "path": path
        }
    
    return results


def run_config_check():
    """Check configuration files and their validity."""
    config_dir = os.path.join(get_app_directory(), "config")
    config_files = {
        "user.config.json": {
            "required_fields": ["theme", "welcome_screen", "startup_diagnostic"]
        },
        "backup.config.json": {
            "required_fields": ["frequency", "keep_versions"]
        },
        "diagnostic.config.json": {
            "required_fields": ["debug_mode", "log_level"]
        }
    }
    
    results = {}
    for filename, info in config_files.items():
        filepath = os.path.join(config_dir, filename)
        exists = os.path.exists(filepath)
        valid = False
        missing_fields = []
        
        if exists:
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                missing_fields = [
                    field for field in info["required_fields"]
                    if field not in data
                ]
                valid = not missing_fields
            except Exception as e:
                valid = False
                missing_fields = ["Invalid JSON format"]
        
        results[filename] = {
            "exists": exists,
            "valid": valid,
            "missing_fields": missing_fields
        }
    
    return results


def run_log_check():
    """Check log files integrity and backup status."""
    log_dir = os.path.join(get_app_directory(), "logs")
    results = {
        "system_logs": check_log_directory(os.path.join(log_dir, "system")),
        "user_logs": check_log_directory(os.path.join(log_dir, "user_actions")),
        "comparison_logs": check_log_directory(
            os.path.join(log_dir, "comparisons", "snapshots")
        )
    }
    return results


def check_log_directory(directory):
    """Check a specific log directory for valid log files."""
    if not os.path.exists(directory):
        return {
            "status": "missing",
            "files": [],
            "errors": ["Directory does not exist"]
        }

    log_files = []
    errors = []
    
    for filename in os.listdir(directory):
        if not filename.endswith('.log'):
            continue
            
        filepath = os.path.join(directory, filename)
        try:
            # Basic log file validation
            with open(filepath, 'r') as f:
                first_line = f.readline().strip()
                if not first_line or 'ERROR' in first_line:
                    errors.append(f"Invalid log format in {filename}")
                else:
                    log_files.append(filename)
        except Exception as e:
            errors.append(f"Error reading {filename}: {str(e)}")
    
    return {
        "status": "ok" if not errors else "warning",
        "files": log_files,
        "errors": errors
    }


def get_diagnostic_summary():
    """Get a complete diagnostic summary of the application state."""
    version_info = full_version_string()
    dir_check = run_directory_check()
    config_check = run_config_check()
    log_check = run_log_check()
    
    # Process directory check
    dir_status = []
    for name, info in dir_check.items():
        if not info["exists"]:
            dir_status.append(f"❌ {name:<20} …missing")
        elif not info["writable"]:
            dir_status.append(f"⚠️  {name:<20} …not writable")
        else:
            dir_status.append(f"✅ {name:<20} …ready")
    
    # Process config check
    config_status = []
    for filename, info in config_check.items():
        if not info["exists"]:
            config_status.append(f"❌ {filename:<20} …missing")
        elif not info["valid"]:
            fields = ", ".join(info["missing_fields"])
            config_status.append(
                f"⚠️  {filename:<20} …invalid (missing: {fields})"
            )
        else:
            config_status.append(f"✅ {filename:<20} …valid")
    
    # Process log check
    log_status = []
    for category, info in log_check.items():
        if info["status"] == "missing":
            log_status.append(f"❌ {category:<20} …directory missing")
        elif info["errors"]:
            log_status.append(
                f"⚠️  {category:<20} …warnings ({len(info['errors'])})"
            )
        else:
            log_status.append(f"✅ {category:<20} …valid")
    
    # Compile complete diagnostic report
    report = {
        "Directory Check": "\n".join(dir_status),
        "Config File Check": "\n".join(config_status),
        "Log Integrity": "\n".join(log_status),
        "Version Info": version_info,
        "Summary": get_diagnostic_conclusion(dir_check, config_check, log_check)
    }
    
    return report


def _check_directories(dir_check):
    """Check directory status and return any errors and warnings."""
    errors = []
    warnings = []
    
    for name, info in dir_check.items():
        if not info["exists"]:
            errors.append(f"Missing directory: {name}")
        elif not info["writable"]:
            warnings.append(f"Directory not writable: {name}")
    
    return errors, warnings


def _check_configs(config_check):
    """Check configuration files and return any errors and warnings."""
    errors = []
    warnings = []
    
    for filename, info in config_check.items():
        if not info["exists"]:
            errors.append(f"Missing config: {filename}")
        elif not info["valid"]:
            warnings.append(
                f"Invalid config {filename}: "
                f"{', '.join(info['missing_fields'])}"
            )
    
    return errors, warnings


def _check_logs(log_check):
    """Check log status and return any errors and warnings."""
    errors = []
    warnings = []
    
    for category, info in log_check.items():
        if info["status"] == "missing":
            errors.append(f"Missing log directory: {category}")
        elif info["errors"]:
            warnings.extend(info["errors"])
    
    return errors, warnings


def _format_diagnostic_message(errors, warnings):
    """Format the diagnostic conclusion message."""
    if errors:
        msg = (
            f"Found {len(errors)} error(s) and {len(warnings)} warning(s).\n"
            "⚠️  Some errors require immediate attention!\n\n"
            f"Errors:\n{chr(10).join('- ' + e for e in errors)}"
        )
        if warnings:
            msg += f"\n\nWarnings:\n{chr(10).join('- ' + w for w in warnings)}"
    elif warnings:
        msg = (
            f"System operational with {len(warnings)} warning(s).\n"
            "⚠️  Review warnings at your convenience.\n\n"
            f"Warnings:\n{chr(10).join('- ' + w for w in warnings)}"
        )
    else:
        msg = "✅ All systems operational.\nNo errors or warnings detected."
    
    return msg


def get_diagnostic_conclusion(dir_check, config_check, log_check):
    """Generate a conclusion based on diagnostic results."""
    dir_errors, dir_warnings = _check_directories(dir_check)
    config_errors, config_warnings = _check_configs(config_check)
    log_errors, log_warnings = _check_logs(log_check)
    
    all_errors = dir_errors + config_errors + log_errors
    all_warnings = dir_warnings + config_warnings + log_warnings
    
    return _format_diagnostic_message(all_errors, all_warnings)
