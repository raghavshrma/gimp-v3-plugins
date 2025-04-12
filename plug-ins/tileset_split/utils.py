from typing import Literal

import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp, Gegl

MAIN_GROUP_NAME = "l0-tiles"
REF_GROUP_NAME = "ref-tiles"
RAW_GROUP_NAME = "raw-tiles"


def create_main_group(image: Gimp.Image, base: Gimp.Layer) -> Gimp.GroupLayer:
    return new_group(image, base, MAIN_GROUP_NAME)


def get_main_group(image: Gimp.Image):
    return find_group(image, MAIN_GROUP_NAME)


def create_raw_group(image: Gimp.Image, base: Gimp.Layer) -> Gimp.GroupLayer:
    return new_group(image, base, RAW_GROUP_NAME)


def get_raw_group(image: Gimp.Image):
    return find_group(image, RAW_GROUP_NAME)


def create_ref_group(
    image: Gimp.Image, base: Gimp.Layer, level: int
) -> Gimp.GroupLayer:
    return new_group(image, base, f"l{level}-{REF_GROUP_NAME}")


def get_ref_group(image: Gimp.Image, level: int):
    name = f"l{level}-{REF_GROUP_NAME}"
    group = image.get_layer_by_name(name)

    if group is None:
        main_group = get_main_group(image)
        group = Gimp.GroupLayer.new(image, name)
        image.insert_layer(group, main_group.get_parent(), 0)
    elif not group.is_group_layer():
        raise Exception(f"Layer '{name}' is not a group layer")

    return group

def hide_ref_group(image: Gimp.Image, level: int, hide: bool = True):
    name = f"l{level}-{REF_GROUP_NAME}"
    group = image.get_layer_by_name(name)

    if group is not None:
        group.set_visible(not hide)

def new_group(image: Gimp.Image, base_layer: Gimp.Layer, name: str) -> Gimp.GroupLayer:
    existing = image.get_layer_by_name(name)
    if existing:
        raise Exception(f"Layer group '{name}' already exists.")

    group = Gimp.GroupLayer.new(image, name)
    image.insert_layer(group, base_layer.get_parent(), 0)
    return group


def find_group(image: Gimp.Image, name: str) -> Gimp.Layer:
    group = image.get_layer_by_name(name)
    if group is None:
        raise Exception(f"Layer Group '{name}' not found")
    if not group.is_group_layer():
        raise Exception(f"Layer '{name}' is not a group layer")
    return group


def find_layer(image: Gimp.Image, name: str, allow_none: bool = False) -> Gimp.Layer | None:
    layer = image.get_layer_by_name(name)
    if layer is None:
        if allow_none:
            Gimp.message(f"Layer '{name}' not found, skipping it's processing")
            return None

        raise Exception(f"Layer '{name}' not found")
    return layer

def hide_layer(image: Gimp.Image, name: str, hide: bool = True):
    layer = find_layer(image, name)
    layer.set_visible(not hide)

def remove_layer(image: Gimp.Image, name: str):
    layer = find_layer(image, name, True)
    if layer is not None:
        image.remove_layer(layer)


def offset_wrap(layer: Gimp.Layer, off_x: int, off_y: int):
    color = Gegl.Color.new("0")
    layer.offset(True, Gimp.OffsetType.WRAP_AROUND, color, off_x, off_y)

def get_grid_size(image: Gimp.Image) -> int:
    _, grid, _ = image.grid_get_spacing()
    return int(grid)

def copy(image: Gimp.Image, source: Gimp.Layer, parent: Gimp.GroupLayer | None, w: int, h: int, x: int, y: int) -> Gimp.Layer:
    layer = source.copy()
    image.insert_layer(layer, parent, 0)
    layer.resize(w, h, x, y)
    return layer

def replace(image: Gimp.Image, source: Gimp.Layer, target: Gimp.Layer) -> Gimp.Layer:
    parent = target.get_parent()
    layer = source.copy()
    image.insert_layer(layer, parent, 0)
    _, off_x, off_y = target.get_offsets()
    layer.set_offsets(off_x, off_y)
    name = target.get_name()
    image.remove_layer(target)
    layer.set_name(name)
    return layer

def change_offset(layer: Gimp.Layer, x: int, y: int):
    _, off_x, off_y = layer.get_offsets()
    layer.set_offsets(off_x + x, off_y + y)

def merge_down(image: Gimp.Image, layer: Gimp.Layer, merge_type: Gimp.MergeType = Gimp.MergeType.EXPAND_AS_NECESSARY) -> Gimp.Layer:
    return image.merge_down(layer, merge_type)

def get_primary(image: Gimp.Image, orientation: Literal["h", "v"]) -> Gimp.Layer:
    return find_layer(image, f"l0-{orientation}-1-primary")

def get_plus_layer(image: Gimp.Image, orientation: Literal["h", "v"], idx: int = 2) -> Gimp.Layer:
    suffix = "-primary" if idx == 1 else ""
    return find_layer(image, f"l0-{orientation}-{idx}{suffix}")