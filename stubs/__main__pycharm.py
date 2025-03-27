# # The generator3 module can be downloaded from this repository:
# # https://github.com/JetBrains/intellij-community/tree/master/python/helpers/generator3


import os
import gi

import sys

from generator3.constants import Timer
from generator3.core import (
    GenerationStatus,
    generate_skeleton,
    build_cache_dir_path,
)

_root = os.path.dirname(os.path.dirname(__file__))
_out_dir = os.path.join(_root, ".venv", "lib", "gimp", "stubs")
_site_dir = os.path.join(_root, ".venv", "lib", "python3.10", "site-packages")


class CustomGenerator(object):
    def __init__(self, out_dir: str, roots: list[str] = None):
        """
        :param str out_dir:
            The output directory where the generated skeletons will be written to.

            - The cache directory is created as the sibling of this output directory.

        :param list[str] roots:
            A list of paths to the directories where the generator should look for the modules.
        """

        self.out_dir = out_dir.rstrip(os.path.sep)
        # TODO make cache directory configurable via CLI
        self.cache_dir = os.path.join(os.path.dirname(self.out_dir), "cache")
        self.roots = roots
        self.out_state_json = {"sdk_skeletons": {}}

    def process_module(self, mod_name: str) -> GenerationStatus:
        mod_path = None
        cache_dir = build_cache_dir_path(self.cache_dir, mod_name, mod_path)

        return generate_skeleton(
            name=mod_name,
            mod_file_name=None,
            mod_cache_dir=cache_dir,
            output_dir=self.out_dir,
        )

    def generate(self, namespace: str):
        print("Generating module: {}".format(namespace))
        timer = Timer()
        mod_name = "gi.repository." + namespace
        if self.process_module(mod_name) == GenerationStatus.FAILED:
            sys.exit(1)

        print("Generated module: {} in {} ms".format(namespace, timer.elapsed()))
        print("-----------------------------")


def stub_gen_all(generator: SkeletonGenerator):
    # generator = SkeletonGenerator(
    #     output_dir=_out_path,
    #     roots=target_roots,
    #     state_json=None,
    #     write_state_json=False,
    # )

    timer = Timer()
    generator.discover_and_process_all_modules()
    print("Generation completed in {} ms".format(timer.elapsed()))


MOD_LIST: list[(str, str)] = [
    # 'AppStreamGlib', "1.0"),
    ("Atk", "1.0"),
    ("Babl", "0.1"),
    # ("DBus", "1.0"),
    # ("DBusGLib", "1.0"),
    # ("GDesktopEnums", "3.0"),
    ("GExiv2", "0.10"),
    # ("GIRepository", "2.0"),
    # ("GL", "1.0"),
    ("GLib", "2.0"),
    ("GModule", "2.0"),
    ("GObject", "2.0"),
    ("Gdk", "3.0"),
    ("GdkPixbuf", "2.0"),
    ("GdkPixdata", "2.0"),
    ("Gegl", "0.4"),
    ("Gimp", "3.0"),
    ("GimpUi", "3.0"),
    ("Gio", "2.0"),
    ("Gtk", "3.0"),
    # ("HarfBuzz", "0.0"),
    # ("Json", "1.0"),
    # ("Libproxy", "1.0"),
    # ("MyPaint", "1.6"),
    ("Pango", "1.0"),
    # ("PangoCairo", "1.0"),
    # ("PangoFT2", "1.0"),
    # ("PangoFc", "1.0"),
    # ("PangoOT", "1.0"),
    # ("Poppler", "0.18"),
    # ("Rsvg", "2.0"),
    # ("Vulkan", "1.0"),
    # ("cairo", "1.0"),
    ("fontconfig", "2.0"),
    ("freetype2", "2.0"),
    # ("libxml2", "2.0"),
    # ("win32", "1.0"),
    # ("xfixes", "4.0"),
    # ("xft", "2.0"),
    # ("xlib", "2.0"),
    # ("xrandr", "1.3"),
]


def main():
    gen = CustomGenerator(out_dir=_out_dir)

    for namespace, version in MOD_LIST:
        gi.require_version(namespace, version)
        gen.generate(namespace)

        source_file = os.path.join(_out_dir, "gi", "repository", namespace + ".py")
        target_file = os.path.join(_site_dir, "gi", "repository", namespace + ".py")

        os.system(f"cp '{source_file}' '{target_file}'")


main()
