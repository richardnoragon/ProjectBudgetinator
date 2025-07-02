# version.py
"""
version.py

Provides version and schema information for ProjectBudgetinator.
"""
# version.py

__version__ = "1.0.0"
__schema__ = "v1"

def get_version():
    """
    Return the current application version string.
    """
    return __version__

def get_schema():
    """
    Return the current schema version string.
    """
    return __schema__

def full_version_string():
    """
    Return a formatted string with both app version and schema version.
    """
    return f"App Version {__version__} (Schema: {__schema__})"
