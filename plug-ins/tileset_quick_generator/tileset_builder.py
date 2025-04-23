import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

import utils
from tileset_collection import TilesetSource, TilesetTargetGroup
from generator_config import GeneratorConfig
from collections.abc import Callable


class Builder:
    def __init__(self, config: GeneratorConfig, is_color_source: bool):
        self.config = config
        self.image = config.image

        self.target_root: None | Gimp.GroupLayer = None
        self._source_list: list[TilesetSource] = []
        self._hidden_list: list[Gimp.Item] = []
        self.is_color_source = is_color_source
        self.prefix = is_color_source and "c-" or "o-"
        root_group_name = is_color_source and "colors" or "outlines"
        self.root = config.find_group(root_group_name)

        self.src_sample: None | TilesetSource = None
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
        self.src_edges_h: list[TilesetSource] = []
        self.src_edges_v: list[TilesetSource] = []
        self.src_singles_h: list[TilesetSource] = []
        self.src_singles_v: list[TilesetSource] = []

        self.grid = utils.get_grid_size(config.image)
        self.src_custom: dict[str, TilesetSource] = {}

    def _init_source(self, layer: str | Gimp.Layer) -> TilesetSource:
        layer = type(layer) == str and f"{self.prefix}{layer}" or layer
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

    def setup_level_group(self, level: int):
        name = f"{self.prefix}l{level}"
        group = utils.ref

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

    @staticmethod
    def copy(src: TilesetSource, col: int, row: int) -> Gimp.Layer:
        if src is None:
            return None

        return src.copy(col, row)

    @staticmethod
    def copy_block(
        src: TilesetSource, col: int, row: int, cols: int, rows: int
    ) -> Gimp.Layer:
        if src is None:
            return None

        return src.copy_block2(col, row, cols, rows)

    @staticmethod
    def copy_full(src: TilesetSource, col: int, row: int) -> Gimp.Layer:
        if src is None:
            return None

        return src.copy_block2(col, row, 1, 2)

    # region Center Tiles
    def setup_sample(self):
        self.src_sample = self._init_source("sample")

    def sample_edge_top_full(self, index: int = 1):
        return self.copy_full(self.src_sample, 2 + index, 2)

    def sample_edge_top_ext(self, index: int = 1):
        return self.copy(self.src_sample, 2 + index, 2)

    def sample_edge_top(self, index: int = 1):
        return self.copy(self.src_sample, 2 + index, 3)

    def sample_edge_bottom(self, index: int = 1):
        return self.copy(self.src_sample, 2 + index, 9)

    def sample_edge_left(self, index: int = 1):
        return self.copy(self.src_sample, 2, 3 + index)

    def sample_edge_right(self, index: int = 1):
        return self.copy(self.src_sample, 9, 3 + index)

    def deep_dark(self):
        return self.copy(self.src_sample, 4, 5)

    def deep_light(self):
        return self.copy(self.src_sample, 4, 6)

    def deep_edge_top(self):
        return self.copy(self.src_sample, 4, 4)

    def deep_edge_bottom(self):
        return self.copy(self.src_sample, 4, 8)

    def deep_edge_left(self):
        return self.copy(self.src_sample, 3, 5)

    def deep_edge_right(self):
        return self.copy(self.src_sample, 8, 5)

    def deep_corner_tl(self):
        return self.copy(self.src_sample, 3, 4)

    def deep_corner_tr(self):
        return self.copy(self.src_sample, 8, 4)

    def deep_corner_bl(self):
        return self.copy(self.src_sample, 3, 8)

    def deep_corner_br(self):
        return self.copy(self.src_sample, 8, 8)

    # endregion

    # region Block Plus

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

    # endregion

    # region Variations

    def setup_variations(self):
        for i in range(1, 5):
            plus_h = utils.get_plus_layer(self.image, "h", i)
            self.src_edges_h.append(self._init_source(plus_h))
            single_h = utils.get_singles_layer(self.image, "h", i)
            self.src_singles_h.append(self._init_source(single_h))

        for i in range(1, 4):
            plus_v = utils.get_plus_layer(self.image, "v", i)
            self.src_edges_v.append(self._init_source(plus_v))
            single_v = utils.get_singles_layer(self.image, "v", i)
            self.src_singles_v.append(self._init_source(single_v))

    def var_top_full(self, index: int):
        return self.src_edges_h[index - 1].copy_block2(2, 1, 1, 2)

    def var_top(self, index: int):
        return self.src_edges_h[index - 1].copy(2, 2)

    def var_bottom(self, index: int):
        return self.src_edges_h[index - 1].copy(2, 3)

    def var_left(self, index: int):
        return self.src_edges_v[index - 1].copy(1, 2)

    def var_right(self, index: int):
        return self.src_edges_v[index - 1].copy(3, 2)

    def var_single_h_full(self, index: int):
        return self.src_singles_h[index - 1].copy_block2(2, 1, 1, 2)

    def var_single_h(self, index: int):
        return self.src_singles_h[index - 1].copy(2, 2)

    def var_single_v(self, index: int):
        return self.src_singles_v[index - 1].copy(2, 2)

    # endregion

    # region Block Singles

    def setup_block_singles(self):
        self.src_single_h = self._init_source(
            utils.get_singles_layer(self.image, "h", 1)
        )
        self.src_single_v = self._init_source(
            utils.get_singles_layer(self.image, "v", 1)
        )

    def single_h_full(self) -> Gimp.Layer:
        return self.src_single_h.copy_block(2, 1, 2)

    def single_h(self) -> Gimp.Layer:
        return self.src_single_h.copy_index(5)

    def single_v(self) -> Gimp.Layer:
        return self.src_single_v.copy_index(5)

    # endregion

    # region Block Corners

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

    # endregion

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

    # region Block Connector

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

    # endregion


class BuilderSet:
    def __init__(self, config: GeneratorConfig):
        self.config = config
        self.image = config.image

        self.colors = Builder(config, True)
        self.outlines = Builder(config, False)
        self.grid = config.grid
        self.is_color_target = config.is_color_target
        self.set_target_spacing(0, 0, 6, 6)
        self._orientation_h = True

    def initiate_level(self, level: int, dependencies: list[int] = []):
        self.level_root = self.config.initiate_level(level, dependencies)
        self.level_root_name = self.level_root.get_name()
        return self.level_root

    def set_target_spacing(self, x: int, y: int, dx: int, dy: int, orient_h: bool = True):
        self._x = x * self.grid
        self._y = y * self.grid
        self._cx = self._x
        self._cy = self._y
        self._dx = dx * self.grid
        self._dy = dy * self.grid

        self._orientation_h = orient_h
        if orient_h:
            max_blocks = (self.image.get_width() - self._x) // self._dx
            self._max_z = self._x + (max_blocks * self._dx)
        else:
            max_blocks = (self.image.get_height() - self._y) // self._dy
            self._max_z = self._y + (max_blocks * self._dy)

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

    def create_target(self, type: str = None, cols: int = 5, rows: int = 5):
        target = self.create_target_at(self._cx, self._cy, type, cols, rows)
        self.next_target_position()
        return target

    def create_target_at(
        self, x: int, y: int, type: str = None, cols: int = 5, rows: int = 5
    ):
        parent = self.level_root
        suffix = type and f"-{type}" or ""
        name = f"{self.level_root_name}{suffix}"
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

    def cleanup(self):
        self.outlines.cleanup()
        self.colors.cleanup()
