#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from collections.abc import Callable

import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp
import gimp_error, l0_slicing, l1_primary_tiles, l2_corners
import l3_corners_finalise
import l4a_singles_hv_raw, l4b_singles_hv_1_tile_raw, l4c_singles_hv_1_tile_final
import l5a_connector_base_blocks_raw, l5b_connector_refs, l5c_block_connector_finalise
import l6a_slope_refs, l6b_slope_refs, l6c_slope_refs
import l9_consolidate_tileset

OPERATIONS: list[tuple[str, int, str, str]] = [
    ("l0-slicing", 0, "L0: Slicing", "Performs slicing on the base sample tileset"),
    ("l1-primary-tiles", 1, "L1: Primary Tiles", "Re-offsets the primary tiles"),
    ("l2", 2, "L2: Corner Tiles", "Prepare reference tiles for corners"),
    ("l3", 3, "L3: Finalise Corner Tiles", "Finalise corner tiles"),
    ("l4a", 4, "L4a: Singles 1st Ref - H&V", "Singles 1st Reference - (horizontal and vertical)"),
    ("l4b", 5, "L4b: Singles HV-1 Tile Raw", "Singles - Horizontal and Vertical - 1 Tile Raw offset"),
    ("l4c", 6, "L4c: Singles HV-1 Tile Final", "Singles - Horizontal and Vertical - 1 Tile Finalise"),
    ("l5a", 7, "L5a: Block Connector Base", "Connector base blocks raw for transparent corners and edges"),
    ("l5b", 8, "L5b: Block Connector Refs", "Connector references and raw"),
    ("l5c", 9, "L5c: Block Connector Finalise", "Finalise block connectors"),
    ("l6a", 10, "L6a: Slope Refs", "Slope Tile Refs A"),
    ("l6b", 11, "L6b: Slope Refs", "Slope Tile Refs B"),
    ("l6c", 12, "L6c: Slope Refs", "Slope Tile Refs C"),
    ("l9", 99, "L9: Consolidate Tileset", "Consolidate tileset"),
]

DICT = {
    "l0-slicing": l0_slicing.handle,
    "l1-primary-tiles": l1_primary_tiles.handle,
    "l2": l2_corners.handle,
    "l3": l3_corners_finalise.handle,
    "l4a": l4a_singles_hv_raw.handle,
    "l4b": l4b_singles_hv_1_tile_raw.handle,
    "l4c": l4c_singles_hv_1_tile_final.handle,
    "l5a": l5a_connector_base_blocks_raw.handle,
    "l5b": l5b_connector_refs.handle,
    "l5c": l5c_block_connector_finalise.handle,
    "l6a": l6a_slope_refs.handle,
    "l6b": l6b_slope_refs.handle,
    "l6c": l6c_slope_refs.handle,
    "l9": l9_consolidate_tileset.handle,
}

def run_any(
        procedure: Gimp.Procedure,
        run_mode: Gimp.RunMode,
        image: Gimp.Image,
        # drawable: Gimp.Layer,
        config: Gimp.ProcedureConfig,
        data):

    # if drawable.get_name() != "level-0":
    #     return gimp_error.calling(procedure, "Select a level-0 layer")
    #
    # if drawable.get_parent() is None:
    #     return gimp_error.calling(procedure, "Select a level-0 layer inside a group")

    drawable = image.get_layer_by_name("level-0")
    if drawable is None:
        return gimp_error.calling(procedure, "level-0 layer not found")

    if drawable.get_parent() is None:
        return gimp_error.calling(procedure, "level-0 layer not inside a group")



    image.undo_group_start()
    operation = config.get_property("operation")

    handler = DICT.get(operation)
    if not handler:
        image.undo_group_end()
        return gimp_error.calling(procedure, "Unknown operation: " + operation)

    handler(image, drawable, config)

    Gimp.displays_flush()
    image.undo_group_end()
    return gimp_error.success(procedure)

# def run_all(
#         procedure: Gimp.Procedure,
#         run_mode: Gimp.RunMode,
#         image: Gimp.Image,
#         drawables: list[Gimp.Drawable],
#         config: Gimp.ProcedureConfig,
#         data):
#

# def run_any(
#         procedure: Gimp.Procedure,
#         run_mode: Gimp.RunMode,
#         image: Gimp.Image,
#         config: Gimp.ProcedureConfig,
#         data):
#
#     return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, None)

