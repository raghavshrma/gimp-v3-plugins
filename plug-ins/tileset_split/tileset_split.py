#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gimp", "3.0")

from gi.repository import Gimp, GObject
import sys
import handler, gimp_error, dialog_window

plug_in_binary = "tileset-split"
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

    if hasattr(handler, "run_any"):
        return handler.run_any(procedure, run_mode, image, config, data)

    if hasattr(handler, "run_all"):
        return handler.run_all(procedure, run_mode, image, drawables, config, data)

    if not hasattr(handler, 'run_one'):
        return gimp_error.calling(procedure, "misconfigured plug-in. Needs at least on run method")

    if len(drawables) == 1:
        if not isinstance(drawables[0], Gimp.Layer):
            return gimp_error.calling(procedure, "works with layers only.")

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
        image.undo_group_end()
        Gimp.message(str(e.with_traceback(None)))
        return gimp_error.execution(procedure, e)

class TilesetSplit(Gimp.PlugIn):
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
        procedure.set_menu_label("Tileset Split")
        procedure.set_attribution("Raghav", "Raghav, Tileset Project", "2025")
        procedure.add_menu_path("<Image>/Tileset/Transform/")
        procedure.set_documentation("Tileset Split", None)

        choice = Gimp.Choice.new()
        for op_nick, op_id, op_label, op_help in handler.OPERATIONS:
            choice.add(op_nick, op_id, op_label, op_help)
        # choice.add("L0: Slicing", 0, "Slicing", "Performs slicing on the base sample tileset")
        # choice.add("L1: Primary Tiles", 1, "Primary Tiles", "Re-offsets the primary tiles")

        procedure.add_choice_argument("operation", "Operation", "Operation to perform", choice, handler.OPERATIONS[0][0], GObject.ParamFlags.READWRITE)

        return procedure

Gimp.main(TilesetSplit.__gtype__, sys.argv)
