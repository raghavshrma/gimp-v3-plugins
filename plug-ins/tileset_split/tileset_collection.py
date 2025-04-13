import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp
import utils

class Area:
    def __init__(self, x: int, y: int, w: int, h: int):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def crop(self, layer: Gimp.Layer):
        wid = layer.get_width()
        hei = layer.get_height()

        layer.resize(self.w, self.h, -self.x, -self.y)
        layer.resize(wid, hei, self.x, self.y)

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

    def validate_index(self, index: int):
        _validate_index(index, self.cols, self.rows)

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


class TilesetSource(TilesetBase):
    """
    Class to handle tileset blocks.
    """

    def __init__(self, image: Gimp.Image, layer: Gimp.Layer | str, parent: Gimp.GroupLayer | None = None):
        g = utils.get_grid_size(image)
        if type(layer) == str:
            layer = utils.find_layer(image, layer)

        super().__init__(image, layer.get_width() // g, layer.get_height() // g)
        self.layer = layer
        self.default_parent = parent or layer.get_parent()

    def copy(self, index: int, name: str = None, parent: Gimp.GroupLayer | None = None) -> Gimp.Layer:
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

    def copy_area(self, index: int, x: int, y: int, w: int, h: int) -> Gimp.Layer:
        copy = self.copy(index)
        copy.resize(w, h, -x, -y)
        copy.resize(self.grid, self.grid, x, y)
        return copy

    def copy_area2(self, index: int, area: Area) -> Gimp.Layer:
        copy = self.copy(index)
        area.crop(copy)
        return copy

    def copy_block(self, index: int, cols: int, rows: int):
        pass


class TilesetTarget(TilesetBase):
    """
    Class to handle tileset blocks.
    """

    def __init__(self, image: Gimp.Image, name: str, parent: Gimp.GroupLayer | None, cols: int, rows: int, x: int,
                 y: int, allow_replacement: bool = False):
        super().__init__(image, cols, rows)
        self.off_x = x
        self.off_y = y

        layer = image.get_layer_by_name(name)
        if layer is not None:
            if not allow_replacement:
                raise ValueError(f"Layer '{name}' already exists. Use allow_replacement=True to replace it.")

            image.remove_layer(layer)

        layer = Gimp.Layer.new(image, name, self.wid, self.hei, Gimp.ImageType.RGBA_IMAGE, 1.0, Gimp.LayerMode.NORMAL)
        image.insert_layer(layer, parent, 0)
        layer.set_offsets(x, y)
        self.layer = layer
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
        """
        Add a tile to the target layer.
        :param layer: Layer to add.
        :param index: Index of the tile to add. ranges from 1 to total_tiles
        """
        self.move_to(layer, index)
        self.layer = utils.merge_down(self.image, layer)
        return self.layer

    def add_from(self, source: TilesetSource, source_index: int, target_index: int):
        # Gimp.active
        layer = source.copy(source_index, self.default_parent)
        self.add_at(layer, target_index)



def _validate_index(index: int, cols: int, rows: int):
    total_tiles = rows * cols
    if index < 0 or index >= total_tiles:
        raise ValueError(f"Index {index} is out of range for this tileset. {total_tiles} tiles available."
                         + f" - {rows} rows x {cols} cols")


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
