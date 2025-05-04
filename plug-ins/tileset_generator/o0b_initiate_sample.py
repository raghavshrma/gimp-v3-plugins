import gi

gi.require_version("Gimp", "3.0")
import utils
from gi.repository import Gimp, Gegl

from generator_config import GeneratorConfig
from tileset_builder import Builder, BuilderSet, QuickBuilder
from tileset_collection import TilesetTargetGroup
from tileset_collection import AreaBuilder, Area


def handle(config: GeneratorConfig):
    raise Exception("Not supported yet, use quick() instead")

def quick(config: GeneratorConfig):
    s = _initiate(config)
    layer = s.build3("init-sample", _build_init_sample)
    s.cleanup()
    s.image.lower_item_to_bottom(layer)

    # bll = s.image.select_rectangle(Gimp.ChannelOps.REPLACE, 192, 1056, 192, 192)
    # Gimp.message("Select the area to trim: " + str(bll))
    # Gimp.Selection.


def _initiate(config: GeneratorConfig):
    s = BuilderSet(config)
    root = config.setup_root()
    layer_name = config.get_level_name(0)
    utils.set_visible_layers(config.image, root, [layer_name])
    s.setup(_setup_sources)
    s.set_target_size(14, 8)
    s.set_target_spacing(0, 9, 4, 4)
    return s

def _setup_sources(src: Builder):
    src.setup_sample()

def _build_init_sample(t: TilesetTargetGroup, src: QuickBuilder):
    area = AreaBuilder(src.grid, 12)
    a_h = area.mid_seam_horizontal()
    a_v = area.mid_seam_vertical()
    a_t = area.mid_seam_top()

    for i in src.config.range_cols(0):
        t.add(i + 2, 1, a_t.crop(src.sample_seam_edge_top()))
        t.add(i + 2, 5, a_h.crop(src.sample_seam_edge_bottom()))
        t.add(i + 2, 6, a_t.crop(src.sample_seam_single_row()))

    for i in src.config.range_rows(0):
        t.add(2, i + 2, a_v.crop(src.sample_seam_edge_left()))
        t.add(5, i + 2, a_v.crop(src.sample_seam_edge_right()))
        t.add(7, i + 2, a_v.crop(src.sample_seam_single_col()))


    # inner corners

    t.add(9, 1, a_h.crop(src.sample_seam_edge_bottom()))
    t.add(9, 1, a_v.crop(src.sample_seam_edge_right()))
    t.add(10, 1, a_v.crop(src.sample_seam_edge_left()))

    t.add(9, 2, a_t.crop(src.sample_seam_edge_top()))
    t.add(9, 2, a_v.crop(src.sample_seam_edge_right()))
    t.add(10, 2, a_v.crop(src.sample_seam_edge_left()))




    # center blocks

    t.new_fill_layer("init-sample-fill", 1, 1, 14, 8)
    t.set_fill_color("rgba(0, 0, 0, 1)")
    t.fill_rect(3, 3, 2, 2)
    t.fill_rect(7, 7, 1, 1)
    t.fill_rect(9, 5, 2, 3)

