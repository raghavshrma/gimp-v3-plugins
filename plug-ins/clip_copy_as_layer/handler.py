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
        data,
):
    image.undo_group_start()

    # clip_transform(image, drawable)
    # image.undo_group_end()
    # return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, None)


    success = Gimp.edit_copy([drawable])
    if not success:
        image.undo_group_end()
        return gimp_error.execution("Could not copy selection.")

    [floating_sel] = Gimp.edit_paste(drawable, False)
    # Gimp.message("Floating Layer: %s" % floating_sel)
    image.raise_item_to_top(floating_sel)
    Gimp.floating_sel_to_layer(floating_sel)

    image.undo_group_end()
    return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, None)

def clip_transform(image: Gimp.Image, layer: Gimp.Layer):
    e_layer = image.get_layer_by_name("shrunk")
    if e_layer:
        image.remove_layer(e_layer)

    rows = cols = 20
    group = Gimp.GroupLayer.new(image, "shrunk")
    image.insert_layer(group, None, 0)

    for r in range(rows):
        for c in range(cols):
            copy = layer.copy()
            image.insert_layer(copy, group, 0)
            copy.resize(96, 96, -c * 102, -r * 102)
            copy.set_offsets(96 * c, 96 * r)

    group.merge()
    layer.set_visible(False)
