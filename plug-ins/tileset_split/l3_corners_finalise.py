import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

import utils


def handle(image: Gimp.Image, sample: Gimp.Layer, config: Gimp.ProcedureConfig):
    _hide_prev_layers(image)
    _finalise_outer_corners(image, sample)
    _finalise_inner_corners(image, sample)


def _hide_prev_layers(image: Gimp.Image):
    utils.hide_layer(image, "l2-inner-ground-filler")
    utils.hide_layer(image, "l2-inner-corners-ref")
    utils.hide_layer(image, "l2-outer-corners-ref")


def _finalise_outer_corners(image: Gimp.Image, sample: Gimp.Layer):
    raw = utils.find_layer(image, "l2-outer-corners-raw", True)
    if raw is None:
        return

    utils.remove_layer(image, "l2-outer-corners")
    raw.set_visible(True)
    main_group = utils.get_main_group(image)
    g = utils.get_grid_size(image)
    wid = sample.get_width()
    off_x, off_y = 0, 0

    # Top-Left Corner
    l = utils.copy(image, raw, main_group, g, g * 2, 0, 0)
    l.set_offsets(off_x, off_y)
    l.set_name("l2-outer-corners")

    # Top-Right Corner
    l = utils.copy(image, raw, main_group, g, g * 2, -2 * g, 0)
    l.set_offsets(off_x + wid - g, off_y)
    utils.merge_down(image, l)

    # Bottom-Left Corner
    l = utils.copy(image, raw, main_group, g, g, 0, -3 * g)
    l.set_offsets(off_x, off_y + 2 * g)
    utils.merge_down(image, l)

    # Bottom-Right Corner
    l = utils.copy(image, raw, main_group, g, g, -2 * g, -3 * g)
    l.set_offsets(off_x + wid - g, off_y + 2 * g)
    l = utils.merge_down(image, l)

    raw.set_visible(False)


def _finalise_inner_corners(image: Gimp.Image, sample: Gimp.Layer):
    raw = utils.find_layer(image, "l2-inner-corners-raw", True)
    if raw is None:
        return

    raw.set_visible(True)
    utils.remove_layer(image, "l2-inner-corners")
    main_group = utils.get_main_group(image)
    g = utils.get_grid_size(image)
    off_x, off_y = 0, sample.get_height() + g

    # Top-Left Corner
    l = utils.copy(image, raw, main_group, g, g, 0, 0)
    l.set_offsets(off_x, off_y)
    # l.set_name("l2-inner-corners-2")

    l = utils.copy(image, raw, main_group, g, g, -2 * g, 0)
    l.set_offsets(off_x + g, off_y)
    utils.merge_down(image, l)

    l = utils.copy(image, raw, main_group, g, 2 * g, 0, -2 * g)
    l.set_offsets(off_x, off_y + g)
    utils.merge_down(image, l)

    l = utils.copy(image, raw, main_group, g, 2 * g, -2 * g, -2 * g)
    l.set_offsets(off_x + g, off_y + g)
    l = utils.merge_down(image, l)

    l.set_name("l2-inner-corners")
    raw.set_visible(False)
    utils.hide_layer(image, "l2-inner-corners-raw-h")
    utils.hide_layer(image, "l2-inner-corners-raw-v")

    _build_inner_corners_ref(image, sample, l)


def _build_inner_corners_ref(image: Gimp.Image, sample: Gimp.Layer, corners: Gimp.Layer):
    utils.remove_layer(image, "l3-inner-corners-ref")
    ref_group = utils.get_ref_group(image, 1)
    g = utils.get_grid_size(image)
    off_x, off_y = sample.get_width() + g, 0

    l = utils.copy(image, corners, ref_group, g, g * 3, -g, 0)
    l.set_offsets(off_x, off_y)
    l.set_name("l3-inner-corners-ref")

    l = utils.copy(image, corners, ref_group, g, g * 3, 0, 0)
    l.set_offsets(off_x + 2 * g, off_y)
    utils.merge_down(image, l)



