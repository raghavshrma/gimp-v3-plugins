from types import ModuleType

from tilegen.v1_extended_top import (
    l0a_initiate, l0b_initiate_sample,
    l1a_seamless_edge_tiles, l1b_edge_tiles_refs,
    l2a_corners_refs, l2b_corner_edges_sanity,
    l3a_seamless_single_tiles, l3b_single_tiles_refs, l3c_single_corners,
    l4a_transition_tiles,
    l5a_connector_refs,
    l6a_slope_refs, l6b_slope_refs, l6c_slope_refs,
    l9b_consolidate_sample, l9a_consolidate_tileset,
)

NAME = "V1: Extended Top"

OPERATIONS: list[tuple[str, str, ModuleType]] = [
    ("0.a", "Initiate", l0a_initiate),
    ("0.b", "Initiate Sample", l0b_initiate_sample),
    ("1.a", "Seamless Edge Tiles", l1a_seamless_edge_tiles),
    ("1.b", "Edge Tiles", l1b_edge_tiles_refs),
    ("2.a", "Edge Corners", l2a_corners_refs),
    ("2.b", "Edge Corners Sanity", l2b_corner_edges_sanity),
    ("3.a", "Seamless Single Tiles", l3a_seamless_single_tiles),
    ("3.b", "Single Tiles", l3b_single_tiles_refs),
    ("3.c", "Single Corners", l3c_single_corners),
    ("4.a", "Transition Tiles", l4a_transition_tiles),
    ("5.a", "Connectors", l5a_connector_refs),
    ("9.a", "Consolidate Tileset", l9a_consolidate_tileset),
    ("9.b", "Consolidate Sample", l9b_consolidate_sample),
]
