import gi

gi.require_version("Gimp", "3.0")

from generator_config import GeneratorConfig
from tileset_builder import Builder, BuilderSet
from tileset_collection import TilesetTargetGroup, AreaBuilder
import utils

def handle(config: GeneratorConfig):
    timer = utils.ProcessTimer()
    config.set_visible_levels([0])
    s = BuilderSet(config)
    s.setup(_setup_sources)

    _build_sample(s)
    s.cleanup()
    timer.end("Consolidate sample")


def _setup_sources(src: Builder):
    src.setup_sample()
    src.setup_edges()
    src.setup_corners()
    src.setup_singles(corners=False)

def _build_sample(s: BuilderSet):
    s.set_target_spacing(0, 0, 1, 1, True)
    s.set_target_size(10, 10)
    l = s.build3("sample", _build)
    s.image.lower_item_to_bottom(l)
    s.image.raise_item(l)

def _build(t: TilesetTargetGroup, src: Builder):
    t.add(1, 1, src.out_corner_tl_full())
    t.add(8, 1, src.out_corner_tr_full())
    t.add(1, 8, src.out_corner_bl())
    t.add(8, 8, src.out_corner_br())

    t.add(1, 9, src.single_left_full())
    t.add(8, 9, src.single_right_full())
    t.add(10, 1, src.single_top_full())
    t.add(10, 8, src.single_bottom())

    for i in range(1, 7):
        t.add(i + 1, 1, src.edge_top_full(i))
        t.add(i + 1, 8, src.edge_bottom(i))
        t.add(i + 1, 9, src.single_h_full(i))

    for i in range(1, 6):
        t.add(1, i + 2, src.edge_left(i))
        t.add(8, i + 2, src.edge_right(i))
        t.add(10, i + 2, src.single_v(i))

    t.add(2, 3, src.deep_center_complete())
