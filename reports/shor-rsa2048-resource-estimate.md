# How Many Physical Qubits to Break RSA-2048?

A resource estimate for Shor's algorithm under realistic surface-code error correction.

## Headline answer

Under the superconducting baseline (physical error rate 1e-03,
1000 ns surface-code cycle, 1% threshold), factoring a 2048-bit RSA modulus
with Shor's algorithm is estimated to require **22.9 million
physical qubits** at code distance **d = 29**, running for about
**7.5 hours**. This reproduces the order of magnitude of Gidney &
Ekera (2021): roughly 20 million qubits in roughly 8 hours.

## Method

The estimate combines three published ingredients:

1. **Logical resources (algorithm).** The number of logical qubits and Toffoli (magic-state) gates
   for Shor / RSA-2048 are taken at the order of magnitude reported by Gidney & Ekera (2021):
   ~6,200 algorithmic logical qubits and ~2.7e+09 Toffoli
   gates, with a factory/routing tile multiplier of 2.2 (a layout
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

| Profile | p | cycle (ns) | distance d | qubits/patch | physical qubits | runtime (h) |
|---------|---|------------|-----------|--------------|-----------------|-------------|
| Superconducting (Gidney-Ekera baseline) | 1e-03 | 1000 | 29 | 1,681 | 22.9 million | 7.5 |
| Superconducting (optimistic) | 3e-04 | 500 | 19 | 721 | 9.8 million | 3.8 |
| Superconducting (conservative) | 3e-03 | 1000 | 55 | 6,049 | 82.5 million | 7.5 |

## Sensitivity analysis

The physical error rate is the dominant lever: it enters the required distance exponentially, so a
modest improvement removes millions of qubits, while a modest regression can make the computation
infeasible (the rate approaching threshold).


**physical_error_rate**

| multiplier | distance | physical qubits | runtime (h) |
|-----------|----------|-----------------|-------------|
| 0.5x | 23 | 14.4 million | 7.5 |
| 0.75x | 25 | 17.0 million | 7.5 |
| 1x | 29 | 22.9 million | 7.5 |
| 1.5x | 35 | 33.4 million | 7.5 |
| 2x | 41 | 45.8 million | 7.5 |

**cycle_time_ns**

| multiplier | distance | physical qubits | runtime (h) |
|-----------|----------|-----------------|-------------|
| 0.5x | 29 | 22.9 million | 3.8 |
| 0.75x | 29 | 22.9 million | 5.6 |
| 1x | 29 | 22.9 million | 7.5 |
| 1.5x | 29 | 22.9 million | 11.2 |
| 2x | 29 | 22.9 million | 15.0 |

**code_threshold**

| multiplier | distance | physical qubits | runtime (h) |
|-----------|----------|-----------------|-------------|
| 0.5x | 41 | 45.8 million | 7.5 |
| 0.75x | 33 | 29.7 million | 7.5 |
| 1x | 29 | 22.9 million | 7.5 |
| 1.5x | 25 | 17.0 million | 7.5 |
| 2x | 23 | 14.4 million | 7.5 |

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
