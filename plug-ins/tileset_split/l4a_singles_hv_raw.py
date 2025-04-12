import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

import utils


def handle(image: Gimp.Image, sample: Gimp.Layer, config: Gimp.ProcedureConfig):
    _hide_prev_layers(image)
    _build_refs_h(image, sample)
    _build_refs_v(image, sample)


def _hide_prev_layers(image: Gimp.Image):
    utils.hide_layer(image, "l3-inner-corners-ref")


def _build_refs_h(image: Gimp.Image, sample: Gimp.Layer):
    g = utils.get_grid_size(image)
    f = g // 2

    ref_group = utils.get_ref_group(image, 4)
    main_group = utils.get_main_group(image)
    off_x, off_y = sample.get_width(), 0

    cols = sample.get_width() // g

    for i in range(1, cols - 1):
        h_layer = utils.get_plus_layer(image, "h", i)

        l = utils.copy(image, h_layer, main_group, g, g + f, -g, 0)
        l.set_offsets(off_x + i * g, off_y)
        l.set_name(f"l4-singles-h-{i}")

        l = utils.copy(image, h_layer, main_group, g, f, -g, -2 * g - f)
        l.set_offsets(off_x + i * g, off_y + g + f)
        l = utils.merge_down(image, l)
        l.resize(g * 3, g * 3, g, 0)

        l = utils.copy(image, h_layer, ref_group, g, g * 2, -g, 0)
        l.set_offsets(off_x + i * g, off_y + 2 * g)
        l.set_name(f"l4-singles-h-top-ref-{i}")
        l.resize(3 * g, 3 * g, g, 0)

        l = utils.copy(image, h_layer, ref_group, g, g, -g, -2 * g)
        l.set_offsets(off_x + i * g, off_y + 4 * g)
        l.set_name(f"l4-singles-h-down-ref-{i}")
        l.resize(3 * g, 3 * g, g, g)

def _build_refs_v(image: Gimp.Image, sample: Gimp.Layer):
    g = utils.get_grid_size(image)
    f = g // 2

    ref_group = utils.get_ref_group(image, 4)
    main_group = utils.get_main_group(image)
    off_x, off_y = 4 * g, 3 * g

    rows = sample.get_height() // g

    for i in range(1, rows - 1):
        v_layer = utils.get_plus_layer(image, "v", i)

        l = utils.copy(image, v_layer, main_group, f, g, 0, -g)
        l.set_offsets(off_x, off_y + i * g)
        l.set_name(f"l4-singles-v-{i}")

        l = utils.copy(image, v_layer, main_group, f, g, -2 * g - f, -g)
        l.set_offsets(off_x + f, off_y + i * g)
        l = utils.merge_down(image, l)
        l.resize(g * 3, g * 3, g, g)

        l = utils.copy(image, v_layer, ref_group, g, g, 0, -g)
        l.set_offsets(off_x + 3 * g, off_y + (2 + i) * g)
        l.set_name(f"l4-singles-v-left-ref-{i}")
        l.resize(3 * g, 3 * g, g, g)

        l = utils.copy(image, v_layer, ref_group, g, g, -2 * g, -g)
        l.set_offsets(off_x + 4 * g, off_y + (2 + i) * g)
        l.set_name(f"l4-singles-v-right-ref-{i}")
        l.resize(3 * g, 3 * g, g, g)
