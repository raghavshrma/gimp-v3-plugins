#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gimp", "3.0")

from gi.repository import Gimp
from gi.repository import GLib

error_prefix = "Procedure 'clip-cut-as-layer'"


def _gimp_error(procedure: Gimp.Procedure, status, message: str):
    return procedure.new_return_values(
        status,
        GLib.Error("%s: %s" % (error_prefix, message)),
    )


def calling(procedure: Gimp.Procedure, message: str):
    return _gimp_error(procedure, Gimp.PDBStatusType.CALLING_ERROR, message)


def execution(procedure: Gimp.Procedure, message: str):
    return _gimp_error(procedure, Gimp.PDBStatusType.EXECUTION_ERROR, message)


def success(procedure: Gimp.Procedure):
    return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, None)
