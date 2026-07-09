"""RocketCAE Streamlit GUI."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import numpy as np
import pandas as pd
import streamlit as st
from rocketcae.cea_runner import run_rocket
from rocketcae.models import EngineInputs
from rocketcae.optimize import multi_objective_of_sweep, optimize_of, pareto_front_2d
from rocketcae.propellants import get_pair, list_propellant_pairs
from rocketcae.ranking import rank_propellant_pairs
from rocketcae.sweeps import sweep_of, sweep_to_dataframe

st.set_page_config(page_title="RocketCAE", page_icon="R", layout="wide")

with st.sidebar:
    st.markdown("### RocketCAE")
    st.caption("CEA trades -- not flight hardware")
    st.markdown("> *May your c* be high, walls cool, delta-v non-weaponized.*")
    st.markdown("**Tagline:** Pad-to-orbit theory -- not silo kits.")
    st.divider()
    st.markdown("[GitHub](https://github.com/Nikabanzai/RocketCAE) | [CEA docs](https://nasa.github.io/cea/)")

st.title("RocketCAE")
st.caption("Preliminary LRE explorer via NASA CEA + ideal sizing. Not flight design. Not targeting. Not an ICBM kit.")

with st.expander("Disclaimer", expanded=False):
    st.markdown("CEA equilibrium + ideal rocket equation only. No turbopumps, guidance, re-entry, or warheads. Heritage: CHEMA concept (THK 2017), new Python code.")

with st.expander("Validation", expanded=False):
    if st.button("Run Ex.8+13 numerical validation"):
        from rocketcae.validation import format_validation_report, validation_passed
        with st.spinner("Validating..."):
            rep = format_validation_report(cases="all")
        st.code(rep)
        st.success("Pass") if validation_passed(cases="all") else st.error("Fail")

pairs = list_propellant_pairs()
pair_labels = {p.label: p.key for p in pairs}
tabs = st.tabs(["Single run", "O/F sweep", "Optimize", "Rank", "Pareto", "Mission helper"])
tab_run, tab_sweep, tab_opt, tab_rank, tab_pareto, tab_mission = tabs

with tab_run:
    c1, c2, c3 = st.columns(3)
    label = c1.selectbox("Pair", list(pair_labels), index=1)
    pair = get_pair(pair_labels[label])
    of = c2.slider("O/F", float(pair.of_min), float(pair.of_max), float(pair.of_default), 0.01)
    pc = c3.number_input("Pc [bar]", 1.0, 300.0, 50.0)
    eps = st.number_input("Ae/At", 2.0, 200.0, 40.0)
    if st.button("Run CEA", type="primary"):
        with st.spinner("Solving..."):
            r = run_rocket(EngineInputs(fuel=pair.fuel.name, oxidizer=pair.oxidizer.name, of_ratio=of, pc_bar=pc, area_ratio=eps, fuel_temp_k=pair.fuel.temp_k, oxidizer_temp_k=pair.oxidizer.temp_k))
        if not r.success:
            st.error(r.message)
        else:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Isp", f"{r.isp_s:.1f} s")
            m2.metric("Isp vac", f"{r.isp_vac_s:.1f} s")
            m3.metric("c*", f"{r.cstar_m_s:.0f} m/s")
            m4.metric("Tc", f"{r.tc_k:.0f} K")
            st.bar_chart(pd.DataFrame({"v": [r.isp_s, r.isp_vac_s, r.cstar_m_s/10, r.tc_k/10]}, index=["Isp", "Isp_vac", "c*/10", "Tc/10"]))
            st.json(r.to_dict())

with tab_sweep:
    label = st.selectbox("Pair", list(pair_labels), index=1, key="sw")
    pair = get_pair(pair_labels[label])
    c1, c2, c3 = st.columns(3)
    pc = c1.number_input("Pc", 1.0, 300.0, 50.0, key="swpc")
    eps = c2.number_input("eps", 2.0, 200.0, 40.0, key="sweps")
    n = c3.slider("N", 5, 41, 21)
    if st.button("Sweep O/F"):
        base = EngineInputs(fuel=pair.fuel.name, oxidizer=pair.oxidizer.name, of_ratio=pair.of_default, pc_bar=pc, area_ratio=eps, fuel_temp_k=pair.fuel.temp_k, oxidizer_temp_k=pair.oxidizer.temp_k)
        with st.spinner("Sweeping..."):
            df = sweep_to_dataframe(sweep_of(base, pair.of_min, pair.of_max, n=n))
        st.dataframe(df, use_container_width=True)
        ok = df[df.success]
        if len(ok):
            L, R = st.columns(2)
            L.line_chart(ok.set_index("of_ratio")[["isp_s", "isp_vac_s"]])
            R.line_chart(ok.set_index("of_ratio")[["tc_k"]])
            st.line_chart(ok.set_index("of_ratio")[["cstar_m_s", "cf"]])
            b = ok.loc[ok.isp_vac_s.idxmax()]
            st.info(f"Best Isp_vac {b.isp_vac_s:.1f} s at O/F={b.of_ratio:.3f} (Tc={b.tc_k:.0f} K)")

with tab_opt:
    label = st.selectbox("Pair", list(pair_labels), index=1, key="op")
    pair = get_pair(pair_labels[label])
    c1, c2 = st.columns(2)
    pc = c1.number_input("Pc", 1.0, 300.0, 50.0, key="opc")
    eps = c2.number_input("eps", 2.0, 200.0, 40.0, key="oeps")
    objective = st.selectbox("Objective", ["isp", "isp_vac", "cstar", "density_isp"])
    if st.button("Optimize"):
        base = EngineInputs(fuel=pair.fuel.name, oxidizer=pair.oxidizer.name, of_ratio=pair.of_default, pc_bar=pc, area_ratio=eps, fuel_temp_k=pair.fuel.temp_k, oxidizer_temp_k=pair.oxidizer.temp_k)
        res = optimize_of(base, pair.of_min, pair.of_max, objective=objective)
        if res.success:
            st.success(f"Best {res.objective}={res.best_value:.4g} at O/F={res.best_inputs.of_ratio:.4f}")
            if res.history:
                st.line_chart(pd.DataFrame(res.history).set_index("of_ratio")[["value"]])
            st.json(res.best_result.to_dict())
        else:
            st.error(res.message)

with tab_rank:
    c1, c2 = st.columns(2)
    pc = c1.number_input("Pc", 1.0, 300.0, 50.0, key="rpc")
    eps = c2.number_input("eps", 2.0, 200.0, 40.0, key="reps")
    if st.button("Rank pairs"):
        df = rank_propellant_pairs(pc_bar=pc, area_ratio=eps)
        st.dataframe(df, use_container_width=True)
        ok = df[df.success]
        if len(ok):
            st.bar_chart(ok.set_index("label")[["isp_vac_s", "isp_s"]])
            st.bar_chart(ok.set_index("label")[["tc_k"]])

with tab_pareto:
    label = st.selectbox("Pair", list(pair_labels), index=1, key="pa")
    pair = get_pair(pair_labels[label])
    c1, c2, c3 = st.columns(3)
    pc = c1.number_input("Pc", 1.0, 300.0, 50.0, key="ppc")
    eps = c2.number_input("eps", 2.0, 200.0, 40.0, key="peps")
    n = c3.slider("N", 10, 41, 21, key="pn")
    if st.button("Pareto"):
        base = EngineInputs(fuel=pair.fuel.name, oxidizer=pair.oxidizer.name, of_ratio=pair.of_default, pc_bar=pc, area_ratio=eps, fuel_temp_k=pair.fuel.temp_k, oxidizer_temp_k=pair.oxidizer.temp_k)
        pts = multi_objective_of_sweep(base, pair.of_min, pair.of_max, n=n)
        points = [(o1, -o2, r) for _, o1, o2, r in pts]
        front = pareto_front_2d(points, maximize=(True, False))
        all_df = pd.DataFrame({"of_ratio": [r.inputs.of_ratio for *_, r in pts], "isp_s": [o1 for _, o1, _, _ in pts], "tc_k": [-o2 for _, _, o2, _ in pts]})
        front_df = pd.DataFrame({"of_ratio": [r.inputs.of_ratio for _, _, r in front], "isp_s": [a for a, _, _ in front], "tc_k": [b for _, b, _ in front]})
        L, R = st.columns(2)
        L.scatter_chart(all_df, x="tc_k", y="isp_s")
        R.dataframe(front_df, use_container_width=True)

with tab_mission:
    st.subheader("Mission helper -- napkin-level stage from CEA")
    st.info("Useful: CEA Isp, ideal delta-v propellant mass, tanks, 1-D nozzle, burn time, real-engine sanity check. Peaceful orbital math only.")
    c1, c2, c3 = st.columns(3)
    label = c1.selectbox("Pair", list(pair_labels), index=1, key="mh")
    pair = get_pair(pair_labels[label])
    of = c2.slider("O/F", float(pair.of_min), float(pair.of_max), float(pair.of_default), 0.01, key="mhof")
    pc = c3.number_input("Pc", 1.0, 300.0, 50.0, key="mhpc")
    c1, c2, c3, c4 = st.columns(4)
    eps = c1.number_input("Ae/At", 2.0, 200.0, 40.0, key="mheps")
    dv = c2.number_input("Delta-v [m/s]", 100.0, 12000.0, 3000.0, 50.0)
    payload = c3.number_input("Payload [kg]", 1.0, 1e6, 100.0)
    thrust_kn = c4.number_input("Thrust [kN]", 0.1, 10000.0, 50.0)
    structure = st.slider("Structural fraction", 0.03, 0.25, 0.10, 0.01)
    use_vac = st.checkbox("Use vacuum Isp", value=True)
    if st.button("Run mission helper", type="primary"):
        from rocketcae.mission import run_mission_helper
        with st.spinner("Building brief..."):
            res = run_mission_helper(pair_key=pair_labels[label], of_ratio=of, pc_bar=pc, area_ratio=eps, delta_v_m_s=dv, payload_kg=payload, structural_fraction=structure, thrust_n=thrust_kn * 1000.0, use_vacuum_isp=use_vac, report_path='results/design_brief.md')
        if not res.cea.success:
            st.error(res.cea.message)
        else:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Isp vac", f"{res.cea.isp_vac_s:.1f} s")
            m2.metric("Isp", f"{res.cea.isp_s:.1f} s")
            if res.sizing and res.sizing.success:
                m3.metric("Propellant", f"{res.sizing.propellant_mass_kg:.0f} kg")
                m4.metric("Gross", f"{res.sizing.gross_mass_kg:.0f} kg")
                mass_df = pd.DataFrame({"kg": [res.sizing.payload_kg, res.sizing.inert_mass_kg, res.sizing.propellant_mass_kg]}, index=["Payload", "Inert", "Propellant"])
                g1, g2 = st.columns(2)
                g1.bar_chart(mass_df)
                if res.tanks:
                    g2.bar_chart(pd.DataFrame({"L": [res.tanks["v_fuel_L"], res.tanks["v_oxidizer_L"]], "kg": [res.tanks["m_fuel_kg"], res.tanks["m_oxidizer_kg"]]}, index=["Fuel", "Oxidizer"]))
            if res.nozzle and res.nozzle.success:
                n1, n2, n3, n4 = st.columns(4)
                n1.metric("Dt mm", f"{res.nozzle.throat_diameter_m*1000:.1f}")
                n2.metric("De mm", f"{res.nozzle.exit_diameter_m*1000:.1f}")
                n3.metric("At cm2", f"{res.nozzle.throat_area_m2*1e4:.2f}")
                n4.metric("eps", f"{res.nozzle.area_ratio:.1f}")
                x = np.linspace(0, 1, 40)
                area = 1.0 + (res.nozzle.area_ratio - 1.0) * (x ** 1.3)
                st.line_chart(pd.DataFrame({"radius_norm": np.sqrt(area)}, index=x))
                st.caption("Cartoon nozzle radius vs station (not CAD)")
            if res.burn and res.burn.success:
                b1, b2, b3 = st.columns(3)
                b1.metric("Burn s", f"{res.burn.burn_time_s:.1f}")
                b2.metric("mdot", f"{res.burn.mdot_kg_s:.3f}")
                b3.metric("I_tot kNs", f"{res.burn.total_impulse_n_s/1e3:.1f}")
                t = np.linspace(0, res.burn.burn_time_s, 50)
                st.line_chart(pd.DataFrame({"prop_left_kg": res.sizing.propellant_mass_kg * (1 - t / res.burn.burn_time_s)}, index=t))
            if res.comparisons:
                st.dataframe(res.comparisons, use_container_width=True)
                st.bar_chart(pd.DataFrame(res.comparisons).set_index("name")[["ref_isp_s"]])
            st.download_button("Download design brief", res.brief_markdown, "design_brief.md", "text/markdown")
            with st.expander("Brief", expanded=True):
                st.markdown(res.brief_markdown)

st.divider()
st.markdown("CEA | RocketCAE | Peaceful propulsion trades | ICBM jokes: politely declined")
