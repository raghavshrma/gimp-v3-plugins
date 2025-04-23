import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

import utils
from tileset_builder import Builder
from datetime import datetime


def handle(image: Gimp.Image, sample: Gimp.Layer, config: Gimp.ProcedureConfig):
    group = utils.get_ref_group(image, 5)
    builder = Builder(image, sample, group)
    builder.parent.set_visible(True)
    g = utils.get_grid_size(image)
    x, y = 6 * g, 5 * g
    dx, dy = 6 * g, 5 * g

    start = datetime.now()

    utils.find_or_create_layer(image, "l5-block-connectors", 4, 8, utils.get_main_group(image))

    builder.setup_block_edges()
    builder.setup_block_corners()
    builder.setup_block_singles()
    builder.setup_block_connectors_base()
    builder.setup_block_connectors()
    builder.setup_variations()

    # _build_type_1(builder, 1, x + 0 * dx, y + 0 * dy)
    # _build_type_2(builder, 2, x + 1 * dx, y + 0 * dy)
    _build_type_3(builder, 3, x + 0 * dx, y + 1 * dy)
    # _build_type_4(builder, 4, x + 1 * dx, y + 1 * dy)
    # _build_type_5(builder, 5, x + 0 * dx, y + 2 * dy)
    # _build_type_6(builder, 6, x + 1 * dx, y + 2 * dy)
    # _build_type_7(builder, 7, x - 1 * dx, y + 1 * dy)
    # _build_type_8(builder, 8, x - 1 * dx, y + 2 * dy)

    Gimp.message(f"Built connector references in {datetime.now() - start}")

    builder.cleanup()


def _build_type_1(bld: Builder, idx: int, x: int, y: int):
    t_raw = _get_raw_group(bld, idx, x, y)
    t_raw.add(2, 2, [
        bld.inner_corner_bl(),
        bld.d(2), bld.d(7),
        bld.c(3), bld.a(1),
        bld.block_connector(idx, 1),
    ])

    t_raw.add(4, 2, [
        bld.inner_corner_br(),
        bld.d(1), bld.d(8),
        bld.c(2), bld.a(1),
        bld.block_connector(idx, 2),
    ])

    t_raw.add(2, 4, [
        bld.inner_corner_tl(),
        bld.d(3), bld.d(6),
        bld.c(3), bld.a(4),
        bld.block_connector(idx, 3),
    ])

    t_raw.add(4, 4, [
        bld.inner_corner_tr(),
        bld.d(4), bld.d(5),
        bld.c(2), bld.a(4),
        bld.block_connector(idx, 4),
    ])

    t_raw.finalise()

    t_ref = _get_ref_group(bld, idx, x, y)
    t_ref.add(1, 1, bld.single_h_full())
    t_ref.add(2, 1, bld.edge_top_extra())
    t_ref.add(3, 1, bld.edge_top_full())
    t_ref.add(4, 1, bld.edge_top_extra())
    t_ref.add(5, 1, bld.single_h_full())

    t_ref.add(2, 3, [bld.edge_left(), bld.inner_corner_tl_extra()])
    t_ref.add(3, 3, bld.center_light())
    t_ref.add(4, 3, [bld.edge_right(), bld.inner_corner_tr_extra()])

    t_ref.add(1, 3, bld.single_h_full())
    t_ref.add(3, 4, bld.edge_bottom())
    t_ref.add(5, 3, bld.single_h_full())

    t_ref.finalise()


