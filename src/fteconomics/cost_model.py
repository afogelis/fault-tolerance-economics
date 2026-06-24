"""Combine algorithm, hardware and overhead into a full resource estimate.

The estimate proceeds in three steps:

1. Spread a total error budget across every logical tile and every logical
   cycle to obtain a per-cycle error target.
2. Solve the surface-code suppression law for the smallest distance meeting it.
3. Multiply the per-patch qubit count by the number of tiles for the physical
   footprint, and the Toffoli count by a per-Toffoli time for the runtime.

Two parameters are calibrated so that the superconducting baseline reproduces
the headline result of Gidney & Ekera (2021): ``toffoli_cycle_factor`` (giving
roughly 8 hours) and the default error budget / tile multiplier (giving roughly
20 million qubits). Both are exposed so the sensitivity analysis can vary them.
"""

from __future__ import annotations

from pydantic import BaseModel

from .algorithm_cost import AlgorithmSpec
from .hardware_profiles import HardwareProfile
from .qec_overhead import physical_qubits_per_patch, required_distance


class ResourceEstimate(BaseModel):
    """The output of a resource estimation run."""

    model_config = {"frozen": True}

    algorithm: str
    hardware: str
    code_distance: int
    physical_qubits_per_patch: int
    logical_tiles: float
    total_physical_qubits: int
    total_logical_cycles: float
    runtime_seconds: float
    runtime_hours: float
    cost_usd: float


def estimate_resources(
    algorithm: AlgorithmSpec,
    hardware: HardwareProfile,
    *,
    target_total_error: float = 0.01,
    cycles_per_toffoli: float = 1.0,
    toffoli_cycle_factor: float = 10.0,
    prefactor: float = 0.1,
) -> ResourceEstimate:
    """Estimate physical qubits, runtime and cost for ``algorithm`` on ``hardware``."""
    if not 0.0 < target_total_error < 1.0:
        raise ValueError("target_total_error must be in (0, 1)")

    logical_tiles = algorithm.total_logical_tiles()
    total_logical_cycles = algorithm.toffoli_count * cycles_per_toffoli
    target_per_cycle = target_total_error / (logical_tiles * total_logical_cycles)

    distance = required_distance(
        target_per_cycle,
        hardware.physical_error_rate,
        threshold=hardware.code_threshold,
        prefactor=prefactor,
    )
    per_patch = physical_qubits_per_patch(distance)
    total_physical_qubits = int(round(logical_tiles * per_patch))

    seconds_per_toffoli = toffoli_cycle_factor * hardware.cycle_time_ns * 1e-9
    runtime_seconds = algorithm.toffoli_count * seconds_per_toffoli
    runtime_hours = runtime_seconds / 3600.0

    qubit_hours = total_physical_qubits * runtime_hours
    cost_usd = qubit_hours * hardware.usd_per_physical_qubit_hour

    return ResourceEstimate(
        algorithm=algorithm.name,
        hardware=hardware.name,
        code_distance=distance,
        physical_qubits_per_patch=per_patch,
        logical_tiles=logical_tiles,
        total_physical_qubits=total_physical_qubits,
        total_logical_cycles=total_logical_cycles,
        runtime_seconds=runtime_seconds,
        runtime_hours=runtime_hours,
        cost_usd=cost_usd,
    )


def sensitivity_sweep(
    algorithm: AlgorithmSpec,
    hardware: HardwareProfile,
    *,
    parameter: str,
    multipliers: tuple[float, ...] = (0.5, 0.75, 1.0, 1.5, 2.0),
) -> list[tuple[float, ResourceEstimate]]:
    """Vary one hardware parameter by ``multipliers`` and re-estimate.

    Supported parameters: ``physical_error_rate``, ``cycle_time_ns``,
    ``code_threshold``. Returns ``(multiplier, estimate)`` pairs.
    """
    if parameter not in {"physical_error_rate", "cycle_time_ns", "code_threshold"}:
        raise ValueError(f"unsupported sensitivity parameter: {parameter}")

    results: list[tuple[float, ResourceEstimate]] = []
    base_value = getattr(hardware, parameter)
    for multiplier in multipliers:
        updated = hardware.model_copy(update={parameter: base_value * multiplier})
        try:
            estimate = estimate_resources(algorithm, updated)
        except ValueError:
            continue  # e.g. error rate pushed at/above threshold
        results.append((multiplier, estimate))
    return results
