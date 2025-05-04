import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

import utils
from tileset_collection import TilesetSource, TilesetTargetGroup
from generator_config import GeneratorConfig
from collections.abc import Callable

CONNECTOR_GRID_MAP = {
    1: [(2, 2), (4, 2), (2, 4), (4, 4)],
    2: [(2, 2), (4, 2), (2, 4), (4, 4)],
    3: [(2, 2), (4, 2), (2, 4), (4, 4)],
    4: [(2, 2), (4, 2), (2, 4), (4, 4)],
    5: [(2, 3), (4, 3), (3, 4), (3, 2)],
    6: [(2, 2), (2, 4), (4, 3)],
}


class BaseBuilder:
    def __init__(self, config: GeneratorConfig, is_color_source: bool):
        self.config = config
        self.image = config.image
        self.is_quick = config.is_quick

        self.target_root: None | Gimp.GroupLayer = None
        self._source_list: list[TilesetSource] = []
        self._hidden_list: list[Gimp.Item] = []
        self.is_color_source = is_color_source
        self.prefix = config.get_prefix(is_color_source)
        root_group_name = config.get_root_name(is_color_source)
        self.root = config.find_group(root_group_name)

        self.grid = config.grid
        self.src_custom: dict[str, TilesetSource] = {}

        self.src_sample: None | TilesetSource = None
        self.src_empty: None | TilesetSource = None
        self.is_empty_allowed = True

        self._setup_empty()

    def layer_name(self, name: str):
        return f"{self.prefix}{name}"

    def _init_source(self, layer: str | Gimp.Layer) -> TilesetSource:
        layer = type(layer) == str and self.layer_name(layer) or layer
        source = TilesetSource(self.image, layer, self.target_root)
        self._source_list.append(source)
        self._check_hidden_source(source.layer)
        self._check_hidden_source(source.layer.get_parent())
        return source

    def _check_hidden_source(self, layer: Gimp.Item):
        if not layer:
            return

        if not layer.get_visible():
            layer.set_visible(True)
            self._hidden_list.append(layer)

    def _bulk_src(
        self, layers: dict[str, Gimp.Layer], name: str, allow_none: bool = False
    ):
        name = self.layer_name(name)
        layer = layers.get(name)
        if layer is None:
            if allow_none:
                return None
            raise ValueError(f"Layer {name} not found in the image.")
        return self._init_source(layer)

    def custom_source(self, layer: str | Gimp.Layer) -> TilesetSource:
        key = type(layer) == str and layer or layer.get_name()
        source = self._init_source(layer)
        self.src_custom[key] = source
        return source

    def set_temp_parent(self, parent: Gimp.GroupLayer):
        self._set_all_parent(parent)

    def unset_temp_parent(self):
        self._set_all_parent(self.target_root)

    def _set_all_parent(self, parent: Gimp.GroupLayer):
        for source in self._source_list:
            source.default_parent = parent

    def cleanup(self):
        for layer in self._hidden_list:
            layer.set_visible(False)

    def get_target_group(
        self,
        name: str,
        x: int,
        y: int,
        cols: int = 5,
        rows: int = 5,
        parent: Gimp.GroupLayer | None = None,
    ) -> TilesetTargetGroup:
        parent = parent or self.target_root or self.root
        target_group = TilesetTargetGroup(
            self.image, name, parent, cols, rows, x, y, True
        )
        self.set_temp_parent(target_group.group)
        return target_group

    # region Copy Logics

    def copy(self, src: TilesetSource, col: int, row: int):
        if src is None:
            return self.empty_block(1, 1)

        return src.copy(col, row)

    def copy_index(self, src: TilesetSource, index: int):
        if src is None:
            return self.empty_block(1, 1)

        return src.copy_index(index)

    def copy_block(self, src: TilesetSource, col: int, row: int, cols: int, rows: int):
        if src is None:
            return self.empty_block(cols, rows)

        return src.copy_block2(col, row, cols, rows)

    def copy_full(self, src: TilesetSource, col: int, row: int):
        if src is None:
            return self.empty_block(1, 2)

        return src.copy_block2(col, row - 1, 1, 2)

    def copy_l(self, src: list[TilesetSource], index: int, col: int, row: int):
        src = utils.element_at(src, index - 1)
        return self.copy(src, col, row)

    def copy_block_l(
        self,
        src: list[TilesetSource],
        index: int,
        col: int,
        row: int,
        cols: int,
        rows: int,
    ):
        src = utils.element_at(src, index - 1)
        return self.copy_block(src, col, row, cols, rows)

    def copy_full_l(self, src: list[TilesetSource], index: int, col: int, row: int):
        src = utils.element_at(src, index - 1)
        return self.copy_full(src, col, row)

    def copy_custom(self, key: str, col: int, row: int):
        return self.copy(self.src_custom.get(key), col, row)

    def copy_block_custom(self, key: str, col: int, row: int, cols: int, rows: int):
        return self.copy_block(self.src_custom.get(key), col, row, cols, rows)

    # endregion

    # region Empty Tiles

    def _setup_empty(self):
        self.src_empty = self._init_source("empty")

    def empty_block(self, cols: int = 1, rows: int = 1):
        if not self.is_empty_allowed:
            return None
        return self.src_empty.copy_block2(1, 1, cols, rows)

    # endregion


