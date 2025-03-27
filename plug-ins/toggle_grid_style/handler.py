#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp, Gegl
import gimp_error

COLOR_DARK = "rgba(.1, .1, .15, 0.6)"
COLOR_LIGHT = "rgba(.9, .9, .9, 0.6)"
COLOR_NONE = "rgba(0, 0, 0, 0)"


def run_any(
    procedure: Gimp.Procedure,
    run_mode: Gimp.RunMode,
    image: Gimp.Image,
    config: Gimp.ProcedureConfig,
    data,
):
    """
    - If the grid is invisible
        - Set: [Color: Light, Style: 0, Visible: True]
    - If the grid is visible:
        - If Color: Light
            - Set: [Color: Dark]
        - If Color: Dark
            - If Style >= 2
                - Set: [Visible: False]
            - Otherwise:
                - Set: [Color: Light, Style: Style + 1]
    """

    style = image.grid_get_style()
    color = image.grid_get_foreground_color()
    r, _, _, a = color.get_rgba()

    if a < 0.5:  # Invisible
        color_str = COLOR_LIGHT
        style = Gimp.GridStyle.DOTS
    elif r > 0.5:  # Color: Light
        color_str = COLOR_DARK
    else:  # Color: Dark
        color_str = COLOR_LIGHT
        match style:
            case Gimp.GridStyle.DOTS:
                style = Gimp.GridStyle.INTERSECTIONS
            case Gimp.GridStyle.INTERSECTIONS:
                style = Gimp.GridStyle.ON_OFF_DASH
            case _:
                color_str = COLOR_NONE

    image.grid_set_foreground_color(Gegl.Color.new(color_str))
    image.grid_set_style(style)

    return gimp_error.success(procedure)
