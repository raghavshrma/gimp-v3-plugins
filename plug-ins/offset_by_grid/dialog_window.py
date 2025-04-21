#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

gi.require_version("GimpUi", "3.0")
from gi.repository import GimpUi
from gi.repository import Gtk

import gimp_error

# Change to _show if dialog is interactive
def show(binary: str, procedure: Gimp.Procedure, config: Gimp.ProcedureConfig):
    GimpUi.init(binary)

    dialog = GimpUi.ProcedureDialog.new(procedure, config, "Offset By Grid")
    # dialog.fill(None)

    # make dialogue spawn in center of screen
    store = GimpUi.IntStore.new(["+X", "-X", "+Y", "-Y"])
    widget = dialog.get_int_radio("offset-type", store)
    widget.show()
    area = dialog.get_content_area()
    area.add(widget)

    dialog.set_position(Gtk.WindowPosition.CENTER)

    if dialog.run():
        dialog.destroy()
        return True, None
    else:
        dialog.destroy()
        return False, gimp_error.cancel(procedure)
