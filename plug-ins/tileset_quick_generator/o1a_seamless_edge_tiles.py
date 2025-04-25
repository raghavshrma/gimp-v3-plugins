import gi

gi.require_version("Gimp", "3.0")
import utils
from generator_config import GeneratorConfig
from tileset_builder import Builder, BuilderSet
from tileset_collection import TilesetTargetGroup


def handle(config: GeneratorConfig):
    s = BuilderSet(config)
    s.initiate_level(1)
    s.setup(_setup_sources)
    s.set_target_size(3, 3)
    s.set_target_spacing(1, 1, 4, 4)
    _build_edge_h_ref_tile(s)
    _build_edge_v_ref_tile(s)

    s.cleanup()


def _setup_sources(src: Builder):
    src.setup_sample()


def _build_edge_h_ref_tile(s: BuilderSet):
    def _build(t: TilesetTargetGroup, src: Builder):
        t.add(2, 1, src.sample_edge_top_full())
        t.add(2, 3, src.sample_edge_bottom())

    layer = s.build3("edge-h-seamless", _build)
    utils.seamless_offset_h(layer, s.grid)


def _build_edge_v_ref_tile(s: BuilderSet):
    def _build(t: TilesetTargetGroup, src: Builder):
        t.add(1, 2, src.sample_edge_left())
        t.add(2, 2, src.deep_dark())
        t.add(3, 2, src.sample_edge_right())

    layer = s.build3("edge-v-seamless", _build)
    utils.seamless_offset_v(layer, s.grid)

