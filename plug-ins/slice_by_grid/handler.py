#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp
import gimp_error
import math

def run_one(
        procedure: Gimp.Procedure,
        run_mode: Gimp.RunMode,
        image: Gimp.Image,
        drawable: Gimp.Drawable,
        config: Gimp.ProcedureConfig,
        data):

    image.undo_group_start()
    has_selection = not Gimp.Selection.is_empty(image)

    if has_selection:
        copied = Gimp.edit_copy([drawable])
        if not copied:
            image.undo_group_end()
            return gimp_error.execution(procedure, "selected region could not be copied (probably is empty)")

        [layer] = Gimp.edit_paste(drawable, False)
        Gimp.floating_sel_to_layer(layer)
        layer.set_name("__temp__")
    else:
        layer: Gimp.Layer = drawable

    wid, hei = layer.get_width(), layer.get_height()
    success, grid_wid, grid_hei = image.grid_get_spacing()

    group = Gimp.GroupLayer.new(image, "Slices")
    image.insert_layer(group, None, 0)

    rows = int(math.ceil(hei / grid_hei))
    cols = int(math.ceil(wid / grid_wid))

    _, off_x, off_y = layer.get_offsets()

    for row in range(rows):
        for col in range(cols):
            x = col * grid_wid
            y = row * grid_hei

            copy = layer.copy()
            idx = row * cols + col
            image.insert_layer(copy, group, idx)

            copy.set_name(f"slice-{row + 1}x{col + 1}")
            copy.resize(grid_wid, grid_hei, -x, -y)

            # x = col * grid_wid + off_x
            # y = row * grid_hei + off_y
            # image.select_rectangle(Gimp.ChannelOps.REPLACE, x, y, grid_wid, grid_hei)
            # copied = Gimp.edit_copy([layer])
            #
            # if not copied: continue
            #
            # new_layer: Gimp.Layer = Gimp.Layer.new(image, f"S_{row}_{col}", grid_wid, grid_hei, Gimp.ImageType.RGBA_IMAGE, 100, Gimp.LayerMode.NORMAL)
            # image.insert_layer(new_layer, group, row * cols + col)
            # new_layer.set_offsets(x, y)
            #
            # [floating_sel] = Gimp.edit_paste(new_layer, False)
            # Gimp.floating_sel_anchor(floating_sel)

    # check if layer name contains __temp__ and remove it
    if "__temp__" in layer.get_name():
        image.remove_layer(layer)

    image.undo_group_end()
    return gimp_error.success(procedure)
