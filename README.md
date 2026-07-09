# PyCHEMA

> **Formerly developed under the working name RocketCAE.** Renamed to **PyCHEMA** to honor the 2017 CHEMA project and avoid confusion with the unrelated PyPI package [RocketCEA](https://pypi.org/project/rocketcea/) and NASA's `cea` package.

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![CEA](https://img.shields.io/badge/engine-NASA%20CEA-informational)](https://github.com/nasa/cea)

**Preliminary liquid rocket engine trade studies** using [NASA CEA](https://github.com/nasa/cea) — Python library, CLI, and Streamlit GUI.

> **Not flight hardware design.** Outputs are theoretical chemical-equilibrium performance only (Isp, c\*, Tc, …). They do **not** include turbopumps, cooling, structures, injectors, or vehicle Δv.

## Heritage (CHEMA → PyCHEMA)

PyCHEMA is a **modern Python continuation of the CHEMA *concept*** from a 2017 graduation project at the University of Turkish Aeronautical Association:

> *Preliminary Design, Basic Simulation and Optimization of Liquid Rocket Engines*  
> M. A. Kul, Y. Seymen, M. E. Yıldız, S. M. Köroğlu  
> Advisors: Assist. Prof. S. Balage, Assist. Prof. D. S. Körpe

CHEMA used MATLAB + legacy CEA executables. **PyCHEMA is a new codebase** (not a port of the MATLAB GUI) that keeps the same educational goal — explore many bipropellant design points and lightly optimize — on top of the official modern [`cea`](https://github.com/nasa/cea) package.

Original MATLAB dumps, media, and binaries are **not** published here (local-only / gitignored). See [docs/heritage.md](docs/heritage.md).

## Features

| Capability | Command / entry |
|------------|-----------------|
| Single bipropellant evaluation | `pychema run` |
| O/F, Pc, Ae/At sweeps | `pychema sweep` |
| Maximize Isp / c\* / density-Isp | `pychema optimize` |
| Rank curated propellant pairs | `pychema rank` |
| Pareto (max Isp, min Tc) | `pychema pareto` |
| **RP-1311 samples 1–14** (smoke + Ex.8/13 numerical) | `pychema validate` |
| GUI | `streamlit run app/streamlit_app.py` |
| **Mission helper** (Δv, tanks, nozzle, brief) | `pychema mission` |
| Ideal stage sizing | `pychema size` |
| Real-engine Isp references | `pychema refs` |

## Validation (NASA RP-1311 samples 1–14)

| Mode | What it does |
|------|----------------|
| `--case list` | Catalog of all 14 classic SAMPLE PROBLEMS |
| `--case samples` | Smoke-run official `cea` drivers example1…14 |
| `--case ex8` / `ex13` / `all` | Numerical table checks for Ex.8 & Ex.13 |
| `--case full` | Numerical + smoke |

```bash
python -m pychema.cli validate --case list
python -m pychema.cli validate --case samples
python -m pychema.cli validate --case all
python -m pychema.cli validate --case full
python examples/run_rp1311_all.py
```

Docs: [docs/rp1311_samples.md](docs/rp1311_samples.md), [docs/validation.md](docs/validation.md).

## Requirements

- Python **3.11+**
- `pip install cea` (Fortran **not** required for the published wheel)

## Install

```bash
git clone https://github.com/Nikabanzai/PyCHEMA.git
cd PyCHEMA
python -m venv .venv

# Windows
.venv\Scripts\activate

python -m pip install -U pip
python -m pip install -e ".[dev]"
```

## Quick start

```bash
pychema list-pairs

# LOX/LH2 near Example 8 conditions
pychema run --pair lox_lh2 --of 5.55 --pc 53.3 --eps 25

# LOX/RP-1 (CHEMA-style sample)
pychema run --pair lox_rp1 --of 2.3 --pc 66.5 --eps 16

pychema sweep --pair lox_ch4 --param of --n 21
pychema optimize --pair lox_lh2 --vars of --objective isp
pychema rank --pc 50 --eps 40
pychema validate

streamlit run app/streamlit_app.py
```

If console scripts are not on `PATH`:

```bash
python -m pychema.cli validate
```

## Curated propellant pairs

| Key | Pair |
|-----|------|
| `lox_lh2` | LOX / LH2 |
| `lox_rp1` | LOX / RP-1 |
| `lox_ch4` | LOX / LCH4 |
| `lox_ethanol` | LOX / Ethanol |
| `nto_mmh` | NTO / MMH (`CH6N2(L)` in CEA) |
| `nto_hydrazine` | NTO / Hydrazine |

Arbitrary CEA species: `--fuel` / `--oxidizer`.

## Project layout

```text
PyCHEMA/
  src/pychema/     # library + CLI + validation
  app/               # Streamlit GUI
  tests/
  examples/          # including rp1311_example8.py
  docs/              # heritage, validation
  results/           # generated CSVs (content gitignored)
```

## Citing

If you use PyCHEMA, please cite NASA CEA / RP-1311 for the thermodynamics engine, and optionally this software (see [CITATION.cff](CITATION.cff)).

```bibtex
@software{PyCHEMA2026,
  author = {Kul, Muhammed Ali},
  title  = {PyCHEMA: Preliminary liquid rocket trades via NASA CEA},
  year   = {2026},
  url    = {https://github.com/Nikabanzai/PyCHEMA},
  note   = {Conceptual successor to CHEMA 2017, DOI 10.13140/RG.2.2.31672.55043}
}
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Issues and PRs welcome for propellant data, validation cases, and docs.

## Acknowledgements

- **NASA CEA** — Chemical Equilibrium with Applications ([Apache-2.0](https://github.com/nasa/cea))
- **CHEMA (2017)** — Kul, Seymen, Yıldız, Köroğlu; advisors Balage & Körpe — THK University, June 2017, DOI [10.13140/RG.2.2.31672.55043](https://doi.org/10.13140/RG.2.2.31672.55043)  
  *Concept predecessor only; PyCHEMA is independently implemented.*

## Disclaimer

Same spirit as CHEMA: theoretical results may differ greatly from reality. No liability for decisions based on these outputs.

## License

Application code: **Apache-2.0** (see [LICENSE](LICENSE)).  
CEA is a separate dependency with its own license and NOTICE.

## References

1. McBride, B.J., Gordon, S., *Computer Program for Calculation of Complex Chemical Equilibrium Compositions and Applications II. Users Manual and Program Description*, NASA RP-1311, 1996. [NTRS 19960044559](https://ntrs.nasa.gov/citations/19960044559)  
2. NASA CEA documentation — [Example 8 (RP-1311)](https://nasa.github.io/cea/examples/rocket/example8.html)  
3. [nasa/cea](https://github.com/nasa/cea) on GitHub  





## Real-life preliminary helpers

See [docs/engineering_helpers.md](docs/engineering_helpers.md) for Δv sizing, tank volumes, 1-D nozzle geometry, design briefs, and open-literature engine comparison. GUI tab: **Mission helper**.

## Related work

Open-source LRE tools we study for ideas (not dependencies): see [docs/related_work.md](docs/related_work.md) (e.g. cmflannery/rocket, aerospike GUI).


## Nozzle geometry (CHEMA Rao restored)

`ash
# One-shot design: CEA + Rao contour + CAD files
python -m pychema.cli design --pair lox_rp1 --thrust 50000 --pc 50 --eps 25

# Contour only
python -m pychema.cli nozzle --kind rao --dt-mm 80 --eps 25
`

See [docs/chema_gap_analysis.md](docs/chema_gap_analysis.md) and [docs/related_work.md](docs/related_work.md).
