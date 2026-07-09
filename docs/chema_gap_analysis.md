# CHEMA feature gap analysis → PyCHEMA

Source: `Chema/ChemaV7.m` (GUIDE GUI, 2017) + paper DOI 10.13140/RG.2.2.31672.55043.

## Feature matrix

| CHEMA capability | PyCHEMA status | Notes |
|------------------|------------------|-------|
| Write CEA input + run CEA300.exe | **Replaced** | Official `cea` Python API |
| Multi fuel/oxidizer slots (up to 3+3) | Partial | Curated pairs; multi-species later |
| FAC (`ac/at`) / mdot / sub / sup ratios | Partial | IAC default; FAC via validation Ex.9 |
| Frozen + ions flags | Not yet | Ex.12 sample smoke covers frozen path |
| Parse CEA plot columns (Isp, Ivac, Mach, …) | **Yes** | `EngineResult` |
| **Rao nozzle 80% + plot + 3-D revolve** | **Restored** | `pychema.nozzle` |
| CAD coordinates export | **Restored** | CSV + XYZ for SolidWorks |
| Optimize O/F, P, ε for max Isp/thrust | Partial | O/F + O/F+Pc optimize; thrust max later |
| Rank fuels | **Yes** | `rank` |
| Vehicle flight (`chema` ODE, drag/gravity loss) | Out of scope | Ballistic toy — not restored (weapons-adjacent) |
| Audio error prompts | No | Text errors only |
| Mission Δv / propellant sizing | **Better than CHEMA** | `mission` helper |
| RP-1311 numerical validation | **New** | Not in CHEMA |
| Streamlit multi-tab GUI | **Yes** | Modern CHEMA GUI analogue |

## Algorithms restored from CHEMA nozzle block

From `ChemaV7.m` `%% Nozzle` section:

- `per = 0.8` Rao length fraction of 15° cone  
- Entrance arc radius `1.5 * Rt`  
- Exit-side throat arc `0.382 * Rt`  
- Inflection angle `theta = 40°`  
- Parabola `x = a y² + b y + c` matched to slope and exit  
- Optional chamber length empirical fit from throat diameter  

## Stolen patterns (clean-room)

| Source | Pattern | Our module |
|--------|---------|------------|
| cmflannery/rocket | design_engine(thrust, Pc, MR) | `design.py` |
| cmflannery/rocket | contour.to_csv | `nozzle.to_csv` |
| mvernacc/aerospike | XYZ CAD export | `nozzle.to_xyz_cad` |
| CHEMA | Rao geometry | `nozzle.rao_bell_contour` |

## Deliberately not restored

- Audio tutorials  
- Full 6-DOF / range ODE (“Ancalagon Rocket” prints)  
- Personal media / CVs / WAV  
