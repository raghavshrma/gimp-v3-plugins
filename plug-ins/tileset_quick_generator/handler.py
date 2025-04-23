#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from collections.abc import Callable

import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp
from generator_config import GeneratorConfig
import gimp_error
import o1a_primary_edge_tiles, o1b_edge_tiles_refs
import o2_corners
import o3_corners_finalize
import o4a_singles_hv_raw, o4b_singles_hv_1_tile_raw, o4c_singles_hv_1_tile_final
import o5a_connector_base_blocks_raw, o5b_connector_refs, o5c_block_connector_finalize
import o6a_slope_refs, o6b_slope_refs, o6c_slope_refs
import o9_consolidate_tileset

OPERATIONS: list[
    tuple[str, str, str, Callable[[GeneratorConfig], None]]
] = [
    (
        "1.a",
        "Primary Edge Tiles",
        "Offsets primary edge tiles to be made seamless",
        o1a_primary_edge_tiles.handle,
    ),
    (
        "1.b",
        "Edge Tiles Refs",
        "Prepares the reference for all the edge tiles",
        o1b_edge_tiles_refs.handle,
    ),
    # ("o2", "Corner Tiles", "Prepare reference tiles for corners"),
    # ("o3", "Finalise Corner Tiles", "Finalise corner tiles"),
    # ("o4a", "Singles 1st Ref - H&V", "Singles 1st Reference - (horizontal and vertical)"),
    # ("o4b", "Singles HV-1 Tile Raw", "Singles - Horizontal and Vertical - 1 Tile Raw offset"),
    # ("o4c", "Singles HV-1 Tile Final", "Singles - Horizontal and Vertical - 1 Tile Finalise"),
    # ("o5a", "Block Connector Base", "Connector base blocks raw for transparent corners and edges"),
    # ("o5b", "Block Connector Refs", "Connector references and raw"),
    # ("o5c", "Block Connector Finalise", "Finalise block connectors"),
    # ("o6a", "Slope Refs", "Slope Tile Refs A"),
    # ("o6b", "Slope Refs", "Slope Tile Refs B"),
    # ("o6c", "Slope Refs", "Slope Tile Refs C"),
    # ("o9", "Consolidate Tileset", "Consolidate tileset"),
]

# DICT = {
#     "o0-slicing": o1a_primary_edge_tiles.handle,
#     "o1-primary-tiles": o1b_edge_tiles_refs.handle,
#     "o2": o2_corners.handle,
#     "o3": o3_corners_finalize.handle,
#     "o4a": o4a_singles_hv_raw.handle,
#     "o4b": o4b_singles_hv_1_tile_raw.handle,
#     "o4c": o4c_singles_hv_1_tile_final.handle,
#     "o5a": o5a_connector_base_blocks_raw.handle,
#     "o5b": o5b_connector_refs.handle,
#     "o5c": o5c_block_connector_finalize.handle,
#     "o6a": o6a_slope_refs.handle,
#     "o6b": o6b_slope_refs.handle,
#     "o6c": o6c_slope_refs.handle,
#     "o9": o9_consolidate_tileset.handle,
# }

def run_one(
    procedure: Gimp.Procedure,
    run_mode: Gimp.RunMode,
    image: Gimp.Image,
    drawable: Gimp.Layer,
    config: Gimp.ProcedureConfig,
    data,
):
    operation: int = config.get_property("operation")
    op = OPERATIONS[operation]
    if not op:
        return gimp_error.calling(procedure, "Unknown operation: " + operation)

    image.undo_group_start()

    _, _, _, handler = op
    gen_config = GeneratorConfig(image, drawable, config)
    handler(gen_config)
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
