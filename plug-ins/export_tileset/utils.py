import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp, Gio
from datetime import datetime


def get_pot_size(x: int) -> int:
    """
    Get the next power of two size for a given dimension.
    """

    if x == 0:
        return 1
    return 1 << (x - 1).bit_length()


class ProcessTimer:
    def __init__(self):
        self.start = datetime.now()

    def end(self, msg: str):
        end = datetime.now()
        elapsed = end - self.start
        seconds = round(elapsed.total_seconds(), 1)
        Gimp.message(f"{msg} in {seconds}s.")