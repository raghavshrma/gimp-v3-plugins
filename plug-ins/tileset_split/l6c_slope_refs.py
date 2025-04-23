import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp
from datetime import  datetime

import utils
from tileset_collection import TilesetSource, TilesetTargetGroup
from tileset_builder import Builder


def handle(image: Gimp.Image, sample: Gimp.Layer, config: Gimp.ProcedureConfig):
    # utils.find_or_create_layer(image, "l6-slopes", 4, 8, utils.get_main_group(image))
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

    _build_slopes_6(builder, 6, x + 0 * dx, y + 2 * dy)
    _build_slopes_7(builder, 7, x + 1 * dx, y + 2 * dy)
    _build_slopes_8(builder, 8, x + 0 * dx, y + 3 * dy)
    _build_slopes_9(builder, 9, x + 1 * dx, y + 3 * dy)

    Gimp.message(f"Built connector references in {datetime.now() - start}")

    builder.cleanup()

def _build_slopes_6(bld: Builder, idx: int, x: int, y: int):
    t_raw = _get_raw_group(bld, idx, x, y)
    _add_raw_source(bld, t_raw, 2)
    t_raw.add(2, 2, bld.inner_corner_tl_extra())
    t_raw.add(4, 2, bld.inner_corner_tr_extra())
    t_raw.finalise()

    t_ref = _get_ref_group(bld, idx, x, y)
    t_ref.add(1, 2, bld.single_h_full())
    t_ref.add(2, 3, bld.block_connect_3_left())
    t_ref.add(4, 3, bld.block_connect_3_right())
    t_ref.add(5, 2, bld.single_h_full())

    t_ref.finalise()

def _build_slopes_7(bld: Builder, idx: int, x: int, y: int):
    t_raw = _get_raw_group(bld, idx, x, y)
    _add_raw_source(bld, t_raw, 3)
    t_raw.add(2, 2, bld.inner_corner_tl_extra())
    t_raw.add(4, 2, bld.inner_corner_tr_extra())
    t_raw.finalise()

    t_ref = _get_ref_group(bld, idx, x, y)
    t_ref.add(3, 1, bld.single_h_full())
    t_ref.add(1, 2, bld.single_h_full())
    t_ref.add(2, 3, bld.block_connect_3_left())
    t_ref.add(4, 3, bld.block_connect_3_right())
    t_ref.add(5, 2, bld.single_h_full())


    t_ref.finalise()

def _build_slopes_8(bld: Builder, idx: int, x: int, y: int):
    t_raw = _get_raw_group(bld, idx, x, y)
    _add_raw_source(bld, t_raw, 4)
    t_raw.add(2, 2, bld.inner_corner_tl_extra())
    t_raw.add(4, 2, bld.inner_corner_tr_extra())
    t_raw.finalise()

    t_ref = _get_ref_group(bld, idx, x, y)
    t_ref.add(3, 1, bld.edge_top_full())

    t_ref.add(1, 2, bld.single_h_full())
    t_ref.add(2, 3, bld.block_connect_5_left())
    t_ref.add(3, 3, bld.center_light())
    t_ref.add(4, 3, bld.block_connect_5_right())
    t_ref.add(5, 2, bld.single_h_full())

    t_ref.finalise()

def _build_slopes_9(bld: Builder, idx: int, x: int, y: int):
    t_raw = _get_raw_group(bld, idx, x, y)
    t_raw.add(2, 2, [bld.inner_corner_tl()])
    t_raw.add(4, 2, [bld.inner_corner_tr()])
    t_raw.add(2, 4, [bld.inner_corner_bl()])
    t_raw.add(4, 4, [bld.inner_corner_br()])
    t_raw.finalise()

    t_ref = _get_ref_group(bld, idx, x, y)
    source = TilesetSource(bld.image, f"l6-slopes-raw-4", t_ref.group)

    t_ref.add(2, 1, source.copy(2, 2))
    t_ref.add(3, 1, bld.edge_top())
    t_ref.add(4, 1, source.copy(4, 2))

    t_ref.add(1, 1, source.copy_block2(2, 1, 1, 2))
    t_ref.add(3, 2, bld.center_light())
    t_ref.add(5, 1, source.copy_block2(4, 1, 1, 2))

    t_ref.add(1, 3, bld.edge_left())
    t_ref.add(2, 3, bld.deep_left())
    t_ref.add(3, 3, bld.center_dark())
    t_ref.add(4, 3, bld.deep_right())
    t_ref.add(5, 3, bld.edge_right())

    t_ref.add(1, 4, source.copy(2, 4))
    t_ref.add(3, 4, bld.center_light())
    t_ref.add(5, 4, source.copy(4, 4))

    t_ref.add(2, 5, source.copy(2, 4))
    t_ref.add(3, 5, bld.edge_bottom())
    t_ref.add(4, 5, source.copy(4, 4))

    t_ref.finalise()

def _get_raw_group(builder: Builder, idx: int, x: int, y: int):
    name = f"l6-slopes-raw-{idx}"
    return builder.get_target_group(name, x, y, 5, 5)

def _add_raw_source(builder: Builder, t_raw: TilesetTargetGroup, source_idx: int):
    base = TilesetSource(builder.image, f"l6-slopes-raw-{source_idx}", t_raw.group)
    t_raw.add(1, 1, base.copy_block2(1, 1, 5, 3))

def _get_ref_group(builder: Builder, idx: int, x: int, y: int):
    name = f"l6-slopes-ref-{idx}"
    return builder.get_target_group(name, x, y, 5, 5)