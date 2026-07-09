# PyCHEMA — announcement copy (Zenodo / ResearchGate / LinkedIn)

**Project name:** PyCHEMA
**Package / CLI:** `pychema`
**Repository:** https://github.com/Nikabanzai/PyCHEMA
**Former working name:** RocketCAE (renamed to avoid confusion with PyPI **RocketCEA**)
**License:** Apache-2.0 (application code)
**Depends on:** official NASA `cea` (not RocketCEA)
**Heritage:** CHEMA 2017, DOI 10.13140/RG.2.2.31672.55043

Replace `[ZENODO_DOI]` after you publish the Zenodo archive.

---

## 1. Zenodo

### Title
```
PyCHEMA: Open-Source Preliminary Liquid Rocket Trade Studies with NASA CEA
```

### Resource type
Software

### Version
0.2.0

### License
Apache-2.0

### Authors
Muhammed Ali Kul (Turkish Technic)

### Keywords
```
liquid rocket engine, NASA CEA, chemical equilibrium, CHEMA, specific impulse, nozzle design, Rao nozzle, open source, Python, preliminary design, optimization
```

### Description / abstract
```
PyCHEMA is an open-source Python toolkit for preliminary liquid bipropellant
rocket engine trade studies using the official NASA Chemical Equilibrium with
Applications library (Python package "cea").

Features include equilibrium rocket performance (Isp, vacuum Isp, c*, Tc, Cf);
parameter sweeps and optimization; ranking of curated propellant pairs;
mission-oriented preliminary sizing (ideal delta-v, propellant mass, tank volumes,
1-D throat/exit sizing, constant-thrust burn time); Rao 80% bell and conical
nozzle contours with CSV and CAD-friendly XYZ export; a Streamlit GUI and CLI;
and automated validation against NASA RP-1311 sample problems (detailed numerical
checks for Examples 8 and 13; smoke tests for samples 1-14).

Conceptual heritage: PyCHEMA continues the aims of the 2017 graduation project
CHEMA — "Preliminary Design, Basic Simulation and Optimization of Liquid Rocket
Engines" (University of Turkish Aeronautical Association;
DOI 10.13140/RG.2.2.31672.55043; Kul, Seymen, Yildiz, Koroglu; advisors Balage
and Korpe). The original work used MATLAB with legacy CEA. PyCHEMA is a new
independent codebase and does not redistribute the original MATLAB sources.

Naming note: PyCHEMA is unrelated to the PyPI package "RocketCEA" (a separate
FORTRAN CEA2 wrapper). Thermochemistry uses the official nasa/cea package.
The project was briefly developed under the working name RocketCAE before rename.

Scope: chemical-equilibrium and ideal-rocket-equation estimates for educational
and conceptual design only — not flight-qualified design data.

Repository: https://github.com/Nikabanzai/PyCHEMA
```

### Related identifiers
- Cites / Continues: DOI 10.13140/RG.2.2.31672.55043
- Related software note: uses nasa/cea; distinct from pypi rocketcea

### BibTeX (after Zenodo)
```bibtex
@software{PyCHEMA2026,
  author  = {Kul, Muhammed Ali},
  title   = {PyCHEMA: Open-Source Preliminary Liquid Rocket Trade Studies with NASA CEA},
  year    = {2026},
  version = {0.2.0},
  doi     = {[ZENODO_DOI]},
  url     = {https://github.com/Nikabanzai/PyCHEMA},
  note    = {Continues the CHEMA 2017 concept (DOI 10.13140/RG.2.2.31672.55043)}
}
```

---

## 2. ResearchGate — Software / Technical item

### Title
```
PyCHEMA: Open-Source Preliminary Liquid Rocket Trade Studies with NASA CEA (2026)
```

### Abstract
```
PyCHEMA is a modern open-source Python continuation of the CHEMA concept from our
2017 graduation project on preliminary liquid rocket engine design and optimization
(DOI: 10.13140/RG.2.2.31672.55043).

The 2017 CHEMA work used MATLAB with NASA CEA. PyCHEMA reimplements that idea with
the official nasa/cea package, a CLI and Streamlit GUI, RP-1311 validation, mission
sizing helpers, and Rao nozzle geometry with CAD export.

This project is not the PyPI package RocketCEA. It uses NASA's modern cea library.

GitHub: https://github.com/Nikabanzai/PyCHEMA
Zenodo: [ZENODO_DOI]

Educational and conceptual use only — not a substitute for certified flight design.
```