def _build_type_2(bld: Builder, idx: int, x: int, y: int):
    t_raw = _get_raw_group(bld, idx, x, y)
    t_raw.add(2, 2, [
        bld.inner_corner_tr(),
        bld.d(2), bld.d(7),
        bld.c(1), bld.a(3),
        bld.block_connector(idx, 1),
    ])

    t_raw.add(4, 2, [
        bld.inner_corner_tl(),
        bld.d(1), bld.d(8),
        bld.c(1), bld.a(2),
        bld.block_connector(idx, 2),
    ])

    t_raw.add(2, 4, [
        bld.inner_corner_br(),
        bld.d(3), bld.d(6),
        bld.c(4), bld.a(3),
        bld.block_connector(idx, 3),
    ])

    t_raw.add(4, 4, [
        bld.inner_corner_bl(),
        bld.d(4), bld.d(5),
        bld.c(4), bld.a(2),
        bld.block_connector(idx, 4),
    ])

    t_raw.finalise()

    t_ref = _get_ref_group(bld, idx, x, y)
    t_ref.add(2, 1, [bld.single_v(), bld.inner_corner_tr_extra()])
    t_ref.add(4, 1, [bld.single_v(), bld.inner_corner_tl_extra()])

    t_ref.add(3, 1, bld.edge_top_full())

    t_ref.add(2, 3, bld.edge_left())
    t_ref.add(3, 3, bld.center_light())
    t_ref.add(4, 3, bld.edge_right())

    t_ref.add(3, 4, bld.edge_bottom())

    t_ref.add(2, 5, bld.single_v())
    t_ref.add(4, 5, bld.single_v())
    t_ref.finalise()


def _build_type_3(bld: Builder, idx: int, x: int, y: int):
    t_raw = _get_raw_group(bld, idx, x, y)
    t_raw.add(2, 2, [
        # bld.var_single_v(1),
        # bld.c_right(), bld.b_tr(), bld.b_br(),
        bld.edge_left(),
        bld.c(1), bld.c(2), bld.c(4),
        bld.b(2), bld.b(4),
        bld.a(3),
        # bld.block_connector(idx, 1),
    ])

    t_raw.add(4, 2, [
        # bld.var_single_h(1),
        # bld.c_down(), bld.b_bl(), bld.b_br(),
        bld.edge_top(),
        bld.c(2), bld.c(3), bld.c(4),
        bld.b(3), bld.b(4),
        bld.a(1),
        # bld.block_connector(idx, 2),
    ])

    t_raw.add(2, 4, [
        # bld.var_single_h(3),
        # bld.c_up(), bld.b_tl(), bld.b_tr(),
        bld.edge_bottom(),
        bld.c(1), bld.c(2), bld.c(3),
        bld.b(1), bld.b(2),
        bld.a(4),
        # bld.block_connector(idx, 3),
    ])

    t_raw.add(4, 4, [
        # bld.var_single_v(1),
        # bld.c_left(), bld.b_tl(), bld.b_bl(),
        bld.edge_right(),
        bld.c(1), bld.c(3), bld.c(4),
        bld.b(1), bld.b(3),
        bld.a(2),
        # bld.block_connector(idx, 4),
    ])

    t_raw.finalise()

    t_ref = _get_ref_group(bld, idx, x, y)
    t_ref.add(2, 1, [bld.single_v(), bld.inner_corner_tr_extra()])

    t_ref.add(3, 1, bld.single_h_full())
    t_ref.add(4, 1, bld.edge_top_extra())
    t_ref.add(5, 1, bld.single_h_full())

    t_ref.add(2, 3, [bld.single_v(), bld.inner_corner_tl_extra(), bld.inner_corner_tr_extra()])
    t_ref.add(4, 3, [bld.single_v(), bld.inner_corner_tl_extra()])

    t_ref.add(1, 3, bld.single_h_full())
    t_ref.add(3, 3, bld.single_h_full())

    t_ref.add(4, 5, bld.single_v())
    t_ref.finalise()


