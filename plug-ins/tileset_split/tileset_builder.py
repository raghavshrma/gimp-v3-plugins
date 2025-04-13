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

        self.src_a = TilesetSource(image, "l5-series-a", self.parent)
        self.src_b = TilesetSource(image, "l5-series-b", self.parent)
        self.src_c = TilesetSource(image, "l5-series-c", self.parent)
        self.src_d1 = TilesetSource(image, "l5-series-d1", self.parent)
        self.src_d2 = TilesetSource(image, "l5-series-d2", self.parent)
        self.src_plus_h = TilesetSource(image, utils.get_plus_layer(image, "h", 1), self.parent)
        self.src_plus_v = TilesetSource(image, utils.get_plus_layer(image, "v", 1), self.parent)
        self.src_single_h = TilesetSource(image, utils.get_singles_layer(image, "h", 1), self.parent)
        self.src_single_v = TilesetSource(image, utils.get_singles_layer(image, "v", 1), self.parent)
        self.src_inner_corners = TilesetSource(image, "l2-inner-corners", self.parent)
        self.src_outer_corners = TilesetSource(image, "l2-outer-corners", self.parent)
        self.src_sample = TilesetSource(image, sample, self.parent)

        self.grid = utils.get_grid_size(image)
        self._show_all()

    def set_temp_parent(self, parent: Gimp.GroupLayer):
        self._set_all_parent(parent)

    def unset_temp_parent(self):
        self._set_all_parent(self.parent)

    def _set_all_parent(self, parent: Gimp.GroupLayer):
        self.src_a.default_parent = parent
        self.src_b.default_parent = parent
        self.src_c.default_parent = parent
        self.src_d1.default_parent = parent
        self.src_d2.default_parent = parent
        self.src_plus_h.default_parent = parent
        self.src_plus_v.default_parent = parent
        self.src_single_h.default_parent = parent
        self.src_single_v.default_parent = parent
        self.src_inner_corners.default_parent = parent
        self.src_outer_corners.default_parent = parent
        self.src_sample.default_parent = parent

    def _show_all(self):
        # self.src_a.layer.set_visible(True)
        # self.src_b.layer.set_visible(True)
        # self.src_c.layer.set_visible(True)
        # self.src_d1.layer.set_visible(True)
        # self.src_d2.layer.set_visible(True)
        # self.src_plus_h.layer.set_visible(True)
        # self.src_plus_v.layer.set_visible(True)
        # self.src_single_h.layer.set_visible(True)
        # self.src_single_v.layer.set_visible(True)
        # self.src_corners.layer.set_visible(True)
        self.src_sample.layer.set_visible(True)

    def hide_extras(self):
        self.src_sample.layer.set_visible(False)

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

    def a(self, index: int) -> Gimp.Layer:
        return self.src_a.copy(index)

    def b(self, index: int) -> Gimp.Layer:
        return self.src_b.copy(index)

    def c(self, index: int) -> Gimp.Layer:
        return self.src_c.copy(index)

    def d(self, index: int) -> Gimp.Layer:
        if index <= 2:
            return self.src_d1.copy(index)
        elif index <= 4:
            return self.src_d2.copy(index - 2)
        elif index <= 6:
            return self.src_d1.copy(index - 2)
        else:
            return self.src_d2.copy(index - 4)

    def top_full(self) -> Gimp.Layer:
        return self.src_plus_h.copy_block(2, 1, 2)

    def top(self) -> Gimp.Layer:
        return self.src_plus_h.copy(5)

    def top_extra(self) -> Gimp.Layer:
        return self.src_plus_h.copy(2)

    def bottom(self) -> Gimp.Layer:
        return self.src_plus_h.copy(8)

    def left(self) -> Gimp.Layer:
        return self.src_plus_v.copy(4)

    def right(self) -> Gimp.Layer:
        return self.src_plus_v.copy(6)

    def single_h_full(self) -> Gimp.Layer:
        return self.src_single_h.copy_block(2, 1, 2)

    def single_h(self) -> Gimp.Layer:
        return self.src_single_h.copy(5)

    def single_v(self) -> Gimp.Layer:
        return self.src_single_v.copy(5)

    def inner_corner_tl(self):
        return self.src_inner_corners.copy2(2, 3)

    def inner_corner_tr(self):
        return self.src_inner_corners.copy2(1, 3)

    def inner_corner_bl(self):
        return self.src_inner_corners.copy2(2, 1)

    def inner_corner_br(self):
        return self.src_inner_corners.copy2(1, 1)

    def inner_corner_tl_extra(self):
        return self.src_inner_corners.copy2(2, 2)

    def inner_corner_tr_extra(self):
        return self.src_inner_corners.copy2(1, 2)

    def outer_corner_tl(self):
        return self.src_outer_corners.copy2(1, 2)

    def outer_corner_tr(self):
        return self.src_outer_corners.copy2(6, 2)

    def outer_corner_bl(self):
        return self.src_outer_corners.copy2(1, 3)

    def outer_corner_br(self):
        return self.src_outer_corners.copy2(6, 3)

    def outer_corner_tl_full(self):
        return self.src_outer_corners.copy_block2(1, 1, 1, 2)

    def outer_corner_tr_full(self):
        return self.src_outer_corners.copy_block2(6, 1, 1, 2)

    def outer_corner_tl_extra(self):
        return self.src_outer_corners.copy2(1, 1)

    def outer_corner_tr_extra(self):
        return self.src_outer_corners.copy2(6, 1)

    def center_dark(self):
        return self.src_sample.copy(21)

    def center_light(self):
        return self.src_sample.copy(21)

    def deep_top(self):
        return self.src_sample.copy2(3, 3)

    def deep_bottom(self):
        return self.src_sample.copy2(3, 5)

    def deep_left(self):
        return self.src_sample.copy2(2, 4)

    def deep_right(self):
        return self.src_sample.copy2(5, 4)

    def deep_corner_tl(self):
        return self.src_sample.copy2(2, 3)

    def deep_corner_tr(self):
        return self.src_sample.copy2(5, 3)

    def deep_corner_bl(self):
        return self.src_sample.copy2(2, 5)

    def deep_corner_br(self):
        return self.src_sample.copy2(5, 5)
