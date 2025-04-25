#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from collections.abc import Callable

import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp
from generator_config import GeneratorConfig
import gimp_error
import o0a_initiate
import o1a_seamless_edge_tiles, o1b_edge_tiles_refs
import o2a_corners_refs, o2b_corner_edges_sanity
import o3a_seamless_single_tiles, o3b_single_tiles_refs, o3c_single_corners
import o4a_transition_tiles
import o5a_connector_refs
import o6a_slope_refs, o6b_slope_refs, o6c_slope_refs
import o9a_consolidate_sample, o9b_consolidate_tileset

OPERATIONS: list[tuple[str, str, Callable[[GeneratorConfig], None]]] = [
    ("0.a", "Initiate", o0a_initiate.handle),
    ("1.a", "Seamless Edge Tiles", o1a_seamless_edge_tiles.handle),
    ("1.b", "Edge Tiles", o1b_edge_tiles_refs.handle),
    ("2.a", "Edge Corners", o2a_corners_refs.handle),
    ("2.b", "Edge Corners Sanity", o2b_corner_edges_sanity.handle),
    ("3.a", "Seamless Single Tiles", o3a_seamless_single_tiles.handle),
    ("3.b", "Single Tiles", o3b_single_tiles_refs.handle),
    ("3.c", "Single Corners", o3c_single_corners.handle),
    ("4.a", "Transition Tiles", o4a_transition_tiles.handle),
    ("5.a", "Connectors", o5a_connector_refs.handle),
    ("9.a", "Consolidate Sample", o9a_consolidate_sample.handle),
    ("9.b", "Consolidate Tileset", o9b_consolidate_tileset.handle),
]


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
        return gimp_error.calling(procedure, f"Unknown operation: {operation}")

    image.undo_group_start()

    op_id, _, handler = op

    gen_config = GeneratorConfig(image, drawable, config)
    handler(gen_config)
    Gimp.displays_flush()
    image.undo_group_end()
    return gimp_error.success(procedure)
