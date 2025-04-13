#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp, Gio
import gimp_error
import math


def run_any(
        procedure: Gimp.Procedure,
        run_mode: Gimp.RunMode,
        image: Gimp.Image,
        config: Gimp.ProcedureConfig,
        data,
):
    path = image.get_xcf_file().get_parse_name()

    if not path:
        return gimp_error.calling(procedure, "Image not saved")

    _, grid_x, grid_y = image.grid_get_spacing()

    if grid_x != grid_y:
        return gimp_error.calling(procedure, "Grid not square")

    grid = int(grid_x)

    err = _export_hq(procedure, config, image, path, grid)
    if err:
        return err

    err = _export_lq(procedure, config, image, path)
    if err:
        return err

    return gimp_error.success(procedure)


def _export_hq(
        procedure: Gimp.Procedure,
        config: Gimp.ProcedureConfig,
        source_image: Gimp.Image,
        path: str,
        grid: int,
) -> Gimp.ValueArray | None:
    if not config.get_property("hq-export"):
        return None

    spacing = config.get_property("hq-spacing")

    image = source_image.duplicate()
    new_display = Gimp.Display.new(image)
    image.undo_disable()

    image.grid_set_spacing(grid + spacing, grid + spacing)
    # layer = image.merge_visible_layers(Gimp.MergeType.CLIP_TO_IMAGE)
    layer = image.flatten()
    # other_layers = image.get_layers()
    # for other_layer in other_layers:
    #     if not other_layer.get_visible():
    #         image.remove_layer(other_layer)

    if spacing > 0:
        _add_spacing(image, layer, grid, spacing, config.get_property("hq-fill-spacing"))
    else:
        new_wid = _get_pot_size(image.get_width())
        new_hei = _get_pot_size(image.get_height())
        image.resize(new_wid, new_hei, 0, 0)

    hq_path = f"{path[:-4]}.png"
    file = Gio.File.new_for_path(hq_path)
    saved = Gimp.file_save(Gimp.RunMode.NONINTERACTIVE, image, file, None)
    Gimp.message(f"Saved HQ file {hq_path}: {saved}")

    image.delete()
    new_display.delete()
    Gimp.displays_flush()


def _add_spacing(image: Gimp.Image, source_layer: Gimp.Layer, grid: int, spacing: int, fill_spacing: bool):
    img_w, img_h = image.get_width(), image.get_height()

    rows = math.ceil((img_h / grid))
    cols = math.ceil((img_w / grid))

    new_width = _get_pot_size(cols * grid + (cols - 1) * spacing)
    new_height = _get_pot_size(rows * grid + (rows - 1) * spacing)
    image.resize(new_width, new_height, 0, 0)

    final_layer = Gimp.Layer.new(
        image,
        "final_layer",
        new_width,
        new_height,
        Gimp.ImageType.RGBA_IMAGE,
        100,
        Gimp.LayerMode.NORMAL,
    )
    image.insert_layer(final_layer, None, 0)

    Gimp.debug_timer_start()

    for row in reversed(range(rows)):
        # if row < rows - 2:
        #     break

        for col in reversed(range(cols)):
            x = col * grid
            y = row * grid

            nx = x + (col * spacing)
            ny = y + (row * spacing)

            # _copy_block(image, source_layer, x, y, final_layer, nx, ny, grid)
            copy = _copy_block3(image, source_layer, col, row, grid)
            copy.set_offsets(nx, ny)

            if fill_spacing:
                _fill_space_pixels2(image, final_layer, nx, ny, grid, spacing)

        # source_layer.set_visible(False)
        # final_layer = image.merge_visible_layers(Gimp.MergeType.CLIP_TO_IMAGE)
        # source_layer.set_visible(True)

    time = Gimp.debug_timer_end()
    Gimp.message(f"Prepared spaced tileset in: {time}s")
    source_layer.set_visible(False)


def _copy_block3(
        image: Gimp.Image,
        source: Gimp.Layer,
        col: int,
        row: int,
        grid: int,
):
    copy = source.copy()
    image.insert_layer(copy, None, 0)
    copy.resize(grid, grid, -col * grid, -row * grid)
    return copy


def _copy_block(
        image: Gimp.Image,
        source: Gimp.Layer,
        sx: int,
        sy: int,
        target: Gimp.Layer,
        tx: int,
        ty: int,
        grid: int,
):
    image.select_rectangle(Gimp.ChannelOps.REPLACE, sx, sy, grid, grid)
    copied = Gimp.edit_copy([source])
    if not copied:
        return

    # noinspection PyTypeChecker
    floating_sel: Gimp.Layer = Gimp.edit_paste(target, False)[0]
    floating_sel.set_offsets(tx, ty)
    Gimp.floating_sel_anchor(floating_sel)


def _copy_block2(
        image: Gimp.Image,
        source: Gimp.Layer,
        sx: int,
        sy: int,
        target: Gimp.Layer,
        tx: int,
        ty: int,
        grid: int,
):
    for i in range(grid):
        for j in range(grid):
            color = source.get_pixel(sx + i, sy + j)
            target.set_pixel(tx + i, ty + j, color)


def _get_pot_size(x: int) -> int:
    """
    Get the next power of two size for a given dimension.
    """

    if x == 0:
        return 1
    return 1 << (x - 1).bit_length()


