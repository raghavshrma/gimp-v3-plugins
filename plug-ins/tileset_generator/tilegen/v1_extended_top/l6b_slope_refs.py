import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp
from datetime import datetime

from tilegen.core import GeneratorConfig, TargetSet, TilesetTargetGroup, utils, TilesetSource
from tilegen.v1_extended_top.v1_builder import V1SourceSet


def handle(image: Gimp.Image, sample: Gimp.Layer, config: Gimp.ProcedureConfig):
    # utils.find_or_create_layer(image, "l6-slopes", 4, 8, utils.get_main_group(image))
    group = utils.get_ref_group(image, 6)
    builder = V1SourceSet(image, sample, group)
    builder.target_root.set_visible(True)
    g = utils.get_grid_size(image)
    x, y = 6 * g, 2 * g
    dx, dy = 6 * g, 4 * g

    start = datetime.now()

    builder.setup_edges()
    builder.setup_corners()
    builder.setup_singles()
    builder.setup_transition_tiles()
    builder.setup_connectors()
    # builder.setup_slope_connectors()

    _build_slopes_1(builder, 1, x + 1 * dx, y + 0 * dy)
    _build_slopes_2(builder, 2, x + 0 * dx, y + 1 * dy)
    _build_slopes_3(builder, 3, x + 1 * dx, y + 1 * dy)

    Gimp.message(f"Built connector references in {datetime.now() - start}")

    builder.cleanup()


def _build_slopes_1(bld: V1SourceSet, idx: int, x: int, y: int):
    t_raw = _get_raw_group(bld, idx, x, y)
    t_raw.add(2, 1, bld.out_corner_tl_ext())
    t_raw.add(2, 2, bld.single_h_left())
    t_raw.add(4, 1, [bld.out_corner_tr_ext()])
    t_raw.add(4, 2, [bld.single_h_right()])
    t_raw.add(2, 3, [bld.out_corner_tl_ext()])
    t_raw.add(2, 4, [bld.single_h_left()])
    t_raw.add(4, 3, [bld.out_corner_tr_ext()])
    t_raw.add(4, 4, [bld.single_h_right()])
    t_raw.finalize()

    t_ref = _get_ref_group(bld, idx, x, y)
    t_ref.add(3, 1, bld.single_h_full())
    t_ref.add(3, 3, bld.single_h_full())

    t_ref.finalize()


def _build_slopes_2(bld: V1SourceSet, idx: int, x: int, y: int):
    t_raw = _get_raw_group(bld, idx, x, y)
    t_raw.add(2, 1, bld.single_v_top_full())
    t_raw.add(4, 1, bld.single_v_top_full())
    t_raw.add(2, 4, bld.single_v_bottom())
    t_raw.add(4, 4, bld.single_v_bottom())
    t_raw.finalize()

    t_ref = _get_ref_group(bld, idx, x, y)
    t_ref.add(2, 3, bld.single_v())
    t_ref.add(4, 3, bld.single_v())

    t_ref.finalize()


def _build_slopes_3(bld: V1SourceSet, idx: int, x: int, y: int):
    t_raw = _get_raw_group(bld, idx, x, y)
    t_raw.add(2, 1, bld.out_corner_tl_ext())
    t_raw.add(2, 2, bld.single_corner_tl())
    t_raw.add(4, 1, bld.out_corner_tr_ext())
    t_raw.add(4, 2, bld.single_corner_tr())
    t_raw.add(2, 4, bld.single_corner_bl())
    t_raw.add(4, 4, bld.single_corner_br())
    t_raw.finalize()

    t_ref = _get_ref_group(bld, idx, x, y)
    t_ref.add(3, 1, bld.single_h_full())
    t_ref.add(2, 3, bld.single_v())
    t_ref.add(4, 3, bld.single_v())
    t_ref.add(3, 3, bld.single_h_full())

    t_ref.finalize()


def _get_raw_group(builder: V1SourceSet, idx: int, x: int, y: int):
    name = f"l6-slopes-raw-{idx}"
    return builder.get_target_group(name, x, y, 5, 5)


def _add_raw_source(builder: V1SourceSet, t_raw: TilesetTargetGroup, source_idx: int):
    base = TilesetSource(builder.image, f"l6-slopes-raw-{source_idx}", t_raw.group)
    t_raw.add(1, 1, base.copy_block2(1, 1, 5, 5))


def _get_ref_group(builder: V1SourceSet, idx: int, x: int, y: int):
    name = f"l6-slopes-ref-{idx}"
    return builder.get_target_group(name, x, y, 5, 5)
