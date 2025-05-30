import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

from tilegen.core import GeneratorConfig, TargetSet, TilesetTargetGroup, utils
from tilegen.v1_extended_top.v1_builder import V1SourceSet

def handle(config: GeneratorConfig):
    timer = utils.ProcessTimer()

    src = V1SourceSet(config)
    s = src.create_target_set()
    s.initiate_level(5)
    s.setup(_setup_sources)
    s.set_target_spacing(1, 1, 6, 6)
    s.set_target_size(5, 5)

    _build_connectors_1(s, 1)
    _build_connectors_2(s, 2)
    _build_connectors_3(s, 3)
    _build_connectors_4(s, 4)
    _build_connectors_5(s, 5)
    _build_connectors_6(s, 6)
    # _build_connectors_7(s, 7)
    # _build_connectors_8(s, 8)

    s.cleanup()
    timer.end("Connectors")

def quick(config: GeneratorConfig):
    handle(config)

def _setup_sources(src: V1SourceSet):
    src.setup_sample()
    src.setup_edges()
    src.setup_corners()
    src.setup_singles(corners=False)
    src.setup_transition_tiles()


def _build_connectors_1(s: TargetSet, idx: int):
    def _ref(t: TilesetTargetGroup, src: V1SourceSet):
        t.add(1, 1, src.single_h_full())
        t.add(2, 1, src.edge_top_ext())
        t.add(3, 1, src.edge_top_full())
        t.add(4, 1, src.edge_top_ext())
        t.add(5, 1, src.single_h_full())

        t.add(2, 3, [src.edge_left(), src.in_corner_tl_ext()])
        t.add(3, 3, src.deep_dark())
        t.add(4, 3, [src.edge_right(), src.in_corner_tr_ext()])

        t.add(1, 3, src.single_h_full())
        t.add(3, 4, src.edge_bottom())
        t.add(5, 3, src.single_h_full())

    def _main(t: TilesetTargetGroup, src: V1SourceSet):
        t.add(2, 2, [
            src.in_corner_bl(),
            src.d_right_u(),
            src.d_down_l(),
            src.c_left(),
            src.a_up(),
        ])

        if src.config.is_quick:
            return

        t.add(2, 4, [
            src.in_corner_br(),
            src.d_left_u(),
            src.d_down_r(),
            src.c_right(),
            src.a_up(),
        ])

        t.add(4, 2, [
            src.in_corner_tl(),
            src.d_right_d(),
            src.d_up_l(),
            src.c_left(),
            src.a_down(),
        ])

        t.add(4, 4, [
            src.in_corner_tr(),
            src.d_left_d(),
            src.d_up_r(),
            src.c_right(),
            src.a_down(),
        ])

    s.build3(f"connector-{idx}-ref", _ref, move=False, fill=True)
    s.build3(f"connector-{idx}", _main)


def _build_connectors_2(s: TargetSet, idx: int):
    def _ref(t: TilesetTargetGroup, src: V1SourceSet):
        t.add(2, 1, [src.single_v(), src.in_corner_tr_ext()])
        t.add(4, 1, [src.single_v(), src.in_corner_tl_ext()])

        t.add(3, 1, src.edge_top_full())

        t.add(2, 3, src.edge_left())
        t.add(3, 3, src.deep_light())
        t.add(4, 3, src.edge_right())

        t.add(3, 4, src.edge_bottom())

        t.add(2, 5, src.single_v())
        t.add(4, 5, src.single_v())

    def _main(t: TilesetTargetGroup, src: V1SourceSet):
        t.add(2, 2, [
            src.in_corner_tr(),
            src.d(2),
            src.d(7),
            src.c(1),
            src.a(3),
        ])

        if src.config.is_quick:
            return

        t.add(2, 4, [
            src.in_corner_tl(),
            src.d(1),
            src.d(8),
            src.c(1),
            src.a(2),
        ])

        t.add(4, 2, [
            src.in_corner_br(),
            src.d(3),
            src.d(6),
            src.c(4),
            src.a(3),
        ])

        t.add(4, 4, [
            src.in_corner_bl(),
            src.d(4),
            src.d(5),
            src.c(4),
            src.a(2),
        ])

    s.build3(f"connector-{idx}-ref", _ref, move=False, fill=True)
    s.build3(f"connector-{idx}", _main)


