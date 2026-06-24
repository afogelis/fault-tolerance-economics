"""Quantitative resource and cost modelling for fault-tolerant quantum computing."""

from .algorithm_cost import SHOR_RSA_2048, AlgorithmSpec
from .cost_model import ResourceEstimate, estimate_resources, sensitivity_sweep
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
    "SHOR_RSA_2048",
    "AlgorithmSpec",
    "HardwareProfile",
    "ResourceEstimate",
    "build_report",
    "estimate_resources",
    "logical_error_per_cycle",
    "physical_qubits_per_patch",
    "required_distance",
    "sensitivity_sweep",
    "write_report",
]
