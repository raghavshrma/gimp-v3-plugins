#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp, Gegl
import gimp_error

COLOR_DARK = "rgba(.1, .1, .15, 0.6)"
COLOR_LIGHT = "rgba(.9, .9, .9, 0.6)"
COLOR_NONE = "rgba(0, 0, 0, 0)"

# noinspection PyTypeChecker
OPTIONS: list[tuple[str, Gimp.GridStyle]] = [
    (COLOR_NONE, Gimp.GridStyle.INTERSECTIONS),
    (COLOR_DARK, Gimp.GridStyle.INTERSECTIONS),
    (COLOR_LIGHT, Gimp.GridStyle.INTERSECTIONS),
    (COLOR_DARK, Gimp.GridStyle.DOTS),
    (COLOR_LIGHT, Gimp.GridStyle.DOTS),
    (COLOR_DARK, Gimp.GridStyle.ON_OFF_DASH),
    (COLOR_LIGHT, Gimp.GridStyle.ON_OFF_DASH),
]

def run_any(
    procedure: Gimp.Procedure,
    run_mode: Gimp.RunMode,
    image: Gimp.Image,
    config: Gimp.ProcedureConfig,
    data,
):
    color = image.grid_get_foreground_color()
    r, _, _, a = color.get_rgba()

    # First time, it should start from 0
    grid_type: int = 0 if a == 1.0 else config.get_property("grid_type")
    grid_type += 1  # Increment to cycle through the options
    grid_type = grid_type % len(OPTIONS)
    config.set_property("grid_type", grid_type)

    color_str, style = OPTIONS[grid_type]

    color = Gegl.Color.new(color_str)
    image.grid_set_foreground_color(color)
    image.grid_set_style(style)

    return gimp_error.success(procedure)
