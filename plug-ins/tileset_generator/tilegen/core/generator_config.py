import gi

gi.require_version("Gimp", "3.0")

from gi.repository import Gimp
from tilegen.core import utils

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

        self.is_quick: bool = False
        self.is_color_target: bool = False
        self.prefix: str = ""

        self.grid = utils.get_grid_size(image)
        self._root: Gimp.GroupLayer | None = None
        self._all_roots: list[Gimp.GroupLayer] = []
        self.setup()

    def setup(self):
        self.is_quick = self.config.get_property("quick")
        self.is_color_target: bool = self.config.get_property("target") == 1
        self.prefix = self.get_prefix(self.is_color_target)


    def get_prefix(self, is_color_target: bool):
        prefix = is_color_target and "c-" or "o-"
        if self.is_quick:
            prefix = "q" + prefix
        return prefix

    @staticmethod
    def get_root_name(is_color_target: bool):
        return is_color_target and "colors" or "outlines"

    def setup_root(self, force: bool = False) -> Gimp.GroupLayer:
        if (self._root is None) or force:
            root_group_name = self.get_root_name(self.is_color_target)
            self._root = self.find_group(root_group_name)

            children = self.image.get_layers()
            self._all_roots = []
            for child in children:
                if isinstance(child, Gimp.GroupLayer):
                    child.set_expanded(False)
                    name = child.get_name()
                    if 'colors' in name or 'outlines' in name:
                        self._all_roots.append(child)

        self._root.set_expanded(True)
        return self._root

    def find_group(self, name: str) -> Gimp.GroupLayer:
        return utils.find_group(self.image, name)

    def get_group_layer_dict(self, layer: str | Gimp.GroupLayer):
        layer = type(layer) == str and self.find_group(layer) or layer

        children = layer.get_children()
        group_dict = {}
        for child in children:
            group_dict[child.get_name()] = child

        return group_dict

    def initiate_level(self, level: int, dependencies: list[int] = None):
        """
        - Hides all the other levels except this level and the dependencies
        - Find or creates the layer group for this target
        """

        # other_root_name = self.is_color_target and "outlines" or "colors"
        # utils.hide_layer(self.image, other_root_name)

        group_name = f"{self.prefix}l{level}"
        root = self.setup_root()
        group = utils.find_or_create_group(self.image, group_name, root)
        dependencies = dependencies or []
        dependencies.append(level)
        self.set_visible_levels(dependencies)

        return group

    def set_visible_levels(self, levels: list[int]):
        dependencies = set(self.get_level_names(levels))

        root = self.setup_root()
        children = root.get_children()
        for child in children:
            visible = child.get_name() in dependencies
            child.set_visible(visible)
            child.set_expanded(visible)

    def get_level_names(self, levels: list[int]):
        mapper = map(lambda i: self.get_level_name(i), levels)
        return list(mapper)

    def get_level_name(self, level: int):
        """
        - Returns the name of the level
        - The name is the prefix + level number
        """

        return f"{self.prefix}l{level}" if level > 0 else f"{self.prefix}sample"

    def range_cols(self, start: int = 1):
        end = 3 if self.is_quick else 7
        return range(start, end)

    def range_rows(self, start: int = 1):
        end = 3 if self.is_quick else 6
        return range(start, end)