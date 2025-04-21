#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp, GObject

gi.require_version("GimpUi", "3.0")
from gi.repository import GimpUi
from gi.repository import Gtk

import gimp_error, handler

def show(binary: str, procedure: Gimp.Procedure, config: Gimp.ProcedureConfig, image: Gimp.Image,
         drawable: Gimp.Drawable):
    GimpUi.init(binary)

    dialog = GimpUi.ProcedureDialog.new(procedure, config, "Mask Tileset Blocks")
    dialog.fill(["retain-layer-size"])

    rows, cols = handler.get_dimensions(image, drawable)
    values = handler.get_values(config, rows, cols)

    checkboxes, box_rows = _draw_checklist(rows, cols, values)

    area = dialog.get_content_area()
    area.add(box_rows)

    # make dialogue spawn in center of screen
    dialog.set_position(Gtk.WindowPosition.CENTER)

    if dialog.run():
        dialog.destroy()
        _set_values(checkboxes, config)
        return True, None
    else:
        dialog.destroy()
        _set_values(checkboxes, config)
        return False, gimp_error.cancel(procedure)

def _draw_checklist(rows: int, cols: int, values: list[bool]):
    """
    Draws a checklist of rows and cols
    :param rows: Number of rows
    :param cols: Number of columns
    :return: A list of checkboxes
    """
    box_rows = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    box_rows.set_halign(Gtk.Align.CENTER)
    box_rows.set_hexpand(True)
    checkboxes = []
    for i in range(rows):
        box_cols = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        box_cols.set_hexpand(True)
        for j in range(cols):
            index = i * cols + j
            checkbox = Gtk.CheckButton(active=values[index])
            box_cols.add(checkbox)
            checkboxes.append(checkbox)
            # row.append(checkbox)
        # checkboxes.append(row)
        box_rows.add(box_cols)

    box_rows.show_all()
    return checkboxes, box_rows

def _set_values(checkboxes: list[Gtk.CheckButton], config: Gimp.ProcedureConfig):
    mapped = map(_map_checkbox, checkboxes)
    values = ",".join(list(mapped))
    config.set_property("mask-blocks-str", values)

def _map_checkbox(checkbox: Gtk.CheckButton):
    """
    Maps a checkbox to an integer
    :param checkbox: The checkbox to map
    :return: 1 if the checkbox is checked, 0 otherwise
    """
    value = "1" if checkbox.get_active() else "0"
    return value
