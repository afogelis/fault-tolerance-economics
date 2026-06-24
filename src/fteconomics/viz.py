"""Sensitivity visualisation for resource estimates."""

from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib.axes import Axes

from .algorithm_cost import AlgorithmSpec
from .cost_model import sensitivity_sweep
from .frontier import HISTORICAL_ESTIMATES, PublishedEstimate
from .hardware_profiles import HardwareProfile


def plot_sensitivity(
    algorithm: AlgorithmSpec,
    hardware: HardwareProfile,
    *,
    parameters: tuple[str, ...] = ("physical_error_rate", "cycle_time_ns", "code_threshold"),
    ax: Axes | None = None,
) -> Axes:
    """Plot total physical qubits vs relative change in each hardware parameter.

    A steep curve means the physical-qubit count is highly sensitive to that
    parameter -- the physical error rate is typically the dominant lever because
    it enters the distance requirement exponentially.
    """
    if ax is None:
        _, ax = plt.subplots(figsize=(7, 5))

    for parameter in parameters:
        sweep = sensitivity_sweep(algorithm, hardware, parameter=parameter)
        multipliers = [m for m, _ in sweep]
        qubits = [estimate.total_physical_qubits for _, estimate in sweep]
        ax.plot(multipliers, qubits, marker="o", label=parameter)

    ax.set_yscale("log")
    ax.set_xlabel("Parameter multiplier (relative to baseline)")
    ax.set_ylabel("Total physical qubits")
    ax.set_title("Resource sensitivity to hardware parameters")
    ax.legend()
    ax.grid(True, which="both", alpha=0.3)
    return ax


def plot_qubit_frontier(
    estimates: tuple[PublishedEstimate, ...] = HISTORICAL_ESTIMATES,
    *,
    ax: Axes | None = None,
) -> Axes:
    """Plot the historical physical-qubit cost of factoring RSA-2048 over time.

    The y-axis is logarithmic because successive estimates have fallen by orders
    of magnitude: ~1 billion qubits (2012), ~20 million (2019), ~1 million (2025).
    """
    if ax is None:
        _, ax = plt.subplots(figsize=(7, 5))

    years = [e.year for e in estimates]
    qubits = [e.physical_qubits for e in estimates]
    ax.plot(years, qubits, marker="o", color="#c0392b", linewidth=2)

    for est in estimates:
        ax.annotate(
            f"{est.physical_qubits:.0e}\n{est.label}",
            (est.year, est.physical_qubits),
            textcoords="offset points",
            xytext=(8, 6),
            fontsize=8,
        )

    ax.set_yscale("log")
    ax.set_xlabel("Year of estimate")
    ax.set_ylabel("Physical qubits to factor RSA-2048")
    ax.set_title("Falling cost of quantum factoring (comparable assumptions)")
    ax.grid(True, which="both", alpha=0.3)
    ax.margins(x=0.18)
    return ax
