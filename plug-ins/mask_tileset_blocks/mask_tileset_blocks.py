#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
from gi.repository.GObject import GObject

gi.require_version("Gimp", "3.0")

from gi.repository import Gimp, GObject
import sys
import handler, gimp_error, dialog_window

plug_in_binary = "mask-tileset-blocks"
plug_in_proc = "plug-in-tlk-" + plug_in_binary

def execute(
        procedure: Gimp.Procedure,
        run_mode: Gimp.RunMode,
        image: Gimp.Image,
        drawables: list[Gimp.Drawable],
        config: Gimp.ProcedureConfig,
        data
):
    # if hasattr(handler, 'run_any'):
    #     return handler.run_any(procedure, run_mode, image, config, data)
    #
    # if hasattr(handler, 'run_all'):
    #     return handler.run_all(procedure, run_mode, image, drawables, config, data)

    if not hasattr(handler, 'run_one'):
        return gimp_error.calling(procedure, "misconfigured plug-in. Needs at least on run method")


    if len(drawables) == 1:
        if not isinstance(drawables[0], Gimp.Layer):
            return gimp_error.calling(procedure, "works with layers only.")

        if run_mode == Gimp.RunMode.INTERACTIVE:
            success, ret = dialog_window.show(plug_in_binary, procedure, config, image, drawables[0])
            if not success:
                return ret
        return handler.run_one(procedure, run_mode, image, drawables[0], config, data)

    return gimp_error.calling(procedure, "works with one layer.")

def run_func(
    procedure: Gimp.Procedure,
    run_mode: Gimp.RunMode,
    image: Gimp.Image,
    drawables: list[Gimp.Drawable],
    config: Gimp.ProcedureConfig,
    data,
):
    try:
        return execute(procedure, run_mode, image, drawables, config, data)
    except Exception as e:
        return gimp_error.execution(procedure, e)

class MaskTilesetBlocks(Gimp.PlugIn):
    def do_query_procedures(self):
        return [plug_in_proc]

    def do_create_procedure(self, name):
        if name != plug_in_proc:
            return None

        procedure = Gimp.ImageProcedure.new(self, name, Gimp.PDBProcType.PLUGIN, run_func, None)
        procedure.set_sensitivity_mask(
            Gimp.ProcedureSensitivityMask.DRAWABLE
            | Gimp.ProcedureSensitivityMask.NO_DRAWABLES
        )
        procedure.set_menu_label("Mask Tileset Blocks")
        procedure.set_attribution("Raghav", "Raghav, Tileset Project", "2025")
        procedure.add_menu_path("<Image>/Tileset/Transform/")
        procedure.set_documentation("Mask Tileset Blocks", None)


        procedure.add_string_argument("mask-blocks-str", "Mask Blocks String", "String of blocks to mask", "", GObject.ParamFlags.READWRITE)

        # procedure.add_int32_array_argument(
        #     "mask-blocks",
        #     "Mask Blocks",
        #     "Array of blocks to mask, size: rows * columns",
        #     GObject.ParamFlags.READWRITE,
        # )

        return procedure

Gimp.main(MaskTilesetBlocks.__gtype__, sys.argv)
