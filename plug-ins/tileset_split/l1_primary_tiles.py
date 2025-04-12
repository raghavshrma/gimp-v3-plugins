import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp, Gegl

import utils

def handle(image: Gimp.Image, sample: Gimp.Layer, config: Gimp.ProcedureConfig):
    ref_group = utils.create_ref_group(image, sample)
    grid = int(image.grid_get_spacing()[1])
    _build_horizontal_layer(image, ref_group, grid)
    _build_vertical_layer(image, ref_group, grid)


def _build_horizontal_layer(image: Gimp.Image, group: Gimp.GroupLayer,  grid: int):
    layer = utils.find_layer(image, "l0-h-1-primary")

    if layer.get_width() != grid:
        layer.resize(grid, grid * 3, -grid, 0)

    utils.offset_wrap(layer, grid // 2, 0)

    ref_1 = layer.copy()
    ref_2 = layer.copy()
    image.insert_layer(ref_1, group, 0)
    image.insert_layer(ref_2, group, 0)
    _, off_x, off_y = layer.get_offsets()

    off_x += grid * 5
    ref_1.set_offsets(off_x, off_y)
    ref_2.set_offsets(off_x + grid * 2, off_y)

    ref_layer = image.merge_down(ref_2, Gimp.MergeType.EXPAND_AS_NECESSARY)
    ref_layer.set_name("l1-h-ref")

def _build_vertical_layer(image: Gimp.Image, parent: Gimp.GroupLayer,  grid: int):
    layer = utils.find_layer(image, "l0-v-1-primary")

    if layer.get_height() != grid:
        layer.resize(grid * 3, grid, 0, -grid)

    utils.offset_wrap(layer, 0, grid // 2)

    ref_1 = layer.copy()
    ref_2 = layer.copy()
    image.insert_layer(ref_1, parent, 0)
    image.insert_layer(ref_2, parent, 0)
    _, off_x, off_y = layer.get_offsets()

    off_x += grid * 5
    ref_1.set_offsets(off_x, off_y)
    ref_2.set_offsets(off_x, off_y + grid * 2)

    ref_layer = image.merge_down(ref_2, Gimp.MergeType.EXPAND_AS_NECESSARY)
    ref_layer.set_name("l1-v-ref")
