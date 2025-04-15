import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

import utils
from tileset_builder import Builder
from datetime import datetime


def handle(image: Gimp.Image, sample: Gimp.Layer, config: Gimp.ProcedureConfig):
    builder = Builder(image, sample)
    g = utils.get_grid_size(image)
    x, y = 6 * g, 5 * g
    dx, dy = 6 * g, 5 * g

    start = datetime.now()

    builder.setup_blocks_plus()
    builder.setup_block_corners()
    builder.setup_block_singles()
    builder.setup_block_connectors_base()

    _build_type_1(builder, 1, x + 0 * dx, y + 0 * dy)
    _build_type_2(builder, 2, x + 1 * dx, y + 0 * dy)
    _build_type_3(builder, 3, x + 0 * dx, y + 1 * dy)
    _build_type_4(builder, 4, x + 1 * dx, y + 1 * dy)
    _build_type_5(builder, 5, x + 0 * dx, y + 2 * dy)
    _build_type_6(builder, 6, x + 1 * dx, y + 2 * dy)
    _build_type_7(builder, 7, x - 1 * dx, y + 1 * dy)
    _build_type_8(builder, 8, x - 1 * dx, y + 2 * dy)

    Gimp.message(f"Built connector references in {datetime.now() - start}")

    builder.cleanup()


def _build_type_1(bld: Builder, idx: int, x: int, y: int):
    t_raw = bld.target_group_raw(idx, x, y)
    t_raw.add(2, 2, [
        bld.inner_corner_bl(),
        bld.d(2), bld.d(7),
        bld.c(3), bld.a(1),
    ])

    t_raw.add(4, 2, [
        bld.inner_corner_br(),
        bld.d(1), bld.d(8),
        bld.c(2), bld.a(1),
    ])

    t_raw.add(2, 4, [
        bld.inner_corner_tl(),
        bld.d(3), bld.d(6),
        bld.c(3), bld.a(4),
    ])

    t_raw.add(4, 4, [
        bld.inner_corner_tr(),
        bld.d(4), bld.d(5),
        bld.c(2), bld.a(4),
    ])

    t_raw.finalise()

    t_ref = bld.target_group_ref(idx, x, y)
    t_ref.add(1, 1, bld.single_h_full())
    t_ref.add(2, 1, bld.top_extra())
    t_ref.add(3, 1, bld.top_full())
    t_ref.add(4, 1, bld.top_extra())
    t_ref.add(5, 1, bld.single_h_full())

    t_ref.add(2, 3, [bld.left(), bld.inner_corner_tl_extra()])
    t_ref.add(3, 3, bld.center_light())
    t_ref.add(4, 3, [bld.right(), bld.inner_corner_tr_extra()])

    t_ref.add(1, 3, bld.single_h_full())
    t_ref.add(3, 4, bld.bottom())
    t_ref.add(5, 3, bld.single_h_full())

    t_ref.finalise()


def _build_type_2(bld: Builder, idx: int, x: int, y: int):
    t_raw = bld.target_group_raw(idx, x, y)
    t_raw.add(2, 2, [
        bld.inner_corner_tr(),
        bld.d(2), bld.d(7),
        bld.c(1), bld.a(3),
    ])

    t_raw.add(4, 2, [
        bld.inner_corner_tl(),
        bld.d(1), bld.d(8),
        bld.c(1), bld.a(2),
    ])

    t_raw.add(2, 4, [
        bld.inner_corner_br(),
        bld.d(3), bld.d(6),
        bld.c(4), bld.a(3),
    ])

    t_raw.add(4, 4, [
        bld.inner_corner_bl(),
        bld.d(4), bld.d(5),
        bld.c(4), bld.a(2),
    ])

    t_raw.finalise()

    t_ref = bld.target_group_ref(idx, x, y)
    t_ref.add(2, 1, [bld.single_v(), bld.inner_corner_tr_extra()])
    t_ref.add(4, 1, [bld.single_v(), bld.inner_corner_tl_extra()])

    t_ref.add(3, 1, bld.top_full())

    t_ref.add(2, 3, bld.left())
    t_ref.add(3, 3, bld.center_light())
    t_ref.add(4, 3, bld.right())

    t_ref.add(3, 4, bld.bottom())

    t_ref.add(2, 5, bld.single_v())
    t_ref.add(4, 5, bld.single_v())
    t_ref.finalise()


