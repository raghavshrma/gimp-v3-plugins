import utils
from generator_config import GeneratorConfig
from tileset_builder import Builder, BuilderSet
from tileset_collection import TilesetTargetGroup


def handle(config: GeneratorConfig):
    s = BuilderSet(config)
    s.initiate_level(3)
    s.setup(_setup_sources)

    s.set_target_size(3, 3)
    s.set_target_spacing(0, 5, 1, 4)
    _build_h(s)

    s.set_target_spacing(9, 4, 4, 1, False)
    _build_v(s)

    s.set_target_spacing(9, 1, 4, 4, True)
    _build_singles_refs(s)

    s.cleanup()


def _setup_sources(src: Builder):
    src.setup_sample()
    src.custom_source("l3-single-h-seamless")
    src.custom_source("l3-single-v-seamless")


def _build_h(s: BuilderSet):
    _build_h_left(s)
    _build_h_middle(s)
    _build_h_right(s)


def _build_h_left(s: BuilderSet):
    def _build(t: TilesetTargetGroup, src: Builder):
        t.add(2, 1, src.sample_single_h_left_full())

    s.build3("single-h-left", _build)


def _build_h_right(s: BuilderSet):
    def _build(t: TilesetTargetGroup, src: Builder):
        t.add(2, 1, src.sample_single_h_right_full())

    s.build3("single-h-right", _build)


def _build_h_middle(s: BuilderSet):
    def _first(t: TilesetTargetGroup, src: Builder):
        key = "l3-single-h-seamless"
        t.add(1, 1, src.copy_block_custom(key, 1, 1, 3, 3))

    def _nth(t: TilesetTargetGroup, src: Builder, index: int):
        t.add(2, 1, src.sample_single_h_full(index))

    h1 = s.build3("single-h-1", _first)
    utils.seamless_offset_h(h1, s.grid)

    for i in range(2, 7):
        trg = s.create_target(f"single-h-{i}")
        s.build2(trg, lambda t, src: _nth(t, src, i))


def _build_v(s: BuilderSet):
    _build_v_top(s)
    _build_v_middle(s)
    _build_v_bottom(s)


def _build_v_top(s: BuilderSet):
    def _build(t: TilesetTargetGroup, src: Builder):
        t.add(2, 1, src.sample_single_v_top_full())

    s.build3("single-v-top", _build)


def _build_v_bottom(s: BuilderSet):
    def _build(t: TilesetTargetGroup, src: Builder):
        t.add(2, 2, src.sample_single_v_bottom())

    s.build3("single-v-bottom", _build)


def _build_v_middle(s: BuilderSet):
    def _first(t: TilesetTargetGroup, src: Builder):
        key = "l3-single-v-seamless"
        t.add(1, 1, src.copy_block_custom(key, 1, 1, 3, 3))

    def _nth(t: TilesetTargetGroup, src: Builder, index: int):
        t.add(2, 2, src.sample_single_v(index))

    v1 = s.build3("single-v-1", _first)
    utils.seamless_offset_v(v1, s.grid)

    for i in range(2, 6):
        trg = s.create_target(f"single-v-{i}")
        s.build2(trg, lambda t, src: _nth(t, src, i))


def _build_singles_refs(s: BuilderSet):
    s.setup(_setup_ref_sources)

    def _h_ref(t: TilesetTargetGroup, src: Builder):
        key = "l3-single-h-1"
        t.add(1, 1, src.copy_block_custom(key, 2, 1, 1, 2))
        t.add(3, 1, src.copy_block_custom(key, 2, 1, 1, 2))

    def _v_ref(t: TilesetTargetGroup, src: Builder):
        key = "l3-single-v-1"
        t.add(2, 1, src.copy_custom(key, 2, 2))
        t.add(2, 3, src.copy_custom(key, 2, 2))

    s.build3("single-h-ref", _h_ref, True)
    s.build3("single-v-ref", _v_ref, True)


def _setup_ref_sources(src: Builder):
    src.custom_source("l3-single-h-1")
    src.custom_source("l3-single-v-1")
