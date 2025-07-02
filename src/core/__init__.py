"""
Core package initialization.
"""
from .preferences import PreferencesManager, PreferencesDialog
from .diagnostics import (
    run_directory_check,
    run_config_check,
    run_log_check,
    get_diagnostic_summary
)
from .initialize import init_application, setup_logging
from .project import create_project_folder, initialize_project

__all__ = [
    'PreferencesManager',
    'PreferencesDialog',
    'run_directory_check',
    'run_config_check',
    'run_log_check',
    'get_diagnostic_summary',
    'init_application',
    'setup_logging',
    'create_project_folder',
    'initialize_project'
]
