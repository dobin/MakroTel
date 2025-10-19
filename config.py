# Screen dimensions
HEIGHT = 25

PROG_MODE = "minitel"

PAGE_ROTATION_INTERVAL = 300  # seconds
DEBUG = False

# Timing settings
REFRESH_TIME = 0.20 # seconds
CURSES_WAIT_TIME = 0.00 # seconds

def config_set_mode(mode: str):
    global PROG_MODE
    PROG_MODE = mode
    if PROG_MODE not in ["minitel", "curses"]:
        raise ValueError("Invalid PROG_MODE in config.py, must be 'minitel' or 'curses'")