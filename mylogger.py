import time

from config import *

class MyLogger:
    def __init__(self):
        self.file = open("makrotel.log", "w")

    def log(self, message):
        log = f"{time.ctime()}: {message}"
        if PROG_MODE == "minitel":
            print(log)
        else:
            self.file.write(log + "\n")
            self.file.flush()

    def set_mode(self, mode: str):
        self.mode = mode

myLogger = MyLogger()

