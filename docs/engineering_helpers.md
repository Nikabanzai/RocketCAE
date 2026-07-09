# Engineering helpers (real-life preliminary tools)

RocketCAE is not only "run CEA once." The **mission helper** layer turns equilibrium
Isp into napkin-level stage numbers you can discuss in a design review — with charts
in the GUI and a Markdown brief you can download.

## What it does (useful)

| Tool | Purpose |
|------|---------|
| `rocketcae mission` | CEA + Δv sizing + tanks + 1-D nozzle + burn time + engine comparison + brief |
| `rocketcae size` | Ideal rocket-equation sizing without CEA (bring your own Isp) |
| `rocketcae refs` | Approximate open-literature engine Isp/thrust list |
| GUI **Mission helper** tab | Same workflow with mass/tank/nozzle/burn charts |

### Ideal stage sizing

Given target **Δv**, **Isp**, **payload**, and structural fraction  
λ = m_inert / (m_inert + m_propellant):

- mass ratio m0/mf = exp(Δv / (Isp g0))
- propellant, inert, and gross mass

### Burn profile

Constant thrust & Isp → ṁ, burn time, total impulse.

### Tank volumes

Split biprop mass by O/F; divide by liquid densities; add ullage.

### Nozzle geometry (1-D)

At = F / (Pc · Cf), Ae = ε At, optional Vc = L\* · At.

### Reference engines

Sanity-check CEA Isp against rounded public figures (RS-25, Merlin, RD-180, …).
**Not** certified data.

## What it deliberately does **not** do

- Ballistic trajectories, re-entry, or targeting  
- "Hit any location" / ICBM-style mission design  
- Nuclear / warhead design  
- Guidance, navigation, control  
- Flight-qualified thermal or structural design  

Humor in the UI stays **pad-to-orbit / student nerd** — not weapons marketing.

## Examples

```bash
# Full preliminary brief (writes results/design_brief.md)
python -m rocketcae.cli mission --pair lox_rp1 --dv 3000 --payload 100 --thrust 50000

# Sizing only
python -m rocketcae.cli size --dv 3000 --isp 320 --payload 100 --thrust 50000 --pair lox_rp1

# Reference engines
python -m rocketcae.cli refs

# GUI
python -m streamlit run app/streamlit_app.py
```

## Modules

- `rocketcae.sizing` — Δv / burn / tanks  
- `rocketcae.geometry` — At, Dt, Ae, De, L\*  
- `rocketcae.references` — open-literature engines  
- `rocketcae.report` — Markdown design brief  
- `rocketcae.mission` — orchestrates all of the above with CEA  
