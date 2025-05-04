import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp, Gegl
import utils
from generator_config import GeneratorConfig


def handle(config: GeneratorConfig):
    _initiate(config)

def quick(config: GeneratorConfig):
    _initiate(config)

def _initiate(config: GeneratorConfig):
    colors = utils.find_or_create_group(config.image, "colors", None)
    outlines = utils.find_or_create_group(config.image, "outlines", None)

    groups = [
        (config.get_prefix(True), colors),
        (config.get_prefix(False), outlines),
    ]

    for prefix, group in groups:
        _add_sample_layer(config, prefix, group)
        _add_empty_layer(config, prefix, group)

    _setup_background(config)


def _add_empty_layer(config: GeneratorConfig, prefix: str, parent: Gimp.GroupLayer):
    g = config.grid

    layer_name = f"{prefix}empty"
    layer = _setup_layer(config, layer_name, parent, 7 * g, 5 * g)

    fill_bg = prefix == config.get_prefix(True)

    if fill_bg:
        color = Gegl.Color.new("0")
        color.set_rgba(1, 1, 1, 1)
        Gimp.context_set_background(color)
        layer.fill(Gimp.FillType.BACKGROUND)

    layer.set_visible(False)

def _add_sample_layer(config: GeneratorConfig, prefix: str, parent: Gimp.GroupLayer):
    g = config.grid

    layer_name = f"{prefix}sample"
    wid, hei = (14, 8) if config.is_quick else (10, 10)
    _setup_layer(config, layer_name, parent, wid * g, hei * g)

def _setup_layer(config: GeneratorConfig, name: str, parent: Gimp.GroupLayer | None, wid: int, hei: int) -> Gimp.Layer:
    image = config.image

    layer = image.get_layer_by_name(name)
    if layer is None:
        layer = Gimp.Layer.new(image, name, wid, hei, Gimp.ImageType.RGBA_IMAGE, 100, Gimp.LayerMode.NORMAL)
        layer.set_offsets(0, 0)
        image.insert_layer(layer, parent, 0)
        image.lower_item_to_bottom(layer)
    else:
        layer.set_lock_alpha(False)
        layer.set_lock_content(False)
        layer.set_lock_position(False)
        layer.set_lock_visibility(False)
        layer.resize(wid, hei, 0, 0)
        layer.set_offsets(0, 0)
        image.reorder_item(layer, parent, 0)
        image.lower_item_to_bottom(layer)

    return layer


def _setup_background(config: GeneratorConfig):
    image = config.image
    layer = _setup_layer(config, "Background", None, image.get_width(), image.get_height())
    image.lower_item_to_bottom(layer)
    color = Gegl.Color.new("#e2e2df")
    Gimp.context_set_background(color)

    layer.fill(Gimp.FillType.BACKGROUND)
    layer.set_lock_content(True)
    layer.set_lock_position(True)