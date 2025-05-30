import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp, Gegl
from tilegen.core import utils

class Area:
    def __init__(self, x: int, y: int, w: int, h: int):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def crop(self, layer: Gimp.Layer) -> Gimp.Layer:
        wid = layer.get_width()
        hei = layer.get_height()

        layer.resize(self.w, self.h, -self.x, -self.y)
        layer.resize(wid, hei, self.x, self.y)
        return layer

    @staticmethod
    def left(g: int, f: int):
        return Area(0, 0, g - f, g)

    @staticmethod
    def right(g: int, f: int):
        return Area(f, 0, g - f, g)

    @staticmethod
    def top(g: int, f: int):
        return Area(0, 0, g, g - f)

    @staticmethod
    def bottom(g: int, f: int):
        return Area(0, f, g, g - f)

    @staticmethod
    def top_left(g: int, f: int):
        s = g - f
        return Area(0, 0, s, s)

    @staticmethod
    def top_right(g: int, f: int):
        s = g - f
        return Area(f, 0, s, s)

    @staticmethod
    def bottom_left(g: int, f: int):
        s = g - f
        return Area(0, f, s, s)

    @staticmethod
    def bottom_right(g: int, f: int):
        s = g - f
        return Area(f, f, s, s)


class AreaBuilder:
    def __init__(self, grid: int, factor: int = 3):
        self.grid = grid
        self.factor = grid // factor

    def left(self):
        return Area.left(self.grid, self.factor)

    def right(self):
        return Area.right(self.grid, self.factor)

    def top(self):
        return Area.top(self.grid, self.factor)

    def bottom(self):
        return Area.bottom(self.grid, self.factor)

    def top_left(self):
        return Area.top_left(self.grid, self.factor)

    def top_right(self):
        return Area.top_right(self.grid, self.factor)

    def bottom_left(self):
        return Area.bottom_left(self.grid, self.factor)

    def bottom_right(self):
        return Area.bottom_right(self.grid, self.factor)

    def t(self):
        return self.top()

    def b(self):
        return self.bottom()

    def l(self):
        return self.left()

    def r(self):
        return self.right()

    def tl(self):
        return self.top_left()

    def tr(self):
        return self.top_right()

    def bl(self):
        return self.bottom_left()

    def br(self):
        return self.bottom_right()

    def mid_seam_top(self):
        x = self.grid - self.factor
        y = 0
        w = self.factor * 2
        h = self.grid * 2

        return Area(x, y, w, h)

    def mid_seam_vertical(self):
        x = 0
        y = self.grid - self.factor
        w = self.grid
        h = self.factor * 2

        return Area(x, y, w, h)

    def mid_seam_horizontal(self):
        x = self.grid - self.factor
        y = 0
        w = self.factor * 2
        h = self.grid

        return Area(x, y, w, h)


class TilesetBase:
    def __init__(self, image: Gimp.Image, cols: int, rows: int):
        self.image = image
        self.grid = utils.get_grid_size(image)
        self.cols = cols
        self.rows = rows
        self.wid = cols * self.grid
        self.hei = rows * self.grid
        self.total_tiles = self.rows * self.cols
        self.off_x = 0
        self.off_y = 0
        self.tileset_name = "this tileset"

    def validate_index(self, index: int):
        total_tiles = self.rows * self.cols
        if index < 0 or index >= total_tiles:
            raise ValueError(
                f"Index {index} is out of range for {self.tileset_name}. {total_tiles} tiles available."
                + f" - {self.rows} rows x {self.cols} cols"
            )

    def get_local_coord(self, index: int) -> tuple[int, int]:
        """
        Get the coordinates of a tile in the tileset.
        :param index: Index of the tile.
        :return: Tuple of (x, y) coordinates.
        """
        x, y = _get_coord(index, self.cols, self.grid)
        return x, y

    def get_image_coord(self, index: int) -> tuple[int, int]:
        """
        Get the coordinates of a tile in the tileset.
        :param index: Index of the tile.
        :return: Tuple of (x, y) coordinates.
        """
        x, y = _get_coord(index, self.cols, self.grid)
        return x + self.off_x, y + self.off_y

    def get_index(self, col: int, row: int) -> int:
        return (row - 1) * self.cols + col


