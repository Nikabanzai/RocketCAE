# Validation against NASA RP-1311

PyCHEMA validates live NASA CEA results against published documentation examples.

```bash
python -m pychema.cli validate              # Examples 8 + 13
python -m pychema.cli validate --case ex8
python -m pychema.cli validate --case ex13
python examples/rp1311_example8.py
python examples/rp1311_example13.py
pytest tests/test_rp1311_example8.py -q
```

Implementation: `src/pychema/validation.py`.

**API note:** Older docs show `b"Species"` byte strings; current `cea` 3.x accepts plain `str` names (used here).

---

## Example 8 — LOX / LH2 (IAC)

Source: [Example 8](https://nasa.github.io/cea/examples/rocket/example8.html)

| Parameter | Value |
|-----------|--------|
| Fuel / Ox | H2(L) @ 20.27 K / O2(L) @ 90.17 K |
| O/F | 5.55157 |
| Pc | 53.3172 bar |
| Subsonic Ae/At | 1.58 |
| Supersonic Ae/At | 25, 50, 75 |

### Published performance (excerpt)

| Station | T [K] | Isp [m/s] | Isp_vac [m/s] | Cf | c* [m/s] |
|---------|-------|-----------|---------------|-----|----------|
| Chamber | 3383.845 | — | — | — | 2332.34 |
| Ae/At = 1 | 3185.673 | 1537.917 | 2878.925 | 0.6594 | 2332.34 |
| Ae/At = 25 | 1468.163 | 4124.410 | 4348.510 | 1.7684 | 2332.34 |
| Ae/At = 50 | 1219.613 | 4309.122 | 4487.303 | 1.8476 | 2332.34 |
| Ae/At = 75 | 1088.640 | 4399.121 | 4554.913 | 1.8861 | 2332.34 |

---

## Example 13 — N2H4(L)+Be(a) / H2O2(L) with BeO(L) insert

Source: [Example 13](https://nasa.github.io/cea/examples/rocket/example13.html)

Demonstrates:

- Multi-component fuel (80% N2H4(L) + 20% Be(a) by weight)
- `insert=["BeO(L)"]` for equilibrium initial guess
- Non-negligible **condensed** products (BeO(L), BeO(a), BeO(b))

| Parameter | Value |
|-----------|--------|
| Fuel wt | N2H4(L) 0.8, Be(a) 0.2 |
| Oxidizer | H2O2(L) 100% |
| pct_fuel | 67 → O/F = 33/67 |
| T reactants | 298.15 K |
| Pc | 3000 psi |
| pi_p | 3, 10, 30, 300 |
| trace | 1e-10 |

### Published performance (excerpt)

| Station | Ae/At | T [K] | Isp [s] | Ivac [s] | Cf | Condensed |
|---------|-------|-------|---------|----------|-----|-----------|
| Chamber | 0 | 3002.540 | — | — | — | BeO(L)≈0.192 |
| Throat | 1.0 | 2851.000 | 121.571 | 243.396 | 0.6124 | BeO(L)≈0.173 |
| — | 1.2363 | 2851.000 | 181.306 | 263.111 | 0.9133 | BeO(L)≈0.032 |
| — | 5.3385 | 2068.730 | 303.294 | 338.619 | 1.5279 | BeO(a)≈0.199 |
| — | 30.0004 | 1398.106 | 364.613 | 384.464 | 1.8368 | BeO(a)≈0.199 |

c\* = 6386.75 ft/s (constant).

---

## Pass criteria

Per checkpoint: relative error ≤ **0.5%** **or** quantity-specific absolute tolerance (e.g. 5 K on T, 0.5 s on Isp for Ex.13, 0.002 on major mole fractions).

## References

1. McBride, B.J., Gordon, S., NASA RP-1311, 1996. https://ntrs.nasa.gov/citations/19960044559  
2. https://nasa.github.io/cea/examples/rocket/example8.html  
3. https://nasa.github.io/cea/examples/rocket/example13.html  

---

## Full SAMPLE PROBLEMS (1–14)

See [rp1311_samples.md](rp1311_samples.md) for the complete catalog matching the classic CEA SAMPLE PROBLEMS listing (tp, tv, hp, uv, detonation, shock, rocket IAC/FAC).

```bash
python -m pychema.cli validate --case samples   # smoke all 14
python -m pychema.cli validate --case full      # Ex.8+13 numerical + smoke
```
