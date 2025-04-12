import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

import utils


def handle(image: Gimp.Image, sample: Gimp.Layer, config: Gimp.ProcedureConfig):
    g = utils.get_grid_size(image)
    ref_group = utils.get_ref_group(image, 4)
    off_x, off_y = sample.get_width() * 2, 0

    h_layer = utils.find_layer(image, "l4-singles-h-1")
    l = utils.copy(image, h_layer, ref_group, g, g * 2, -g, 0)
    l.set_offsets(off_x, off_y)
    l.set_name("l4-singles-hv-1-tile-ref")
    utils.offset_wrap(l, g // 2, 0)

    v_layer = utils.find_layer(image, "l4-singles-v-1")
    l = utils.copy(image, v_layer, ref_group, g, g, -g, -g)
    l.set_offsets(off_x, off_y + 2 * g)
    utils.offset_wrap(l, 0, g // 2)
    l = utils.merge_down(image, l)
    l.resize(g * 3, g * 3, g, 0)