def _build_type_4(bld: Builder, idx: int, x: int, y: int):
    t_raw = _get_raw_group(bld, idx, x, y)

    t_raw.add(2, 2, [
        bld.inner_corner_tl(),
        bld.d(2), bld.d(7),
        bld.c(1), bld.c(3),
        bld.b(1), bld.b(2), bld.b(3),
        bld.block_connector(idx, 1),
    ])

    t_raw.add(4, 2, [
        bld.inner_corner_tr(),
        bld.d(1), bld.d(8),
        bld.c(1), bld.c(2),
        bld.b(1), bld.b(2), bld.b(4),
        bld.block_connector(idx, 2),
    ])

    t_raw.add(2, 4, [
        bld.inner_corner_bl(),
        bld.d(3), bld.d(6),
        bld.c(3), bld.c(4),
        bld.b(1), bld.b(3), bld.b(4),
        bld.block_connector(idx, 3),
    ])

    t_raw.add(4, 4, [
        bld.inner_corner_br(),
        bld.d(4), bld.d(5),
        bld.c(2), bld.c(4),
        bld.b(2), bld.b(3), bld.b(4),
        bld.block_connector(idx, 4),
    ])

    t_raw.finalise()

    t_ref = _get_ref_group(bld, idx, x, y)

    t_ref.add(2, 1, [bld.single_v(), bld.inner_corner_tl_extra(), bld.inner_corner_tr_extra()])
    t_ref.add(4, 1, [bld.single_v(), bld.inner_corner_tl_extra(), bld.inner_corner_tr_extra()])

    t_ref.add(1, 1, bld.single_h_full())
    t_ref.add(3, 1, bld.edge_top_full())
    t_ref.add(5, 1, bld.single_h_full())

    t_ref.add(2, 3, [bld.edge_left(), bld.inner_corner_tl_extra()])
    t_ref.add(3, 3, bld.center_light())
    t_ref.add(4, 3, [bld.edge_right(), bld.inner_corner_tr_extra()])

    t_ref.add(1, 3, bld.single_h_full())
    t_ref.add(3, 4, bld.edge_bottom())
    t_ref.add(5, 3, bld.single_h_full())

    t_ref.add(2, 5, bld.single_v())
    t_ref.add(4, 5, bld.single_v())

    t_ref.finalise()


def _build_type_5(bld: Builder, idx: int, x: int, y: int):
    t_raw = _get_raw_group(bld, idx, x, y)

    t_raw.add(3, 2, [
        bld.inner_corner_tl(),
        bld.d(1), bld.d(2),
        bld.c(1),
        bld.b(1), bld.b(2),
        bld.block_connector(idx, 4),
    ])

    t_raw.add(2, 3, [
        bld.inner_corner_tl(),
        bld.d(3), bld.d(7),
        bld.c(3),
        bld.b(1), bld.b(3),
        bld.block_connector(idx, 1),
    ])

    t_raw.add(4, 3, [
        bld.inner_corner_tr(),
        bld.d(4), bld.d(8),
        bld.c(2),
        bld.b(2), bld.b(4),
        bld.block_connector(idx, 2),
    ])

    t_raw.add(3, 4, [
        bld.inner_corner_bl(),
        bld.d(5), bld.d(6),
        bld.c(4),
        bld.b(3), bld.b(4),
        bld.block_connector(idx, 3),
    ])

    t_raw.finalise()

    t_ref = _get_ref_group(bld, idx, x, y)

    t_ref.add(3, 1, [bld.single_v(), bld.inner_corner_tl_extra(), bld.inner_corner_tr_extra()])

    t_ref.add(2, 1, bld.outer_corner_tl_full())
    t_ref.add(4, 1, bld.outer_corner_tr_full())
    t_ref.add(2, 2, bld.inner_corner_tl_extra())
    t_ref.add(4, 2, bld.inner_corner_tr_extra())

    t_ref.add(1, 2, bld.single_h_full())
    t_ref.add(3, 3, bld.center_light())
    t_ref.add(5, 2, bld.single_h_full())

    t_ref.add(2, 4, bld.outer_corner_bl())
    t_ref.add(4, 4, bld.outer_corner_br())

    t_ref.add(3, 5, bld.single_v())
    t_ref.finalise()


