#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

gi.require_version("GimpUi", "3.0")
from gi.repository import GimpUi
from gi.repository import Gtk

OFFSET_OPTIONS = ["0%", "25%", "50%", "75%", "100%"]


def _get_radio_frame(
    config: Gimp.ProcedureConfig, prop_name: str
) -> GimpUi.IntRadioFrame:
    label = config.get_procedure().find_argument(prop_name).get_nick()
    store = GimpUi.IntStore.new(OFFSET_OPTIONS)
    widget = GimpUi.IntRadioFrame.new_from_store(label, store)

    current_index = int(config.get_property(prop_name) / 25)
    widget.set_active(current_index)
    widget.show_all()
    widget.set_hexpand(True)
    return widget


def _apply_value(
    config: Gimp.ProcedureConfig, prop_name: str, widget: GimpUi.IntRadioFrame
):
    value = widget.get_active() * 25
    config.set_property(prop_name, value)


def show(binary: str, procedure: Gimp.Procedure, config: Gimp.ProcedureConfig):
    GimpUi.init(binary)

    dialog = GimpUi.ProcedureDialog.new(procedure, config, "Tileset Offset")

    offset_x_radio = _get_radio_frame(config, "offset-x")
    offset_y_radio = _get_radio_frame(config, "offset-y")

    box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 5)
    box.add(offset_x_radio)
    box.add(offset_y_radio)
    box.show_all()

    box.set_halign(Gtk.Align.FILL)
    box.set_hexpand(True)

    area = dialog.get_content_area()
    area.add(box)

    dialog.fill(["tiles"])

    # make dialogue spawn in center of screen
    dialog.set_position(Gtk.WindowPosition.CENTER)

    if not dialog.run():
        dialog.destroy()
        return False, procedure.new_return_values(Gimp.PDBStatusType.CANCEL, None)
    else:
        _apply_value(config, "offset-x", offset_x_radio)
        _apply_value(config, "offset-y", offset_y_radio)
        dialog.destroy()
        return True, None
