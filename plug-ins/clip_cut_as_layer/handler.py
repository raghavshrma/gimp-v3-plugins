#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp
import gimp_error

def run_one(
        procedure: Gimp.Procedure,
        run_mode: Gimp.RunMode,
        image: Gimp.Image,
        drawable: Gimp.Layer,
        config: Gimp.ProcedureConfig,
        data):



    # has_selection = not Gimp.Selection.is_empty(image)
    _, has_selection, x1, y1, x2, y2 = Gimp.Selection.bounds(image)
    # Gimp.message(f"Selection: bounds: {has_selection}, x1: {x1}, y1: {y1}, x2: {x2}, y2: {y2}")

    image.undo_group_start()

    Gimp.edit_cut([drawable])
    [floating_sel] = Gimp.edit_paste(drawable, False)
    # image.raise_item_to_top(floating_sel)
    Gimp.floating_sel_to_layer(floating_sel)

    image.set_selected_layers([drawable])

    if has_selection:
        image.select_rectangle(Gimp.ChannelOps.REPLACE, x1, y1, x2-x1, y2-y1)

    image.undo_group_end()
    return gimp_error.success(procedure)
