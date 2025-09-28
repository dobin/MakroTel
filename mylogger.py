import time


class MyLogger:
    def __init__(self):
        self.file = open("makrotel.log", "a")

    def log(self, message):
        self.file.write(f"{time.ctime()}: {message}\n")
        self.file.flush()

myLogger = MyLogger()

