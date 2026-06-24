"""Hardware profiles for fault-tolerant resource estimation.

Each profile captures the few physical parameters that dominate surface-code
overhead: the physical (per-operation) error rate, the surface-code cycle time,
and the assumed code threshold. Values are drawn from public roadmaps and
papers and are deliberately conservative ranges, not vendor guarantees; every
figure is a modelling assumption and is cited in the technical report.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class HardwareProfile(BaseModel):
    """A named set of physical-layer assumptions."""

    model_config = {"frozen": True}

    name: str
    physical_error_rate: float = Field(
        ..., gt=0.0, lt=0.5, description="Per-operation error rate p."
    )
    cycle_time_ns: float = Field(..., gt=0.0, description="Time for one surface-code round (ns).")
    code_threshold: float = Field(
        default=0.01, gt=0.0, lt=0.5, description="Assumed threshold p_th."
    )
    usd_per_physical_qubit_hour: float = Field(
        default=0.0, ge=0.0, description="Optional cost assumption ($ per physical qubit-hour)."
    )


# Representative profiles. The error rates and cycle times are order-of-magnitude
# figures from public statements and the QEC literature (see report references),
# chosen to bracket near-term superconducting hardware. They are assumptions.
SUPERCONDUCTING_BASELINE = HardwareProfile(
    name="Superconducting (Gidney-Ekera baseline)",
    physical_error_rate=1e-3,
    cycle_time_ns=1000.0,
    code_threshold=0.01,
    usd_per_physical_qubit_hour=0.0,
)

SUPERCONDUCTING_OPTIMISTIC = HardwareProfile(
    name="Superconducting (optimistic)",
    physical_error_rate=3e-4,
    cycle_time_ns=500.0,
    code_threshold=0.01,
)

SUPERCONDUCTING_CONSERVATIVE = HardwareProfile(
    name="Superconducting (conservative)",
    physical_error_rate=3e-3,
    cycle_time_ns=1000.0,
    code_threshold=0.01,
)

DEFAULT_PROFILES: dict[str, HardwareProfile] = {
    "baseline": SUPERCONDUCTING_BASELINE,
    "optimistic": SUPERCONDUCTING_OPTIMISTIC,
    "conservative": SUPERCONDUCTING_CONSERVATIVE,
}
