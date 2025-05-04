#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gimp", "3.0")

from gi.repository import Gimp, GObject
import sys
import handler, gimp_error, dialog_window

plug_in_binary = "tileset-generator"
plug_in_proc = "plug-in-tlk-" + plug_in_binary

def execute(
        procedure: Gimp.Procedure,
        run_mode: Gimp.RunMode,
        image: Gimp.Image,
        drawables: list[Gimp.Drawable],
        config: Gimp.ProcedureConfig,
        data
):
    if run_mode == Gimp.RunMode.INTERACTIVE and hasattr(dialog_window, "show"):
        success, ret = dialog_window.show(plug_in_binary, procedure, config)
        if not success:
            return ret

    if hasattr(handler, 'run_any'):
        return handler.run_any(procedure, run_mode, image, config, data)

    if hasattr(handler, 'run_all'):
        return handler.run_all(procedure, run_mode, image, drawables, config, data)

    if not hasattr(handler, 'run_one'):
        return gimp_error.calling(procedure, "misconfigured plug-in. Needs at least on run method")

    if len(drawables) == 1:
        layer = drawables[0]
        if not isinstance(layer, Gimp.Layer):
            return gimp_error.calling(procedure, "works with layers only.")

        return handler.run_one(procedure, run_mode, image, layer, config, data)

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
        image.undo_group_end()
        return gimp_error.execution(procedure, e)

class TilesetQuickGenerator(Gimp.PlugIn):
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
        procedure.set_menu_label("Tileset Quick Generator")
        procedure.set_attribution("Raghav", "Raghav, Tileset Project", "2025")
        procedure.add_menu_path("<Image>/Tileset/Transform/")
        procedure.set_documentation("Tileset Quick Generator", None)

        procedure.add_int_argument("operation", "Operation", None, 0, len(handler.OPERATIONS) - 1, 0, GObject.ParamFlags.READWRITE)
        procedure.add_int_argument("target", "Target", None, 0, 1, 0, GObject.ParamFlags.READWRITE)
        procedure.add_boolean_argument("quick", "Quick", None, False, GObject.ParamFlags.READWRITE)

        return procedure

Gimp.main(TilesetQuickGenerator.__gtype__, sys.argv)
