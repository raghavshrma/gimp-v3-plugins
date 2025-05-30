from tilegen.core import GeneratorConfig, TargetSet, TilesetTargetGroup, utils
from tilegen.v1_extended_top.v1_builder import V1SourceSet

def handle(config: GeneratorConfig):
    s = V1SourceSet(config).create_target_set()
    s.initiate_level(3)
    s.setup(_setup_sources)
    s.set_target_spacing(1, 1, 4, 4)
    s.set_target_size(3, 3)

    _build_single_h_seamless_tile(s)
    _build_single_v_seamless_tile(s)

    s.cleanup()

def quick(config: GeneratorConfig):
    handle(config)

def _setup_sources(src: V1SourceSet):
    src.setup_sample()


def _build_single_h_seamless_tile(s: TargetSet):
    def _ref(t: TilesetTargetGroup, src: V1SourceSet):
        t.add(2, 1, src.sample_single_h_full())

    layer = s.build3("single-h-seamless", _ref)
    utils.seamless_offset_h(layer, s.grid)


def _build_single_v_seamless_tile(s: TargetSet):
    def _ref(t: TilesetTargetGroup, src: V1SourceSet):
        t.add(2, 2, src.sample_single_v())

    layer = s.build3("single-v-seamless", _ref)
    utils.seamless_offset_v(layer, s.grid)
