# # The generator3 module can be downloaded from this repository:
# # https://github.com/JetBrains/intellij-community/tree/master/python/helpers/generator3


import os
import gi

gi.require_version("Gimp", "3.0")
gi.require_version("GimpUi", "3.0")
gi.require_version("Gtk", "3.0")


import sys
import logging

_containing_dir = os.path.dirname(os.path.abspath(__file__))
_helpers_dir = os.path.dirname(_containing_dir)

def cleanup_sys_path():
    paths = [
        root
        for root in sys.path
        if os.path.normpath(root) not in (_containing_dir, _helpers_dir)
    ]

    # paths.append(GIMP_RPATH)
    # paths.append(GIMP_LIB_PATH)
    # print("paths", paths)

    return paths


def _enable_segfault_tracebacks():
    try:
        import faulthandler

        faulthandler.enable()
    except ImportError:
        pass


def _configure_multiprocessing():
    required_start_method = os.environ.get("GENERATOR3_MULTIPROCESSING_START_METHOD")
    if required_start_method:
        import multiprocessing

        # Available only since Python 3.4
        multiprocessing.set_start_method(required_start_method)


def setup():
    from generator3.util_methods import configure_logging

    configure_logging(logging.DEBUG)
    _enable_segfault_tracebacks()
    _configure_multiprocessing()
