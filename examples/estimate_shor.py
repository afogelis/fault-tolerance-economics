"""Generate the Shor / RSA-2048 report and the sensitivity plot.

python examples/estimate_shor.py
"""

from __future__ import annotations

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from fteconomics import DEFAULT_PROFILES, SHOR_RSA_2048, estimate_resources, write_report
from fteconomics.viz import plot_sensitivity


def main() -> None:
    os.makedirs("outputs", exist_ok=True)

    estimate = write_report("reports/shor-rsa2048-resource-estimate.md")
    print(
        f"baseline: {estimate.total_physical_qubits:,} physical qubits, "
        f"d={estimate.code_distance}, {estimate.runtime_hours:.1f} hours"
    )

    for name, profile in DEFAULT_PROFILES.items():
        est = estimate_resources(SHOR_RSA_2048, profile)
        print(
            f"  {name:<13} {est.total_physical_qubits / 1e6:6.1f}M qubits  "
            f"d={est.code_distance:<3} {est.runtime_hours:5.1f} h"
        )

    ax = plot_sensitivity(SHOR_RSA_2048, DEFAULT_PROFILES["baseline"])
    ax.figure.tight_layout()
    ax.figure.savefig("outputs/sensitivity.png", dpi=150)
    plt.close(ax.figure)
    print("saved reports/shor-rsa2048-resource-estimate.md and outputs/sensitivity.png")


if __name__ == "__main__":
    main()