class Builder(BaseBuilder):
    def __init__(self, config: GeneratorConfig, is_color_source: bool):
        super().__init__(config, is_color_source)
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


class QuickBuilder(BaseBuilder):
    def __init__(self, config: GeneratorConfig, is_color_source: bool):
        super().__init__(config, is_color_source)
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

    # region Sample Tiles
    def setup_sample(self):
        self.src_sample = self._init_source("sample")

    def sample_block(self, col: int, row: int, cols: int, rows: int):
        return self.copy_block(self.src_sample, col, row, cols, rows)

    def sample_edge_top_full(self, index: int = 1):
        return self.copy_full(self.src_sample, 2 + index, 2)

    def sample_edge_top(self, index: int = 1):
        return self.copy(self.src_sample, 2 + index, 2)

    def sample_edge_top_ext(self, index: int = 1):
        return self.copy(self.src_sample, 2 + index, 1)

    def sample_edge_bottom(self, index: int = 1):
        return self.copy(self.src_sample, 2 + index, 5)

    def sample_edge_left(self, index: int = 1):
        return self.copy(self.src_sample, 2, 2 + index)

    def sample_edge_right(self, index: int = 1):
        return self.copy(self.src_sample, 5, 2 + index)

    def sample_corner_tl_full(self):
        return self.copy_full(self.src_sample, 2, 2)

    def sample_corner_tl_ext(self):
        return self.copy(self.src_sample, 2, 1)

    def sample_corner_tl(self):
        return self.copy(self.src_sample, 2, 2)

    def sample_corner_tr_full(self):
        return self.copy_full(self.src_sample, 5, 2)

    def sample_corner_tr_ext(self):
        return self.copy(self.src_sample, 5, 1)

    def sample_corner_tr(self):
        return self.copy(self.src_sample, 5, 1)

    def sample_corner_bl(self):
        return self.copy(self.src_sample, 2, 5)

    def sample_corner_br(self):
        return self.copy(self.src_sample, 5, 5)

    def sample_single_h(self, index: int = 1):
        return self.copy(self.src_sample, 2 + index, 7)

    def sample_single_h_full(self, index: int = 1):
        return self.copy_full(self.src_sample, 2 + index, 7)

    def sample_single_h_ext(self, index: int = 1):
        return self.copy(self.src_sample, 2 + index, 6)

    def sample_single_h_left(self):
        return self.copy(self.src_sample, 2, 7)

    def sample_single_h_left_full(self):
        return self.copy_full(self.src_sample, 2, 7)

    def sample_single_h_left_ext(self):
        return self.copy(self.src_sample, 2, 6)

    def sample_single_h_right(self):
        return self.copy(self.src_sample, 5, 7)

    def sample_single_h_right_full(self):
        return self.copy_full(self.src_sample, 5, 7)

    def sample_single_h_right_ext(self):
        return self.copy(self.src_sample, 5, 6)

    def sample_single_v(self, index: int = 1):
        return self.copy(self.src_sample, 7, 2 + index)

    def sample_single_v_top(self):
        return self.copy(self.src_sample, 7, 2)

    def sample_single_v_top_full(self):
        return self.copy_full(self.src_sample, 7, 2)

    def sample_single_v_top_ext(self):
        return self.copy(self.src_sample, 7, 1)

    def sample_single_v_bottom(self):
        return self.copy(self.src_sample, 7, 5)

    def deep_dark(self):
        return self.copy(self.src_sample, 7, 7)

    def deep_light(self):
        return self.deep_edge_top()

    def deep_edge_top(self, index: int = 1):
        return self.copy(self.src_sample, 8 + index, 5)

    def deep_edge_bottom(self, index: int = 1):
        return self.copy(self.src_sample, 8 + index, 7)

    def deep_edge_left(self, index: int = 1):
        return self.copy(self.src_sample, 8 + index, 6)

    def deep_edge_right(self, index: int = 1):
        left = self.deep_edge_left(index)
        left.transform_flip_simple(Gimp.OrientationType.HORIZONTAL, True, 0)

    def deep_corner_tl(self):
        return self.copy(self.src_sample, 3, 3)

    def deep_corner_tr(self):
        return self.copy(self.src_sample, 4, 3)

    def deep_corner_bl(self):
        return self.copy(self.src_sample, 3, 4)

    def deep_corner_br(self):
        return self.copy(self.src_sample, 4, 4)

    def sample_seam_edge_top(self):
        return self.sample_block(2, 1, 2, 2)

    def sample_seam_edge_bottom(self):
        return self.sample_block(2, 5, 2, 1)

    def sample_seam_edge_left(self):
        return self.sample_block(2, 2, 1, 2)

    def sample_seam_edge_right(self):
        return self.sample_block(5, 2, 1, 2)

    def sample_seam_single_row(self):
        return self.sample_block(2, 6, 2, 2)

    def sample_seam_single_col(self):
        return self.sample_block(7, 2, 1, 2)

    # endregion

    # region Edges

    def setup_edges(self):
        layers = utils.get_group_layer_dict(self.image, self.layer_name("l1"))

        for i in self.config.range_cols():
            key = self.layer_name(f"l1-edge-h-{i}")
            src = self._init_source(layers[key])
            self.src_edges_h.append(src)

        for i in self.config.range_rows():
            key = self.layer_name(f"l1-edge-v-{i}")
            src = self._init_source(layers[key])
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
        layers = utils.get_group_layer_dict(self.image, self.layer_name("l3"))

        key = self.layer_name("l3-single-h-left")
        src = self._init_source(layers[key])
        self.src_singles_h.append(src)

        for i in self.config.range_cols():
            key = self.layer_name(f"l3-single-h-{i}")
            src = self._init_source(layers[key])
            self.src_singles_h.append(src)

        key = self.layer_name("l3-single-h-right")
        src = self._init_source(layers[key])
        self.src_singles_h.append(src)

        key = self.layer_name("l3-single-v-top")
        src = self._init_source(layers[key])
        self.src_singles_v.append(src)

        for i in self.config.range_rows():
            key = self.layer_name(f"l3-single-v-{i}")
            src = self._init_source(layers[key])
            self.src_singles_v.append(src)

        key = self.layer_name("l3-single-v-bottom")
        src = self._init_source(layers[key])
        self.src_singles_v.append(src)

        if corners:
            key = self.layer_name("l3-single-corners")
            self.src_single_corners = self._init_source(layers[key])

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
        return self.copy_l(self.src_singles_v, 4, 2, 2)

    def single_left_full(self) -> Gimp.Layer:
        return self.copy_full_l(self.src_singles_h, 1, 2, 2)

    def single_left_ext(self) -> Gimp.Layer:
        return self.copy_l(self.src_singles_h, 1, 2, 1)

    def single_left(self) -> Gimp.Layer:
        return self.copy_l(self.src_singles_h, 1, 2, 2)

    def single_right_full(self) -> Gimp.Layer:
        return self.copy_full_l(self.src_singles_h, 4, 2, 2)

    def single_right_ext(self) -> Gimp.Layer:
        return self.copy_l(self.src_singles_h, 4, 2, 1)

    def single_right(self) -> Gimp.Layer:
        return self.copy_l(self.src_singles_h, 4, 2, 2)

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

        for i in range(1, 7):
            layer = layers[f"{self.prefix}l5-connector-{i}"]
            src = self._init_source(layer)
            self.src_connectors.append(src)

    def connector(self, c_type: int, index: int):
        l = CONNECTOR_GRID_MAP[c_type]
        col, row = l[index - 1]
        return self.copy_l(self.src_connectors, c_type, col, row)

    def connect_1_up_l(self):
        return self.connector(1, 1)

    def connect_1_up_r(self):
        return self.connector(1, 2)

    def connect_1_down_l(self):
        return self.connector(1, 3)

    def connect_1_down_r(self):
        return self.connector(1, 4)

    def connect_2_left_u(self):
        return self.connector(2, 1)

    def connect_2_right_u(self):
        return self.connector(2, 2)

    def connect_2_left_d(self):
        return self.connector(2, 3)

    def connect_2_right_d(self):
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


