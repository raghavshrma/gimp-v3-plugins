import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

import utils
from tileset_collection import TilesetSource, TilesetTarget, Area


def handle(image: Gimp.Image, sample: Gimp.Layer, config: Gimp.ProcedureConfig):
    utils.hide_ref_group(image, 4)

    g = utils.get_grid_size(image)
    x, y = sample.get_width() + g, 3 * g
    parent = utils.get_ref_group(image, 5)

    _build_series_a(image, parent, x + 0 * g, y)
    _build_series_b(image, parent, x + 2 * g, y)
    _build_series_c(image, parent, x + 4 * g, y)
    _build_series_d(image, parent, x + 6 * g, y)


def _build_series_a(image: Gimp.Image, parent: Gimp.GroupLayer, x: int, y: int):
    """
    Series a: edge tiles of lighter side
    """

    g, f = utils.get_grid_size_and_factor(image)

    h_layer = TilesetSource(image, utils.get_primary(image, "h"), parent)
    v_layer = TilesetSource(image, utils.get_primary(image, "v"), parent)

    area_l = Area(0, 0, g - f, g)
    area_r = Area(f, 0, g - f, g)
    area_u = Area(0, 0, g, g - f)
    area_d = Area(0, f, g, g - f)

    a = TilesetTarget(image, "l5-series-a", parent, 2, 2, x, y, True)
    a.add_at(h_layer.copy_area2(5, area_u), 1)
    a.add_at(h_layer.copy_area2(8, area_d), 4)

    # a2 = TilesetTarget(image, "l5-series-a2", parent, 2, 2, x, y, True)
    a.add_at(v_layer.copy_area2(6, area_r), 2)
    a.add_at(v_layer.copy_area2(4, area_l), 3)

def _build_series_b(image: Gimp.Image, parent: Gimp.GroupLayer, x: int, y: int):
    """
    Series b: Inner corner tiles of lighter side
    """

    # g = utils.get_grid_size(image)
    # f = g // 2
    g, f = utils.get_grid_size_and_factor(image)
    s = g - f

    corners = TilesetSource(image, "l2-inner-corners", parent)

    area_ul = Area(0, 0, s, s)
    area_ur = Area(f, 0, s, s)
    area_dl = Area(0, f, s, s)
    area_dr = Area(f, f, s, s)

    b = TilesetTarget(image, "l5-series-b", parent, 2, 2, x, y, True)
    b.add_at(corners.copy_area2(6, area_ul), 1)
    b.add_at(corners.copy_area2(5, area_ur), 2)
    b.add_at(corners.copy_area2(2, area_dl), 3)
    b.add_at(corners.copy_area2(1, area_dr), 4)


def _build_series_c(image: Gimp.Image, parent: Gimp.GroupLayer, x: int, y: int):
    """
    Series c: Single Layer - connecting edges
    """

    g, f = utils.get_grid_size_and_factor(image)

    h_layer = TilesetSource(image, utils.get_singles_layer(image, "h", 1), parent)
    v_layer = TilesetSource(image, utils.get_singles_layer(image, "v", 1), parent)

    area_l = Area(0, 0, g - f, g)
    area_r = Area(f, 0, g - f, g)
    area_u = Area(0, 0, g, g - f)
    area_d = Area(0, f, g, g - f)

    c = TilesetTarget(image, "l5-series-c", parent, 2, 2, x, y, True)
    c.add_at(v_layer.copy_area2(5, area_u), 1)
    c.add_at(v_layer.copy_area2(5, area_d), 4)
    c.add_at(h_layer.copy_area2(5, area_r), 2)
    c.add_at(h_layer.copy_area2(5, area_l), 3)


def _build_series_d(image: Gimp.Image, parent: Gimp.GroupLayer, x: int, y: int):
    """
    Series d: Single Layer - connecting edges
    """

    g, f = utils.get_grid_size_and_factor(image)

    corners = TilesetSource(image, "l2-inner-corners", parent)

    area_l = Area(0, 0, g - f, g)
    area_r = Area(f, 0, g - f, g)
    area_u = Area(0, 0, g, g - f)
    area_d = Area(0, f, g, g - f)

    d1 = TilesetTarget(image, "l5-series-d1", parent, 2, 2, x, y, True)
    d1.add_at(corners.copy_area2(6, area_l), 1)
    d1.add_at(corners.copy_area2(5, area_r), 2)
    d1.add_at(corners.copy_area2(2, area_l), 3)
    d1.add_at(corners.copy_area2(1, area_r), 4)

    d2 = TilesetTarget(image, "l5-series-d2", parent, 2, 2, x + 2 * g, y, True)
    d2.add_at(corners.copy_area2(6, area_u), 1)
    d2.add_at(corners.copy_area2(5, area_u), 2)
    d2.add_at(corners.copy_area2(2, area_d), 3)
    d2.add_at(corners.copy_area2(1, area_d), 4)
