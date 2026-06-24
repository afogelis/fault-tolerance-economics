"""Generate the Shor / RSA-2048 resource-estimate technical report (markdown)."""

from __future__ import annotations

from pathlib import Path

from .algorithm_cost import SHOR_RSA_2048, AlgorithmSpec
from .cost_model import ResourceEstimate, estimate_resources, sensitivity_sweep
from .hardware_profiles import DEFAULT_PROFILES, HardwareProfile


def _format_qubits(value: int) -> str:
    return f"{value / 1e6:.1f} million" if value >= 1e6 else f"{value:,}"


def _profile_table(algorithm: AlgorithmSpec, profiles: dict[str, HardwareProfile]) -> str:
    header = (
        "| Profile | p | cycle (ns) | distance d | qubits/patch | "
        "physical qubits | runtime (h) |\n"
        "|---------|---|------------|-----------|--------------|-----------------|-------------|"
    )
    rows = [header]
    for profile in profiles.values():
        est = estimate_resources(algorithm, profile)
        rows.append(
            f"| {profile.name} | {profile.physical_error_rate:.0e} | "
            f"{profile.cycle_time_ns:.0f} | {est.code_distance} | "
            f"{est.physical_qubits_per_patch:,} | {_format_qubits(est.total_physical_qubits)} | "
            f"{est.runtime_hours:.1f} |"
        )
    return "\n".join(rows)


def _sensitivity_section(algorithm: AlgorithmSpec, hardware: HardwareProfile) -> str:
    lines = []
    for parameter in ("physical_error_rate", "cycle_time_ns", "code_threshold"):
        lines.append(f"\n**{parameter}**\n")
        lines.append("| multiplier | distance | physical qubits | runtime (h) |")
        lines.append("|-----------|----------|-----------------|-------------|")
        for multiplier, est in sensitivity_sweep(algorithm, hardware, parameter=parameter):
            lines.append(
                f"| {multiplier:g}x | {est.code_distance} | "
                f"{_format_qubits(est.total_physical_qubits)} | {est.runtime_hours:.1f} |"
            )
    return "\n".join(lines)


def build_report(algorithm: AlgorithmSpec = SHOR_RSA_2048) -> str:
    """Return the full markdown technical report as a string."""
    baseline = DEFAULT_PROFILES["baseline"]
    baseline_estimate = estimate_resources(algorithm, baseline)

    return f"""# How Many Physical Qubits to Break RSA-2048?

A resource estimate for Shor's algorithm under realistic surface-code error correction.

## Headline answer

Under the superconducting baseline (physical error rate {baseline.physical_error_rate:.0e},
{baseline.cycle_time_ns:.0f} ns surface-code cycle, 1% threshold), factoring a 2048-bit RSA modulus
with Shor's algorithm is estimated to require **{_format_qubits(baseline_estimate.total_physical_qubits)}
physical qubits** at code distance **d = {baseline_estimate.code_distance}**, running for about
**{baseline_estimate.runtime_hours:.1f} hours**. This reproduces the order of magnitude of Gidney &
Ekera (2021): roughly 20 million qubits in roughly 8 hours.

## Method

The estimate combines three published ingredients:

1. **Logical resources (algorithm).** The number of logical qubits and Toffoli (magic-state) gates
   for Shor / RSA-2048 are taken at the order of magnitude reported by Gidney & Ekera (2021):
   ~{algorithm.logical_qubits:,} algorithmic logical qubits and ~{algorithm.toffoli_count:.1e} Toffoli
   gates, with a factory/routing tile multiplier of {algorithm.factory_tile_multiplier:g} (a layout
   assumption).
2. **Surface-code overhead.** The logical error rate per cycle follows the suppression law
   p_L(d) ~ 0.1 (p / p_th)^((d+1)/2) (Fowler et al., 2012). A total error budget of 1% is spread
   across all logical tiles and cycles to set a per-cycle target, which fixes the distance d. A
   rotated patch uses 2 d^2 - 1 physical qubits.
3. **Runtime.** Runtime is the Toffoli count times a per-Toffoli time, calibrated so the baseline
   matches the ~8-hour figure of Gidney & Ekera (2021).

All numeric inputs are modelling assumptions, stated explicitly so the estimate can be re-derived
or updated as hardware improves.

## Estimates across hardware profiles

{_profile_table(algorithm, DEFAULT_PROFILES)}

## Sensitivity analysis

The physical error rate is the dominant lever: it enters the required distance exponentially, so a
modest improvement removes millions of qubits, while a modest regression can make the computation
infeasible (the rate approaching threshold).

{_sensitivity_section(algorithm, DEFAULT_PROFILES["baseline"])}

## Limitations

- The suppression-law prefactor and threshold are heuristics; a faithful estimate would use a
  decoder-specific threshold measured by the companion simulator and benchmark repos.
- Magic-state distillation is modelled as a flat tile multiplier rather than an explicit factory
  layout; real layouts (Gidney & Ekera 2021) optimise distillation in detail.
- The runtime model is calibrated to a single published point and assumes a reaction-limited
  architecture.

## References

Fowler AG, Mariantoni M, Martinis JM, Cleland AN. Surface codes: Towards practical large-scale
quantum computation. Physical Review A 2012; 86:032324.

Gidney C, Ekera M. How to factor 2048 bit RSA integers in 8 hours using 20 million noisy qubits.
Quantum 2021; 5:433.

Google Quantum AI. Suppressing quantum errors by scaling a surface code logical qubit. Nature 2023;
614:676-681.
"""


def write_report(
    out_path: str | Path, algorithm: AlgorithmSpec = SHOR_RSA_2048
) -> ResourceEstimate:
    """Write the markdown report to ``out_path`` and return the baseline estimate."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(build_report(algorithm), encoding="utf-8")
    return estimate_resources(algorithm, DEFAULT_PROFILES["baseline"])