def _fill_space_pixels(
        image: Gimp.Image, layer: Gimp.Layer, x: int, y: int, grid: int, spacing: int
):
    half = spacing >> 1

    _repeat_pixels_h(image, layer, x, y, grid, -half)
    _repeat_pixels_h(image, layer, x, y + grid - 1, grid, half)
    _repeat_pixels_v(image, layer, x, y, grid, -half)
    _repeat_pixels_v(image, layer, x + grid - 1, y, grid, half)


def _repeat_pixels_h(
        image: Gimp.Image, layer: Gimp.Layer, x: int, y: int, grid: int, dy: int
):
    end_y = max(0, min(y + dy, layer.get_height()))
    if end_y == y:
        return

    # Top line
    image.select_rectangle(Gimp.ChannelOps.REPLACE, x, y, grid, 1)
    buffer_name = Gimp.edit_named_copy([layer], "block-buffer")

    if buffer_name:
        range_y = range(end_y, y) if y > end_y else range(y + 1, end_y + 1)

        for ty in range_y:
            sel = Gimp.edit_named_paste(layer, buffer_name, False)
            sel.set_offsets(x, ty)
            Gimp.floating_sel_anchor(sel)

        Gimp.buffer_delete(buffer_name)


def _repeat_pixels_v(
        image: Gimp.Image, layer: Gimp.Layer, x: int, y: int, grid: int, dx: int
):
    end_x = max(0, min(x + dx, layer.get_height()))
    if end_x == x:
        return

    # Top line
    image.select_rectangle(Gimp.ChannelOps.REPLACE, x, y, 1, grid)
    buffer_name = Gimp.edit_named_copy([layer], "block-buffer")

    if buffer_name:
        range_x = range(end_x, x) if x > end_x else range(x + 1, end_x + 1)

        for tx in range_x:
            sel = Gimp.edit_named_paste(layer, buffer_name, False)
            sel.set_offsets(tx, y)
            Gimp.floating_sel_anchor(sel)

        Gimp.buffer_delete(buffer_name)


def _fill_space_pixels2(
        image: Gimp.Image, layer: Gimp.Layer, x: int, y: int, grid: int, spacing: int
):
    # wid, hei = layer.get_width(), layer.get_height()
    half = spacing >> 1

    _fill_pixels_h(layer, range(x, x + grid), y, -half)
    _fill_pixels_h(layer, range(x, x + grid), y + grid - 1, half)
    _fill_pixels_v(layer, range(y, y + grid), x, -half)
    _fill_pixels_v(layer, range(y, y + grid), x + grid - 1, half)
    # Corners:
    _fill_pixels_corner(layer, x, y, -half, -half)
    _fill_pixels_corner(layer, x, y + grid - 1, -half, half)
    _fill_pixels_corner(layer, x + grid - 1, y, half, -half)
    _fill_pixels_corner(layer, x + grid - 1, y + grid - 1, half, half)


def _fill_pixels_h(layer: Gimp.Layer, range_sx: range, sy: int, end_ty: int):
    end_ty += sy
    end_ty = max(0, min(end_ty, layer.get_height()))
    if end_ty == sy:
        return

    range_ty = range(end_ty, sy) if sy > end_ty else range(sy + 1, end_ty + 1)

    for x in range_sx:
        color = layer.get_pixel(x, sy)
        _, _, _, a = color.get_rgba()

        if a == 0:
            continue

        for ty in range_ty:
            layer.set_pixel(x, ty, color)


def _fill_pixels_v(layer: Gimp.Layer, range_sy: range, sx: int, end_tx: int):
    end_tx += sx
    end_tx = max(0, min(end_tx, layer.get_width()))
    if end_tx == sx:
        return

    range_tx = range(end_tx, sx) if sx > end_tx else range(sx + 1, end_tx + 1)

    for y in range_sy:
        color = layer.get_pixel(sx, y)
        _, _, _, a = color.get_rgba()

        if a == 0:
            continue

        for tx in range_tx:
            layer.set_pixel(tx, y, color)


def _fill_pixels_corner(layer: Gimp.Layer, x: int, y: int, dx: int, dy: int):
    end_x = max(0, min(x + dx, layer.get_width()))
    end_y = max(0, min(y + dy, layer.get_width()))

    range_x = range(end_x, x) if x > end_x else range(x + 1, end_x + 1)
    range_y = range(end_y, y) if y > end_y else range(y + 1, end_y + 1)

    color = layer.get_pixel(x, y)
    _, _, _, a = color.get_rgba()
    if a == 0:
        return

    for tx in range_x:
        for ty in range_y:
            layer.set_pixel(tx, ty, color)


def _export_lq(
        procedure: Gimp.Procedure,
        config: Gimp.ProcedureConfig,
        source_image: Gimp.Image,
        path: str
) -> Gimp.ValueArray | None:
    if not config.get_property("lq-export"):
        return None

    scaling = config.get_property("lq-scaling")
    if scaling < 1:
        return gimp_error.calling(procedure, "Scaling cannot be less than 1")

    wid, hei = source_image.get_width(), source_image.get_height()

    if wid % scaling != 0 or hei % scaling != 0:
        return gimp_error.calling(procedure, f"Image size {wid}x{hei} not divisible by {scaling}")

    image = source_image.duplicate()
    image.flatten()

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
