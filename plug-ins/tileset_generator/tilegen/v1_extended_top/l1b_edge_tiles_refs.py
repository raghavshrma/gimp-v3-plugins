from tilegen.core import GeneratorConfig, TargetSet, TilesetTargetGroup, utils
from tilegen.v1_extended_top.v1_builder import V1SourceSet

def handle(config: GeneratorConfig):
    src = V1SourceSet(config)
    s = src.create_target_set()
    s.initiate_level(1)
    s.setup(_setup_sources)
    s.set_target_size(3, 3)

    _build_h(s)
    _build_v(s)
    _build_refs(s)

    s.cleanup()

def quick(config: GeneratorConfig):
    handle(config)


def _setup_sources(src: V1SourceSet):
    src.setup_sample()
    src.custom_source("l1-edge-h-seamless")
    src.custom_source("l1-edge-v-seamless")

def _build_h(s: TargetSet):
    s.set_target_spacing(1, 5, 1, 4)

    h1 = s.build3("edge-h-1", _h_first)
    utils.seamless_offset_h(h1, s.grid)

    for i in s.range_cols(2):
        s.build3(f"edge-h-{i}", lambda t, src: _h_nth(t, src, i))


def _build_v(s: TargetSet):
    s.set_target_spacing(9, 5, 4, 1, False)

    v1 = s.build3("edge-v-1", _v_first)
    utils.seamless_offset_v(v1, s.grid)

    for i in s.range_rows(2):
        s.build3(f"edge-v-{i}", lambda t, src: _v_nth(t, src, i))

def _build_refs(s: TargetSet):
    s.set_target_spacing(9, 1, 4, 4, True)
    s.setup(_setup_ref_sources)
    s.build3("edge-h-ref", _h_ref, True)
    s.build3("edge-v-ref", _v_ref, True)


def _h_first(t: TilesetTargetGroup, src: V1SourceSet):
    key = "l1-edge-h-seamless"
    t.add(1, 1, src.copy_block_custom(key, 1, 1, 3, 3))

def _h_nth(t: TilesetTargetGroup, src: V1SourceSet, index: int):
    t.add(2, 1, src.sample_edge_top_full(index))
    t.add(2, 3, src.sample_edge_bottom(index))

def _v_first(t: TilesetTargetGroup, src: V1SourceSet):
    key = "l1-edge-v-seamless"
    t.add(1, 1, src.copy_block_custom(key, 1, 1, 3, 3))

def _v_nth(t: TilesetTargetGroup, src: V1SourceSet, index: int):
    t.add(1, 2, src.sample_edge_left(index))
    t.add(2, 2, src.deep_dark())
    t.add(3, 2, src.sample_edge_right(index))

def _setup_ref_sources(src: V1SourceSet):
    src.custom_source("l1-edge-h-1")
    src.custom_source("l1-edge-v-1")

def _h_ref(t: TilesetTargetGroup, src: V1SourceSet):
    key = "l1-edge-h-1"
    t.add(1, 1, src.copy_block_custom(key, 2, 1, 1, 3))
    t.add(3, 1, src.copy_block_custom(key, 2, 1, 1, 3))

def _v_ref(t: TilesetTargetGroup, src: V1SourceSet):
    key = "l1-edge-v-1"
    t.add(1, 1, src.copy_block_custom(key, 1, 2, 3, 1))
    t.add(1, 3, src.copy_block_custom(key, 1, 2, 3, 1))
