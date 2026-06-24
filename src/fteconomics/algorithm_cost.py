"""Logical-level resource specification for target algorithms.

These are the algorithm-level (hardware-independent) costs: how many logical
qubits the computation occupies and how many non-Clifford (Toffoli/T) gates it
executes. For Shor's algorithm factoring a 2048-bit RSA modulus we use the
estimates of Gidney & Ekera (2021), "How to factor 2048 bit RSA integers in 8
hours using 20 million noisy qubits" (Quantum 5, 433). Their headline result --
about 20 million physical qubits and roughly 8 hours at a 10^-3 physical error
rate -- is the validation target for the cost model in :mod:`fteconomics.cost_model`.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class AlgorithmSpec(BaseModel):
    """Hardware-independent logical resource requirements of an algorithm."""

    model_config = {"frozen": True}

    name: str
    problem_size_bits: int = Field(..., gt=0)
    logical_qubits: int = Field(
        ..., gt=0, description="Algorithmic (data + routing) logical qubits."
    )
    toffoli_count: float = Field(
        ..., gt=0, description="Number of Toffoli (equiv. magic-state) gates."
    )
    # Tile multiplier accounting for magic-state factories and routing space that
    # surround the data qubits in a real layout. Gidney-Ekera-style layouts spend
    # a large fraction of the footprint on distillation; ~2x of the data tiles is
    # a common rule of thumb (modelling assumption, see report).
    factory_tile_multiplier: float = Field(default=2.0, ge=1.0)

    def total_logical_tiles(self) -> float:
        """Logical patches including magic-state factory and routing overhead."""
        return self.logical_qubits * self.factory_tile_multiplier


# Shor / RSA-2048. Logical-qubit and Toffoli figures are taken at the order of
# magnitude reported by Gidney & Ekera (2021); see the report for the exact
# citation and caveats. They are inputs to the model, not outputs of it.
SHOR_RSA_2048 = AlgorithmSpec(
    name="Shor RSA-2048",
    problem_size_bits=2048,
    logical_qubits=6_200,
    toffoli_count=2.7e9,
    factory_tile_multiplier=2.2,
)
