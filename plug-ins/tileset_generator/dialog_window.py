#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import typing

import gi
from gi.repository.GObject import GObject

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

gi.require_version("GimpUi", "3.0")
from gi.repository import GimpUi
from gi.repository import Gtk

import gimp_error
from handler import OPERATIONS

STORE_TARGET = GimpUi.IntStore.new(["Outline", "Colors"])
OPERATION_NAMES = list(map(lambda x: f"{x[0]}: {x[1]}", OPERATIONS))
STORE_OPERATIONS = GimpUi.IntStore.new(OPERATION_NAMES)

# Change to _show if dialog is interactive
def show(binary: str, procedure: Gimp.Procedure, config: Gimp.ProcedureConfig):
    GimpUi.init(binary)

    dialog = GimpUi.ProcedureDialog.new(procedure, config, "Tileset Quick Generator")

    area = dialog.get_content_area()
    main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

    l_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
    r_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

    l_box.add(dialog.get_int_radio("target", STORE_TARGET))
    l_box.add(dialog.get_widget("quick", Gtk.CheckButton.__gtype__))
    # l_box.add(dialog.fill_frame("l-box", "LBox", True, "quick"))
    r_box.add(dialog.get_int_radio("operation", STORE_OPERATIONS))

    main_box.add(l_box)
    main_box.add(r_box)
    area.add(main_box)
    area.show_all()

    dialog.set_position(Gtk.WindowPosition.CENTER)

    if dialog.run():
        dialog.destroy()
        return True, None
    else:
        dialog.destroy()
        return False, gimp_error.cancel(procedure)