def _build_connectors_3(s: TargetSet, idx: int):
    def _ref(t: TilesetTargetGroup, src: V1SourceSet):
        t.add(2, 1, [src.single_v(), src.in_corner_tr_ext()])

        t.add(3, 1, src.single_h_full())
        t.add(4, 1, src.edge_top_ext())
        t.add(5, 1, src.single_h_full())

        t.add(2, 3, [src.single_v(), src.in_corner_tl_ext(), src.in_corner_tr_ext()])
        t.add(4, 3, [src.single_v(), src.in_corner_tl_ext()])

        t.add(1, 3, src.single_h_full())
        t.add(3, 3, src.single_h_full())

        t.add(4, 5, src.single_v())

    def _main(t: TilesetTargetGroup, src: V1SourceSet):
        t.add(2, 2, [
            src.edge_left(),
            src.c(1), src.c(2), src.c(4),
            src.b(2), src.b(4),
            src.a(3),
        ])

        t.add(4, 2, [
            src.edge_top(),
            src.c(2),
            src.c(3),
            src.c(4),
            src.b(3),
            src.b(4),
            src.a(1),
        ])

        if src.config.is_quick:
            return

        t.add(2, 4, [
            src.edge_bottom(),
            src.c(1),
            src.c(2),
            src.c(3),
            src.b(1),
            src.b(2),
            src.a(4),
        ])

        t.add(4, 4, [
            src.edge_right(),
            src.c(1),
            src.c(3),
            src.c(4),
            src.b(1),
            src.b(3),
            src.a(2),
        ])

    s.build3(f"connector-{idx}-ref", _ref, move=False, fill=True)
    s.build3(f"connector-{idx}", _main)


def _build_connectors_4(s: TargetSet, idx: int):
    def _ref(t: TilesetTargetGroup, src: V1SourceSet):
        t.add(2, 1, [src.single_v(), src.in_corner_tl_ext(), src.in_corner_tr_ext()])
        t.add(4, 1, [src.single_v(), src.in_corner_tl_ext(), src.in_corner_tr_ext()])

        t.add(1, 1, src.single_h_full())
        t.add(3, 1, src.edge_top_full())
        t.add(5, 1, src.single_h_full())

        t.add(2, 3, [src.edge_left(), src.in_corner_tl_ext()])
        t.add(3, 3, src.deep_light())
        t.add(4, 3, [src.edge_right(), src.in_corner_tr_ext()])

        t.add(1, 3, src.single_h_full())
        t.add(3, 4, src.edge_bottom())
        t.add(5, 3, src.single_h_full())

        t.add(2, 5, src.single_v())
        t.add(4, 5, src.single_v())

    def _main(t: TilesetTargetGroup, src: V1SourceSet):
        t.add(2, 2, [
            src.in_corner_tl(),
            src.d(2),
            src.d(7),
            src.c(1),
            src.c(3),
            src.b(1),
            src.b(2),
            src.b(3),
        ], )

        if src.config.is_quick:
            return

        t.add(4, 2, [
            src.in_corner_tr(),
            src.d(1),
            src.d(8),
            src.c(1),
            src.c(2),
            src.b(1),
            src.b(2),
            src.b(4),
        ], )

        t.add(2, 4, [
            src.in_corner_bl(),
            src.d(3),
            src.d(6),
            src.c(3),
            src.c(4),
            src.b(1),
            src.b(3),
            src.b(4),
        ], )

        t.add(4, 4, [
            src.in_corner_br(),
            src.d(4),
            src.d(5),
            src.c(2),
            src.c(4),
            src.b(2),
            src.b(3),
            src.b(4),
        ], )

    s.build3(f"connector-{idx}-ref", _ref, move=False, fill=True)
    s.build3(f"connector-{idx}", _main)


def _build_connectors_5(s: TargetSet, idx: int):
    def _ref(t: TilesetTargetGroup, src: V1SourceSet):
        t.add(3, 1, [src.single_v(), src.in_corner_tl_ext(), src.in_corner_tr_ext()])

        t.add(2, 1, src.out_corner_tl_full())
        t.add(4, 1, src.out_corner_tr_full())
        t.add(2, 2, src.in_corner_tl_ext())
        t.add(4, 2, src.in_corner_tr_ext())

        t.add(1, 2, src.single_h_full())
        t.add(3, 3, src.deep_light())
        t.add(5, 2, src.single_h_full())

        t.add(2, 4, src.out_corner_bl())
        t.add(4, 4, src.out_corner_br())

        t.add(3, 5, src.single_v())

    def _main(t: TilesetTargetGroup, src: V1SourceSet):
        t.add(3, 2, [
            src.in_corner_tl(),
            src.d(1),
            src.d(2),
            src.c(1),
            src.b(1),
            src.b(2),
        ], )

        t.add(2, 3, [
            src.in_corner_tl(),
            src.d(3),
            src.d(7),
            src.c(3),
            src.b(1),
            src.b(3),
        ], )

        if src.config.is_quick:
            return

        t.add(4, 3, [
            src.in_corner_tr(),
            src.d(4),
            src.d(8),
            src.c(2),
            src.b(2),
            src.b(4),
        ], )

        t.add(3, 4, [
            src.in_corner_bl(),
            src.d(5),
            src.d(6),
            src.c(4),
            src.b(3),
            src.b(4),
        ], )

    s.build3(f"connector-{idx}-ref", _ref, move=False, fill=True)
    s.build3(f"connector-{idx}", _main)


