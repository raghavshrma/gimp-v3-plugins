from tilegen.core import GeneratorConfig, TargetSet, TilesetTargetGroup, utils
from tilegen.v1_extended_top.v1_builder import V1SourceSet


def handle(config: GeneratorConfig):
    s = V1SourceSet(config).create_target_set()
    s.initiate_level(2, [1])
    s.setup(_setup_sources)
    s.set_target_size(3, 3)
    s.set_target_spacing(1, 14, 4, 4)

    _build_outer_corner_edge_refs(s)
    _build_inner_corner_edge_refs(s)

    s.cleanup()


def quick(config: GeneratorConfig):
    handle(config)


def _setup_sources(src: V1SourceSet):
    src.setup_corners()


def _build_outer_corner_edge_refs(s: TargetSet):
    def _h_ref(t: TilesetTargetGroup, src: V1SourceSet):
        t.add(1, 1, src.out_corner_tl_full())
        t.add(3, 1, src.out_corner_tr_full())
        t.add(1, 3, src.out_corner_bl())
        t.add(3, 3, src.out_corner_br())

    def _v_ref(t: TilesetTargetGroup, src: V1SourceSet):
        t.add(1, 1, src.out_corner_tl())
        t.add(3, 1, src.out_corner_tr())
        t.add(1, 3, src.out_corner_bl())
        t.add(3, 3, src.out_corner_br())

    s.build3("outer-corners-edge-h-ref", _h_ref, fill=True)
    s.build3("outer-corners-edge-v-ref", _v_ref, fill=True)


def _build_inner_corner_edge_refs(s: TargetSet):
    def _h_ref(t: TilesetTargetGroup, src: V1SourceSet):
        t.add(1, 1, src.in_corner_tr_full())
        t.add(3, 1, src.in_corner_tl_full())
        t.add(1, 3, src.in_corner_br())
        t.add(3, 3, src.in_corner_bl())

    def _v_ref(t: TilesetTargetGroup, src: V1SourceSet):
        t.add(1, 1, src.in_corner_bl())
        t.add(3, 1, src.in_corner_br())
        t.add(1, 3, src.in_corner_tl())
        t.add(3, 3, src.in_corner_tr())

        src.is_empty_allowed = False
        t.add(1, 2, src.in_corner_tl_ext())
        t.add(3, 2, src.in_corner_tr_ext())
        src.is_empty_allowed = True

    s.build3("inner-corners-edge-h-ref", _h_ref, fill=True)
    s.build3("inner-corners-edge-v-ref", _v_ref, fill=True)