BuildFnType = Callable[[TilesetTargetGroup, QuickBuilder | Builder], None]
QuickBuildFnType = Callable[[TilesetTargetGroup, QuickBuilder], None]


class BuilderSet:
    def __init__(self, config: GeneratorConfig):
        self.config = config
        self.image = config.image
        self.is_quick = config.is_quick

        BType = QuickBuilder if self.is_quick else Builder
        self.colors = BType(config, True)
        self.outlines = BType(config, False)

        self.grid = config.grid
        self.is_color_target = config.is_color_target
        self._orientation_h = True

        self.level_root: None | Gimp.GroupLayer = None
        self.level_root_name: None | str = None

        self._x = 0
        self._y = 0
        self._cx = 0
        self._cy = 0
        self._dx = 0
        self._dy = 0
        self._max_z = 0
        self._cols = 5
        self._rows = 5

        self.set_target_spacing(0, 0, 6, 6)

    def initiate_level(self, level: int, dependencies: list[int] = None):
        self.level_root = self.config.initiate_level(level, dependencies)
        self.level_root_name = self.level_root.get_name()
        return self.level_root

    def set_target_spacing(
        self, x: int, y: int, dx: int, dy: int, orient_h: bool = True, per_row: int = 0
    ):
        self._x = x * self.grid
        self._y = y * self.grid
        self._cx = self._x
        self._cy = self._y
        self._dx = dx * self.grid
        self._dy = dy * self.grid

        self._orientation_h = orient_h
        if orient_h:
            max_blocks = (self.image.get_width() - self._x) // self._dx
            max_blocks = min(max_blocks, per_row) if per_row > 0 else max_blocks
            self._max_z = self._x + ((max_blocks - 1) * self._dx)
        else:
            max_blocks = (self.image.get_height() - self._y) // self._dy
            max_blocks = min(max_blocks, per_row) if per_row > 0 else max_blocks
            self._max_z = self._y + ((max_blocks - 1) * self._dy)

    def set_target_size(self, cols: int, rows: int):
        self._cols = cols
        self._rows = rows

    def next_target_position(self):
        if self._orientation_h:
            if self._cx >= self._max_z:
                self._cx = self._x
                self._cy += self._dy
            else:
                self._cx += self._dx
        else:
            if self._cy >= self._max_z:
                self._cy = self._y
                self._cx += self._dx
            else:
                self._cy += self._dy

    def next_target_row(self):
        if self._orientation_h:
            self._cx = self._x
            self._cy += self._dy
        else:
            self._cy = self._y
            self._cx += self._dx

    def create_target(self, name: str, cols: int = 0, rows: int = 0):
        return self.create_target_at(self._cx, self._cy, name, cols, rows)

    def create_target_at(
        self, x: int, y: int, name: str = None, cols: int = 0, rows: int = 0
    ):
        cols = cols or self._cols
        rows = rows or self._rows

        if self.level_root is None:
            name = f"{self.config.prefix}{name}"
            parent = self.config.setup_root()
        else:
            name = f"{self.level_root_name}-{name}"
            parent = self.level_root

        target_group = TilesetTargetGroup(
            self.image, name, parent, cols, rows, x, y, True
        )
        self.colors.set_temp_parent(target_group.group)
        self.outlines.set_temp_parent(target_group.group)
        return target_group

    def setup(self, handler: Callable[[Builder], None]):
        handler(self.outlines)
        if self.is_color_target:
            handler(self.colors)

    def build(self, target: TilesetTargetGroup, fn: BuildFnType, fill: bool = False):
        if self.is_color_target:
            fn(target, self.colors)
            # FIXME: Also enable the lX group of outlines
        else:
            if fill:
                fn(target, self.colors)
            fn(target, self.outlines)

    def build2(
        self,
        target: TilesetTargetGroup,
        fn: BuildFnType,
        fill: bool = False,
        move: bool = True,
    ):
        self.build(target, fn, fill)
        layer = target.finalize()
        if move:
            self.next_target_position()
        return layer

    def build3(self, name: str, fn: BuildFnType, fill: bool = False, move: bool = True):
        target = self.create_target(name)
        return self.build2(target, fn, fill, move)

    def quick_build(
        self, name: str, fn: QuickBuildFnType, fill: bool = False, move: bool = True
    ):
        target = self.create_target(name)
        if self.is_color_target:
            fn(target, self.colors)
            # FIXME: Also enable the lX group of outlines
        else:
            if fill:
                fn(target, self.colors)
            fn(target, self.outlines)

        layer = target.finalize()
        if move:
            self.next_target_position()
        return layer

    def cleanup(self):
        self.outlines.cleanup()
        self.colors.cleanup()

    def get_grid_and_factor(self, factor: int = 3):
        return self.grid, self.grid // factor

    def range_cols(self, start: int = 1):
        return self.config.range_cols(start)

    def range_rows(self, start: int = 1):
        return self.config.range_rows(start)