### Acknowledgement
```
This software continues the conceptual aims of CHEMA (Kul, Seymen, Yildiz, Koroglu;
advisors Balage and Korpe; THK University, 2017; DOI 10.13140/RG.2.2.31672.55043).
Thermochemical calculations use NASA CEA.
```

---

## 3. ResearchGate — short Post
```
Open-sourced PyCHEMA — a Python toolkit for preliminary liquid rocket engine trade
studies using official NASA CEA.

It continues our 2017 CHEMA graduation project
(DOI: 10.13140/RG.2.2.31672.55043): performance trades, optimization, mission sizing,
Rao nozzle contours, and NASA RP-1311 validation.

Not to be confused with the separate PyPI package RocketCEA.

GitHub: https://github.com/Nikabanzai/PyCHEMA
Zenodo: [ZENODO_DOI]

Educational / conceptual use only. Feedback welcome.
```

---

## 4. LinkedIn
```
Proud to open-source PyCHEMA — a Python toolkit for preliminary liquid bipropellant
rocket trade studies, built on the official NASA CEA library.

In 2017, our THK University graduation project CHEMA explored LRE design and
optimization with MATLAB + CEA (DOI: 10.13140/RG.2.2.31672.55043). PyCHEMA is a
modern, independent continuation of that idea: CLI + GUI, design-space sweeps,
validation against NASA RP-1311 examples, preliminary stage sizing, and Rao nozzle
export for CAD.

Note: PyCHEMA is unrelated to the PyPI package "RocketCEA"; we use NASA's modern
"cea" package. (Briefly developed as "RocketCAE" before the rename.)

Repo: https://github.com/Nikabanzai/PyCHEMA
Archive: [ZENODO_DOI]

#Aerospace #Propulsion #OpenSource #Python #RocketScience #NASA
```

---

## 5. X / Twitter
```
PyCHEMA is out: open-source Python LRE trades on official NASA CEA.
Continuation of our 2017 CHEMA project (DOI 10.13140/RG.2.2.31672.55043).
Not RocketCEA (different project).
https://github.com/Nikabanzai/PyCHEMA
```

---

## 6. Email to co-authors / advisors
```
Subject: PyCHEMA — open-source continuation of CHEMA (rename from RocketCAE)

Hi all,

I have released an open-source Python tool, PyCHEMA, that continues the conceptual
goals of our 2017 CHEMA graduation project
(DOI 10.13140/RG.2.2.31672.55043): CEA-based liquid rocket trades, optimization,
and preliminary geometry.

The original MATLAB sources are not redistributed. Documentation and the Zenodo
record cite the 2017 report and credit all CHEMA authors and advisors for the
original idea. Code authorship for the 2026 software is listed separately.

We renamed from a working title "RocketCAE" to PyCHEMA to avoid confusion with the
unrelated PyPI package RocketCEA and to honor CHEMA.

GitHub: https://github.com/Nikabanzai/PyCHEMA
Zenodo: [ZENODO_DOI after publish]

Happy to adjust wording if you prefer.

Best regards,
Ali
```

---

## 7. GitHub release notes (v0.2.0)
```
## PyCHEMA v0.2.0 — rebrand

**PyCHEMA** is the project name (formerly working name RocketCAE).

### Why rename?
Avoid confusion with PyPI RocketCEA and NASA package cea.
PyCHEMA honors the 2017 CHEMA graduation project.

### Highlights
- Official NASA cea performance trades
- CLI + Streamlit GUI
- RP-1311 validation
- Mission sizing + design brief
- Rao 80% nozzle + CAD export

### Install
git clone https://github.com/Nikabanzai/PyCHEMA.git
cd PyCHEMA
pip install -e ".[dev]"
pychema validate --case full

### Cite
CHEMA 2017 DOI 10.13140/RG.2.2.31672.55043
This software: [ZENODO_DOI]
```

---

## Checklist
1. Rename GitHub repo to PyCHEMA
2. Tag v0.2.0 and create GitHub Release
3. Zenodo from GitHub release -> paste DOI into README/CITATION
4. ResearchGate Software item + Post
5. LinkedIn post
6. Email co-authors
