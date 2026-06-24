"""Quantitative resource and cost modelling for fault-tolerant quantum computing."""

from .algorithm_cost import SHOR_RSA_2048, AlgorithmSpec
from .cost_model import ResourceEstimate, estimate_resources, sensitivity_sweep
from .frontier import (
    HISTORICAL_ESTIMATES,
    REDUCTION_LEVERS,
    PhysicalBreakdown,
    PublishedEstimate,
    ReductionLever,
    gidney2025_breakdown,
    qubit_reduction_factor,
    spacetime_volume,
)
from .hardware_profiles import DEFAULT_PROFILES, HardwareProfile
from .qec_overhead import (
    logical_error_per_cycle,
    physical_qubits_per_patch,
    required_distance,
)
from .report import build_report, write_report

__version__ = "0.1.0"

__all__ = [
    "DEFAULT_PROFILES",
    "HISTORICAL_ESTIMATES",
    "REDUCTION_LEVERS",
    "SHOR_RSA_2048",
    "AlgorithmSpec",
    "HardwareProfile",
    "PhysicalBreakdown",
    "PublishedEstimate",
    "ReductionLever",
    "ResourceEstimate",
    "build_report",
    "estimate_resources",
    "gidney2025_breakdown",
    "logical_error_per_cycle",
    "physical_qubits_per_patch",
    "qubit_reduction_factor",
    "required_distance",
    "sensitivity_sweep",
    "spacetime_volume",
    "write_report",
]
