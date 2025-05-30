#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp
import gimp_error
import math
from utils import ProcessTimer

def run_one(
        procedure: Gimp.Procedure,
        run_mode: Gimp.RunMode,
        image: Gimp.Image,
        drawable: Gimp.Layer,
        config: Gimp.ProcedureConfig,
        data):

    image.undo_group_start()
    is_temp_layer, layer = get_source_layer(image, drawable)

    target_group = Gimp.GroupLayer.new(image, "Slices")
    image.insert_layer(target_group, None, 0)

    timer = ProcessTimer()
    slice_layer(image, layer, target_group)
    timer.end("Sliced layer")

    target_group.set_expanded(False)

    # image.remove_layer(target_group)
    # image.set_selected_layers([drawable])

    if is_temp_layer:
        image.remove_layer(layer)

    image.undo_group_end()
    return gimp_error.success(procedure)


def get_source_layer(image: Gimp.Image, drawable: Gimp.Layer):
    has_selection = not Gimp.Selection.is_empty(image)

    if has_selection:
        copied = Gimp.edit_copy([drawable])
        if not copied:
            raise Exception("Selected region could not be copied (probably is empty)")

        [layer] = Gimp.edit_paste(drawable, False)
        # noinspection PyTypeChecker
        Gimp.floating_sel_to_layer(layer)
    else:
        layer = drawable

    return has_selection, layer

def slice_layer(image: Gimp.Image, layer: Gimp.Layer, parent: Gimp.GroupLayer):
    success, wid, hei = image.grid_get_spacing()
    # hei = wid = 96
    layer_wid, layer_hei = layer.get_width(), layer.get_height()
    rows = int(math.ceil(layer_hei / hei))
    cols = int(math.ceil(layer_wid / wid))

    for row in range(rows):
        for col in range(cols):
            x = col * wid
            y = row * hei

            if is_empty_block(layer, x, y, wid, hei):
                # Gimp.message(f"Block {row + 1}x{col + 1} is empty")
                continue

            copy = layer.copy()
            idx = row * cols + col
            image.insert_layer(copy, parent, idx)

            # copy.set_name(f"slice-{row + 1}x{col + 1}")
            copy.resize(wid, hei, -x, -y)

def is_empty_block(layer: Gimp.Layer, x: int, y: int, w: int, h: int):
    ex = x + w - 1
    ey = y + h - 1

    for i in range(0, w // 2, 8):
        for j in range(0, h // 2, 8):
            si = x + i
            sj = y + j
            ei = ex - i
            ej = ey - j

            is_empty = is_empty_pixel(layer, si, sj) and \
                is_empty_pixel(layer, si, ej) and \
                is_empty_pixel(layer, ei, sj) and \
                is_empty_pixel(layer, ei, ej)

            if not is_empty:
                return False

    return True

def is_empty_pixel(layer: Gimp.Layer, x: int, y: int):
    color = layer.get_pixel(x, y)
    _, _, _, a = color.get_rgba()
    return a < 0.01
