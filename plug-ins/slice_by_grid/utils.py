import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp
from datetime import datetime


class ProcessTimer:
    def __init__(self):
        self.start = datetime.now()

    def end(self, msg: str):
        end = datetime.now()
        elapsed = end - self.start
        seconds = round(elapsed.total_seconds(), 1)
        Gimp.message(f"{msg} in {seconds}s.")
