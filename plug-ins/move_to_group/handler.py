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

    group_name = config.get_property("group-name")
    if not group_name:
        return gimp_error.calling(procedure, "Group name not provided")


    image.undo_group_start()

    group = image.get_layer_by_name(group_name)
    if group is None:
        group = Gimp.GroupLayer.new(image, group_name)
        image.insert_layer(group, None, 0)
    elif not group.is_group_layer():
        return gimp_error.calling(procedure, f"Layer: {group_name} is not a group layer")

    copy = drawable.copy()
    image.remove_layer(drawable)
    image.insert_layer(copy, group, 0)

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

