import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp, Gegl
import utils

def handle(image: Gimp.Image, drawable: Gimp.Layer, config: Gimp.ProcedureConfig):
    drawable.set_visible(True)
    handler = L0Handler(image, drawable, config)
    handler.process()
    drawable.set_visible(False)

class L0Handler:
    def __init__(self, image: Gimp.Image, drawable: Gimp.Layer, config: Gimp.ProcedureConfig):
        self.image = image
        self.drawable = drawable
        self.config = config

        grid = int(image.grid_get_spacing()[1])
        wid, hei = drawable.get_width(), drawable.get_height()

        rows = int(hei / grid)
        cols = int(wid / grid)
        self.dimensions = grid, wid, hei, rows, cols
        self.group = utils.create_main_group(image, drawable)

    def process(self):
        self.drawable.set_offsets(0, 0)
        self._horizontal_layers()
        self._vertical_layers()

    def _horizontal_layers(self):
        grid, wid, hei, rows, cols = self.dimensions
        layers: list[Gimp.Layer] = []

        off_y_top = 0
        off_y_btm = grid - hei

        for i in reversed(range(1, cols - 1)):
            off_x = -i * grid
            top = self._copy_layer()
            top.resize(grid, grid * 2, off_x, off_y_top)

            btm = self._copy_layer()
            btm.resize(grid, grid, off_x, off_y_btm)

            _, ox, oy = top.get_offsets()
            btm.set_offsets(ox, oy + grid * 2)

            layer = self.image.merge_down(btm, Gimp.MergeType.EXPAND_AS_NECESSARY)
            layer.set_name(f"l0-h-{i}")
            layers.append(layer)

        # Pick primary and offset horizontally 50%
        self._offset_primary(layers[-1], grid // 2, 0)
        #
        for layer in layers:
            layer.resize(grid * 3, grid * 3, grid, 0)

    def _vertical_layers(self):
        grid, wid, hei, rows, cols = self.dimensions
        layers: list[Gimp.Layer] = []

        for i in reversed(range(2, rows - 1)):
            off_y = -i * grid
            # Left
            l1 = self._copy_layer()
            l1.resize(grid, grid, 0, off_y)

            # Right
            l2 = self._copy_layer()
            l2.resize(grid, grid, grid - wid, off_y)

            _, ox, oy = l1.get_offsets()
            l2.set_offsets(ox + grid * 2, oy)

            layer = self.image.merge_down(l2, Gimp.MergeType.EXPAND_AS_NECESSARY)
            layer.set_name(f"l0-v-{i}")
            layer.set_offsets(ox + grid, oy + grid * 3)
            layers.append(layer)

        # Pick primary and offset vertically 50%
        self._offset_primary(layers[-1], 0, grid // 2)

        for layer in layers:
            layer.resize(grid * 3, grid * 3, 0, grid)

    def _create_group(self, name: str):
        group = Gimp.GroupLayer.new(self.image, name)
        self.image.insert_layer(group, self.drawable.get_parent(), -1)
        return group

    def _copy_layer(self) -> Gimp.Layer:
        copy = self.drawable.copy()
        self.image.insert_layer(copy, self.group, 0)
        # copy.set_name(name)
        return copy

    @staticmethod
    def _offset_primary(layer: Gimp.Layer, off_x: int, off_y: int):
        name = layer.get_name()
        layer.set_name(name + "-primary")
        layer.offset(True, Gimp.OffsetType.WRAP_AROUND, Gegl.Color.new("0"), off_x, off_y)
