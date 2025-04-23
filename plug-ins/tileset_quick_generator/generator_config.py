import gi

gi.require_version("Gimp", "3.0")

from gi.repository import Gimp
import utils


class GeneratorConfig:
    """
    Class to manage the configuration of the tileset generator.
    """

    def __init__(
        self, image: Gimp.Image, drawable: Gimp.Layer, config: Gimp.ProcedureConfig
    ):
        self.image = image
        self.drawable = drawable
        self.config = config

        self.is_color_target = config.get_property("target") == 1
        root_group_name = self.is_color_target and "colors" or "outlines"
        self.root = self.find_group(root_group_name)
        self.prefix = self.is_color_target and "c-" or "o-"
        self.grid = utils.get_grid_size(image)

    def find_group(self, name: str) -> Gimp.GroupLayer:
        return utils.find_group(self.image, name)

    def get_group_layer_dict(self, layer: str | Gimp.GroupLayer):
        layer = type(layer) == str and self.find_group(layer) or layer

        children = layer.get_children()
        group_dict = {}
        for child in children:
            group_dict[child.get_name()] = child

        return group_dict

    def initiate_level(self, level: int, dependencies: list[int] = []):
        """
        - Hides all of the other levels except this level and the dependencies
        - Find or creates the layer group for this target
        """

        other_root_name = self.is_color_target and "outlines" or "colors"
        utils.hide_layer(self.image, other_root_name)

        group_name = f"{self.prefix}l{level}"
        group = utils.find_or_create_group(self.image, group_name, self.root)
        dependencies = self.get_level_names(dependencies)
        dependencies.append(group_name)

        children = self.root.get_children()
        for child in children:
            visible = child.get_name() in dependencies
            child.set_visible(visible)

        return group

    def get_level_names(self, levels: list[int]):
        mapper = map(lambda i: self.get_level_name(i), levels)
        return list(mapper)

    def get_level_name(self, level: int):
        """
        - Returns the name of the level
        - The name is the prefix + level number
        """

        return f"{self.prefix}l{level}" if level > 0 else f"{self.prefix}sample"
