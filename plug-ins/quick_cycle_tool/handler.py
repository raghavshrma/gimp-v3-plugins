#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp
import gimp_error

def run_any(
        procedure: Gimp.Procedure,
        run_mode: Gimp.RunMode,
        image: Gimp.Image,
        config: Gimp.ProcedureConfig,
        data):

    # index = config.get_property("index")
    # Gimp.message(f"Index: {index}")
    # config.set_property("index", index + 1)

    Gimp.message("Can't change active tool through script")
    return gimp_error.success(procedure)
