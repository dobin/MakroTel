# Screen dimensions
WIDTH = 40
HEIGHT = 25
CHAR_BG = " "

MODE = "minitel"

DEBUG = False

# Timing settings
REFRESH_TIME = 0.20 # seconds
CURSES_WAIT_TIME = 0.01 # seconds

def config_set_mode(mode: str):
    global MODE
    MODE = mode
    if MODE not in ["minitel", "curses"]:
        raise ValueError("Invalid MODE in config.py, must be 'minitel' or 'curses'")