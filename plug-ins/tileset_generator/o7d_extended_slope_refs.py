import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp
from datetime import datetime

import utils
from tileset_collection import TilesetSource, TilesetTargetGroup
from tileset_builder import Builder


def handle(image: Gimp.Image, sample: Gimp.Layer, config: Gimp.ProcedureConfig):
    utils.find_or_create_layer(image, "l6-slopes", 4, 8, utils.get_main_group(image))
    group = utils.get_ref_group(image, 6)
    builder = Builder(image, sample, group)
    builder.target_root.set_visible(True)
    g = utils.get_grid_size(image)
    x, y = 6 * g, 3 * g
    dx, dy = 7 * g, 5 * g

    start = datetime.now()

    builder.setup_edges()
    builder.setup_corners()
    builder.setup_singles()
    builder.setup_transition_tiles()
    builder.setup_connectors()
    # builder.setup_slope_connectors()

    _build_slopes_1(builder, 1, x + 0 * dx, y + 0 * dy)
    _build_slopes_2(builder, 2, x + 1 * dx, y + 0 * dy)

    Gimp.message(f"Built connector references in {datetime.now() - start}")

    builder.cleanup()


def _build_slopes_1(bld: Builder, idx: int, x: int, y: int):
    t_raw = _get_raw_group(bld, idx, x, y)
    t_raw.add(2, 2, [bld.edge_left(), bld.in_corner_tl_ext()])
    t_raw.add(3, 1, bld.edge_top_full())
    t_raw.add(5, 1, bld.edge_top_full())
    t_raw.add(6, 2, [bld.edge_right(), bld.in_corner_tr_ext()])
    t_raw.add(2, 4, bld.edge_left())
    t_raw.add(3, 4, bld.edge_bottom())
    t_raw.add(5, 4, bld.edge_bottom())
    t_raw.add(6, 4, bld.edge_right())
    t_raw.finalize()

    t_ref = _get_ref_group(bld, idx, x, y)
    t_ref.add(4, 1, bld.edge_top_full())

    t_ref.add(1, 2, bld.single_h_full())
    t_ref.add(2, 3, bld.block_connect_5_left())
    t_ref.add(3, 3, bld.deep_edge_left())
    t_ref.add(4, 3, bld.deep_dark())
    t_ref.add(5, 3, bld.deep_edge_right())
    t_ref.add(6, 3, bld.block_connect_5_right())
    t_ref.add(7, 2, bld.single_h_full())

    t_ref.add(4, 4, bld.edge_bottom())

    t_ref.finalize()


def _build_slopes_2(bld: Builder, idx: int, x: int, y: int):
    t_raw = _get_raw_group(bld, idx, x, y)
    t_raw.add(2, 2, bld.edge_left())
    t_raw.add(3, 1, bld.edge_top_full())
    t_raw.add(5, 1, bld.edge_top_full())
    t_raw.add(6, 2, bld.edge_right())
    t_raw.add(2, 4, bld.edge_left())
    t_raw.add(3, 4, bld.edge_bottom())
    t_raw.add(5, 4, bld.edge_bottom())
    t_raw.add(6, 4, bld.edge_right())
    t_raw.finalize()

    t_ref = _get_ref_group(bld, idx, x, y)
    t_ref.add(
        4, 1, [bld.single_v(), bld.in_corner_tl_ext(), bld.in_corner_tr_ext()]
    )
    t_ref.add(4, 2, bld.block_connect_5_up())

    t_ref.add(2, 3, bld.edge_left())
    t_ref.add(3, 3, bld.deep_edge_left())
    t_ref.add(4, 3, bld.deep_dark())
    t_ref.add(5, 3, bld.deep_edge_right())
    t_ref.add(6, 3, bld.edge_right())

    t_ref.add(4, 4, bld.block_connect_5_down())
    t_ref.add(4, 5, bld.single_v())

    t_ref.finalize()


def _get_raw_group(builder: Builder, idx: int, x: int, y: int):
    name = f"l6-slopes-{idx}-raw"
    return builder.get_target_group(name, x, y, 7, 5)


def _get_ref_group(builder: Builder, idx: int, x: int, y: int):
    name = f"l6-slopes-{idx}-ref"
    return builder.get_target_group(name, x, y, 7, 5)