class TilesetSource(TilesetBase):
    """
    Class to handle tileset blocks.
    """

    def __init__(
            self,
            image: Gimp.Image,
            layer: Gimp.Layer | str,
            parent: Gimp.GroupLayer | None = None,
    ):
        g = utils.get_grid_size(image)
        if type(layer) == str:
            layer = utils.find_layer(image, layer)

        super().__init__(image, layer.get_width() // g, layer.get_height() // g)
        self.layer = layer
        self.tileset_name = layer.get_name()
        self.default_parent = parent or layer.get_parent()

    def copy_index(
            self, index: int, name: str = None, parent: Gimp.GroupLayer | None = None
    ) -> Gimp.Layer:
        """
        Copy a tile from the base layer to the main group.
        :param index: Index of the tile to copy. ranges from 1 to total_tiles
        :param name: Name of the copied tile. If None, uses the default name.
        :param parent: Parent group layer to insert the copied tile into. If None, uses the default parent.
        """
        index -= 1
        self.validate_index(index)
        x, y = self.get_local_coord(index)

        parent = parent or self.default_parent
        copy = utils.copy(self.image, self.layer, parent, self.grid, self.grid, -x, -y)
        if name:
            copy.set_name(name)

        return copy

    def copy(self, col: int, row: int) -> Gimp.Layer:
        index = self.get_index(col, row)
        return self.copy_index(index)

    def copy_block(self, index: int, cols: int, rows: int):
        index -= 1
        self.validate_index(index)
        x, y = self.get_local_coord(index)
        copy = utils.copy(
            self.image,
            self.layer,
            self.default_parent,
            self.grid * cols,
            self.grid * rows,
            -x,
            -y,
        )
        return copy

    def copy_block2(self, col: int, row: int, cols: int, rows: int):
        index = self.get_index(col, row)
        return self.copy_block(index, cols, rows)

    def copy_area(self, index: int, x: int, y: int, w: int, h: int) -> Gimp.Layer:
        copy = self.copy_index(index)
        copy.resize(w, h, -x, -y)
        copy.resize(self.grid, self.grid, x, y)
        return copy

    def copy_area2(self, index: int, area: Area) -> Gimp.Layer:
        copy = self.copy_index(index)
        area.crop(copy)
        return copy


class TilesetTarget(TilesetBase):
    """
    Class to handle tileset blocks.
    """

    def __init__(
            self,
            image: Gimp.Image,
            name: str,
            parent: Gimp.GroupLayer | None,
            cols: int,
            rows: int,
            x: int,
            y: int,
            allow_replacement: bool = False,
    ):
        super().__init__(image, cols, rows)
        self.off_x = x
        self.off_y = y

        layer = image.get_layer_by_name(name)
        if layer is not None:
            if not allow_replacement:
                raise ValueError(
                    f"Layer '{name}' already exists. Use allow_replacement=True to replace it."
                )

            image.remove_layer(layer)

        layer = Gimp.Layer.new(
            image,
            name,
            self.wid,
            self.hei,
            Gimp.ImageType.RGBA_IMAGE,
            1.0,
            Gimp.LayerMode.NORMAL,
        )
        image.insert_layer(layer, parent, 0)
        layer.set_offsets(x, y)
        self.layer = layer
        self.tileset_name = layer.get_name()
        self.default_parent = parent

    def move_to(self, layer: Gimp.Layer, index: int):
        """
        Move a tile to the target layer.
        :param layer: Layer to move.
        :param index: Index of the tile to move. ranges from 1 to total_tiles
        """
        index -= 1
        self.validate_index(index)
        x, y = self.get_image_coord(index)
        layer.set_offsets(x, y)

    def add_at(self, layer: Gimp.Layer, index: int) -> Gimp.Layer:
        return self.add(index, layer)

    def add(self, index: int, layer: Gimp.Layer):
        """
        Add a tile to the target layer.
        :param index: Index of the tile to add. ranges from 1 to total_tiles
        :param layer: Layer to add.
        """
        self.move_to(layer, index)
        self.layer = utils.merge_down(self.image, layer)
        return self.layer

    def add2(self, col: int, row: int, layer: Gimp.Layer):
        index = (row - 1) * self.cols + col
        return self.add(index, layer)

    def add_all(self, col: int, row: int, layers: list[Gimp.Layer]):
        index = (row - 1) * self.cols + col
        for layer in layers:
            self.add(index, layer)

        return self.layer

    def add_from(self, source: TilesetSource, source_index: int, target_index: int):
        # Gimp.active
        layer = source.copy_index(source_index, self.default_parent)
        self.add_at(layer, target_index)


class TilesetTargetGroup(TilesetBase):
    """
    Class to handle tileset blocks.
    """

    def __init__(
            self,
            image: Gimp.Image,
            name: str,
            parent: Gimp.GroupLayer | None,
            cols: int,
            rows: int,
            x: int,
            y: int,
            allow_replacement: bool = False,
    ):
        super().__init__(image, cols, rows)
        self.off_x = x
        self.off_y = y

        group = image.get_layer_by_name(name)
        if group is not None:
            if not allow_replacement:
                raise ValueError(
                    f"Layer '{name}' already exists. Use allow_replacement=True to replace it."
                )

            image.remove_layer(group)

        # layer = Gimp.Layer.new(image, name, self.wid, self.hei, Gimp.ImageType.RGBA_IMAGE, 1.0, Gimp.LayerMode.NORMAL)
        group = Gimp.GroupLayer.new(image, name)
        image.insert_layer(group, parent, 0)
        # group.set_offsets(x, y)
        self.group = group
        self.tileset_name = group.get_name()
        self.default_parent = group
        self.fill_layer: None | Gimp.Layer = None

    def move_to(self, layer: Gimp.Layer, index: int):
        """
        Move a tile to the target layer.
        :param layer: Layer to move.
        :param index: Index of the tile to move. ranges from 1 to total_tiles
        """
        if layer is None:
            return

        index -= 1
        self.validate_index(index)
        x, y = self.get_image_coord(index)
        layer.set_offsets(x, y)

    def add_at(self, layer: Gimp.Layer, index: int) -> Gimp.Layer:
        return self.addi(index, layer)

    def addi(self, index: int, layer: Gimp.Layer):
        """
        Add a tile to the target layer.
        :param index: Index of the tile to add. ranges from 1 to total_tiles
        :param layer: Layer to add.
        """
        self.move_to(layer, index)
        return self.group

    def add(self, x: int, y: int, layers: Gimp.Layer | list[Gimp.Layer]):
        index = (y - 1) * self.cols + x
        if isinstance(layers, list):
            for l in layers:
                self.addi(index, l)
        else:
            self.addi(index, layers)

        return self.group

    def add_all(self, col: int, row: int, layers: list[Gimp.Layer]):
        index = (row - 1) * self.cols + col
        for layer in layers:
            self.addi(index, layer)

        return self.group

    def add_from(self, source: TilesetSource, source_index: int, target_index: int):
        # Gimp.active
        layer = source.copy_index(source_index, None, self.group)
        self.add_at(layer, target_index)

    def new_fill_layer(self, name: str | None, col: int, row: int, cols: int, rows: int) -> Gimp.Layer:
        wid = cols * self.grid
        hei = rows * self.grid

        layer = Gimp.Layer.new(self.image, name, wid, hei, Gimp.ImageType.RGBA_IMAGE, 100, Gimp.LayerMode.NORMAL)
        self.image.insert_layer(layer, self.group, 0)
        self.add(col, row, layer)
        self.fill_layer = layer
        return layer

    def select_rect(self, col: int, row: int, cols: int, rows: int):
        x = self.off_x + (col - 1) * self.grid
        y = self.off_y + (row - 1) * self.grid
        wid = cols * self.grid
        hei = rows * self.grid
        self.image.select_rectangle(Gimp.ChannelOps.REPLACE, x, y, wid, hei)

    @staticmethod
    def set_fill_color(color_name: str):
        color = Gegl.Color.new(color_name)
        Gimp.context_set_foreground(color)

    def fill_rect(self, col: int, row: int, cols: int, rows: int):
        if self.fill_layer is None:
            raise ValueError("Fill layer is not set. Use new_fill_layer() to create one.")

        self.select_rect(col, row, cols, rows)
        self.fill_layer.edit_fill(Gimp.FillType.FOREGROUND)
        Gimp.Selection.none(self.image)

    def finalize(self) -> Gimp.Layer:
        result = self.group.merge()
        self.group = None

        _, x0, y0 = result.get_offsets()
        x1, y1 = self.off_x, self.off_y
        result.resize(self.wid, self.hei, x0 - x1, y0 - y1)
        return result


def _validate_index(index: int, cols: int, rows: int):
    total_tiles = rows * cols
    if index < 0 or index >= total_tiles:
        raise ValueError(
            f"Index {index} is out of range for this tileset. {total_tiles} tiles available."
            + f" - {rows} rows x {cols} cols"
        )


def _get_coord(index: int, cols: int, grid: int) -> tuple[int, int]:
    """
    Get the coordinates of a tile in the tileset.
    :param index: Index of the tile.
    :param cols: Number of columns in the tileset.
    :param grid: Size of each tile.
    :return: Tuple of (x, y) coordinates.
    """
    x = (index % cols) * grid
    y = (index // cols) * grid
    return x, y
