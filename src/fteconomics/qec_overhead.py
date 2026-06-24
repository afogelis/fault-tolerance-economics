"""Surface-code overhead: distance selection and physical-qubit footprint.

The model uses the standard heuristic for the suppression of logical errors by
a distance-``d`` surface code (Fowler, Mariantoni, Martinis & Cleland, 2012):

    p_L(d) ~ A * (p / p_th) ** ((d + 1) / 2)

with prefactor ``A`` of order 0.1 and threshold ``p_th`` of order 1%. Given a
per-logical-qubit, per-cycle error budget we solve for the smallest odd
distance that meets it. A rotated surface-code patch uses ``2 d**2 - 1``
physical qubits (``d**2`` data qubits and ``d**2 - 1`` measure qubits).
"""

from __future__ import annotations

import math


def logical_error_per_cycle(
    distance: int, physical_error_rate: float, *, threshold: float = 0.01, prefactor: float = 0.1
) -> float:
    """Return the heuristic logical error rate per cycle for one patch."""
    if distance < 1:
        raise ValueError("distance must be >= 1")
    ratio = physical_error_rate / threshold
    return prefactor * ratio ** ((distance + 1) / 2.0)


def required_distance(
    target_error_per_cycle: float,
    physical_error_rate: float,
    *,
    threshold: float = 0.01,
    prefactor: float = 0.1,
    max_distance: int = 101,
) -> int:
    """Smallest odd distance whose per-cycle logical error meets the target.

    Guard clauses reject a physical rate at or above threshold (where no finite
    distance helps) and non-positive targets.
    """
    if physical_error_rate >= threshold:
        raise ValueError("physical error rate is at or above threshold; no distance suffices")
    if target_error_per_cycle <= 0.0:
        raise ValueError("target_error_per_cycle must be positive")

    for distance in range(3, max_distance + 1, 2):
        if (
            logical_error_per_cycle(
                distance, physical_error_rate, threshold=threshold, prefactor=prefactor
            )
            <= target_error_per_cycle
        ):
            return distance
    raise ValueError(f"no distance <= {max_distance} meets the target error budget")


def physical_qubits_per_patch(distance: int) -> int:
    """Physical qubits in one rotated surface-code patch: ``2 d**2 - 1``."""
    if distance < 1:
        raise ValueError("distance must be >= 1")
    return 2 * distance * distance - 1


def analytic_distance(
    target_error_per_cycle: float,
    physical_error_rate: float,
    *,
    threshold: float = 0.01,
    prefactor: float = 0.1,
) -> float:
    """Continuous (non-rounded) distance from inverting the suppression law.

    Useful for sensitivity analysis where a smooth response is preferable to the
    step function produced by rounding up to the next odd integer.
    """
    ratio = physical_error_rate / threshold
    if ratio <= 0.0 or ratio >= 1.0:
        return math.inf
    return 2.0 * math.log(target_error_per_cycle / prefactor) / math.log(ratio) - 1.0
