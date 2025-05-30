from tilegen.core import BaseSourceSet, GeneratorConfig, TargetSet, TilesetSource, AreaBuilder


class V3Source(BaseSourceSet):
    def __init__(self, config: GeneratorConfig):
        super().__init__(config, config.is_color_target)
        self.src_edge_sample: TilesetSource | None = None

        seam_area_builder = AreaBuilder(config.grid, 24)
        self.seam_area_h = seam_area_builder.mid_seam_horizontal()
        self.seam_area_v = seam_area_builder.mid_seam_vertical()

    # region Edge Sample
    def setup_edge_sample(self):
        self.src_edge_sample = self._init_source("edge-sample")

    def sample_edge(self, x: int, y: int):
        return self.copy(self.src_edge_sample, x, y)

    def edge_sample_block(self, x: int, y: int, wid: int, hei: int):
        return self.copy_block(self.src_edge_sample, x, y, wid, hei)

    def _edge_seam_h(self, x: int, y: int):
        block = self.edge_sample_block(x, y, 2, 1)
        return self.seam_area_h.crop(block)

    def _edge_seam_v(self, x: int, y: int):
        block = self.edge_sample_block(x, y, 1, 2)
        return self.seam_area_v.crop(block)

    def seam_edge_top(self):
        return self._edge_seam_h(1, 1)

    def seam_edge_bottom(self):
        return self._edge_seam_h(1, 3)

    def seam_edge_left(self):
        return self._edge_seam_v(1, 1)

    def seam_edge_right(self):
        return self._edge_seam_v(3, 1)

    def seam_single_h(self):
        return self._edge_seam_h(1, 5)

    def seam_single_v(self):
        return self._edge_seam_v(5, 1)

    def sample_edge_top(self):
        return self.sample_edge(2, 1)

    def sample_edge_bottom(self):
        return self.sample_edge(2, 3)

    def sample_edge_left(self):
        return self.sample_edge(1, 2)

    def sample_edge_right(self):
        return self.sample_edge(3, 2)

    def sample_corner_tl(self):
        return self.sample_edge(1, 1)

    def sample_corner_tr(self):
        return self.sample_edge(3, 1)

    def sample_corner_bl(self):
        return self.sample_edge(1, 3)

    def sample_corner_br(self):
        return self.sample_edge(3, 3)

    def sample_single_h(self):
        return self.sample_edge(2, 5)

    def sample_single_left(self):
        return self.sample_edge(1, 5)

    def sample_single_right(self):
        return self.sample_edge(3, 5)

    def sample_single_v(self):
        return self.sample_edge(5, 2)

    def sample_single_top(self):
        return self.sample_edge(5, 1)

    def sample_single_bottom(self):
        return self.sample_edge(5, 3)

    # endregion



V3Target = TargetSet[V3Source]