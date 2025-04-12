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
        drawable: Gimp.Drawable,
        config: Gimp.ProcedureConfig,
        data,
):
    image.undo_group_start()
    success = Gimp.edit_copy([drawable])
    if not success:
        image.undo_group_end()
        return gimp_error.execution("Could not copy selection.")

    [floating_sel] = Gimp.edit_paste(drawable, False)
    # Gimp.message("Floating Layer: %s" % floating_sel)
    image.raise_item_to_top(floating_sel)
    Gimp.floating_sel_to_layer(floating_sel)

    image.undo_group_end()
    return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, None)
