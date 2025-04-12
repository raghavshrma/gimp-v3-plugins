#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp
import gimp_error

def get_dimensions(image: Gimp.Image, drawable: Gimp.Drawable) -> tuple[int, int]:
    _, g_wid, g_hei = image.grid_get_spacing()
    wid, hei = drawable.get_width(), drawable.get_height()

    rows = int(hei / g_hei)
    cols = int(wid / g_wid)
    return rows, cols

def get_values(config: Gimp.ProcedureConfig, rows: int, cols: int) -> list[bool]:
    """
    Get the values from the config

    :param config: The config
    :param rows: Number of rows
    :param cols: Number of columns
    :return: A list of values
    """
    value: str = config.get_property("mask-blocks-str")
    values = value.split(",")

    if len(values) != rows * cols:
        return [False] * (rows * cols)

    mapped = map(lambda v: v == "1", values)
    return list(mapped)

    # values = config.get_core_object_array("mask-blocks")
    # v2 = config.get_property("mask-blocks")
    # Gimp.message(f"v2: {v2}")

    # config.set_property("mask-blocks", values)

    # Gimp.message(f"Values: {values}")
    # if values is None or len(values) != rows * cols:
    #     values = [0] * (rows * cols)


def run_one(
        procedure: Gimp.Procedure,
        run_mode: Gimp.RunMode,
        image: Gimp.Image,
        drawable: Gimp.Layer,
        config: Gimp.ProcedureConfig,
        data):

    image.undo_group_start()

    _, g_wid, g_hei = image.grid_get_spacing()
    wid, hei = drawable.get_width(), drawable.get_height()
    _, off_x, off_y = drawable.get_offsets()

    rows = int(hei / g_hei)
    cols = int(wid / g_wid)
    values = get_values(config, rows, cols)

    Gimp.Selection.none(image)

    x2, y2 = off_x, off_y
    x1, y1 = x2 + wid, y2 + hei

    for row in range(rows):
        for col in range(cols):
            index = row * cols + col
            if not values[index]:
                continue

            # Get the tile coordinates
            x = col * g_wid + off_x
            y = row * g_hei + off_y

            image.select_rectangle(Gimp.ChannelOps.ADD, x, y, g_wid, g_hei)

            x1 = min(x1, x)
            y1 = min(y1, y)
            x2 = max(x2, x + g_wid)
            y2 = max(y2, y + g_hei)

    # Add your code here.
    Gimp.Selection.invert(image)
    drawable.edit_clear()
    Gimp.Selection.none(image)

    if x2 > x1:
        drawable.resize(x2 - x1, y2 - y1, off_x - x1, off_y - y1)


    # Gimp.Selection.edit_clear()

    image.undo_group_end()
    return gimp_error.success(procedure)
