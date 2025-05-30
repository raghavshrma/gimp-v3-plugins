import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

from tilegen.core import BaseSourceSet, GeneratorConfig, TilesetSource, utils, TargetSet

CONNECTOR_GRID_MAP = {
    1: [(2, 2), (4, 2), (2, 4), (4, 4)],
    2: [(2, 2), (4, 2), (2, 4), (4, 4)],
    3: [(2, 2), (4, 2), (2, 4), (4, 4)],
    4: [(2, 2), (4, 2), (2, 4), (4, 4)],
    5: [(2, 3), (4, 3), (3, 4), (3, 2)],
    6: [(2, 2), (2, 4), (4, 3)],
}

class V1SourceSet(BaseSourceSet):
    def __init__(self, config: GeneratorConfig):
        super().__init__(config, config.is_color_target)
        self.src_a: None | TilesetSource = None
        self.src_b: None | TilesetSource = None
        self.src_c: None | TilesetSource = None
        self.src_d1: None | TilesetSource = None
        self.src_d2: None | TilesetSource = None
        self.src_edges_h: list[TilesetSource] = []
        self.src_edges_v: list[TilesetSource] = []
        self.src_inner_corner: None | TilesetSource = None
        self.src_outer_corner: None | TilesetSource = None
        self.src_singles_h: list[TilesetSource] = []
        self.src_singles_v: list[TilesetSource] = []
        self.src_single_corners: TilesetSource | None = None
        self.src_connectors: list[TilesetSource] = []

    def create_target_set(self):
        return TargetSet(self)

    # region Sample Tiles
    def setup_sample(self):
        self.src_sample = self._init_source("sample")

    def sample_block(self, col: int, row: int, cols: int, rows: int):
        return self.copy_block(self.src_sample, col, row, cols, rows)

    def sample_edge_top_full(self, index: int = 1):
        return self.copy_full(self.src_sample, 1 + index, 2)

    def sample_edge_top(self, index: int = 1):
        return self.copy(self.src_sample, 1 + index, 2)

    def sample_edge_top_ext(self, index: int = 1):
        return self.copy(self.src_sample, 1 + index, 1)

    def sample_edge_bottom(self, index: int = 1):
        return self.copy(self.src_sample, 1 + index, 8)

    def sample_edge_left(self, index: int = 1):
        return self.copy(self.src_sample, 1, 2 + index)

    def sample_edge_right(self, index: int = 1):
        return self.copy(self.src_sample, 8, 2 + index)

    def sample_corner_tl_full(self):
        return self.copy_full(self.src_sample, 1, 2)

    def sample_corner_tl_ext(self):
        return self.copy(self.src_sample, 1, 1)

    def sample_corner_tl(self):
        return self.copy(self.src_sample, 1, 2)

    def sample_corner_tr_full(self):
        return self.copy_full(self.src_sample, 8, 2)

    def sample_corner_tr_ext(self):
        return self.copy(self.src_sample, 8, 1)

    def sample_corner_tr(self):
        return self.copy(self.src_sample, 8, 1)

    def sample_corner_bl(self):
        return self.copy(self.src_sample, 1, 8)

    def sample_corner_br(self):
        return self.copy(self.src_sample, 8, 8)

    def sample_single_h(self, index: int = 1):
        return self.copy(self.src_sample, 1 + index, 10)

    def sample_single_h_full(self, index: int = 1):
        return self.copy_full(self.src_sample, 1 + index, 10)

    def sample_single_h_ext(self, index: int = 1):
        return self.copy(self.src_sample, 1 + index, 9)

    def sample_single_h_left(self):
        return self.copy(self.src_sample, 1, 10)

    def sample_single_h_left_full(self):
        return self.copy_full(self.src_sample, 1, 10)

    def sample_single_h_left_ext(self):
        return self.copy(self.src_sample, 1, 9)

    def sample_single_h_right(self):
        return self.copy(self.src_sample, 8, 10)

    def sample_single_h_right_full(self):
        return self.copy_full(self.src_sample, 8, 10)

    def sample_single_h_right_ext(self):
        return self.copy(self.src_sample, 8, 9)

    def sample_single_v(self, index: int = 1):
        return self.copy(self.src_sample, 10, 2 + index)

    def sample_single_v_top(self):
        return self.copy(self.src_sample, 10, 2)

    def sample_single_v_top_full(self):
        return self.copy_full(self.src_sample, 10, 2)

    def sample_single_v_top_ext(self):
        return self.copy(self.src_sample, 10, 1)

    def sample_single_v_bottom(self):
        return self.copy(self.src_sample, 10, 8)

    def deep_dark(self):
        return self.copy(self.src_sample, 3, 4)

    def deep_light(self):
        return self.copy(self.src_sample, 3, 5)

    def deep_edge_top(self):
        return self.copy(self.src_sample, 3, 3)

    def deep_edge_bottom(self):
        return self.copy(self.src_sample, 3, 7)

    def deep_edge_left(self):
        return self.copy(self.src_sample, 2, 4)

    def deep_edge_right(self):
        return self.copy(self.src_sample, 7, 4)

    def deep_corner_tl(self):
        return self.copy(self.src_sample, 2, 3)

    def deep_corner_tr(self):
        return self.copy(self.src_sample, 7, 3)

    def deep_corner_bl(self):
        return self.copy(self.src_sample, 2, 7)

    def deep_corner_br(self):
        return self.copy(self.src_sample, 7, 7)

    def deep_center_complete(self):
        return self.copy_block(self.src_sample, 2, 3, 6, 5)

    # endregion

    # region Edges

    def setup_edges(self):
        layers = utils.get_group_layer_dict(self.image, f"{self.prefix}l1")

        for i in self.config.range_cols():
            layer = layers[f"{self.prefix}l1-edge-h-{i}"]
            src = self._init_source(layer)
            self.src_edges_h.append(src)

        for i in self.config.range_rows():
            layer = layers[f"{self.prefix}l1-edge-v-{i}"]
            src = self._init_source(layer)
            self.src_edges_v.append(src)

    def edge_top_full(self, index: int = 1) -> Gimp.Layer:
        return self.copy_full_l(self.src_edges_h, index, 2, 2)

    def edge_top(self, index: int = 1) -> Gimp.Layer:
        return self.copy_l(self.src_edges_h, index, 2, 2)

    def edge_top_ext(self, index: int = 1) -> Gimp.Layer:
        return self.copy_l(self.src_edges_h, index, 2, 1)

    def edge_bottom(self, index: int = 1) -> Gimp.Layer:
        return self.copy_l(self.src_edges_h, index, 2, 3)

    def edge_left(self, index: int = 1) -> Gimp.Layer:
        return self.copy_l(self.src_edges_v, index, 1, 2)

    def edge_right(self, index: int = 1) -> Gimp.Layer:
        return self.copy_l(self.src_edges_v, index, 3, 2)

    # endregion

    # region Corners

    def setup_corners(self):
        self.src_inner_corner = self._init_source("l2-inner-corners")
        self.src_outer_corner = self._init_source("l2-outer-corners")

    def in_corner_tl(self):
        return self.copy(self.src_inner_corner, 3, 4)

    def in_corner_tr(self):
        return self.copy(self.src_inner_corner, 1, 4)

    def in_corner_bl(self):
        return self.copy(self.src_inner_corner, 3, 1)

    def in_corner_br(self):
        return self.copy(self.src_inner_corner, 1, 1)

    def in_corner_tl_full(self):
        return self.copy_full(self.src_inner_corner, 3, 4)

    def in_corner_tr_full(self):
        return self.copy_full(self.src_inner_corner, 1, 4)

    def in_corner_tl_ext(self):
        return self.copy(self.src_inner_corner, 3, 3)

    def in_corner_tr_ext(self):
        return self.copy(self.src_inner_corner, 1, 3)

    def out_corner_tl(self):
        return self.copy(self.src_outer_corner, 1, 2)

    def out_corner_tr(self):
        return self.copy(self.src_outer_corner, 3, 2)

    def out_corner_bl(self):
        return self.copy(self.src_outer_corner, 1, 4)

    def out_corner_br(self):
        return self.copy(self.src_outer_corner, 3, 4)

    def out_corner_tl_full(self):
        return self.copy_full(self.src_outer_corner, 1, 2)

    def out_corner_tr_full(self):
        return self.copy_full(self.src_outer_corner, 3, 2)

    def out_corner_tl_ext(self):
        return self.copy(self.src_outer_corner, 1, 1)

    def out_corner_tr_ext(self):
        return self.copy(self.src_outer_corner, 3, 1)

    # endregion

    # region Singles

    def setup_singles(self, corners: bool = True):
        layers = utils.get_group_layer_dict(self.image, f"{self.prefix}l3")

        layer = layers[f"{self.prefix}l3-single-h-left"]
        src = self._init_source(layer)
        self.src_singles_h.append(src)

        for i in self.config.range_cols():
            layer = layers[f"{self.prefix}l3-single-h-{i}"]
            src = self._init_source(layer)
            self.src_singles_h.append(src)

        layer = layers[f"{self.prefix}l3-single-h-right"]
        src = self._init_source(layer)
        self.src_singles_h.append(src)

        layer = layers[f"{self.prefix}l3-single-v-top"]
        src = self._init_source(layer)
        self.src_singles_v.append(src)

        for i in self.config.range_rows():
            layer = layers[f"{self.prefix}l3-single-v-{i}"]
            src = self._init_source(layer)
            self.src_singles_v.append(src)

        layer = layers[f"{self.prefix}l3-single-v-bottom"]
        src = self._init_source(layer)
        self.src_singles_v.append(src)

        if corners:
            layer = layers[f"{self.prefix}l3-single-corners"]
            self.src_single_corners = self._init_source(layer)

    def single_h_full(self, index: int = 1) -> Gimp.Layer:
        return self.copy_full_l(self.src_singles_h, index + 1, 2, 2)

    def single_h_ext(self, index: int = 1) -> Gimp.Layer:
        return self.copy_l(self.src_singles_h, index + 1, 2, 1)

    def single_h(self, index: int = 1) -> Gimp.Layer:
        return self.copy_l(self.src_singles_h, index + 1, 2, 2)

    def single_v(self, index: int = 1) -> Gimp.Layer:
        return self.copy_l(self.src_singles_v, index + 1, 2, 2)

    def single_top_full(self) -> Gimp.Layer:
        return self.copy_full_l(self.src_singles_v, 1, 2, 2)

    def single_top_ext(self) -> Gimp.Layer:
        return self.copy_l(self.src_singles_v, 1, 2, 1)

    def single_top(self) -> Gimp.Layer:
        return self.copy_l(self.src_singles_v, 1, 2, 2)

    def single_bottom(self) -> Gimp.Layer:
        return self.copy_l(self.src_singles_v, 7, 2, 2)

    def single_left_full(self) -> Gimp.Layer:
        return self.copy_full_l(self.src_singles_h, 1, 2, 2)

    def single_left_ext(self) -> Gimp.Layer:
        return self.copy_l(self.src_singles_h, 1, 2, 1)

    def single_left(self) -> Gimp.Layer:
        return self.copy_l(self.src_singles_h, 1, 2, 2)

    def single_right_full(self) -> Gimp.Layer:
        return self.copy_full_l(self.src_singles_h, 8, 2, 2)

    def single_right_ext(self) -> Gimp.Layer:
        return self.copy_l(self.src_singles_h, 8, 2, 1)

    def single_right(self) -> Gimp.Layer:
        return self.copy_l(self.src_singles_h, 8, 2, 2)

    def single_corner_tl_full(self) -> Gimp.Layer:
        return self.copy_full(self.src_single_corners, 2, 2)

    def single_corner_tl_ext(self) -> Gimp.Layer:
        return self.copy(self.src_single_corners, 2, 1)

    def single_corner_tl(self) -> Gimp.Layer:
        return self.copy(self.src_single_corners, 2, 2)

    def single_corner_tr_full(self) -> Gimp.Layer:
        return self.copy_full(self.src_single_corners, 4, 2)

    def single_corner_tr_ext(self) -> Gimp.Layer:
        return self.copy(self.src_single_corners, 4, 1)

    def single_corner_tr(self) -> Gimp.Layer:
        return self.copy(self.src_single_corners, 4, 2)

    def single_corner_bl(self) -> Gimp.Layer:
        return self.copy(self.src_single_corners, 2, 4)

    def single_corner_br(self) -> Gimp.Layer:
        return self.copy(self.src_single_corners, 4, 4)

    # endregion

    # region Transition Tiles
    def setup_transition_tiles(self, allow_none: bool = True):
        layers = utils.get_group_layer_dict(self.image, self.layer_name("l4"))
        self.src_a = self._bulk_src(layers, "l4-transition-ref-a", allow_none)
        self.src_b = self._bulk_src(layers, "l4-transition-ref-b", allow_none)
        self.src_c = self._bulk_src(layers, "l4-transition-ref-c", allow_none)
        self.src_d1 = self._bulk_src(layers, "l4-transition-ref-d1", allow_none)
        self.src_d2 = self._bulk_src(layers, "l4-transition-ref-d2", allow_none)

    def a(self, index: int) -> Gimp.Layer:
        return self.copy_index(self.src_a, index)

    def b(self, index: int) -> Gimp.Layer:
        return self.copy_index(self.src_b, index)

    def c(self, index: int) -> Gimp.Layer:
        return self.copy_index(self.src_c, index)

    def d(self, index: int) -> Gimp.Layer:
        if index <= 2:
            return self.copy_index(self.src_d1, index)
        elif index <= 4:
            return self.copy_index(self.src_d2, index - 2)
        elif index <= 6:
            return self.copy_index(self.src_d1, index - 2)
        else:
            return self.copy_index(self.src_d2, index - 4)

    def a_up(self):
        return self.a(1)

    def a_right(self):
        return self.a(2)

    def a_left(self):
        return self.a(3)

    def a_down(self):
        return self.a(4)

    def b_tl(self):
        return self.b(1)

    def b_tr(self):
        return self.b(2)

    def b_bl(self):
        return self.b(3)

    def b_br(self):
        return self.b(4)

    def c_up(self):
        return self.c(1)

    def c_right(self):
        return self.c(2)

    def c_left(self):
        return self.c(3)

    def c_down(self):
        return self.c(4)

    def d_left_u(self):
        return self.d(1)

    def d_right_u(self):
        return self.d(2)

    def d_up_l(self):
        return self.d(3)

    def d_up_r(self):
        return self.d(4)

    def d_left_d(self):
        return self.d(5)

    def d_right_d(self):
        return self.d(6)

    def d_down_l(self):
        return self.d(7)

    def d_down_r(self):
        return self.d(8)

    # endregion

    # region Connectors

    def setup_connectors(self):
        layers = utils.get_group_layer_dict(self.image, f"{self.prefix}l5")

        for i in self.config.range_cols():
            layer = layers[f"{self.prefix}l5-connector-{i}"]
            src = self._init_source(layer)
            self.src_connectors.append(src)

    def connector(self, c_type: int, index: int):
        l = CONNECTOR_GRID_MAP[c_type]
        col, row = l[index - 1]
        return self.copy_l(self.src_connectors, c_type, col, row)

    def connect_1_up_r(self):
        return self.connector(1, 1)

    def connect_1_up_l(self):
        return self.connector(1, 2)

    def connect_1_down_r(self):
        return self.connector(1, 3)

    def connect_1_down_l(self):
        return self.connector(1, 4)

    def connect_2_left_d(self):
        return self.connector(2, 1)

    def connect_2_right_d(self):
        return self.connector(2, 2)

    def connect_2_left_u(self):
        return self.connector(2, 3)

    def connect_2_right_u(self):
        return self.connector(2, 4)

    def connect_3_left(self):
        return self.connector(3, 1)

    def connect_3_up(self):
        return self.connector(3, 2)

    def connect_3_down(self):
        return self.connector(3, 3)

    def connect_3_right(self):
        return self.connector(3, 4)

    def connect_4_tl(self):
        return self.connector(4, 1)

    def connect_4_tr(self):
        return self.connector(4, 2)

    def connect_4_bl(self):
        return self.connector(4, 3)

    def connect_4_br(self):
        return self.connector(4, 4)

    def connect_5_right(self):
        return self.connector(5, 1)

    def connect_5_down(self):
        return self.connector(5, 2)

    def connect_5_up(self):
        return self.connector(5, 3)

    def connect_5_left(self):
        return self.connector(5, 4)

    def connect_6_tl_br(self):
        return self.connector(6, 1)

    def connect_6_tr_bl(self):
        return self.connector(6, 2)

    def connect_6_all(self):
        return self.connector(6, 3)

    # endregion

V1TargetSet = TargetSet[V1SourceSet]