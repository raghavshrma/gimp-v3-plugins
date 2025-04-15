import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

import utils
from tileset_collection import TilesetSource, TilesetTargetGroup

class Builder:
    def __init__(self, image: Gimp.Image, sample: Gimp.Layer):
        self.image = image
        self.sample = sample
        self.parent = utils.get_ref_group(image, 5)
        self._source_list: list[TilesetSource] = []
        self._hidden_list: list[Gimp.Layer] = []

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

        self.grid = utils.get_grid_size(image)

    def _init_source(self, layer: str | Gimp.Layer) -> TilesetSource:
        source = TilesetSource(self.image, layer, self.parent)
        self._source_list.append(source)
        if not source.layer.get_visible():
            source.layer.set_visible(True)
            self._hidden_list.append(source.layer)

        return source

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

    def target_group_raw(self, idx: int, x: int, y: int, cols: int = 5, rows: int = 5) -> TilesetTargetGroup:
        name = f"l5-type-{idx}-raw"
        return self.get_target_group(name, x, y, cols, rows)

    def target_group_ref(self, idx: int, x: int, y: int, cols: int = 5, rows: int = 5) -> TilesetTargetGroup:
        name = f"l5-type-{idx}-ref"
        return self.get_target_group(name, x, y, cols, rows)

    def get_target_group(self, name: str, x: int, y: int, cols: int = 5, rows: int = 5) -> TilesetTargetGroup:
        target_group = TilesetTargetGroup(self.image, name, self.parent, cols, rows, x, y, True)
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

    def setup_blocks_plus(self):
        self.src_plus_h = self._init_source(utils.get_plus_layer(self.image, "h", 1))
        self.src_plus_v = self._init_source(utils.get_plus_layer(self.image, "v", 1))

    def top_full(self) -> Gimp.Layer:
        return self.src_plus_h.copy_block(2, 1, 2)

    def top(self) -> Gimp.Layer:
        return self.src_plus_h.copy_index(5)

    def top_extra(self) -> Gimp.Layer:
        return self.src_plus_h.copy_index(2)

    def bottom(self) -> Gimp.Layer:
        return self.src_plus_h.copy_index(8)

    def left(self) -> Gimp.Layer:
        return self.src_plus_v.copy_index(4)

    def right(self) -> Gimp.Layer:
        return self.src_plus_v.copy_index(6)

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

    # endregion

    #region Block Connector

    def setup_block_connectors(self):
        self.src_block_connectors = self._init_source("l5-block-connectors")

    def block_connector(self, block_type: int, index: int) -> Gimp.Layer:
        block_type -= 1
        index -= 1
        col = 2 * (block_type % 2) + (index % 2) + 1
        row = 2 * (block_type // 2) + (index // 2) + 1

        return self.src_block_connectors.copy(col, row)