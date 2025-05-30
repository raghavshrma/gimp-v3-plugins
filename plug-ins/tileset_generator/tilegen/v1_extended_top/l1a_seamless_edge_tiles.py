import gi

from tilegen.core import GeneratorConfig, TargetSet, TilesetTargetGroup, utils
from tilegen.v1_extended_top.v1_builder import V1SourceSet

gi.require_version("Gimp", "3.0")

def handle(config: GeneratorConfig):
    s = _initiate(config)
    _build_edge_h_ref_tile(s)
    _build_edge_v_ref_tile(s)

    s.cleanup()


def _initiate(config: GeneratorConfig):
    src = V1SourceSet(config)
    s = src.create_target_set()
    s.initiate_level(1)
    s.setup(_setup_sources)
    s.set_target_size(3, 3)
    s.set_target_spacing(1, 1, 4, 4)
    return s

def _setup_sources(src: V1SourceSet):
    src.setup_sample()


def _build_edge_h_ref_tile(s: TargetSet):
    def _build(t: TilesetTargetGroup, src: V1SourceSet):
        t.add(2, 1, src.sample_edge_top_full())
        t.add(2, 3, src.sample_edge_bottom())

    layer = s.build3("edge-h-seamless", _build)
    utils.seamless_offset_h(layer, s.grid)


def _build_edge_v_ref_tile(s: TargetSet):
    def _build(t: TilesetTargetGroup, src: V1SourceSet):
        t.add(1, 2, src.sample_edge_left())
        t.add(2, 2, src.deep_dark())
        t.add(3, 2, src.sample_edge_right())

    layer = s.build3("edge-v-seamless", _build)
    utils.seamless_offset_v(layer, s.grid)

# -----------------------

def quick(config: GeneratorConfig):
    handle(config)
