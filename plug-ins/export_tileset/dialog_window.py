#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

gi.require_version("GimpUi", "3.0")
from gi.repository import GimpUi
from gi.repository import Gtk

import gimp_error

def show(binary: str, procedure: Gimp.Procedure, config: Gimp.ProcedureConfig):
    GimpUi.init(binary)

    dialog = GimpUi.ProcedureDialog.new(procedure, config, "Export Tileset")

    # noinspection PyTypeChecker
    hq_box: Gtk.Box = dialog.fill_box("hq-box", ["hq-spacing", "hq-fill-spacing"])
    hq_box.set_orientation(Gtk.Orientation.HORIZONTAL)
    dialog.fill_frame("hq-frame", "hq-export", False, "hq-box")

    # noinspection PyTypeChecker
    dialog.fill_box("lq-box", ["lq-scaling"])
    dialog.fill_frame("lq-frame", "lq-export", False, "lq-box")

    dialog.fill(["hq-frame", "lq-frame"])

    dialog.set_position(Gtk.WindowPosition.CENTER)

    if not dialog.run():
        dialog.destroy()
        return False, gimp_error.cancel(procedure)
    else:
        dialog.destroy()
        return True, None