def _build_type_3(bld: Builder, idx: int, x: int, y: int):
    t_raw = bld.target_group_raw(idx, x, y)
    t_raw.add(2, 2, [
        bld.left(),
        bld.c(1), bld.c(2), bld.c(4),
        bld.b(2), bld.b(4),
        bld.a(3),
    ])

    t_raw.add(4, 2, [
        bld.top(),
        bld.c(2), bld.c(3), bld.c(4),
        bld.b(3), bld.b(4),
        bld.a(1),
    ])

    t_raw.add(2, 4, [
        bld.bottom(),
        bld.c(1), bld.c(2), bld.c(3),
        bld.b(1), bld.b(2),
        bld.a(4),
    ])

    t_raw.add(4, 4, [
        bld.right(),
        bld.c(1), bld.c(3), bld.c(4),
        bld.b(1), bld.b(3),
        bld.a(2),
    ])

    t_raw.finalise()

    t_ref = bld.target_group_ref(idx, x, y)
    t_ref.add(2, 1, [bld.single_v(), bld.inner_corner_tr_extra()])

    t_ref.add(3, 1, bld.single_h_full())
    t_ref.add(4, 1, bld.top_extra())
    t_ref.add(5, 1, bld.single_h_full())

    t_ref.add(2, 3, [bld.single_v(), bld.inner_corner_tl_extra(), bld.inner_corner_tr_extra()])
    t_ref.add(4, 3, [bld.single_v(), bld.inner_corner_tl_extra()])

    t_ref.add(1, 3, bld.single_h_full())
    t_ref.add(3, 3, bld.single_h_full())

    t_ref.add(4, 5, bld.single_v())
    t_ref.finalise()


def _build_type_4(bld: Builder, idx: int, x: int, y: int):
    t_raw = bld.target_group_raw(idx, x, y)

    t_raw.add(2, 2, [
        bld.inner_corner_tl(),
        bld.d(2), bld.d(7),
        bld.c(1), bld.c(3),
        bld.b(1), bld.b(2), bld.b(3),
    ])

    t_raw.add(4, 2, [
        bld.inner_corner_tr(),
        bld.d(1), bld.d(8),
        bld.c(1), bld.c(2),
        bld.b(1), bld.b(2), bld.b(4),
    ])

    t_raw.add(2, 4, [
        bld.inner_corner_bl(),
        bld.d(3), bld.d(6),
        bld.c(3), bld.c(4),
        bld.b(1), bld.b(3), bld.b(4),
    ])

    t_raw.add(4, 4, [
        bld.inner_corner_br(),
        bld.d(4), bld.d(5),
        bld.c(2), bld.c(4),
        bld.b(2), bld.b(3), bld.b(4),
    ])

    t_raw.finalise()

    t_ref = bld.target_group_ref(idx, x, y)

    t_ref.add(2, 1, [bld.single_v(), bld.inner_corner_tl_extra(), bld.inner_corner_tr_extra()])
    t_ref.add(4, 1, [bld.single_v(), bld.inner_corner_tl_extra(), bld.inner_corner_tr_extra()])

    t_ref.add(1, 1, bld.single_h_full())
    t_ref.add(3, 1, bld.top_full())
    t_ref.add(5, 1, bld.single_h_full())

    t_ref.add(2, 3, [bld.left(), bld.inner_corner_tl_extra()])
    t_ref.add(3, 3, bld.center_light())
    t_ref.add(4, 3, [bld.right(), bld.inner_corner_tr_extra()])

    t_ref.add(1, 3, bld.single_h_full())
    t_ref.add(3, 4, bld.bottom())
    t_ref.add(5, 3, bld.single_h_full())

    t_ref.add(2, 5, bld.single_v())
    t_ref.add(4, 5, bld.single_v())

    t_ref.finalise()


