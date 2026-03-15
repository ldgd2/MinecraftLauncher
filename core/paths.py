import sys
import os

def get_resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and for PyInstaller.
    Bundled files live in _MEIPASS.
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def get_config_path():
    """
    Get path to config file (settings.json), next to the executable.
    Does NOT use _MEIPASS, so full external persistence works.
    """
    if getattr(sys, 'frozen', False):
        # running inside a PyInstaller Bundle
        base_path = os.path.dirname(sys.executable)
    else:
        # running in normal Python interpretter
        base_path = os.path.abspath(".")
        
    return os.path.join(base_path, "settings.json")
