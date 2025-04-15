import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

import utils
from tileset_collection import TilesetSource, TilesetTargetGroup


def handle(image: Gimp.Image, sample: Gimp.Layer, config: Gimp.ProcedureConfig):
    utils.hide_ref_group(image, 5, False)
    g = utils.get_grid_size(image)
    x, y = 7 * g, 3 * g

    main_group = utils.get_main_group(image)
    target = TilesetTargetGroup(image, "l5-block-connectors", main_group, 4, 8, x, y, True)

    _finalise_type_o(image, target, 1, 1, 1)
    _finalise_type_o(image, target, 2, 3, 1)
    _finalise_type_o(image, target, 3, 1, 3)
    _finalise_type_o(image, target, 4, 3, 3)
    _finalise_type_5(image, target, 5, 1, 5)
    _finalise_type_6(image, target, 6, 3, 5)
    _finalise_type_o(image, target, 7, 1, 7)
    _finalise_type_8(image, target, 8, 3, 7)

    target.finalise()
    utils.hide_ref_group(image, 5)

def _finalise_type_o(image: Gimp.Image, target: TilesetTargetGroup, idx: int, col: int, row: int):
    source = _get_source(image, idx, target)
    target.add(col + 0, row + 0, source.copy(2, 2))
    target.add(col + 1, row + 0, source.copy(4, 2))
    target.add(col + 0, row + 1, source.copy(2, 4))
    target.add(col + 1, row + 1, source.copy(4, 4))

def _finalise_type_5(image: Gimp.Image, target: TilesetTargetGroup, idx: int, col: int, row: int):
    source = _get_source(image, idx, target)
    target.add(col + 0, row + 0, source.copy(2, 3))
    target.add(col + 1, row + 0, source.copy(4, 3))
    target.add(col + 0, row + 1, source.copy(3, 4))
    target.add(col + 1, row + 1, source.copy(3, 2))


def _finalise_type_6(image: Gimp.Image, target: TilesetTargetGroup, idx: int, col: int, row: int):
    source = _get_source(image, idx, target)
    target.add(col + 0, row + 0, source.copy(2, 2))
    target.add(col + 0, row + 1, source.copy(2, 4))
    target.add(col + 1, row + 0, source.copy(4, 3))

def _finalise_type_8(image: Gimp.Image, target: TilesetTargetGroup, idx: int, col: int, row: int):
    source = _get_source(image, idx, target)
    target.add(col + 0, row + 0, source.copy(1, 2))
    target.add(col + 0, row + 1, source.copy(3, 2))
    target.add(col + 1, row - 1, source.copy_block2(5, 1, 1, 2))
    target.add(col + 1, row + 1, source.copy(5, 4))

def _get_source(image, index: int, target: TilesetTargetGroup) -> TilesetSource:
    return TilesetSource(image, f"l5-type-{index}-raw", target.group)