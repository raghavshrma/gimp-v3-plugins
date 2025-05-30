from tilegen.core import GeneratorConfig, TargetSet, TilesetTargetGroup, utils
from tilegen.v1_extended_top.v1_builder import V1SourceSet


def handle(config: GeneratorConfig):
    s = V1SourceSet(config).create_target_set()
    s.initiate_level(4) # to create l4 group
    s.initiate_level(3)
    s.setup(_setup_sources)

    s.set_target_size(5, 5)
    s.set_target_spacing(13, 5, 1, 4, False)

    s.build3("single-corners", _build_corners, move=False)
    s.build3("single-corners-ref", _build_corners_refs, fill=True)

    s.cleanup()

def quick(config: GeneratorConfig):
    handle(config)

def _setup_sources(src: V1SourceSet):
    src.setup_sample()
    src.setup_corners()
    src.setup_singles(corners = False)
    src.setup_transition_tiles()

def _build_corners_refs(t: TilesetTargetGroup, src: V1SourceSet):
    t.add(3, 1, src.single_h_full())

    t.add(2, 3, [src.single_v(), src.in_corner_tr_ext()])
    t.add(4, 3, [src.single_v(), src.in_corner_tl_ext()])

    t.add(3, 3, src.single_h_full())

def _build_corners(t: TilesetTargetGroup, src: V1SourceSet):
    t.add(2, 1, src.single_left_full())
    t.add(2, 2, [
        src.c(2),
        src.c(4),
        src.b(4),
    ], )

    if src.config.is_quick:
        return

    t.add(4, 1, src.single_right_full())
    t.add(4, 2, [
        src.c(3),
        src.c(4),
        src.b(3),
    ], )

    t.add(2, 4, [
        src.single_left(),
        src.c(1),
        src.c(2),
        src.b(2),
    ], )

    t.add(4, 4, [
        src.single_right(),
        src.c(1),
        src.c(3),
        src.b(1),
    ], )
    pass