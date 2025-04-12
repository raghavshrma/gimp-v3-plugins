#!python3
import datetime
import os
import re

print("Enter details for the new plug-in:")


def get_input(prompt: str, regex: re.Pattern[str] = None, default: str = None) -> str:
    prompt = f"{prompt} ({default}): " if default else f"{prompt}: "

    while True:
        value = input(prompt).strip()
        if not value:
            if default:
                return default

            print("Required input.")
            continue

        if regex and not regex.match(value):
            print("Invalid input.")
            continue

        return value


print("\nPlugin Information:")
label = get_input("Label", regex=re.compile(r"^[a-zA-Z][\w\s]+$"), default="New Plugin")
binary = get_input(
    "Binary Name",
    regex=re.compile(r"^[a-z-]+$"),
    default=re.compile(r"\W+").sub("-", label.lower()),
)
description = get_input("Description", default=label)
menu_path = get_input(
    "Menu Path", regex=re.compile(r"^[a-zA-Z][\w\s/]+$"), default="Tileset/"
)

if not menu_path.endswith("/"):
    menu_path += "/"

binary_py = binary.replace("-", "_")
plugin_dir = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "plug-ins", binary_py
)
plugin_file = os.path.join(plugin_dir, f"{binary_py}.py")

if os.path.exists(plugin_file):
    override = input("Plugin already exists. Override? (y/N): ").strip().lower()
    if override != "y":
        print("Exiting.")
        exit()

os.makedirs(plugin_dir, exist_ok=True)


def write_file(title: str | None, file: str, content: str):
    with open(file, "w") as fd:
        fd.write(content)
        fd.close()
        if title:
            pretty_file = file.replace(plugin_dir, f"plug-ins/{binary_py}").lstrip("/")
            print(f"{title}: {pretty_file}")


print(f"\nPlugin Directory: {plugin_dir}")

write_file(
    "Handler",
    f"{plugin_dir}/handler.py",
    """#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp
import gimp_error

def run_one(
        procedure: Gimp.Procedure,
        run_mode: Gimp.RunMode,
        image: Gimp.Image,
        drawable: Gimp.Drawable,
        config: Gimp.ProcedureConfig,
        data):

    image.undo_group_start()

    # Add your code here.

    image.undo_group_end()
    return gimp_error.success(procedure)

# def run_all(
#         procedure: Gimp.Procedure,
#         run_mode: Gimp.RunMode,
#         image: Gimp.Image,
#         drawables: list[Gimp.Drawable],
#         config: Gimp.ProcedureConfig,
#         data):
#

# def run_any(
#         procedure: Gimp.Procedure,
#         run_mode: Gimp.RunMode,
#         image: Gimp.Image,
#         config: Gimp.ProcedureConfig,
#         data):
#
#     return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, None)

""",
)

write_file(
    None,
    f"{plugin_dir}/gimp_error.py",
    f"""#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gimp", "3.0")

from gi.repository import Gimp
from gi.repository import GLib

error_prefix="Procedure '{binary}'"

def _gimp_error(procedure: Gimp.Procedure, status, message: str):
    return procedure.new_return_values(
        status,
        GLib.Error("%s: %s" % (error_prefix, message)),
    )

def calling(procedure: Gimp.Procedure, message: str):
    return _gimp_error(procedure, Gimp.PDBStatusType.CALLING_ERROR, message)

def execution(procedure: Gimp.Procedure, message: str):
    return _gimp_error(procedure, Gimp.PDBStatusType.EXECUTION_ERROR, message)

def success(procedure: Gimp.Procedure):
    return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, None)

def cancel(procedure: Gimp.Procedure):
    return procedure.new_return_values(Gimp.PDBStatusType.CANCEL, None)
""",
)


write_file(
    None,
    f"{plugin_dir}/dialog_window.py",
    f"""#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

gi.require_version("GimpUi", "3.0")
from gi.repository import GimpUi
from gi.repository import Gtk

import gimp_error

# Change to _show if dialog is interactive
def _show(binary: str, procedure: Gimp.Procedure, config: Gimp.ProcedureConfig):
    GimpUi.init(binary)

    dialog = GimpUi.ProcedureDialog.new(procedure, config, "{label}")
    dialog.fill(None)

    # make dialogue spawn in center of screen
    dialog.set_position(Gtk.WindowPosition.CENTER)

    if dialog.run():
        dialog.destroy()
        return True, None
    else:
        dialog.destroy()
        return False, gimp_error.cancel(procedure)
""",
)

class_name = binary.title().replace("-", "")

write_file(
    "Binary",
    plugin_file,
    f"""#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gimp", "3.0")

from gi.repository import Gimp
import sys
import handler, gimp_error, dialog_window

plug_in_binary = "{binary}"
plug_in_proc = "plug-in-tlk-" + plug_in_binary

def execute(
        procedure: Gimp.Procedure,
        run_mode: Gimp.RunMode,
        image: Gimp.Image,
        drawables: list[Gimp.Drawable],
        config: Gimp.ProcedureConfig,
        data
):
    if run_mode == Gimp.RunMode.INTERACTIVE and hasattr(dialog_window, "show"):
        success, ret = dialog_window.show(plug_in_binary, procedure, config)
        if not success:
            return ret

    if hasattr(handler, 'run_any'):
        return handler.run_any(procedure, run_mode, image, config, data)

    if hasattr(handler, 'run_all'):
        return handler.run_all(procedure, run_mode, image, drawables, config, data)

    if not hasattr(handler, 'run_one'):
        return gimp_error.calling(procedure, "misconfigured plug-in. Needs at least on run method")

    if len(drawables) == 1:
        if not isinstance(drawables[0], Gimp.Layer):
            return gimp_error.calling(procedure, "works with layers only.")

        return handler.run_one(procedure, run_mode, image, drawables[0], config, data)

    return gimp_error.calling(procedure, "works with one layer.")

def run_func(
    procedure: Gimp.Procedure,
    run_mode: Gimp.RunMode,
    image: Gimp.Image,
    drawables: list[Gimp.Drawable],
    config: Gimp.ProcedureConfig,
    data,
):
    try:
        return execute(procedure, run_mode, image, drawables, config, data)
    except Exception as e:
        image.undo_group_end()
        return gimp_error.execution(procedure, e)

class {class_name}(Gimp.PlugIn):
    def do_query_procedures(self):
        return [plug_in_proc]

    def do_create_procedure(self, name):
        if name != plug_in_proc:
            return None

        procedure = Gimp.ImageProcedure.new(self, name, Gimp.PDBProcType.PLUGIN, run_func, None)
        procedure.set_sensitivity_mask(
            Gimp.ProcedureSensitivityMask.DRAWABLE
            | Gimp.ProcedureSensitivityMask.NO_DRAWABLES
        )
        procedure.set_menu_label("{label}")
        procedure.set_attribution("Raghav", "Raghav, Tileset Project", "{datetime.date.today().year}")
        procedure.add_menu_path("<Image>/{menu_path}")
        procedure.set_documentation("{description}", None)

        return procedure

Gimp.main({class_name}.__gtype__, sys.argv)
""",
)

os.system(f"chmod u+x '{plugin_file}'")
