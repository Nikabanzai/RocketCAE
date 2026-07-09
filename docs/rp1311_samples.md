# NASA RP-1311 sample problems (full set)

Classic CEA **SAMPLE PROBLEMS** from McBride & Gordon, NASA RP-1311 (1996).
Modern Python drivers ship with the `cea` package:

```text
site-packages/cea/samples/rp1311/example1.py … example14.py
```

PyCHEMA provides:

| Layer | Command |
|-------|---------|
| Catalog | `python -m pychema.cli validate --case list` |
| Smoke (all 14) | `python -m pychema.cli validate --case samples` |
| Numerical Ex.8+13 | `python -m pychema.cli validate --case all` |
| Everything | `python -m pychema.cli validate --case full` |

## Catalog

| # | Family | Title | Reactants |
|---|--------|-------|-----------|
| 1 | tp | Assigned T and P | H2 / Air |
| 2 | tv | Assigned T and density | H2 / Air |
| 3 | hp | Combustion at assigned P | toluene+octane / Air |
| 4 | uv | Assigned U and density | same as 3 |
| 5 | hp | Solid propellant combustion | AP + binder + Al + … |
| 6 | detonation | Chapman–Jouguet | H2 / O2 |
| 7 | shock | Shock tube | H2+O2+Ar |
| 8 | rocket_iac | Rocket IAC LOX/LH2 | H2(L)/O2(L) **[numerical]** |
| 9 | rocket_fac | Rocket FAC LOX/LH2 | H2(L)/O2(L) |
| 10 | rocket_fac | Rocket FAC via ṁ/Ac | H2(L)/O2(L) |
| 11 | rocket_iac | Rocket ions Li/F2 | Li(cr)/F2(L) |
| 12 | rocket_iac | Rocket MMH/NTO eql+frozen | CH6N2(L)/N2O4(L) |
| 13 | rocket_iac | Rocket tripropellant + insert | N2H4+Be / H2O2 **[numerical]** |
| 14 | tp | Condensed H2O effects | H2(L)/O2(L) |

**[numerical]** = PyCHEMA compares key outputs to published documentation tables.

## Problem families → CEA solvers

| Family | CEA class |
|--------|-----------|
| tp, tv, hp, uv, sp, sv | `EqSolver` / `EqSolution` |
| detonation | `DetonationSolver` |
| shock | `ShockSolver` |
| rocket_iac / rocket_fac | `RocketSolver` |

## Legacy input snippets

The classic free-form CEA input for each sample is reproduced in NASA RP-1311 and the user-provided SAMPLE PROBLEMS listing (Examples 1–14). PyCHEMA does not re-ship those `.inp` files; it uses the maintained Python ports in `nasa/cea`.

## References

1. McBride & Gordon, NASA RP-1311, 1996 — https://ntrs.nasa.gov/citations/19960044559  
2. https://nasa.github.io/cea/  
3. Package samples: `python -c "import cea,pathlib; print(pathlib.Path(cea.__file__).parent/'samples'/'rp1311')"`
