"""The 2012 -> 2019 -> 2025 quantum-factoring cost frontier.

The companion :mod:`fteconomics.cost_model` reproduces the *2019* Gidney-Ekera
estimate (~20 million qubits, ~8 hours) from first principles. This module adds
the *2025* state of the art: Gidney's "How to factor 2048 bit RSA integers with
less than a million noisy qubits" (arXiv:2505.15917), which lowers the estimate
to under one million physical qubits (a ~20x reduction) under identical hardware
assumptions.

Rather than re-deriving the 2025 number with the simplified uniform-patch model
used for 2019, the headline is reconstructed here from the *components* reported
in the paper -- cold (yoked) storage, hot storage and the compute/factory region
-- so the ~900k total is traceable to its sources. The module also attributes the
reduction to its three enabling techniques and exposes the historical frontier
for plotting.

References
----------
Gidney C. How to factor 2048 bit RSA integers with less than a million noisy
qubits. arXiv:2505.15917, 2025.
Gidney C, Ekera M. How to factor 2048 bit RSA integers in 8 hours using 20
million noisy qubits. Quantum 2021; 5:433.
Chevignard C, Fouque P-A, Schrottenloher A. Reducing the Number of Qubits in
Quantum Factoring. Cryptology ePrint Archive, Paper 2024/222, 2024.
Gidney C, Newman M, Brooks P, Jones C. Yoked surface codes. Nature
Communications 2025.
Gidney C, Shutty N, Jones C. Magic state cultivation: growing T states as cheap
as CNOT gates. arXiv:2409.17595, 2024.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

# --- Gidney 2025 (arXiv:2505.15917), the n = 2048 layout (Section 3.4) --------
# Every constant below is reported in the paper for the n=2048, s=8 parameter row.
_COLD_LOGICAL_QUBITS = 1280  # m input qubits held in cold storage
_COLD_DENSITY = 430  # physical qubits per logical qubit, yoked 2D parity-check code
_HOT_LOGICAL_QUBITS = 131  # 3f + 2l + len(m) active patches in hot storage
_HOT_DENSITY = 1352  # 2*(d+1)^2 with hot distance d = 25
_COMPUTE_PATCHES = 126  # 7x18 region: six 3x4 cultivation factories + workspace
_HOT_DISTANCE = 25

GIDNEY_2025_TOFFOLI_COUNT = 6.5e9
GIDNEY_2025_MAX_ACTIVE_LOGICAL = 1409  # max simultaneously-active logical qubits
GIDNEY_2025_RUNTIME_HOURS = 12.07 * 9.1 / 0.933  # ~12 h/shot, 9.1 shots, 93.3% no-error


class PhysicalBreakdown(BaseModel):
    """Component-wise reconstruction of a physical-qubit total."""

    model_config = {"frozen": True}

    cold_storage_qubits: int
    hot_storage_qubits: int
    compute_region_qubits: int

    @property
    def total(self) -> int:
        return self.cold_storage_qubits + self.hot_storage_qubits + self.compute_region_qubits


class PublishedEstimate(BaseModel):
    """A published physical-cost estimate for factoring RSA-2048."""

    model_config = {"frozen": True}

    year: int
    label: str
    physical_qubits: float = Field(..., gt=0)
    runtime_hours: float | None = None
    logical_qubits: int | None = None
    toffoli_count: float | None = None
    citation: str


def gidney2025_breakdown() -> PhysicalBreakdown:
    """Reconstruct the ~898k-qubit 2025 estimate from its reported components.

    cold storage : 1280 logical x 430 phys = 550,400
    hot storage  : 131 logical x 1352 phys = 177,112
    compute      : 126 hot patches x 1352  = 170,352
    total        : 897,864  (the paper rounds up to 1,000,000 for slack)
    """
    return PhysicalBreakdown(
        cold_storage_qubits=_COLD_LOGICAL_QUBITS * _COLD_DENSITY,
        hot_storage_qubits=_HOT_LOGICAL_QUBITS * _HOT_DENSITY,
        compute_region_qubits=_COMPUTE_PATCHES * _HOT_DENSITY,
    )


# --- Historical frontier (Figure 1 of arXiv:2505.15917) -----------------------
HISTORICAL_ESTIMATES: tuple[PublishedEstimate, ...] = (
    PublishedEstimate(
        year=2012,
        label="Fowler et al. / Jones et al. (2012)",
        physical_qubits=1.0e9,
        citation="Fowler AG, Mariantoni M, Martinis JM, Cleland AN. Physical Review A 2012; 86:032324.",
    ),
    PublishedEstimate(
        year=2019,
        label="Gidney & Ekera (2019/2021)",
        physical_qubits=2.0e7,
        runtime_hours=8.0,
        logical_qubits=6200,
        toffoli_count=3.0e9,
        citation="Gidney C, Ekera M. Quantum 2021; 5:433.",
    ),
    PublishedEstimate(
        year=2025,
        label="Gidney (2025)",
        physical_qubits=1.0e6,
        runtime_hours=GIDNEY_2025_RUNTIME_HOURS,
        logical_qubits=GIDNEY_2025_MAX_ACTIVE_LOGICAL,
        toffoli_count=GIDNEY_2025_TOFFOLI_COUNT,
        citation="Gidney C. arXiv:2505.15917, 2025.",
    ),
)


class ReductionLever(BaseModel):
    """One technique contributing to the 2019 -> 2025 reduction."""

    model_config = {"frozen": True}

    name: str
    effect: str
    citation: str


REDUCTION_LEVERS: tuple[ReductionLever, ...] = (
    ReductionLever(
        name="Approximate residue arithmetic",
        effect=(
            "Cuts the logical-qubit count from a bit more than 3n to about 0.5n "
            "(~6200 -> ~1400 for n=2048) by computing approximate modular "
            "exponentiations with small intermediate values."
        ),
        citation="Chevignard, Fouque, Schrottenloher. Cryptology ePrint 2024/222, 2024.",
    ),
    ReductionLever(
        name="Yoked surface codes",
        effect=(
            "Stores idle logical qubits ~3x more densely (430 vs 1352 physical "
            "qubits per logical qubit) by concatenating surface-code patches "
            "below a 2D parity-check code in 'cold storage'."
        ),
        citation="Gidney, Newman, Brooks, Jones. Nature Communications 2025.",
    ),
    ReductionLever(
        name="Magic state cultivation",
        effect=(
            "Replaces the first distillation stage, shrinking each factory from a "
            "15x8 to a 3x4 patch footprint and freeing most of the area the 2019 "
            "layout spent on distillation."
        ),
        citation="Gidney, Shutty, Jones. arXiv:2409.17595, 2024.",
    ),
)


def qubit_reduction_factor() -> float:
    """Factor by which the 2025 estimate lowers the 2019 physical-qubit count."""
    by_year = {e.year: e for e in HISTORICAL_ESTIMATES}
    return by_year[2019].physical_qubits / by_year[2025].physical_qubits


def spacetime_volume(physical_qubits: float, runtime_hours: float) -> float:
    """Physical qubit-hours: a single-number space-time cost for comparison."""
    return physical_qubits * runtime_hours
