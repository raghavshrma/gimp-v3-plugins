import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp, Gegl

from tilegen.core import utils
from tilegen.core.tileset_collection import TilesetSource, TilesetTargetGroup
from tilegen.core.generator_config import GeneratorConfig
from collections.abc import Callable

from typing import TypeVar, Generic


class BaseSourceSet:
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

    def create_target_set(self):
        return TargetSet(self)

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
        layer = self._find_or_create_empty_layer()
        self.src_empty = self._init_source(layer)

    def _find_or_create_empty_layer(self) -> Gimp.Layer:
        image = self.image
        layer = image.get_layer_by_name("empty")
        if layer is None:
            layer = Gimp.Layer.new(image, "empty", 5 * self.grid, 5 * self.grid, Gimp.ImageType.RGBA_IMAGE, 100,
                                   Gimp.LayerMode.NORMAL)
            image.insert_layer(layer, None, 0)
            image.lower_item_to_bottom(layer)
            Gimp.context_set_background(Gegl.Color.new("white"))
            layer.fill(Gimp.FillType.BACKGROUND)

        return layer

    def empty_block(self, cols: int = 1, rows: int = 1):
        if not self.is_empty_allowed:
            return None
        return self.src_empty.copy_block2(1, 1, cols, rows)

    # endregion


T = TypeVar('T', bound=BaseSourceSet)


class TargetSet(Generic[T]):
    _BuildFnType = Callable[[TilesetTargetGroup, T], None]

    def __init__(self, source: T):
        self.config = source.config
        self.image = self.config.image
        self.is_quick = self.config.is_quick
        self.source = source

        self.grid = self.config.grid

        self.level_root: None | Gimp.GroupLayer = None
        self.level_root_name: None | str = None

        self._orientation_h = True
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
        self.source.set_temp_parent(target_group.group)
        return target_group

    def setup(self, handler: Callable[[T], None]):
        handler(self.source)
        # FIXME: handle the setup for all other sources too

    def build(self, target: TilesetTargetGroup, fn: _BuildFnType, fill: bool = False):
        fn(target, self.source)
        # FIXME: fill handling to be done by creating a dummy source from the given one
        # and using it as well (before the fn call) to fill the target if `fill` is True

    def build2(self, target: TilesetTargetGroup, fn: _BuildFnType, fill: bool = False, move: bool = True):
        self.build(target, fn, fill)
        layer = target.finalize()
        if move:
            self.next_target_position()
        return layer

    def build3(self, name: str, fn: _BuildFnType, fill: bool = False, move: bool = True):
        target = self.create_target(name)
        return self.build2(target, fn, fill, move)

    def quick_build(self, name: str, fn: _BuildFnType, fill: bool = False, move: bool = True):
        target = self.create_target(name)
        self.build(target, fn, fill)
        layer = target.finalize()
        if move:
            self.next_target_position()
        return layer

    def cleanup(self):
        self.source.cleanup()
        # FIXME: cleanup the dummy sources if any were created

    def get_grid_and_factor(self, factor: int = 3):
        return self.grid, self.grid // factor

    def range_cols(self, start: int = 1):
        # FIXME: this is a property of SourceSet, not GeneralConfig
        return self.config.range_cols(start)

    def range_rows(self, start: int = 1):
        # FIXME: this is a property of SourceSet, not GeneralConfig
        return self.config.range_rows(start)