def _build_connectors_6(s: TargetSet, idx: int):
    def _ref(t: TilesetTargetGroup, src: V1SourceSet):
        t.add(2, 1, [src.edge_left(), src.in_corner_tl_ext()])
        t.add(3, 1, src.deep_corner_bl())

        t.add(1, 1, src.edge_top_full())
        t.add(3, 2, src.edge_bottom())
        t.add(4, 2, [src.single_v(), src.in_corner_tl_ext(), src.in_corner_tr_ext()])

        t.add(1, 3, src.deep_edge_right())
        t.add(2, 3, src.edge_right())
        t.add(3, 3, src.single_h())
        t.add(5, 2, src.single_h_full())

        t.add(1, 4, src.edge_bottom())
        t.add(3, 4, src.edge_top())
        t.add(4, 4, src.single_v())

        t.add(2, 5, src.edge_left())
        t.add(3, 5, src.deep_corner_tl())

    def _main(t: TilesetTargetGroup, src: V1SourceSet):
        t.add(4, 3, [
            src.in_corner_tl(),
            src.c(1),
            src.c(2),
            src.c(3),
            src.c(4),
            src.b(1),
            src.b(2),
            src.b(3),
            src.b(4),
        ], )

        t.add(2, 2, [
            src.in_corner_tl(),
            src.d(1),
            src.d(3),
            src.d(6),
            src.d(8),
            src.b(1),
            src.b(4),
        ], )

        if src.config.is_quick:
            return

        t.add(2, 4, [
            src.in_corner_tr(),
            src.d(2),
            src.d(4),
            src.d(5),
            src.d(7),
            src.b(2),
            src.b(3),
        ], )

    s.build3(f"connector-{idx}-ref", _ref, move=False, fill=True)
    s.build3(f"connector-{idx}", _main)


def _build_connectors_7(s: TargetSet, idx: int):
    def _ref(t: TilesetTargetGroup, src: V1SourceSet):
        t.add(2, 1, src.out_corner_tl_ext())
        t.add(3, 1, src.single_h_full())
        t.add(4, 1, src.out_corner_tr_ext())

        t.add(2, 3, [src.single_v(), src.in_corner_tr_ext()])
        t.add(4, 3, [src.single_v(), src.in_corner_tl_ext()])

        t.add(3, 3, src.single_h_full())

    def _main(t: TilesetTargetGroup, src: V1SourceSet):
        t.add(2, 2, [
            src.out_corner_tl(),
            src.c(2),
            src.c(4),
            src.b(4),
        ], )

        t.add(4, 2, [
            src.out_corner_tr(),
            src.c(3),
            src.c(4),
            src.b(3),
        ], )

        t.add(2, 4, [
            src.out_corner_bl(),
            src.c(1),
            src.c(2),
            src.b(2),
        ], )

        t.add(4, 4, [
            src.out_corner_br(),
            src.c(1),
            src.c(3),
            src.b(1),
        ], )

    s.build3(f"connector-{idx}-ref", _ref, move=False, fill=True)
    s.build3(f"connector-{idx}", _main)


def _build_connectors_8(s: TargetSet, idx: int):
    def _ref(t: TilesetTargetGroup, src: V1SourceSet):
        t.add(1, 1, src.out_corner_tl_ext())
        t.add(2, 1, src.single_h_full())
        t.add(3, 1, src.out_corner_tr_ext())

        t.add(5, 3, src.single_v())

    def _main(t: TilesetTargetGroup, src: V1SourceSet):
        t.add(1, 2, [
            src.out_corner_tl(),
            src.c(2),
            src.a(4),
        ], )

        t.add(3, 2, [
            src.out_corner_tr(),
            src.c(3),
            src.a(4),
        ], )

        t.add(5, 2, [src.single_v()])
        t.add(5, 4, [src.single_v()])

    s.build3(f"connector-{idx}-ref", _ref, move=False, fill=True)
    s.build3(f"connector-{idx}", _main)
