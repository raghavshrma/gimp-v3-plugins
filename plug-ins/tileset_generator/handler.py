#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

from tilegen.core import GeneratorConfig

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

from tilegen import v3

import gimp_error

MODULES = [
    # (v1_extended_top.NAME, v1_extended_top.OPERATIONS),
    ("V1: Extended Top", []),
    ("V2: Quick", []),
    (v3.NAME, v3.OPERATIONS),
    # ("V3: Tileset Generator", []),
    # (v3.NAME, v3.OPERATIONS),
]

def run_one(
        procedure: Gimp.Procedure,
        run_mode: Gimp.RunMode,
        image: Gimp.Image,
        drawable: Gimp.Layer,
        config: Gimp.ProcedureConfig,
        data,
):
    # module: int = config.get_property("module")
    module = 2
    operation: int = config.get_property("operation")
    if not (0 <= module < len(MODULES)):
        return gimp_error.calling(procedure, f"Invalid module index: {module}")

    module_name, operations = MODULES[module]

    if not (0 <= operation < len(operations)):
        return gimp_error.calling(procedure, f"Invalid operation index: {operation} for module {module_name}")

    op_id, op_name, handler = operations[operation]
    gen_config = GeneratorConfig(image, drawable, config)

    if gen_config.is_quick:
        if not hasattr(handler, 'quick'):
            return gimp_error.calling(procedure, f"Handler {op_id}: {op_name} does not support quick mode.")

        fn = handler.quick
    else:
        fn = handler.handle

    # Gimp.message(f"Running {module_name} operation: {op_name} (ID: {op_id}), fn: {fn.__name__}")

    image.undo_group_start()
    fn(gen_config)
    Gimp.displays_flush()
    image.undo_group_end()
    return gimp_error.success(procedure)
