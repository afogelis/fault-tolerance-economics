# Fault-Tolerance Economics

A transparent resource and cost model for fault-tolerant quantum computing. Given a hardware
profile (physical error rate, surface-code cycle time, threshold) and an algorithm's logical
requirements, it estimates the **physical qubits**, **runtime** and **cost** needed to run the
computation under realistic error-correction overhead.

The headline application answers a concrete strategic question:

> **How many physical qubits are needed to run Shor's algorithm on RSA-2048 under realistic error
> assumptions?**

This is repo 5 of a seven-part [QEC research portfolio](https://github.com/afogelis/qec-portfolio).

## What this demonstrates

- **Quantitative modelling and forecasting:** propagating physical assumptions through the surface-code suppression law to a physical-qubit and runtime budget.
- **Sensitivity / scenario analysis:** identifying which hardware parameter (the physical error rate) dominates the cost, and by how much.
- **Strategy translation:** turning a physics result into a decision-ready estimate with explicit assumptions and citations - the kind of analysis a research-operations or TPM role values.

## Headline result

Calibrated to reproduce Gidney & Ekera (2021), the baseline superconducting profile
(p = 1e-3, 1 us cycle, 1% threshold) yields roughly **20 million physical qubits** at code distance
**d ~ 27-29**, running for about **8 hours**. See
[`reports/shor-rsa2048-resource-estimate.md`](reports/shor-rsa2048-resource-estimate.md) for the
full report, profile comparison and sensitivity tables.

![Sensitivity of the physical-qubit estimate to each input assumption (tornado chart).](docs/sensitivity.png)

*Sensitivity of the physical-qubit budget to each modelling assumption. The physical error rate dominates because it enters the required code distance exponentially.*

## Install and run

```bash
pip install -e ".[dev]"
pytest
python examples/estimate_shor.py     # writes the report + outputs/sensitivity.png
```

```bash
fteconomics estimate --profile baseline
fteconomics report --output reports/shor-rsa2048-resource-estimate.md
```

## Model in brief

1. **Logical resources** (Gidney & Ekera 2021): algorithmic logical qubits and Toffoli count for Shor / RSA-2048, plus a factory/routing tile multiplier.
2. **Surface-code overhead** (Fowler et al. 2012): `p_L(d) ~ 0.1 (p / p_th)^((d+1)/2)`; a total error budget fixes the distance, and a rotated patch uses `2 d^2 - 1` physical qubits.
3. **Runtime**: Toffoli count times a per-Toffoli time, calibrated so the baseline matches the published ~8-hour figure.

All numeric inputs are explicit modelling assumptions; the physical error rate is the dominant
lever because it enters the distance requirement exponentially.

## Layout

- `src/fteconomics/hardware_profiles.py` — hardware assumptions
- `src/fteconomics/qec_overhead.py` — distance selection + patch footprint
- `src/fteconomics/algorithm_cost.py` — Shor / RSA-2048 logical resources
- `src/fteconomics/cost_model.py` — full estimate + sensitivity sweep
- `src/fteconomics/report.py` — markdown report generator
- `reports/` — generated technical report
- `tests/` — numeric model tests

## References

- Fowler AG, Mariantoni M, Martinis JM, Cleland AN. Surface codes: Towards practical large-scale quantum computation. Physical Review A 2012; 86:032324.
- Gidney C, Ekera M. How to factor 2048 bit RSA integers in 8 hours using 20 million noisy qubits. Quantum 2021; 5:433.
- Google Quantum AI. Suppressing quantum errors by scaling a surface code logical qubit. Nature 2023; 614:676-681.

## License

MIT — see [LICENSE](LICENSE).
