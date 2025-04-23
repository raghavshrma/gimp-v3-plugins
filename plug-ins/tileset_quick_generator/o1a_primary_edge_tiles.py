import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp, Gegl
import utils
from generator_config import GeneratorConfig
from tileset_builder import Builder, BuilderSet


def handle(config: GeneratorConfig):
    s = BuilderSet(config)
    s.initiate_level(1)
    s.setup(_setup_sources)
    s.set_target_spacing(1, 1, 4, 4)
    _build_edge_h_ref_tile(s)
    _build_edge_v_ref_tile(s)

    s.cleanup()


def _setup_sources(src: Builder):
    src.setup_sample()


def _build_edge_h_ref_tile(s: BuilderSet):
    t_ref = s.create_target("edge-h-seamless", 3, 3)
    t_ref.add(2, 1, s.outlines.sample_edge_top_full())
    t_ref.add(2, 3, s.outlines.sample_edge_bottom())
    layer = t_ref.finalize()
    g = s.grid
    layer.resize(g, 3 * g, -g, 0)
    utils.offset_wrap(layer, s.grid // 2, 0)
    layer.resize(3 * g, 3 * g, g, 0)


def _build_edge_v_ref_tile(s: BuilderSet):
    t_ref = s.create_target("edge-v-seamless", 3, 3)
    t_ref.add(1, 2, s.outlines.sample_edge_left())
    t_ref.add(2, 2, s.outlines.deep_dark())
    t_ref.add(3, 2, s.outlines.sample_edge_right())
    layer = t_ref.finalize()

    g = s.grid
    layer.resize(3 * g, g, 0, -g)
    utils.offset_wrap(layer, 0, s.grid // 2)
    layer.resize(3 * g, 3 * g, 0, g)
