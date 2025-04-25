import os

import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp, Gio

from generator_config import GeneratorConfig
from tileset_builder import Builder, BuilderSet
from tileset_collection import TilesetTargetGroup
import utils

def handle(config: GeneratorConfig):
    timer = utils.ProcessTimer()
    s = BuilderSet(config)
    s.initiate_level(9)
    s.setup(_setup_sources)

    _build_sample(s)
    s.cleanup()
    timer.end("Consolidate Tileset")
    _export_image(s)


def _setup_sources(src: Builder):
    src.setup_sample()
    src.setup_edges()
    src.setup_corners()
    src.setup_singles(corners=True)
    src.setup_connectors()

def _build_sample(s: BuilderSet):
    s.set_target_spacing(0, 0, 1, 1, True)
    s.set_target_size(13, 10)
    s.build3("final", _build_blocks)

def _build_all(t: TilesetTargetGroup, src: Builder):
    _build_blocks(t, src)

def _build_blocks(t: TilesetTargetGroup, src: Builder):
    t.add(1, 1, src.out_corner_tl_full())
    t.add(8, 1, src.out_corner_tr_full())
    t.add(1, 8, src.out_corner_bl())
    t.add(8, 8, src.out_corner_br())

    t.add(1, 9, src.single_left_full())
    t.add(8, 9, src.single_right_full())
    t.add(9, 1, src.single_top_full())
    t.add(9, 8, src.single_bottom())

    for i in range(1, 7):
        t.add(i + 1, 1, src.edge_top_full(i))
        t.add(i + 1, 8, src.edge_bottom(i))
        t.add(i + 1, 9, src.single_h_full(i))

    for i in range(1, 6):
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

def _export_image(s: BuilderSet):
    image = s.image
    bg_layer = utils.find_layer(image, "Background")
    bg_layer.set_lock_visibility(False)
    bg_layer.set_visible(False)

    path = image.get_xcf_file().get_parse_name()
    path = f"{path[:-4]}.png"
    file = Gio.File.new_for_path(path)
    saved = Gimp.file_save(Gimp.RunMode.NONINTERACTIVE, image, file, None)
    Gimp.message(f"Saved tileset {path}: {saved}")
    bg_layer.set_visible(True)

    if saved:
        os.system(f"open '{path}'")

