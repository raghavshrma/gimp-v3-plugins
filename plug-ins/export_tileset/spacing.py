import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp, Gegl
import utils
import math


class Spacing:
    def __init__(self, image: Gimp.Image, src_layer: Gimp.Layer, grid: int, spacing: int, fill_space: bool):
        self.image = image
        self.src_layer = src_layer
        self.grid = grid
        self.spacing = spacing
        self.fill_space = fill_space

        self.rows = math.ceil((image.get_height() / grid))
        self.cols = math.ceil((image.get_width() / grid))

        self._setup_image_size()
        self.img_wid = self.image.get_width()
        self.img_hei = self.image.get_height()

        self.fill_layer = self._create_fill_layer()

    def _setup_image_size(self):
        new_wid = utils.get_pot_size(self.cols * self.grid + (self.cols - 1) * self.spacing)
        new_hei = utils.get_pot_size(self.rows * self.grid + (self.rows - 1) * self.spacing)
        self.image.resize(new_wid, new_hei, 0, 0)

    def _create_fill_layer(self):
        fill_layer = Gimp.Layer.new(
            self.image,
            "fill_layer",
            self.img_wid,
            self.img_hei,
            Gimp.ImageType.RGBA_IMAGE,
            100,
            Gimp.LayerMode.NORMAL,
        )
        self.image.insert_layer(fill_layer, None, 0)
        return fill_layer

    def run(self):
        timer = utils.ProcessTimer()

        bg_layer = Gimp.Layer.new(self.image, "background", self.image.get_width(), self.image.get_height(),
                                  Gimp.ImageType.RGBA_IMAGE, 100, Gimp.LayerMode.NORMAL)
        self.image.insert_layer(bg_layer, None, 0)
        self.image.lower_item_to_bottom(bg_layer)
        bg_layer.fill(Gimp.FillType.BACKGROUND)

        self._add_spacing()
        self.image.remove_layer(bg_layer)

        timer.end("Prepared spaced tileset")
        self.src_layer.set_visible(False)

    def _add_spacing(self):
        rows, cols, grid, space = self.rows, self.cols, self.grid, self.spacing
        fill_repeat = space // 2

        for row in range(rows):
            y = row * grid
            group, row_layer = self._create_row_layer(row)

            for col in range(cols):
                x = col * grid

                nx = x + (col * space)
                ny = y + (row * space)

                # _copy_block(image, source_layer, x, y, final_layer, nx, ny, grid)
                block = self._copy_block(row_layer, group, col)
                block.set_offsets(nx, ny)

                if self.fill_space:
                    self._fill_space(group, block, nx, ny, fill_repeat)
                # if fill_space:
                #     _fill_space_pixels2(src_image, final_layer, nx, ny, grid, space)

            self.image.remove_layer(row_layer)
            # row_layer.set_visible(False)
            group.merge()

    def _create_row_layer(self, row: int):
        group = Gimp.GroupLayer.new(self.image, f"row-{row}")
        self.image.insert_layer(group, None, 0)

        row_layer = self.src_layer.copy()
        self.image.insert_layer(row_layer, group, 0)
        row_layer.resize(self.cols * self.grid, self.grid, 0, -row * self.grid)
        return group, row_layer

    def _copy_block(self, row_layer: Gimp.Layer, group: Gimp.GroupLayer, col: int):
        block = row_layer.copy()
        self.image.insert_layer(block, group, 0)
        block.resize(self.grid, self.grid, -col * self.grid, 0)
        return block

    def _fill_space(self, group: Gimp.GroupLayer, block: Gimp.Layer, x: int, y: int, repeat: int):
        g = self.grid
        s_rep = repeat - 1

        side = self._copy_block_side(group, block, g, 1, 0, 0)
        self._fill_side(group, side, x, y - 1, s_rep, 0, -1)

        side = self._copy_block_side(group, block, g, 1, 0, 1 - g)
        self._fill_side(group, side, x, y + g, s_rep, 0, 1)

        side = self._copy_block_side(group, block, 1, g, 0, 0)
        self._fill_side(group, side, x - 1, y, s_rep, -1, 0)

        side = self._copy_block_side(group, block, 1, g, 1 - g, 0)
        self._fill_side(group, side, x + g, y, s_rep, 1, 0)

        pixel = block.get_pixel(0, 0)
        self._fill_pixels(pixel, x - repeat, y - repeat, repeat)

        pixel = block.get_pixel(g - 1, 0)
        self._fill_pixels(pixel, x + g, y - repeat, repeat)

        pixel = block.get_pixel(0, g - 1)
        self._fill_pixels(pixel, x - repeat, y + g, repeat)

        pixel = block.get_pixel(g - 1, g - 1)
        self._fill_pixels(pixel, x + g, y + g, repeat)

    def _copy_block_side(self, group: Gimp.GroupLayer, block: Gimp.Layer, w: int, h: int, off_x: int, off_y: int):
        copy = block.copy()
        self.image.insert_layer(copy, group, 0)
        copy.resize(w, h, off_x, off_y)
        return copy

    def _fill_side(self, group: Gimp.GroupLayer, side: Gimp.Layer, x: int, y: int, rep: int, x_incr, y_incr: int):
        side.set_offsets(x, y)

        for _ in range(rep):
            copy = side.copy()
            self.image.insert_layer(copy, group, 0)
            x += x_incr
            y += y_incr
            copy.set_offsets(x, y)

    def _fill_pixels(self, pixel: Gegl.Color, x: int, y: int, rep: int):
        _, _, _, alpha = pixel.get_rgba()
        if alpha < .01:
            return

        layer = self.fill_layer

        for i in range(rep):
            for j in range(rep):
                a = x + i
                b = y + j
                if 0 <= a < self.img_wid and 0 <= b < self.img_hei:
                    layer.set_pixel(a, b, pixel)


