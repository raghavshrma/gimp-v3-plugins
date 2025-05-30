from tilegen.core import GeneratorConfig, TargetSet, TilesetTargetGroup, utils
from tilegen.v1_extended_top.v1_builder import V1SourceSet

def handle(config: GeneratorConfig):
    src = V1SourceSet(config)
    s = src.create_target_set()
    s.initiate_level(2, [1])
    s.setup(_setup_sources)
    s.set_target_size(3, 4)
    s.set_target_spacing(1, 9, 4, 5)

    _build_outer_corners(s)
    _build_inner_corners(s)

    s.cleanup()

def quick(config: GeneratorConfig):
    handle(config)


def _setup_sources(src: V1SourceSet):
    src.setup_sample()
    src.setup_edges()


def _build_outer_corners(s: TargetSet):
    def _ref(t: TilesetTargetGroup, src: V1SourceSet):
        t.add(2, 1, src.edge_top_full())
        t.add(2, 4, src.edge_bottom())
        t.add(1, 3, src.edge_left())
        t.add(3, 3, src.edge_right())

    def _main(t: TilesetTargetGroup, src: V1SourceSet):
        t.add(1, 1, src.sample_corner_tl_full())
        t.add(3, 1, src.sample_corner_tr_full())
        t.add(1, 4, src.sample_corner_bl())
        t.add(3, 4, src.sample_corner_br())

    s.build3("outer-corners", _main, move=False)
    s.build3("outer-corners-ref", _ref, fill=True)


def _build_inner_corners(s: TargetSet):
    def _ref(t: TilesetTargetGroup, src: V1SourceSet):
        t.add(2, 1, src.edge_bottom())
        t.add(2, 3, src.edge_top_full())
        t.add(1, 2, src.edge_right())
        t.add(3, 2, src.edge_left())
        t.add(1, 3, src.edge_right())
        t.add(3, 3, src.edge_left())

    def _main(t: TilesetTargetGroup, src: V1SourceSet):
        t.add(1, 1, src.edge_bottom())
        t.add(3, 1, src.edge_bottom())
        t.add(1, 4, src.edge_top())
        t.add(3, 4, src.edge_top())

    s.build3("inner-corners", _main, move=False)
    s.build3("inner-corners-ref", _ref, fill=True)

