import pytest

from fteconomics import (
    DEFAULT_PROFILES,
    SHOR_RSA_2048,
    estimate_resources,
    logical_error_per_cycle,
    physical_qubits_per_patch,
    required_distance,
    sensitivity_sweep,
)


def test_logical_error_decreases_with_distance_below_threshold():
    p = 1e-3
    low = logical_error_per_cycle(5, p)
    high = logical_error_per_cycle(11, p)
    assert high < low


def test_required_distance_is_odd_and_meets_target():
    d = required_distance(1e-12, 1e-3)
    assert d % 2 == 1
    assert logical_error_per_cycle(d, 1e-3) <= 1e-12


def test_required_distance_rejects_above_threshold():
    with pytest.raises(ValueError):
        required_distance(1e-12, 0.02, threshold=0.01)


def test_patch_qubit_count():
    assert physical_qubits_per_patch(3) == 17
    assert physical_qubits_per_patch(5) == 49


def test_baseline_reproduces_gidney_ekera_order_of_magnitude():
    estimate = estimate_resources(SHOR_RSA_2048, DEFAULT_PROFILES["baseline"])
    # Gidney & Ekera (2021): ~20 million qubits, ~8 hours.
    assert 5e6 <= estimate.total_physical_qubits <= 5e7
    assert 2.0 <= estimate.runtime_hours <= 40.0
    assert 20 <= estimate.code_distance <= 35


def test_lower_error_rate_reduces_qubits():
    baseline = estimate_resources(SHOR_RSA_2048, DEFAULT_PROFILES["baseline"])
    optimistic = estimate_resources(SHOR_RSA_2048, DEFAULT_PROFILES["optimistic"])
    assert optimistic.total_physical_qubits < baseline.total_physical_qubits


def test_sensitivity_sweep_returns_points():
    sweep = sensitivity_sweep(
        SHOR_RSA_2048, DEFAULT_PROFILES["baseline"], parameter="cycle_time_ns"
    )
    assert len(sweep) >= 3
    # Halving the cycle time should roughly halve the runtime.
    runtimes = {m: est.runtime_hours for m, est in sweep}
    assert runtimes[0.5] < runtimes[1.0] < runtimes[2.0]
