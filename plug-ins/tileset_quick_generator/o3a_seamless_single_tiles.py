import utils
from generator_config import GeneratorConfig
from tileset_builder import Builder, BuilderSet
from tileset_collection import TilesetTargetGroup

def handle(config: GeneratorConfig):
    s = BuilderSet(config)
    s.initiate_level(3)
    s.setup(_setup_sources)
    s.set_target_spacing(1, 1, 4, 4)
    s.set_target_size(3, 3)

    _build_single_h_seamless_tile(s)
    _build_single_v_seamless_tile(s)

    s.cleanup()


def _setup_sources(src: Builder):
    src.setup_sample()


def _build_single_h_seamless_tile(s: BuilderSet):
    def _ref(t: TilesetTargetGroup, src: Builder):
        t.add(2, 1, src.sample_single_h_full())

    layer = s.build3("single-h-seamless", _ref)
    utils.seamless_offset_h(layer, s.grid)


def _build_single_v_seamless_tile(s: BuilderSet):
    def _ref(t: TilesetTargetGroup, src: Builder):
        t.add(2, 2, src.sample_single_v())

    layer = s.build3("single-v-seamless", _ref)
    utils.seamless_offset_h(layer, s.grid)
