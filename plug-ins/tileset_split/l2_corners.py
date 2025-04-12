import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

import utils


def handle(image: Gimp.Image, sample: Gimp.Layer, config: Gimp.ProcedureConfig):
    sample.set_visible(True)
    _hide_prev_layers(image)
    ref_group = utils.get_ref_group(image, 1)
    _build_outer_corners(image, sample)
    _build_outer_corners_ref(image, sample, ref_group)
    ref_layer = _build_inner_corners_ref(image, sample, ref_group)
    _build_inner_ground_filler(image, ref_layer)
    _build_inner_corners(image, ref_layer)
    sample.set_visible(False)

def _hide_prev_layers(image: Gimp.Image):
    layer = utils.find_layer(image, "l1-v-ref")
    layer.set_visible(False)

    layer = utils.find_layer(image, "l1-h-ref")
    layer.set_visible(False)


def _build_outer_corners(image: Gimp.Image, sample: Gimp.Layer):
    # 1. Pick the corner tiles from the sample and add to the l0-group
    g = utils.get_grid_size(image)
    main_group = utils.get_main_group(image)
    wid, hei = sample.get_width(), sample.get_height()
    off_x, off_y = wid, 0

    c1 = utils.copy(image, sample, main_group, g, g * 2, 0, 0)
    c1.set_offsets(off_x, off_y)
    c1.set_name("l2-outer-corners-raw")

    c2 = utils.copy(image, sample, main_group, g, g * 2, g - wid, 0)
    c2.set_offsets(off_x + g * 2, off_y)
    image.merge_down(c2, Gimp.MergeType.EXPAND_AS_NECESSARY)

    c3 = utils.copy(image, sample, main_group, g, g, 0, g - hei)
    c3.set_offsets(off_x, off_y + g * 3)
    image.merge_down(c3, Gimp.MergeType.EXPAND_AS_NECESSARY)

    c4 = utils.copy(image, sample, main_group, g, g, g - wid, g - hei)
    c4.set_offsets(off_x + g * 2, off_y + g * 3)
    image.merge_down(c4, Gimp.MergeType.EXPAND_AS_NECESSARY)


def _build_outer_corners_ref(image: Gimp.Image, sample: Gimp.Layer, ref_group: Gimp.GroupLayer):
    g = utils.get_grid_size(image)
    wid, hei = sample.get_width(), sample.get_height()
    off_x, off_y = wid, 0

    # 2. Create the reference layer
    h_layer = utils.get_primary(image, "h")
    v_layer = utils.get_primary(image, "v")

    h1 = utils.copy(image, h_layer, ref_group, g, g * 2, 0, 0)
    h1.set_offsets(off_x + g, off_y)
    h1.set_name("l2-outer-corners-ref")

    h2 = utils.copy(image, h_layer, ref_group, g, g, 0, -2 * g)
    h2.set_offsets(off_x + g, off_y + g * 3)
    image.merge_down(h2, Gimp.MergeType.EXPAND_AS_NECESSARY)

    v1 = utils.copy(image, v_layer, ref_group, g, g, 0, 0)
    v1.set_offsets(off_x, off_y + g * 2)
    image.merge_down(v1, Gimp.MergeType.EXPAND_AS_NECESSARY)

    v2 = utils.copy(image, v_layer, ref_group, g, g, -2 * g, 0)
    v2.set_offsets(off_x + g * 2, off_y + g * 2)
    image.merge_down(v2, Gimp.MergeType.EXPAND_AS_NECESSARY)


def _build_inner_corners_ref(image: Gimp.Image, sample: Gimp.Layer, ref_group: Gimp.GroupLayer):
    g = utils.get_grid_size(image)
    wid, hei = sample.get_width(), sample.get_height()
    off_x, off_y = wid, g * 5

    # 2. Create the reference layer
    h_layer = utils.get_primary(image, "h")
    v_layer = utils.get_primary(image, "v")

    h1 = utils.copy(image, h_layer, ref_group, g, g * 2, 0, 0)
    h1.set_offsets(off_x + g, off_y + 2 * g)
    h1.set_name("l2-inner-corners-ref")

    h2 = utils.copy(image, h_layer, ref_group, g, g, 0, -2 * g)
    h2.set_offsets(off_x + g, off_y)
    image.merge_down(h2, Gimp.MergeType.EXPAND_AS_NECESSARY)

    v1 = utils.copy(image, v_layer, ref_group, g, g, 0, 0)
    v1.set_offsets(off_x + g * 2, off_y + g)
    image.merge_down(v1, Gimp.MergeType.EXPAND_AS_NECESSARY)

    v2 = utils.copy(image, v_layer, ref_group, g, g, -2 * g, 0)
    v2.set_offsets(off_x, off_y + g)
    return image.merge_down(v2, Gimp.MergeType.EXPAND_AS_NECESSARY)


def _build_inner_corners(image: Gimp.Image, ref_layer: Gimp.Layer):
    g = utils.get_grid_size(image)
    main_group = utils.get_main_group(image)
    _, off_x, off_y = ref_layer.get_offsets()
    off_x += g * 4

    # sides row of inner corners - to top
    l = utils.copy(image, ref_layer, main_group, g * 3, g, 0, -g)
    l.set_offsets(off_x, off_y)
    l.set_name("l2-inner-corners-raw-v")

    # sides row of inner corners - to bottom
    l = utils.copy(image, ref_layer, main_group, g * 3, g, 0, -g)
    l.set_offsets(off_x, off_y + 3 * g)
    l = image.merge_down(l, Gimp.MergeType.EXPAND_AS_NECESSARY)

    image.select_rectangle(Gimp.ChannelOps.REPLACE, off_x + g, off_y, g, g * 4)
    l.edit_clear()
    Gimp.Selection.none(image)

    # top-down rows of inner corners - to left
    l = utils.copy(image, ref_layer, main_group, g, g * 4, -g, 0)
    l.set_offsets(off_x, off_y - g * 5)
    l.set_name("l2-inner-corners-raw-h")

    l = utils.copy(image, ref_layer, main_group, g, g * 4, -g, 0)
    l.set_offsets(off_x + 2 * g, off_y - g * 5)
    image.merge_down(l, Gimp.MergeType.EXPAND_AS_NECESSARY)

def _build_inner_ground_filler(image: Gimp.Image, ref_layer: Gimp.Layer):
    g = utils.get_grid_size(image)
    # noinspection PyTypeChecker
    ref_group: Gimp.GroupLayer = ref_layer.get_parent()
    _, off_x, off_y = ref_layer.get_offsets()
    off_x += g * 4

    v_layer = utils.get_plus_layer(image, "v", 2)

    l = utils.copy(image, v_layer, ref_group, g, g, 0, -g)
    l.set_offsets(off_x + 2 * g, off_y + g * 2)
    l.set_name("l2-inner-ground-filler")

    l = utils.copy(image, v_layer, ref_group, g, g, -2 * g, -g)
    l.set_offsets(off_x, off_y + g * 2)
    l = image.merge_down(l, Gimp.MergeType.EXPAND_AS_NECESSARY)

    l.resize(g * 3, g * 4, 0, 2 * g)
