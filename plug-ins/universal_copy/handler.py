#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp
import gimp_error
import os

# def run_one(
#         procedure: Gimp.Procedure,
#         run_mode: Gimp.RunMode,
#         image: Gimp.Image,
#         drawable: Gimp.Drawable,
#         config: Gimp.ProcedureConfig,
#         data):

#     image.undo_group_start()

#     # Add your code here.

#     image.undo_group_end()
#     return gimp_error.success(procedure)

def run_all(
        procedure: Gimp.Procedure,
        run_mode: Gimp.RunMode,
        source_image: Gimp.Image,
        drawables: list[Gimp.Drawable],
        config: Gimp.ProcedureConfig,
        data):

    if Gimp.Selection.is_empty(source_image):
        x1, y1, x2, y2 = source_image.get_width(), source_image.get_height(), 0, 0
        for drawable in drawables:
            _, u1, v1 = drawable.get_offsets()
            u2 = u1 + drawable.get_width()
            v2 = v1 + drawable.get_height()
            x1 = min(x1, u1)
            y1 = min(y1, v1)
            x2 = max(x2, u2)
            y2 = max(y2, v2)

        wid = x2 - x1
        hei = y2 - y1
    else:
        _, non_empty, x1, y1, x2, y2 = Gimp.Selection.bounds(source_image)
        wid = x2 - x1
        hei = y2 - y1

    # Gimp.message(f"Selection size: {wid}, {hei}")
    # Gimp.message(f"Drawables: {drawables}")
    if run_mode == Gimp.RunMode.NONINTERACTIVE and len(drawables) == 0:
        drawables = source_image.get_selected_layers()

    success = Gimp.edit_copy(drawables)
    if not success:
        return gimp_error.calling(procedure, "failed to copy layers")

    tmp_image = Gimp.Image.new(wid, hei, source_image.get_base_type())
    tmp_layer = Gimp.Layer.new(tmp_image, "layer", wid, hei, Gimp.ImageType.RGBA_IMAGE, 100, Gimp.LayerMode.NORMAL)
    tmp_image.insert_layer(tmp_layer, None, 0)
    # new_display = Gimp.Display.new(tmp_image)
    pasted_layers = Gimp.edit_paste(tmp_layer, False)

    if len(pasted_layers) == 1:
        # noinspection PyTypeChecker
        Gimp.floating_sel_anchor(pasted_layers[0])

    Gimp.edit_copy_visible(tmp_image)
    Gimp.displays_flush()


    exit_code = os.system("shortcuts run 'GIMP Copy'")
    message = "Copied to universal keyboard" if exit_code == 0 \
        else f"Universal Copy failed with error code: {exit_code}"

    Gimp.message(message)
    tmp_image.delete()

    return gimp_error.success(procedure)


# def run_any(
#         procedure: Gimp.Procedure,
#         run_mode: Gimp.RunMode,
#         image: Gimp.Image,
#         config: Gimp.ProcedureConfig,
#         data):
#
#     return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, None)

