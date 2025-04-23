import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

import utils
from generator_config import GeneratorConfig
from tileset_builder import Builder, BuilderSet
from tileset_collection import TilesetSource


def handle(config: GeneratorConfig):
    s = BuilderSet(config)
    s.initiate_level(1)
    s.setup(_setup_sources)

    s.set_target_spacing(1, 5, 1, 4)
    h1 = _build_edges_h(s)

    s.set_target_spacing(9, 5, 4, 1, False)
    v1 = _build_edges_v(s)

    s.set_target_spacing(9, 1, 4, 4, True)
    _build_edge_refs(s, h1, v1)

    s.cleanup()


def _setup_sources(src: Builder):
    src.setup_sample()
    src.custom_source("l1-edge-h-seamless")
    src.custom_source("l1-edge-v-seamless")


def _build_edges_h(s: BuilderSet):
    src = s.outlines.src_custom["l1-edge-h-seamless"]
    trg = s.create_target("edge-h-1", 3, 3)
    trg.add(1, 1, src.copy_block2(1, 1, 3, 3))
    layer = trg.finalize()
    g = s.grid
    layer.resize(g, 3 * g, -g, 0)
    utils.offset_wrap(layer, s.grid // 2, 0)
    layer.resize(3 * g, 3 * g, g, 0)

    for i in range(2, 7):
        trg = s.create_target(f"edge-h-{i}", 3, 3)
        trg.add(2, 1, s.outlines.sample_edge_top_full(i))
        trg.add(2, 3, s.outlines.sample_edge_bottom(i))
        trg.finalize()

    return layer


def _build_edges_v(s: BuilderSet):
    src = s.outlines.src_custom["l1-edge-v-seamless"]
    trg = s.create_target("edge-v-1", 3, 3)
    trg.add(1, 1, src.copy_block2(1, 1, 3, 3))
    layer = trg.finalize()
    g = s.grid
    layer.resize(3 * g, g, 0, -g)
    utils.offset_wrap(layer, 0, s.grid // 2)
    layer.resize(3 * g, 3 * g, 0, g)

    for i in range(2, 6):
        trg = s.create_target(f"edge-v-{i}", 3, 3)
        trg.add(1, 2, s.outlines.sample_edge_left(i))
        trg.add(2, 2, s.outlines.deep_dark())
        trg.add(3, 2, s.outlines.sample_edge_right(i))
        trg.finalize()

    return layer


def _build_edge_refs(s: BuilderSet, h1: Gimp.Layer, v1: Gimp.Layer):
    trg = s.create_target("edge-h-ref", 3, 3)
    h_source = TilesetSource(s.image, h1, trg.group)
    trg.add(1, 1, h_source.copy_block2(2, 1, 1, 3))
    trg.add(3, 1, h_source.copy_block2(2, 1, 1, 3))
    trg.finalize()

    trg = s.create_target("edge-v-ref", 3, 3)
    v_source = TilesetSource(s.image, v1, trg.group)
    trg.add(1, 1, v_source.copy_block2(1, 2, 3, 1))
    trg.add(1, 3, v_source.copy_block2(1, 2, 3, 1))
    trg.finalize()
