import os

import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp, Gio

from tilegen.core import GeneratorConfig, TargetSet, TilesetTargetGroup, utils
from tilegen.v1_extended_top.v1_builder import V1SourceSet, V1TargetSet


def handle(config: GeneratorConfig):
    s = V1SourceSet(config).create_target_set()
    # group = s.initiate_level(0)
    # utils.set_visible_layers(config.image, group, [])

    # s.setup(_setup_sources)
    #
    # _build_sample(s)
    # s.cleanup()
    # timer.end("Consolidate Tileset")
    # _export_image(s)


def _setup_sources(src: V1SourceSet):
    src.setup_sample()


def _build_sample(s: V1TargetSet):
    s.set_target_spacing(0, 0, 1, 1, True)
    s.set_target_size(13, 10)
    s.build3("final", _build_blocks)


def _build_all(t: TilesetTargetGroup, src: V1SourceSet):
    _build_blocks(t, src)


def _build_blocks(t: TilesetTargetGroup, src: V1SourceSet):
    t.add(1, 1, src.out_corner_tl_full())
    t.add(8, 1, src.out_corner_tr_full())
    t.add(1, 8, src.out_corner_bl())
    t.add(8, 8, src.out_corner_br())

    t.add(1, 9, src.single_left_full())
    t.add(8, 9, src.single_right_full())
    t.add(9, 1, src.single_top_full())
    t.add(9, 8, src.single_bottom())

    for i in src.config.range_cols():
        t.add(i + 1, 1, src.edge_top_full(i))
        t.add(i + 1, 8, src.edge_bottom(i))
        t.add(i + 1, 9, src.single_h_full(i))

    for i in src.config.range_rows():
        t.add(1, i + 2, src.edge_left(i))
        t.add(8, i + 2, src.edge_right(i))
        t.add(9, i + 2, src.single_v(i))

    t.add(2, 3, src.deep_center_complete())

    t.add(10, 1, src.in_corner_br())
    t.add(11, 1, src.in_corner_bl())
    t.add(10, 2, src.in_corner_tr_full())
    t.add(11, 2, src.in_corner_tl_full())

    t.add(12, 1, src.single_corner_tl_full())
    t.add(13, 1, src.single_corner_tr_full())
    t.add(12, 3, src.single_corner_bl())
    t.add(13, 3, src.single_corner_br())

    for i in range(0, 6):
        c = 10 + (i % 2) * 2
        r = 4 + (i // 2) * 2

        t.add(c + 0, r + 0, src.connector(i + 1, 1))
        t.add(c + 1, r + 0, src.connector(i + 1, 2))
        t.add(c + 0, r + 1, src.connector(i + 1, 3))

        if i < 5:
            t.add(c + 1, r + 1, src.connector(i + 1, 4))


def quick(config: GeneratorConfig):
    timer = utils.ProcessTimer()
    s = V1SourceSet(config).create_target_set()
    s.initiate_level(9)
    s.setup(_setup_quick)

    s.set_target_spacing(0, 0, 1, 1, True)
    s.set_target_size(14, 8)
    s.build3("final", _build_quick)
    s.cleanup()
    timer.end("Consolidate Tileset")
    _export_image(s)


def _setup_quick(src: V1SourceSet):
    src.setup_sample()
    src.setup_edges()
    src.setup_corners()
    src.setup_singles(corners=True)
    src.setup_connectors()


def _build_quick(t: TilesetTargetGroup, src: V1SourceSet):
    t.add(2, 1, src.out_corner_tl_full())
    t.add(5, 1, src.out_corner_tr_full())
    t.add(2, 5, src.out_corner_bl())
    t.add(5, 5, src.out_corner_br())

    t.add(2, 6, src.single_left_full())
    t.add(5, 6, src.single_right_full())
    t.add(7, 1, src.single_top_full())
    t.add(7, 5, src.single_bottom())

    for i in src.config.range_cols():
        t.add(i + 2, 1, src.edge_top_full(i))
        t.add(i + 2, 5, src.edge_bottom(i))
        t.add(i + 2, 6, src.single_h_full(i))

    for i in src.config.range_rows():
        t.add(2, i + 2, src.edge_left(i))
        t.add(5, i + 2, src.edge_right(i))
        t.add(7, i + 2, src.single_v(i))

    t.add(3, 3, src.deep_corner_tl())
    t.add(4, 3, src.deep_corner_tr())
    t.add(3, 4, src.deep_corner_bl())
    t.add(4, 4, src.deep_corner_br())
    t.add(7, 7, src.deep_dark())

    t.add(9, 1, src.in_corner_br())
    t.add(10, 1, src.in_corner_bl())
    t.add(9, 2, src.in_corner_tr_full())
    t.add(10, 2, src.in_corner_tl_full())

    for i in src.config.range_cols():
        t.add(8 + i, 5, src.deep_edge_top(i))
        t.add(8 + i, 6, src.deep_edge_left(i))
        t.add(8 + i, 7, src.deep_edge_bottom(i))


    t.add(12, 1, src.single_corner_tl_full())
    t.add(13, 2, src.connector(1, 1))

    t.add(12, 3, src.connector(2, 1))
    t.add(13, 3, src.connector(5, 4))

    t.add(12, 4, src.connector(3, 1))
    t.add(13, 4, src.connector(5, 1))

    t.add(12, 5, src.connector(4, 1))
    t.add(13, 5, src.connector(6, 1))

    t.add(12, 6, src.edge_top_ext())
    t.add(12, 7, src.connector(3, 2))
    t.add(13, 7, src.connector(6, 3))


def _export_image(s: V1TargetSet):
    image = s.image
    xcf_file = image.get_xcf_file()
    if xcf_file is None:
        Gimp.message("No XCF file found.")
        return

    bg_layer = utils.find_layer(image, "Background")
    bg_layer.set_lock_visibility(False)
    bg_layer.set_visible(False)

    path = xcf_file.get_parse_name()
    suffix = s.is_quick and "-quick" or ""
    path = f"{path[:-4]}{suffix}.png"
    file = Gio.File.new_for_path(path)
    saved = Gimp.file_save(Gimp.RunMode.NONINTERACTIVE, image, file, None)
    Gimp.message(f"Saved tileset {path}: {saved}")
    bg_layer.set_visible(True)

    if saved:
        os.system(f"open '{path}'")
