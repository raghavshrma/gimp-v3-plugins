#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp, Gio
import gimp_error
import os

def run_one(
        procedure: Gimp.Procedure,
        run_mode: Gimp.RunMode,
        image: Gimp.Image,
        drawable: Gimp.Layer,
        config: Gimp.ProcedureConfig,
        data):

    file = image.get_xcf_file()
    if file is None:
        return gimp_error.calling(procedure, "No XCF file found.")

    file_path = file.get_path()

    directory = os.path.dirname(file_path)
    basename = os.path.basename(file_path)
    basename = basename.replace('.xcf', f"-{drawable.get_name()}.png")
    file_path = os.path.join(directory, basename)

    wid = drawable.get_width()
    hei = drawable.get_height()
    base_type = image.get_base_type()

    new_image = Gimp.Image.new(wid, hei, base_type)
    Gimp.Selection.none(image)
    copied = Gimp.edit_copy([drawable])

    if not copied:
        return gimp_error.execution(procedure, "Failed to copy drawable.")

    new_layer = Gimp.Layer.new(new_image, drawable.get_name(), wid, hei, Gimp.ImageType.RGBA_IMAGE, 100, Gimp.LayerMode.NORMAL)
    new_image.insert_layer(new_layer, None, 0)

    [floating_sel] = Gimp.edit_paste(new_layer, False)
    Gimp.floating_sel_anchor(floating_sel)
    # new_display = Gimp.Display.new(new_image)

    file = Gio.File.new_for_path(file_path)
    saved = Gimp.file_save(Gimp.RunMode.NONINTERACTIVE, new_image, file, None)

    if not saved:
        return gimp_error.execution(procedure, f"Failed to save {file_path}")

    os.system(f"open '{file_path}'")

    Gimp.message(f"Saved layer image at: {file_path}")
    return gimp_error.success(procedure)
