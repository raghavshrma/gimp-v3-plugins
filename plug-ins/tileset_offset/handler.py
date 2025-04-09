#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp
from gi.repository import Gegl
import gimp_error


def run_one(
    procedure: Gimp.Procedure,
    run_mode: Gimp.RunMode,
    image: Gimp.Image,
    drawable: Gimp.Layer,
    config: Gimp.ProcedureConfig,
    data,
):

    if drawable.get_name() == "draft":
        return gimp_error.calling(procedure, "Cannot perform this operation on draft layer")

    image.undo_group_start()

    tiler = Tiler(image, drawable, config)
    tiler.tile()

    image.undo_group_end()
    Gimp.displays_flush()
    return gimp_error.success(procedure)


class Tiler(object):
    def __init__(
        self, image: Gimp.Image, drawable: Gimp.Layer, config: Gimp.ProcedureConfig
    ):
        self.image = image
        self.config = config
        self.drawable = drawable

        if Gimp.Selection.is_empty(image):
            self.wid = drawable.get_width()
            self.hei = drawable.get_height()
        else:
            _, non_empty, x1, y1, x2, y2 = Gimp.Selection.bounds(image)
            self.wid = x2 - x1
            self.hei = y2 - y1

        # Gimp.message("Selection size: %d, %d" % (self.wid, self.hei))
        self.off_x = int(config.get_property("offset-x") * self.wid / 100)
        self.off_y = int(config.get_property("offset-y") * self.hei / 100)

        self.tile_x = self.off_x > 0
        self.tile_y = self.off_y > 0
        self.tiles = config.get_property("tiles")
        self.tiles_layer: Gimp.Layer | None = None

    COPY_BUFFER_NAME = "tileset-offset-buffer"

    def tile(self):
        self.tiles_layer = self._create_tiles_layer()
        x, y = self._center_block_pos()
        # Gimp.message("Centering block at %d, %d" % (x, y))
        self._fill_tiles_layer(x, y)
        self._apply_offset()
        self._final_copy_to_clipboard(x, y)
        self.image.set_selected_layers([self.drawable])

    def _create_tiles_layer(self) -> Gimp.Layer:
        layer_wid = self.wid
        layer_hei = self.hei
        tiles_mult = (2 * self.tiles + 1)

        if self.tile_x:
            layer_wid *= tiles_mult
        if self.tile_y:
            layer_hei *= tiles_mult

        layer = _find_or_create_layer(self.image, "draft", layer_wid, layer_hei)

        layer.set_offsets(self.wid, self.image.get_height() - self.hei - layer_hei)
        return layer

    def _center_block_pos(self) -> tuple[int, int]:
        _, grid_w, grid_h = self.image.grid_get_spacing()
        x = int(grid_w)
        y = int(self.image.get_height() - grid_h - self.hei)

        if self.tile_x:
            x += self.wid * self.tiles

        if self.tile_y:
            y -= self.hei * self.tiles

        return x, y

    def _fill_tiles_layer(self, x: int, y: int):
        buffer_name = Gimp.edit_named_copy([self.drawable], Tiler.COPY_BUFFER_NAME)
        if not buffer_name:
            raise Exception("Failed to copy the source layer")

        start, end = -self.tiles, self.tiles + 1

        x_range = range(start, end) if self.tile_x else range(0, 1)
        y_range = range(start, end) if self.tile_y else range(0, 1)

        for i in x_range:
            for j in y_range:
                self._paste_block(x + i * self.wid, y + j * self.hei)

        Gimp.buffer_delete(buffer_name)

        # Cropping the target layer to the expected size,
        # Some the pasting logic above adds some extra padding to the layer
        self.remove_extra_padding(x, y)

    def _paste_block(self, off_x: int, off_y: int):
        # Paste the copied buffer into the target layer
        layer = Gimp.edit_named_paste(self.tiles_layer, Tiler.COPY_BUFFER_NAME, False)
        layer.set_offsets(off_x, off_y)
        Gimp.floating_sel_anchor(layer)

    def remove_extra_padding(self, x, y):
        _, x0, y0 = self.tiles_layer.get_offsets()
        dw = self.wid * self.tiles if self.tile_x else 0
        dh = self.hei * self.tiles if self.tile_y else 0

        x1, y1 = x - dw, y - dh  # top-left of expected tiles
        x2, y2 = x + self.wid + dw, y + self.hei + dh  # bottom-right of expected tiles
        self.tiles_layer.resize(x2 - x1, y2 - y1, x0 - x1, y0 - y1)

    def _apply_offset(self):
        transparent = Gegl.Color.new("00000000")
        self.tiles_layer.offset(
            True, Gimp.OffsetType.WRAP_AROUND, transparent, self.off_x, self.off_y
        )

    def _final_copy_to_clipboard(self, x: int, y: int):
        self.image.select_rectangle(Gimp.ChannelOps.REPLACE, x, y, self.wid, self.hei)
        # self.image.set_selected_layers([self.tiles_layer])
        # Gimp.edit_copy([self.tiles_layer])

        copy_proc = Gimp.get_pdb().lookup_procedure("plug-in-tlk-universal-copy")
        config = copy_proc.create_config()
        config.set_property("run-mode", Gimp.RunMode.NONINTERACTIVE)
        config.set_property("image", self.image)
        config.set_core_object_array('drawables', [self.tiles_layer])
        copy_proc.run(config)

        Gimp.Selection.none(self.image)


def _find_or_create_layer(
    image: Gimp.Image, name: str, wid: int, hei: int
) -> Gimp.Layer:
    layer = image.get_layer_by_name(name)
    if layer:
        image.remove_layer(layer)

    layer = Gimp.Layer.new(
        image, name, wid, hei, Gimp.ImageType.RGBA_IMAGE, 100, Gimp.LayerMode.NORMAL
    )
    image.insert_layer(layer, None, 0)

    # if not layer:
    # else:
    #     image.raise_item_to_top(layer)
    #     layer.edit_clear()
    #     layer.set_visible(False)
    #     layer.resize(wid, hei, 0, 0)
    #     raise Exception("hello-world")

    return layer
