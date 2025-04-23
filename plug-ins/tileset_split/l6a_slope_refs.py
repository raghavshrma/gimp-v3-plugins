import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp
from datetime import  datetime

import utils
from tileset_collection import TilesetSource, TilesetTargetGroup
from tileset_builder import Builder


def handle(image: Gimp.Image, sample: Gimp.Layer, config: Gimp.ProcedureConfig):
    utils.find_or_create_layer(image, "l6-slopes", 4, 8, utils.get_main_group(image))
    group = utils.get_ref_group(image, 6)
    builder = Builder(image, sample, group)
    builder.parent.set_visible(True)
    g = utils.get_grid_size(image)
    x, y = 6 * g, 2 * g
    dx, dy = 6 * g, 4 * g

    start = datetime.now()

    builder.setup_block_edges()
    builder.setup_block_corners()
    builder.setup_block_singles()
    builder.setup_block_connectors_base()
    builder.setup_block_connectors()
    # builder.setup_slope_connectors()

    _build_slopes_4(builder, 4, x + 0 * dx, y + 0 * dy)

    Gimp.message(f"Built connector references in {datetime.now() - start}")

    builder.cleanup()

def _build_slopes_4(bld: Builder, idx: int, x: int, y: int):
    t_raw = _get_raw_group(bld, idx, x, y)

    t_raw.add(2, 1, bld.outer_corner_tl_full())
    t_raw.add(4, 1, bld.outer_corner_tr_full())
    t_raw.add(2, 4, [bld.outer_corner_bl()])
    t_raw.add(4, 4, [bld.outer_corner_br()])
    t_raw.finalise()

    t_ref = _get_ref_group(bld, idx, x, y)
    t_ref.add(3, 1, bld.edge_top_full())
    t_ref.add(2, 3, bld.edge_left())
    t_ref.add(3, 3, bld.center_light())
    t_ref.add(4, 3, bld.edge_right())
    t_ref.add(3, 4, bld.edge_bottom())

    t_ref.finalise()

def _get_raw_group(builder: Builder, idx: int, x: int, y: int):
    name = f"l6-slopes-raw-{idx}"
    return builder.get_target_group(name, x, y, 5, 5)

def _get_ref_group(builder: Builder, idx: int, x: int, y: int):
    name = f"l6-slopes-ref-{idx}"
    return builder.get_target_group(name, x, y, 5, 5)