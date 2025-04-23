import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp
from datetime import  datetime

import utils
from tileset_collection import TilesetSource, TilesetTargetGroup
from tileset_builder import Builder


def handle(image: Gimp.Image, sample: Gimp.Layer, config: Gimp.ProcedureConfig):
    utils.find_or_create_layer(image, "l6-slopes", 4, 8, utils.get_main_group(image))
    g = utils.get_grid_size(image)
    target = TilesetTargetGroup(image, "l9-tileset", None, 13, 12, 7 * g * 0, 8 * g * 0, True)
    builder = Builder(image, sample, target.group)
    start = datetime.now()

    builder.setup_block_edges()
    builder.setup_variations()
    builder.setup_block_corners()
    builder.setup_block_singles()
    builder.setup_block_connectors()

    _build_plus(builder, target)
    _build_corners(builder, target)
    _build_block_connectors(builder, target)

    target.finalise()
    builder.cleanup()
    sample.get_parent().set_visible(False)

    Gimp.message(f"Built primary tileset in {datetime.now() - start}")

def _build_plus(builder: Builder, target: TilesetTargetGroup):
    for i in range(1, 5):
        target.add(1 + i, 1, builder.var_top_full(i))
        target.add(1 + i, 7, builder.var_bottom(i))
        target.add(1 + i, 8, builder.var_single_h(i))

    for i in range(1, 4):
        target.add(1, 2 + i, builder.var_left(i))
        target.add(6, 2 + i, builder.var_right(i))
        target.add(7, 2 + i, builder.var_single_v(i))
        target.add(2, 2 + i, builder.src_sample.copy_block2(2, 2 + i, 4, 1))

    i = 3 # Fixme - add 1 more vertical variation
    target.add(1, 3 + i, builder.var_left(i))
    target.add(6, 3 + i, builder.var_right(i))
    target.add(7, 3 + i, builder.var_single_v(i))
    target.add(2, 3 + i, builder.src_sample.copy_block2(2, 2 + i, 4, 1))


def _build_corners(builder: Builder, target: TilesetTargetGroup):
    target.add(1, 1, builder.outer_corner_tl_full())
    target.add(6,1, builder.outer_corner_tr_full())
    target.add(1, 7, builder.outer_corner_bl())
    target.add(6, 7, builder.outer_corner_br())

    target.add(7, 1, builder.single_v_top_full())
    target.add(7, 7, builder.single_v_bottom())
    target.add(1, 8, builder.single_h_left())
    target.add(6, 8, builder.single_h_right())

def _build_block_connectors(builder: Builder, target: TilesetTargetGroup):
    target.add(8, 1, builder.src_inner_corners.copy_block2(1, 1, 2, 3))
    target.add(8, 4, builder.block_connector_all(7))
    target.add(8, 6, builder.block_connector_all(5))
    target.add(7, 8, builder.block_connector(6, 2))
    target.add(8, 8, builder.block_connector(6, 1))
    target.add(9, 8, builder.block_connector(6, 3))

    target.add(10, 1, builder.block_connector_all(1))
    target.add(10, 3, builder.block_connector_all(2))
    target.add(10, 5, builder.block_connector_all(3))
    target.add(10, 7, builder.block_connector_all(4))
