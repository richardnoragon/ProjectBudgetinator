# version.py

__version__ = "1.0.0"
__schema__ = "v1"

def get_version():
    return __version__

def get_schema():
    return __schema__

def full_version_string():
    return f"App Version {__version__} (Schema: {__schema__})"
