import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

import utils
from tileset_collection import TilesetSource, TilesetTargetGroup

class Builder:
    def __init__(self, image: Gimp.Image, sample: Gimp.Layer, parent: Gimp.GroupLayer):
        self.image = image
        self.sample = sample
        self.parent = parent
        self._source_list: list[TilesetSource] = []
        self._hidden_list: list[Gimp.Item] = []

        self.src_sample = self._init_source(sample)
        self.src_a: None | TilesetSource = None
        self.src_b: None | TilesetSource = None
        self.src_c: None | TilesetSource = None
        self.src_d1: None | TilesetSource = None
        self.src_d2: None | TilesetSource = None
        self.src_plus_h: None | TilesetSource = None
        self.src_plus_v: None | TilesetSource = None
        self.src_single_h: None | TilesetSource = None
        self.src_single_v: None | TilesetSource = None
        self.src_inner_corners: None | TilesetSource = None
        self.src_outer_corners: None | TilesetSource = None
        self.src_block_connectors: None | TilesetSource = None
        self.src_vars_plus_h: list[TilesetSource] = []
        self.src_vars_plus_v: list[TilesetSource] = []
        self.src_vars_singles_h: list[TilesetSource] = []
        self.src_vars_singles_v: list[TilesetSource] = []

        self.grid = utils.get_grid_size(image)

    def _init_source(self, layer: str | Gimp.Layer) -> TilesetSource:
        source = TilesetSource(self.image, layer, self.parent)
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

    def set_temp_parent(self, parent: Gimp.GroupLayer):
        self._set_all_parent(parent)

    def unset_temp_parent(self):
        self._set_all_parent(self.parent)

    def _set_all_parent(self, parent: Gimp.GroupLayer):
        for source in self._source_list:
            source.default_parent = parent

    def cleanup(self):
        for layer in self._hidden_list:
            layer.set_visible(False)

    def get_target_group(self, name: str, x: int, y: int, cols: int = 5, rows: int = 5, parent: Gimp.GroupLayer | None = None) -> TilesetTargetGroup:
        parent = parent or self.parent
        target_group = TilesetTargetGroup(self.image, name, parent, cols, rows, x, y, True)
        self.set_temp_parent(target_group.group)
        return target_group

    # region Center Tiles

    def center_dark(self):
        return self.src_sample.copy_index(21)

    def center_light(self):
        return self.src_sample.copy_index(21)

    def deep_top(self):
        return self.src_sample.copy(3, 3)

    def deep_bottom(self):
        return self.src_sample.copy(3, 5)

    def deep_left(self):
        return self.src_sample.copy(2, 4)

    def deep_right(self):
        return self.src_sample.copy(5, 4)

    def deep_corner_tl(self):
        return self.src_sample.copy(2, 3)

    def deep_corner_tr(self):
        return self.src_sample.copy(5, 3)

    def deep_corner_bl(self):
        return self.src_sample.copy(2, 5)

    def deep_corner_br(self):
        return self.src_sample.copy(5, 5)

    # endregion

    #region Block Plus

    def setup_block_edges(self):
        self.src_plus_h = self._init_source(utils.get_plus_layer(self.image, "h", 1))
        self.src_plus_v = self._init_source(utils.get_plus_layer(self.image, "v", 1))

    def edge_top_full(self) -> Gimp.Layer:
        return self.src_plus_h.copy_block(2, 1, 2)

    def edge_top(self) -> Gimp.Layer:
        return self.src_plus_h.copy_index(5)

    def edge_top_extra(self) -> Gimp.Layer:
        return self.src_plus_h.copy_index(2)

    def edge_bottom(self) -> Gimp.Layer:
        return self.src_plus_h.copy_index(8)

    def edge_left(self) -> Gimp.Layer:
        return self.src_plus_v.copy_index(4)

    def edge_right(self) -> Gimp.Layer:
        return self.src_plus_v.copy_index(6)

    #endregion

    #region Variations

    def setup_variations(self):
        for i in range(1, 5):
            plus_h = utils.get_plus_layer(self.image, "h", i)
            self.src_vars_plus_h.append(self._init_source(plus_h))
            single_h = utils.get_singles_layer(self.image, "h", i)
            self.src_vars_singles_h.append(self._init_source(single_h))

        for i in range(1, 4):
            plus_v = utils.get_plus_layer(self.image, "v", i)
            self.src_vars_plus_v.append(self._init_source(plus_v))
            single_v = utils.get_singles_layer(self.image, "v", i)
            self.src_vars_singles_v.append(self._init_source(single_v))

    def var_top_full(self, index: int):
        return self.src_vars_plus_h[index - 1].copy_block2(2, 1, 1, 2)

    def var_top(self, index: int):
        return self.src_vars_plus_h[index - 1].copy(2, 2)

    def var_bottom(self, index: int):
        return self.src_vars_plus_h[index - 1].copy(2, 3)

    def var_left(self, index: int):
        return self.src_vars_plus_v[index - 1].copy(1, 2)

    def var_right(self, index: int):
        return self.src_vars_plus_v[index - 1].copy(3, 2)

    def var_single_h_full(self, index: int):
        return self.src_vars_singles_h[index - 1].copy_block2(2, 1, 1, 2)

    def var_single_h(self, index: int):
        return self.src_vars_singles_h[index - 1].copy(2, 2)

    def var_single_v(self, index: int):
        return self.src_vars_singles_v[index - 1].copy(2, 2)

    #endregion

    #region Block Singles

    def setup_block_singles(self):
        self.src_single_h = self._init_source(utils.get_singles_layer(self.image, "h", 1))
        self.src_single_v = self._init_source(utils.get_singles_layer(self.image, "v", 1))

    def single_h_full(self) -> Gimp.Layer:
        return self.src_single_h.copy_block(2, 1, 2)

    def single_h(self) -> Gimp.Layer:
        return self.src_single_h.copy_index(5)

    def single_v(self) -> Gimp.Layer:
        return self.src_single_v.copy_index(5)

    #endregion

    #region Block Corners

    def setup_block_corners(self):
        self.src_inner_corners = self._init_source("l2-inner-corners")
        self.src_outer_corners = self._init_source("l2-outer-corners")

    def inner_corner_tl(self):
        return self.src_inner_corners.copy(2, 3)

    def inner_corner_tr(self):
        return self.src_inner_corners.copy(1, 3)

    def inner_corner_bl(self):
        return self.src_inner_corners.copy(2, 1)

    def inner_corner_br(self):
        return self.src_inner_corners.copy(1, 1)

    def inner_corner_tl_extra(self):
        return self.src_inner_corners.copy(2, 2)

    def inner_corner_tr_extra(self):
        return self.src_inner_corners.copy(1, 2)

    def outer_corner_tl(self):
        return self.src_outer_corners.copy(1, 2)

    def outer_corner_tr(self):
        return self.src_outer_corners.copy(6, 2)

    def outer_corner_bl(self):
        return self.src_outer_corners.copy(1, 3)

    def outer_corner_br(self):
        return self.src_outer_corners.copy(6, 3)

    def outer_corner_tl_full(self):
        return self.src_outer_corners.copy_block2(1, 1, 1, 2)

    def outer_corner_tr_full(self):
        return self.src_outer_corners.copy_block2(6, 1, 1, 2)

    def outer_corner_tl_extra(self):
        return self.src_outer_corners.copy(1, 1)

    def outer_corner_tr_extra(self):
        return self.src_outer_corners.copy(6, 1)

    #endregion

    # region Block Connectors Base
    def setup_block_connectors_base(self):
        self.src_a = self._init_source("l5-series-a")
        self.src_b = self._init_source("l5-series-b")
        self.src_c = self._init_source("l5-series-c")
        self.src_d1 = self._init_source("l5-series-d1")
        self.src_d2 = self._init_source("l5-series-d2")

    def a(self, index: int) -> Gimp.Layer:
        return self.src_a.copy_index(index)

    def b(self, index: int) -> Gimp.Layer:
        return self.src_b.copy_index(index)

    def c(self, index: int) -> Gimp.Layer:
        return self.src_c.copy_index(index)

    def d(self, index: int) -> Gimp.Layer:
        if index <= 2:
            return self.src_d1.copy_index(index)
        elif index <= 4:
            return self.src_d2.copy_index(index - 2)
        elif index <= 6:
            return self.src_d1.copy_index(index - 2)
        else:
            return self.src_d2.copy_index(index - 4)

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

    #region Block Connector

    def setup_block_connectors(self):
        self.src_block_connectors = self._init_source("l5-block-connectors")

    def block_connector_all(self, block_type: int):
        block_type -= 1
        col = 2 * (block_type % 2) + 1
        row = 2 * (block_type // 2) + 1

        return self.src_block_connectors.copy_block2(col, row, 2, 2)

    def block_connector(self, block_type: int, index: int) -> Gimp.Layer:
        block_type -= 1
        index -= 1
        col = 2 * (block_type % 2) + (index % 2) + 1
        row = 2 * (block_type // 2) + (index // 2) + 1

        return self.src_block_connectors.copy(col, row)

    def single_v_top(self):
        return self.src_block_connectors.copy(4, 7)

    def single_v_top_full(self):
        return self.src_block_connectors.copy_block2(4, 6, 1, 2)

    def single_v_top_extra(self):
        return self.src_block_connectors.copy(4, 6)

    def single_v_bottom(self):
        return self.src_block_connectors.copy(4, 8)

    def single_h_left(self):
        return self.src_block_connectors.copy(3, 7)

    def single_h_right(self):
        return self.src_block_connectors.copy(3, 8)

    def single_corner_tl(self):
        return self.src_block_connectors.copy(1, 7)

    def single_corner_tr(self):
        return self.src_block_connectors.copy(2, 7)

    def single_corner_bl(self):
        return self.src_block_connectors.copy(1, 8)

    def single_corner_br(self):
        return self.src_block_connectors.copy(2, 8)

    def block_connect_5_up(self):
        return self.block_connector(5, 4)

    def block_connect_5_down(self):
        return self.block_connector(5, 3)

    def block_connect_5_left(self):
        return self.block_connector(5, 1)

    def block_connect_5_right(self):
        return self.block_connector(5, 2)

    def block_connect_3_up(self):
        return self.block_connector(3, 3)

    def block_connect_3_down(self):
        return self.block_connector(3, 2)

    def block_connect_3_left(self):
        return self.block_connector(3, 4)

    def block_connect_3_right(self):
        return self.block_connector(3, 1)

    #endregion