def _build_type_6(bld: Builder, idx: int, x: int, y: int):
    t_raw = _get_raw_group(bld, idx, x, y)

    t_raw.add(2, 2, [
        bld.inner_corner_tl(),
        bld.d(1), bld.d(3), bld.d(6), bld.d(8),
        bld.b(1), bld.b(4),
        bld.block_connector(idx, 1),
    ])

    t_raw.add(2, 4, [
        bld.inner_corner_tr(),
        bld.d(2), bld.d(4), bld.d(5), bld.d(7),
        bld.b(2), bld.b(3),
        bld.block_connector(idx, 3),
    ])

    t_raw.add(4, 3, [
        bld.inner_corner_tl(),
        bld.c(1), bld.c(2), bld.c(3), bld.c(4),
        bld.b(1), bld.b(2), bld.b(3), bld.b(4),
        bld.block_connector(idx, 2),
    ])

    t_raw.finalise()

    t_ref = _get_ref_group(bld, idx, x, y)

    t_ref.add(2, 1, [bld.edge_left(), bld.inner_corner_tl_extra()])
    t_ref.add(3, 1, bld.deep_corner_bl())

    t_ref.add(1, 1, bld.edge_top_full())
    t_ref.add(3, 2, bld.edge_bottom())
    t_ref.add(4, 2, [bld.single_v(), bld.inner_corner_tl_extra(), bld.inner_corner_tr_extra()])

    t_ref.add(1, 3, bld.deep_right())
    t_ref.add(2, 3, bld.edge_right())
    t_ref.add(3, 3, bld.single_h())
    t_ref.add(5, 2, bld.single_h_full())

    t_ref.add(1, 4, bld.edge_bottom())
    t_ref.add(3, 4, bld.edge_top())
    t_ref.add(4, 4, bld.single_v())

    t_ref.add(2, 5, bld.edge_left())
    t_ref.add(3, 5, bld.deep_corner_tl())

    t_ref.finalise()


# Single Corners
def _build_type_7(bld: Builder, idx: int, x: int, y: int):
    t_raw = _get_raw_group(bld, idx, x, y)

    t_raw.add(2, 2, [
        bld.outer_corner_tl(),
        bld.c(2), bld.c(4), bld.b(4),
        bld.block_connector(idx, 1),
    ])

    t_raw.add(4, 2, [
        bld.outer_corner_tr(),
        bld.c(3), bld.c(4), bld.b(3),
        bld.block_connector(idx, 2),
    ])

    t_raw.add(2, 4, [
        bld.outer_corner_bl(),
        bld.c(1), bld.c(2), bld.b(2),
        bld.block_connector(idx, 3),
    ])

    t_raw.add(4, 4, [
        bld.outer_corner_br(),
        bld.c(1), bld.c(3), bld.b(1),
        bld.block_connector(idx, 4),
    ])
    t_raw.finalise()

    t_ref = _get_ref_group(bld, idx, x, y)

    t_ref.add(2, 1, bld.outer_corner_tl_extra())
    t_ref.add(3, 1, bld.single_h_full())
    t_ref.add(4, 1, bld.outer_corner_tr_extra())

    t_ref.add(2, 3, [bld.single_v(), bld.inner_corner_tr_extra()])
    t_ref.add(4, 3, [bld.single_v(), bld.inner_corner_tl_extra()])

    t_ref.add(3, 3, bld.single_h_full())

    t_ref.finalise()


# Single Edges
def _build_type_8(bld: Builder, idx: int, x: int, y: int):
    t_raw = _get_raw_group(bld, idx, x, y)

    t_raw.add(1, 2, [
        bld.outer_corner_tl(),
        bld.c(2), bld.a(4),
        bld.block_connector(idx, 1),
    ])

    t_raw.add(3, 2, [
        bld.outer_corner_tr(),
        bld.c(3), bld.a(4),
        bld.block_connector(idx, 3),
    ])

    t_raw.add(5, 1, bld.block_connector(idx - 2, 4))
    t_raw.add(5, 2, [bld.single_v(), bld.block_connector(idx, 2)])
    t_raw.add(5, 4, [bld.single_v(), bld.block_connector(idx, 4)])

    t_raw.finalise()

    t_ref = _get_ref_group(bld, idx, x, y)

    t_ref.add(1, 1, bld.outer_corner_tl_extra())
    t_ref.add(2, 1, bld.single_h_full())
    t_ref.add(3, 1, bld.outer_corner_tr_extra())

    t_ref.add(5, 3, bld.single_v())

    t_ref.finalise()

def _get_raw_group(builder: Builder, idx: int, x: int, y: int):
    name = f"l5-type-{idx}-raw"
    return builder.get_target_group(name, x, y)

def _get_ref_group(builder: Builder, idx: int, x: int, y: int):
    name = f"l5-type-{idx}-ref"
    return builder.get_target_group(name, x, y)