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

    image.undo_group_start()

    # drawable.get_parent().get_children()


    name = drawable.get_name()
    parent = drawable.get_parent()
    layers: list[Gimp.Layer] = parent.get_children() if parent is not None else []
    target_layer: Gimp.Layer | None = None
    found_match = False

    for layer in layers:
        if found_match:
            target_layer = layer
            break

        if layer.get_name() == name:
            found_match = True

    if target_layer.is_group_layer():
        return gimp_error.execution(procedure, "Cannot merge and replace into group layer.")

    if target_layer is None:
        return gimp_error.execution(procedure, "Cannot find target layer to merge and replace into")

    if not isinstance(target_layer, Gimp.Layer):
        return gimp_error.execution(procedure, "Target layer is not a layer")

    Gimp.Selection.none(image)
    target_layer.edit_clear()
    image.merge_down(drawable, Gimp.MergeType.EXPAND_AS_NECESSARY)
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

