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
        image: Gimp.Image,
        drawables: list[Gimp.Drawable],
        config: Gimp.ProcedureConfig,
        data):

    success = Gimp.edit_copy(drawables)
    if not success:
        return gimp_error.calling(procedure, "failed to copy layers")

    exit_code = os.system("shortcuts run 'GIMP Copy'")

    message = "Copied to universal keyboard" if exit_code == 0 \
        else f"Universal Copy failed with error code: {exit_code}"

    Gimp.message(message)

    return gimp_error.success(procedure)


# def run_any(
#         procedure: Gimp.Procedure,
#         run_mode: Gimp.RunMode,
#         image: Gimp.Image,
#         config: Gimp.ProcedureConfig,
#         data):
#
#     return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, None)

