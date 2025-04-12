import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

import utils


def handle(image: Gimp.Image, sample: Gimp.Layer, config: Gimp.ProcedureConfig):
    source = utils.find_layer(image, "l4-singles-hv-1-tile-ref")
    h1 = _finalise_h1(image, source)
    v1 = _finalise_v1(image, source)
    _build_ref_tiles(image, sample, h1, v1)


def _finalise_h1(image: Gimp.Image, source: Gimp.Layer):
    target = utils.find_layer(image, "l4-singles-h-1")
    g = utils.get_grid_size(image)

    h1 = utils.replace(image, source, target)
    h1.resize(g, g * 2, -g, 0)
    utils.offset_wrap(h1, g // 2, 0)
    h1.resize(g * 3, g * 3, g, 0)
    return h1

def _finalise_v1(image: Gimp.Image, source: Gimp.Layer):
    target = utils.find_layer(image, "l4-singles-v-1")
    g = utils.get_grid_size(image)

    v1 = utils.replace(image, source, target)
    v1.resize(g, g, -g, -2 * g)
    utils.offset_wrap(v1, 0, g // 2)
    v1.resize(g * 3, g * 3, g, g)
    utils.change_offset(v1, 0, -g)
    return v1

def _build_ref_tiles(image: Gimp.Image, sample: Gimp.Layer, h1: Gimp.Layer, v1: Gimp.Layer):
    g = utils.get_grid_size(image)
    off_x, off_y = sample.get_width() * 2, g * 3
    ref_group = utils.get_ref_group(image, 4)

    l = utils.copy(image, h1, ref_group, g, g * 2, -g, 0)
    l.set_offsets(off_x, off_y)
    l.set_name("l4c-singles-h-tile-ref")

    l = utils.copy(image, h1, ref_group, g, g * 2, -g, 0)
    l.set_offsets(off_x + 2 * g, off_y)
    l = utils.merge_down(image, l)

    l.resize(3 * g, 3 * g, 0, 0)

    l = utils.copy(image, v1, ref_group, g, g, -g, -g)
    l.set_offsets(off_x + g, off_y)
    l.set_name("l4c-singles-v-tile-ref")

    l = utils.copy(image, v1, ref_group, g, g, -g, -g)
    l.set_offsets(off_x + g, off_y + 2 * g)
    l = utils.merge_down(image, l)

    l.resize(3 * g, 3 * g, g, 0)