def _build_type_5(bld: Builder, idx: int, x: int, y: int):
    t_raw = bld.target_group_raw(idx, x, y)

    t_raw.add(3, 2, [
        bld.inner_corner_tl(),
        bld.d(1), bld.d(2),
        bld.c(1),
        bld.b(1), bld.b(2),
    ])

    t_raw.add(2, 3, [
        bld.inner_corner_tl(),
        bld.d(3), bld.d(7),
        bld.c(3),
        bld.b(1), bld.b(3),
    ])

    t_raw.add(4, 3, [
        bld.inner_corner_tr(),
        bld.d(4), bld.d(8),
        bld.c(2),
        bld.b(2), bld.b(4),
    ])

    t_raw.add(3, 4, [
        bld.inner_corner_bl(),
        bld.d(5), bld.d(6),
        bld.c(4),
        bld.b(3), bld.b(4),
    ])

    t_raw.finalise()

    t_ref = bld.target_group_ref(idx, x, y)

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
    t_raw = bld.target_group_raw(idx, x, y)

    t_raw.add(2, 2, [
        bld.inner_corner_tl(),
        bld.d(1), bld.d(3), bld.d(6), bld.d(8),
        bld.b(1), bld.b(4),
    ])

    t_raw.add(2, 4, [
        bld.inner_corner_tr(),
        bld.d(2), bld.d(4), bld.d(5), bld.d(7),
        bld.b(2), bld.b(3),
    ])

    t_raw.add(4, 3, [
        bld.inner_corner_tl(),
        bld.c(1), bld.c(2), bld.c(3), bld.c(4),
        bld.b(1), bld.b(2), bld.b(3), bld.b(4),
    ])

    t_raw.finalise()

    t_ref = bld.target_group_ref(idx, x, y)

    t_ref.add(2, 1, [bld.left(), bld.inner_corner_tl_extra()])
    t_ref.add(3, 1, bld.deep_corner_bl())

    t_ref.add(1, 1, bld.top_full())
    t_ref.add(3, 2, bld.bottom())
    t_ref.add(4, 2, [bld.single_v(), bld.inner_corner_tl_extra(), bld.inner_corner_tr_extra()])

    t_ref.add(1, 3, bld.deep_right())
    t_ref.add(2, 3, bld.right())
    t_ref.add(3, 3, bld.single_h())
    t_ref.add(5, 2, bld.single_h_full())

    t_ref.add(1, 4, bld.bottom())
    t_ref.add(3, 4, bld.top())
    t_ref.add(4, 4, bld.single_v())

    t_ref.add(2, 5, bld.left())
    t_ref.add(3, 5, bld.deep_corner_tl())

    t_ref.finalise()


# Single Corners
def _build_type_7(bld: Builder, idx: int, x: int, y: int):
    t_raw = bld.target_group_raw(idx, x, y)

    t_raw.add(2, 2, [bld.outer_corner_tl(), bld.c(2), bld.c(4), bld.b(4)])
    t_raw.add(4, 2, [bld.outer_corner_tr(), bld.c(3), bld.c(4), bld.b(3)])
    t_raw.add(2, 4, [bld.outer_corner_bl(), bld.c(1), bld.c(2), bld.b(2)])
    t_raw.add(4, 4, [bld.outer_corner_br(), bld.c(1), bld.c(3), bld.b(1)])
    t_raw.finalise()

    t_ref = bld.target_group_ref(idx, x, y)

    t_ref.add(2, 1, bld.outer_corner_tl_extra())
    t_ref.add(3, 1, bld.single_h_full())
    t_ref.add(4, 1, bld.outer_corner_tr_extra())

    t_ref.add(2, 3, [bld.single_v(), bld.inner_corner_tr_extra()])
    t_ref.add(4, 3, [bld.single_v(), bld.inner_corner_tl_extra()])

    t_ref.add(3, 3, bld.single_h_full())

    t_ref.finalise()


# Single Edges
def _build_type_8(bld: Builder, idx: int, x: int, y: int):
    t_raw = bld.target_group_raw(idx, x, y)

    t_raw.add(1, 2, [
        bld.outer_corner_tl(),
        bld.c(2), bld.a(4),
    ])

    t_raw.add(3, 2, [
        bld.outer_corner_tr(),
        bld.c(3), bld.a(4),
    ])

    t_raw.add(5, 2, bld.single_v())
    t_raw.add(5, 4, bld.single_v())

    t_raw.finalise()

    t_ref = bld.target_group_ref(idx, x, y)

    t_ref.add(1, 1, bld.outer_corner_tl_extra())
    t_ref.add(2, 1, bld.single_h_full())
    t_ref.add(3, 1, bld.outer_corner_tr_extra())

    t_ref.add(5, 3, bld.single_v())

    t_ref.finalise()
