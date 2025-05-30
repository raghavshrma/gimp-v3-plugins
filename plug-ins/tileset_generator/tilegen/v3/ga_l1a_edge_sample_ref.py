from tilegen.core import GeneratorConfig, TilesetTargetGroup, AreaBuilder
from tilegen.v3.v3_collection import V3Source, V3Target

def handle(config: GeneratorConfig):
    s = _initiate(config)
    s.build3("edge-sample-ref-seams", _build_sample_ref_seams)
    s.cleanup()

def _initiate(config: GeneratorConfig):
    s = V3Source(config).create_target_set()
    s.initiate_level(1)
    s.setup(_setup_sources)
    s.set_target_size(5, 5)
    return s


def _setup_sources(src: V3Source):
    src.setup_edge_sample()

def _build_sample_ref_seams(t: TilesetTargetGroup, src: V3Source):
    for i in range(1, 3):
        t.add(i, 1, src.seam_edge_top())
        t.add(i, 3, src.seam_edge_bottom())
        t.add(i, 5, src.seam_single_h())

        t.add(1, i, src.seam_edge_left())
        t.add(3, i, src.seam_edge_right())
        t.add(5, i, src.seam_single_v())
