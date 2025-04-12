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

    Gimp.Selection.none(image)
    drawable.edit_clear()
    [floating_sel] = Gimp.edit_paste(drawable, True)
    if isinstance(floating_sel, Gimp.Layer):
        Gimp.floating_sel_anchor(floating_sel)

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
