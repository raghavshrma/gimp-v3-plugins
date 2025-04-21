#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp, Gegl
import gimp_error

OFFSET_LIST = [
    (1, 0), # Positive X
    (-1, 0), # Negative X
    (0, 1), # Positive Y
    (0, -1) # Negative Y
]

def run_one(
        procedure: Gimp.Procedure,
        run_mode: Gimp.RunMode,
        image: Gimp.Image,
        drawable: Gimp.Drawable,
        config: Gimp.ProcedureConfig,
        data):

    image.undo_group_start()
    offset_type = config.get_property("offset-type")
    mx, my = OFFSET_LIST[offset_type]
    _, g_wid, g_hei = image.grid_get_spacing()
    color = Gegl.Color.new("0")
    drawable.offset(True, Gimp.OffsetType.WRAP_AROUND, color, mx * g_wid, my * g_hei)
    image.undo_group_end()
    return gimp_error.success(procedure)

# def run_all(
#         procedure: Gimp.Procedure,
#         run_mode: Gimp.RunMode,
#         image: Gimp.Image,
#         drawables: list[Gimp.Drawable],
#         config: Gimp.ProcedureConfig,
#         data):
#

# def run_any(
#         procedure: Gimp.Procedure,
#         run_mode: Gimp.RunMode,
#         image: Gimp.Image,
#         config: Gimp.ProcedureConfig,
#         data):
#
#     return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, None)

