from generator_config import GeneratorConfig
from tileset_builder import Builder, BuilderSet
from tileset_collection import TilesetTargetGroup, AreaBuilder

def handle(config: GeneratorConfig):
    s = BuilderSet(config)
    s.initiate_level(4)
    s.setup(_setup_sources)
    s.set_target_spacing(1, 1, 2, 2)
    s.set_target_size(2, 2)

    _build_transition_edges(s)
    _build_transition_corners(s)
    _build_transition_singles(s)
    _build_transition_blocks(s)

    s.cleanup()


def _setup_sources(src: Builder):
    src.setup_edges()
    src.setup_singles(corners=False)
    src.setup_corners()


def _build_transition_edges(s: BuilderSet):
    area = AreaBuilder(s.grid)

    def _build(t: TilesetTargetGroup, src: Builder):
        t.add(1, 1, area.t().crop(src.edge_top()))
        t.add(2, 1, area.r().crop(src.edge_right()))
        t.add(1, 2, area.l().crop(src.edge_left()))
        t.add(2, 2, area.b().crop(src.edge_bottom()))

    s.build3("transition-ref-a", _build)


def _build_transition_corners(s: BuilderSet):
    area = AreaBuilder(s.grid)

    def _build(t: TilesetTargetGroup, src: Builder):
        t.add(1, 1, area.tl().crop(src.in_corner_tl()))
        t.add(2, 1, area.tr().crop(src.in_corner_tr()))
        t.add(1, 2, area.bl().crop(src.in_corner_bl()))
        t.add(2, 2, area.br().crop(src.in_corner_br()))

    s.build3("transition-ref-b", _build)


def _build_transition_singles(s: BuilderSet):
    area = AreaBuilder(s.grid)

    def _build(t: TilesetTargetGroup, src: Builder):
        t.add(1, 1, area.t().crop(src.single_v()))
        t.add(2, 1, area.r().crop(src.single_h()))
        t.add(1, 2, area.l().crop(src.single_h()))
        t.add(2, 2, area.b().crop(src.single_v()))

    s.build3("transition-ref-c", _build)

def _build_transition_blocks(s: BuilderSet):
    area = AreaBuilder(s.grid)

    def _build1(t: TilesetTargetGroup, src: Builder):
        t.add(1, 1, area.l().crop(src.edge_top()))
        t.add(2, 1, area.r().crop(src.edge_top()))
        t.add(1, 2, area.l().crop(src.edge_bottom()))
        t.add(2, 2, area.r().crop(src.edge_bottom()))

    def _build2(t: TilesetTargetGroup, src: Builder):
        t.add(1, 1, area.t().crop(src.edge_left()))
        t.add(2, 1, area.t().crop(src.edge_right()))
        t.add(1, 2, area.b().crop(src.edge_left()))
        t.add(2, 2, area.b().crop(src.edge_right()))

    s.build3("transition-ref-d1", _build1)
    s.build3("transition-ref-d2", _build2)
