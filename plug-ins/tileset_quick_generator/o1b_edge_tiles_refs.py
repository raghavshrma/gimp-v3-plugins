import utils
from generator_config import GeneratorConfig
from tileset_builder import Builder, BuilderSet
from tileset_collection import TilesetTargetGroup


def handle(config: GeneratorConfig):
    s = BuilderSet(config)
    s.initiate_level(1)
    s.setup(_setup_sources)
    s.set_target_size(3, 3)

    s.set_target_spacing(1, 5, 1, 4)
    _build_h(s)

    s.set_target_spacing(9, 5, 4, 1, False)
    _build_v(s)

    s.set_target_spacing(9, 1, 4, 4, True)
    _build_refs(s)

    s.cleanup()


def _setup_sources(src: Builder):
    src.setup_sample()
    src.custom_source("l1-edge-h-seamless")
    src.custom_source("l1-edge-v-seamless")

    if not src.is_color_source:
        src.setup_empty()


def _build_h(s: BuilderSet):
    def _first(t: TilesetTargetGroup, src: Builder):
        key = "l1-edge-h-seamless"
        t.add(1, 1, src.copy_block_custom(key, 1, 1, 3, 3))

    def _nth(t: TilesetTargetGroup, src: Builder, index: int):
        t.add(2, 1, src.sample_edge_top_full(index))
        t.add(2, 3, src.sample_edge_bottom(index))

    h1 = s.build3("edge-h-1", _first)
    utils.seamless_offset_h(h1, s.grid)

    for i in range(2, 7):
        s.build3(f"edge-h-{i}", lambda t, src: _nth(t, src, i))


def _build_v(s: BuilderSet):
    def _first(t: TilesetTargetGroup, src: Builder):
        key = "l1-edge-v-seamless"
        t.add(1, 1, src.copy_block_custom(key, 1, 1, 3, 3))

    def _nth(t: TilesetTargetGroup, src: Builder, index: int):
        t.add(1, 2, src.sample_edge_left(index))
        t.add(2, 2, src.deep_dark())
        t.add(3, 2, src.sample_edge_right(index))

    v1 = s.build3("edge-v-1", _first)
    utils.seamless_offset_v(v1, s.grid)

    for i in range(2, 6):
        s.build3(f"edge-v-{i}", lambda t, src: _nth(t, src, i))


def _build_refs(s: BuilderSet):
    s.setup(_setup_ref_sources)

    def _h_ref(t: TilesetTargetGroup, src: Builder):
        key = "l1-edge-h-1"
        t.add(1, 1, src.copy_block_custom(key, 2, 1, 1, 3))
        t.add(3, 1, src.copy_block_custom(key, 2, 1, 1, 3))

    def _v_ref(t: TilesetTargetGroup, src: Builder):
        key = "l1-edge-v-1"
        t.add(2, 1, src.copy_block_custom(key, 1, 2, 3, 1))
        t.add(2, 3, src.copy_block_custom(key, 1, 2, 3, 1))

    s.build3("edge-h-ref", _h_ref, True)
    s.build3("edge-v-ref", _v_ref, True)


def _setup_ref_sources(src: Builder):
    src.custom_source("l1-edge-h-1")
    src.custom_source("l1-edge-v-1")