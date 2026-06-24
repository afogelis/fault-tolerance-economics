from fteconomics import (
    HISTORICAL_ESTIMATES,
    REDUCTION_LEVERS,
    gidney2025_breakdown,
    qubit_reduction_factor,
    spacetime_volume,
)


def test_gidney2025_breakdown_reconstructs_headline():
    bd = gidney2025_breakdown()
    # Paper's component figures: 550,400 + 177,112 + 170,352 = 897,864.
    assert bd.cold_storage_qubits == 550_400
    assert bd.hot_storage_qubits == 177_112
    assert bd.compute_region_qubits == 170_352
    assert bd.total == 897_864
    # Under the one-million-qubit headline (rounded up for slack in the paper).
    assert bd.total < 1_000_000


def test_reduction_factor_is_about_twentyfold():
    factor = qubit_reduction_factor()
    assert 15 <= factor <= 25


def test_frontier_qubit_count_falls_monotonically_over_time():
    ordered = sorted(HISTORICAL_ESTIMATES, key=lambda e: e.year)
    qubits = [e.physical_qubits for e in ordered]
    assert qubits == sorted(qubits, reverse=True)


def test_2025_uses_fewer_logical_qubits_than_2019():
    by_year = {e.year: e for e in HISTORICAL_ESTIMATES}
    assert by_year[2025].logical_qubits < by_year[2019].logical_qubits


def test_2025_trades_space_for_time():
    by_year = {e.year: e for e in HISTORICAL_ESTIMATES}
    # Fewer qubits but a longer runtime than 2019 (a deliberate space-for-time trade).
    assert by_year[2025].physical_qubits < by_year[2019].physical_qubits
    assert by_year[2025].runtime_hours > by_year[2019].runtime_hours


def test_three_reduction_levers_documented():
    names = {lever.name for lever in REDUCTION_LEVERS}
    assert len(names) == 3


def test_spacetime_volume_positive():
    assert spacetime_volume(1e6, 120.0) == 1.2e8
