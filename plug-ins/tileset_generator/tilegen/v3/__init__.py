from types import ModuleType

from tilegen.v3 import (
    ga_l1a_edge_sample_ref, ga_l1b_edge_sample_export
)

NAME = "V1: Extended Top"

OPERATIONS: list[tuple[str, str, ModuleType]] = [
    ("A|1.a", "Edge Sample Ref", ga_l1a_edge_sample_ref),
    ("A|1.b", "Edge Sample Export", ga_l1b_edge_sample_export),
]
