#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp, Gio
import gimp_error
import utils
from spacing import Spacing


def run_any(
        procedure: Gimp.Procedure,
        run_mode: Gimp.RunMode,
        image: Gimp.Image,
        config: Gimp.ProcedureConfig,
        data,
):
    path = get_export_path(image)
    grid = get_grid_size(image)
    export_hq(config, image, path, grid)
    # export_lq(config, image, path)
    return gimp_error.success(procedure)


def get_export_path(image: Gimp.Image) -> str:
    file = image.get_xcf_file()

    if file is None:
        file = image.get_imported_file()

    if file is None:
        raise Exception("Image not saved / imported")

    path = file.get_parse_name()
    return f"{path[:-4]}.png"


def get_grid_size(image: Gimp.Image):
    _, grid_x, grid_y = image.grid_get_spacing()

    if grid_x != grid_y:
        raise Exception(f"Image grid not square - got: {grid_x}x{grid_y}")

    return int(grid_x)


def export_hq(config: Gimp.ProcedureConfig, src_image: Gimp.Image, path: str, grid: int):
    if not config.get_property("hq-export"):
        return None

    spacing = config.get_property("hq-spacing")

    tmp_image = src_image.duplicate()
    new_display = Gimp.Display.new(tmp_image)
    tmp_image.undo_disable()

    tmp_image.grid_set_spacing(grid + spacing, grid + spacing)
    layer = tmp_image.merge_visible_layers(Gimp.MergeType.CLIP_TO_IMAGE)

    if spacing > 0:
        Spacing(tmp_image, layer, grid, spacing, config.get_property("hq-fill-spacing")).run()
    else:
        new_wid = utils.get_pot_size(tmp_image.get_width())
        new_hei = utils.get_pot_size(tmp_image.get_height())
        tmp_image.resize(new_wid, new_hei, 0, 0)

    save_file(tmp_image, path, "HQ")
    tmp_image.delete()
    new_display.delete()
    Gimp.displays_flush()


def export_lq(
        config: Gimp.ProcedureConfig,
        source_image: Gimp.Image,
        path: str
):

    scaling = config.get_property("lq-scaling")
    if scaling < 1:
        raise Exception("Scaling cannot be less than 1")

    wid, hei = source_image.get_width(), source_image.get_height()

    if wid % scaling != 0 or hei % scaling != 0:
        raise Exception(f"Image size {wid}x{hei} not divisible by {scaling}")

    image = source_image.duplicate()
    image.merge_visible_layers(Gimp.MergeType.CLIP_TO_IMAGE)
    # this changes the background to white (color-2) instead of transparent
    # image.flatten()

    og_interpolation = Gimp.context_get_interpolation()
    Gimp.context_set_interpolation(Gimp.InterpolationType.LINEAR)
    image.scale(wid // scaling, hei // scaling)
    Gimp.context_set_interpolation(og_interpolation)

    lq_path = f"{path[:-4]}_lq.png"
    file = Gio.File.new_for_path(lq_path)
    saved = Gimp.file_save(Gimp.RunMode.NONINTERACTIVE, image, file, None)
    Gimp.message(f"Saved LQ file {lq_path}: {saved}")

    image.delete()
    Gimp.displays_flush()

def save_file(image: Gimp.Image, path: str, name: str):
    file = Gio.File.new_for_path(path)
    saved = Gimp.file_save(Gimp.RunMode.NONINTERACTIVE, image, file, None)
    Gimp.message(f"Saved {name} image at:\n {path}\n\n ---\n Saved: {saved}")