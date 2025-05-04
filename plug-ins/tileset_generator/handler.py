#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from collections.abc import Callable

import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp
from generator_config import GeneratorConfig
from types import ModuleType

import gimp_error
import o0a_initiate, o0b_initiate_sample
import o1a_seamless_edge_tiles, o1b_edge_tiles_refs
import o2a_corners_refs, o2b_corner_edges_sanity
import o3a_seamless_single_tiles, o3b_single_tiles_refs, o3c_single_corners
import o4a_transition_tiles
import o5a_connector_refs
import o6a_slope_refs, o6b_slope_refs, o6c_slope_refs
import o9b_consolidate_sample, o9a_consolidate_tileset

OPERATIONS: list[tuple[str, str, ModuleType]] = [
    ("0.a", "Initiate", o0a_initiate),
    ("0.b", "Initiate Sample", o0b_initiate_sample),
    ("1.a", "Seamless Edge Tiles", o1a_seamless_edge_tiles),
    ("1.b", "Edge Tiles", o1b_edge_tiles_refs),
    ("2.a", "Edge Corners", o2a_corners_refs),
    ("2.b", "Edge Corners Sanity", o2b_corner_edges_sanity),
    ("3.a", "Seamless Single Tiles", o3a_seamless_single_tiles),
    ("3.b", "Single Tiles", o3b_single_tiles_refs),
    ("3.c", "Single Corners", o3c_single_corners),
    ("4.a", "Transition Tiles", o4a_transition_tiles),
    ("5.a", "Connectors", o5a_connector_refs),
    ("9.a", "Consolidate Tileset", o9a_consolidate_tileset),
    ("9.b", "Consolidate Sample", o9b_consolidate_sample),
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


    op_id, op_name, handler = op
    gen_config = GeneratorConfig(image, drawable, config)

    if gen_config.is_quick:
        if not hasattr(handler, 'quick'):
            return gimp_error.calling(procedure, f"Handler {op_id}: {op_name} does not support quick mode.")

        fn = handler.quick
    else:
        fn = handler.handle

    image.undo_group_start()
    fn(gen_config)
    Gimp.displays_flush()
    image.undo_group_end()
    return gimp_error.success(procedure)