def _copy_block3(
        image: Gimp.Image,
        source: Gimp.Layer,
        col: int,
        row: int,
        grid: int,
):
    copy = source.copy()
    image.insert_layer(copy, None, 0)
    copy.resize(grid, grid, -col * grid, -row * grid)
    return copy


def _fill_space_pixels(
        image: Gimp.Image, layer: Gimp.Layer, x: int, y: int, grid: int, spacing: int
):
    half = spacing >> 1

    _repeat_pixels_h(image, layer, x, y, grid, -half)
    _repeat_pixels_h(image, layer, x, y + grid - 1, grid, half)
    _repeat_pixels_v(image, layer, x, y, grid, -half)
    _repeat_pixels_v(image, layer, x + grid - 1, y, grid, half)


def _repeat_pixels_h(
        image: Gimp.Image, layer: Gimp.Layer, x: int, y: int, grid: int, dy: int
):
    end_y = max(0, min(y + dy, layer.get_height()))
    if end_y == y:
        return

    # Top line
    image.select_rectangle(Gimp.ChannelOps.REPLACE, x, y, grid, 1)
    buffer_name = Gimp.edit_named_copy([layer], "block-buffer")

    if buffer_name:
        range_y = range(end_y, y) if y > end_y else range(y + 1, end_y + 1)

        for ty in range_y:
            sel = Gimp.edit_named_paste(layer, buffer_name, False)
            sel.set_offsets(x, ty)
            Gimp.floating_sel_anchor(sel)

        Gimp.buffer_delete(buffer_name)


def _repeat_pixels_v(
        image: Gimp.Image, layer: Gimp.Layer, x: int, y: int, grid: int, dx: int
):
    end_x = max(0, min(x + dx, layer.get_height()))
    if end_x == x:
        return

    # Top line
    image.select_rectangle(Gimp.ChannelOps.REPLACE, x, y, 1, grid)
    buffer_name = Gimp.edit_named_copy([layer], "block-buffer")

    if buffer_name:
        range_x = range(end_x, x) if x > end_x else range(x + 1, end_x + 1)

        for tx in range_x:
            sel = Gimp.edit_named_paste(layer, buffer_name, False)
            sel.set_offsets(tx, y)
            Gimp.floating_sel_anchor(sel)

        Gimp.buffer_delete(buffer_name)


def _fill_space_pixels2(
        image: Gimp.Image, layer: Gimp.Layer, x: int, y: int, grid: int, spacing: int
):
    # wid, hei = layer.get_width(), layer.get_height()
    half = spacing >> 1

    _fill_pixels_h(layer, range(x, x + grid), y, -half)
    _fill_pixels_h(layer, range(x, x + grid), y + grid - 1, half)
    _fill_pixels_v(layer, range(y, y + grid), x, -half)
    _fill_pixels_v(layer, range(y, y + grid), x + grid - 1, half)
    # Corners:
    _fill_pixels_corner(layer, x, y, -half, -half)
    _fill_pixels_corner(layer, x, y + grid - 1, -half, half)
    _fill_pixels_corner(layer, x + grid - 1, y, half, -half)
    _fill_pixels_corner(layer, x + grid - 1, y + grid - 1, half, half)


def _fill_pixels_h(layer: Gimp.Layer, range_sx: range, sy: int, end_ty: int):
    end_ty += sy
    end_ty = max(0, min(end_ty, layer.get_height()))
    if end_ty == sy:
        return

    range_ty = range(end_ty, sy) if sy > end_ty else range(sy + 1, end_ty + 1)

    for x in range_sx:
        color = layer.get_pixel(x, sy)
        _, _, _, a = color.get_rgba()

        if a == 0:
            continue

        for ty in range_ty:
            layer.set_pixel(x, ty, color)


def _fill_pixels_v(layer: Gimp.Layer, range_sy: range, sx: int, end_tx: int):
    end_tx += sx
    end_tx = max(0, min(end_tx, layer.get_width()))
    if end_tx == sx:
        return

    range_tx = range(end_tx, sx) if sx > end_tx else range(sx + 1, end_tx + 1)

    for y in range_sy:
        color = layer.get_pixel(sx, y)
        _, _, _, a = color.get_rgba()

        if a == 0:
            continue

        for tx in range_tx:
            layer.set_pixel(tx, y, color)


def _fill_pixels_corner(layer: Gimp.Layer, x: int, y: int, dx: int, dy: int):
    end_x = max(0, min(x + dx, layer.get_width()))
    end_y = max(0, min(y + dy, layer.get_width()))

    range_x = range(end_x, x) if x > end_x else range(x + 1, end_x + 1)
    range_y = range(end_y, y) if y > end_y else range(y + 1, end_y + 1)

    color = layer.get_pixel(x, y)
    _, _, _, a = color.get_rgba()
    if a == 0:
        return

    for tx in range_x:
        for ty in range_y:
            layer.set_pixel(tx, ty, color)
