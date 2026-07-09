# Related open-source projects (ideas, not dependencies)

Honest notes for RocketCAE maintainers. Neither repo is “trash”; they solve
overlapping problems with different maturity and scope.

## cmflannery/rocket (`openrocketengine`)

- **URL:** https://github.com/cmflannery/rocket  
- **License:** MIT  
- **Stack:** Python, RocketCEA (Fortran), units (`Quantity`), nozzle contours, plotting  
- **Stars / activity:** modest but **actively maintained** (2025–2026 outputs in tree)

### What it does well

| Idea | Why it matters |
|------|----------------|
| `EngineInputs.from_propellants(...)` → design | Clean API: thrust + Pc + MR in, performance + geometry out |
| **Units system** | Avoids bar/Pa/psi bugs |
| **Rao / conical nozzle contours** + CSV export | CHEMA already had Rao figures — natural RocketCAE upgrade |
| Engine **dashboard plots** | Cross-section + performance curves |
| Cycles (GG, SC, pressure-fed) modules | Beyond pure CEA (thermodynamic cycle bookkeeping) |
| Trade study / uncertainty examples | Research-grade workflows |
| Tests + packaging (`pyproject`, CI) | Good hygiene |

### Limits / caveats

- Depends on **RocketCEA** (different CEA binding than NASA’s official `cea` we use)  
- Broader scope → more surface area to maintain  
- “Tanks coming soon” historically; check current code  

### What RocketCAE can lend (implement ourselves, MIT-friendly ideas)

1. **Rao bell nozzle contour** generator + plot + CSV (CHEMA had this; we don’t yet)  
2. **Unit-aware inputs** (even a thin wrapper: always document SI)  
3. **`design_engine(thrust, Pc, MR)`** one-shot that chains CEA → geometry (we half-have this via mission helper)  
4. **Engine dashboard** figure (matplotlib multi-panel export)  
5. Optional later: gas-generator power balance (not required for v0.x)

Do **not** copy their code blindly if licenses conflict with how we vendor; **reimplement** algorithms with our own tests + cite papers (Huzel & Huang, GATech bell nozzle notes).

---

## mvernacc/aerospike-nozzle-design-gui

- **URL:** https://github.com/mvernacc/aerospike-nozzle-design-gui  
- **License:** GPL-2.0  
- **Stack:** Tkinter GUI + numpy/scipy solver; Lee (MSFC) spike contour algorithm  
- **Scope:** **Aerospike / plug nozzle** geometry only  

### What it does well

| Idea | Why it matters |
|------|----------------|
| Live recompute on parameter change | Responsive design loop |
| Plots: radius, p, Isp, M, T vs spike length | Great teaching visuals |
| **Export XYZ for CAD** (SolidWorks curve) | Real engineering handoff |
| Save/load design | Session continuity |
| Classic algorithm + PDF derivation | Traceable method |

### Limits / caveats

- **GPL-2.0:** if we *copy* code into RocketCAE (Apache-2.0), license compatibility needs care (GPL tends to “infect” combined works). Prefer **cite + reimplement** or call as optional external tool.  
- Not biprop CEA / full engine design — niche nozzle type  
- Older Tk style; small codebase (~few files)  

### What RocketCAE can lend

1. **CAD export pattern** (CSV/XYZ of wall contour) for *conventional* Rao/conical nozzles first  
2. **Live parameter → plot** UX (we use Streamlit; same idea)  
3. Optional future: aerospike module **only if** someone needs it — not core CHEMA path  

---

## Verdict

| Repo | Trash? | Steal ideas? | Priority for RocketCAE |
|------|--------|--------------|-------------------------|
| cmflannery/rocket | **No** — solid LRE toolkit | **Yes** — API shape, Rao, dashboards, units | **High** |
| mvernacc/aerospike… | **No** — focused & useful | **Yes** — CAD export, live plots; GPL caution | **Low/medium** (niche) |

**Neither is trash.** RocketCAE’s differentiator remains: official NASA `cea`, RP-1311 validation, CHEMA heritage, Streamlit + mission sizing. Borrow *patterns*, keep our CEA stack, reimplement geometry with citations.
