"""Command-line interface for RocketCAE."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from rocketcae.cea_runner import run_from_pair, run_rocket
from rocketcae.models import EngineInputs
from rocketcae.optimize import multi_objective_of_sweep, optimize_of, optimize_of_pc, pareto_front_2d
from rocketcae.propellants import get_pair, list_propellant_pairs
from rocketcae.ranking import rank_propellant_pairs
from rocketcae.sweeps import sweep_area_ratio, sweep_of, sweep_pc, sweep_to_dataframe


def _print_result(r) -> None:
    if not r.success:
        print(f"FAILED: {r.message}", file=sys.stderr)
        return
    print(f"Fuel/Ox     : {r.inputs.fuel} / {r.inputs.oxidizer}")
    print(f"O/F         : {r.inputs.of_ratio:.4f}")
    print(f"Pc          : {r.pc_bar:.3f} bar")
    print(f"Ae/At       : {r.area_ratio:.3f}")
    print(f"Tc          : {r.tc_k:.1f} K")
    print(f"c*          : {r.cstar_m_s:.1f} m/s")
    print(f"Isp         : {r.isp_m_s:.1f} m/s  ({r.isp_s:.2f} s)")
    print(f"Isp vac     : {r.isp_vac_m_s:.1f} m/s  ({r.isp_vac_s:.2f} s)")
    print(f"Cf          : {r.cf:.4f}")
    if r.density_isp_s is not None:
        print(f"Density-Isp : {r.density_isp_s:.3f} (proxy)")


def cmd_list_pairs(_: argparse.Namespace) -> int:
    for p in list_propellant_pairs():
        print(f"{p.key:16s}  {p.label:20s}  O/F default={p.of_default}  [{p.of_min}-{p.of_max}]  {p.notes}")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    if args.pair:
        r = run_from_pair(args.pair, of_ratio=args.of, pc_bar=args.pc, area_ratio=args.eps)
    else:
        if not args.fuel or not args.oxidizer:
            print("Provide --pair or both --fuel and --oxidizer", file=sys.stderr)
            return 2
        inputs = EngineInputs(
            fuel=args.fuel,
            oxidizer=args.oxidizer,
            of_ratio=args.of or 2.0,
            pc_bar=args.pc,
            area_ratio=args.eps,
        )
        r = run_rocket(inputs)
    _print_result(r)
    if args.json:
        print(json.dumps(r.to_dict(), indent=2))
    return 0 if r.success else 1


def cmd_sweep(args: argparse.Namespace) -> int:
    pair = get_pair(args.pair)
    base = EngineInputs(
        fuel=pair.fuel.name,
        oxidizer=pair.oxidizer.name,
        of_ratio=args.of or pair.of_default,
        pc_bar=args.pc,
        area_ratio=args.eps,
        fuel_temp_k=pair.fuel.temp_k,
        oxidizer_temp_k=pair.oxidizer.temp_k,
    )
    if args.param == "of":
        lo = args.min if args.min is not None else pair.of_min
        hi = args.max if args.max is not None else pair.of_max
        sweep = sweep_of(base, lo, hi, n=args.n)
    elif args.param == "pc":
        lo = args.min if args.min is not None else 10.0
        hi = args.max if args.max is not None else 100.0
        sweep = sweep_pc(base, lo, hi, n=args.n)
    else:
        lo = args.min if args.min is not None else 10.0
        hi = args.max if args.max is not None else 80.0
        sweep = sweep_area_ratio(base, lo, hi, n=args.n)

    df = sweep_to_dataframe(sweep)
    out = Path(args.out) if args.out else Path("results") / f"sweep_{args.param}_{args.pair}.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(df.to_string(index=False))
    print(f"\nWrote {out}")
    return 0


def cmd_optimize(args: argparse.Namespace) -> int:
    pair = get_pair(args.pair)
    base = EngineInputs(
        fuel=pair.fuel.name,
        oxidizer=pair.oxidizer.name,
        of_ratio=pair.of_default,
        pc_bar=args.pc,
        area_ratio=args.eps,
        fuel_temp_k=pair.fuel.temp_k,
        oxidizer_temp_k=pair.oxidizer.temp_k,
    )
    if args.vars == "of":
        res = optimize_of(base, pair.of_min, pair.of_max, objective=args.objective)
    else:
        res = optimize_of_pc(
            base,
            (pair.of_min, pair.of_max),
            (args.pc_min, args.pc_max),
            objective=args.objective,
            maxiter=args.maxiter,
        )
    print(f"Objective : {res.objective}")
    print(f"Success   : {res.success}  ({res.message})")
    print(f"Best value: {res.best_value}")
    if res.best_result:
        _print_result(res.best_result)
    return 0 if res.success else 1


def cmd_rank(args: argparse.Namespace) -> int:
    df = rank_propellant_pairs(pc_bar=args.pc, area_ratio=args.eps)
    print(df.to_string(index=False))
    out = Path(args.out) if args.out else Path("results") / "rank_pairs.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"\nWrote {out}")
    return 0


def cmd_pareto(args: argparse.Namespace) -> int:
    pair = get_pair(args.pair)
    base = EngineInputs(
        fuel=pair.fuel.name,
        oxidizer=pair.oxidizer.name,
        of_ratio=pair.of_default,
        pc_bar=args.pc,
        area_ratio=args.eps,
        fuel_temp_k=pair.fuel.temp_k,
        oxidizer_temp_k=pair.oxidizer.temp_k,
    )
    pts = multi_objective_of_sweep(base, pair.of_min, pair.of_max, n=args.n, obj1="isp", obj2="neg_tc")
    # Convert to (isp, -neg_tc=tc) for display maximization of isp and minimization of tc
    points = [(o1, -o2, r) for _, o1, o2, r in pts]  # isp, tc, result
    front = pareto_front_2d(points, maximize=(True, False))  # max isp, min tc
    print("Pareto front (max Isp, min Tc):")
    for isp, tc, r in front:
        print(f"  O/F={r.inputs.of_ratio:6.3f}  Isp={isp:7.2f} s  Tc={tc:8.1f} K")
    return 0



def cmd_validate(args: argparse.Namespace) -> int:
    from rocketcae import rp1311_catalog, rp1311_smoke, validation

    case = getattr(args, "case", "all")
    if case == "list":
        for s in rp1311_catalog.list_samples():
            flag = " [numerical]" if s.numerical_validation else ""
            print(f"  {s.number:2d}  {s.family:12s}  {s.title}{flag}")
            print(f"      {s.summary}")
        return 0
    if case == "samples":
        results = rp1311_smoke.run_all_official_samples()
        print(rp1311_smoke.format_smoke_report(results))
        return 0 if rp1311_smoke.smoke_passed(results) else 1
    if case == "full":
        print(validation.full_validation_report())
        return 0 if validation.full_validation_passed() else 1
    # ex8 / ex13 / all (numerical only)
    report = validation.format_validation_report(cases=case)
    print(report)
    return 0 if validation.validation_passed(cases=case) else 1



def cmd_refs(_: argparse.Namespace) -> int:
    from rocketcae.references import list_reference_engines
    for e in list_reference_engines():
        iv = f"{e.isp_vac_s:.0f}" if e.isp_vac_s else "-"
        isl = f"{e.isp_sl_s:.0f}" if e.isp_sl_s else "-"
        print(f"{e.key:14s}  {e.name:28s}  Isp_sl={isl:>5}s  Isp_vac={iv:>5}s  {e.oxidizer}/{e.fuel}")
    return 0


def cmd_mission(args: argparse.Namespace) -> int:
    from rocketcae.mission import run_mission_helper

    res = run_mission_helper(
        pair_key=args.pair,
        of_ratio=args.of,
        pc_bar=args.pc,
        area_ratio=args.eps,
        delta_v_m_s=args.dv,
        payload_kg=args.payload,
        structural_fraction=args.structure,
        thrust_n=args.thrust,
        use_vacuum_isp=not args.use_sl_isp,
        report_path=args.out,
    )
    print(res.brief_markdown)
    if res.brief_path:
        print(f"\nWrote {res.brief_path}")
    return 0 if res.cea.success else 1


def cmd_size(args: argparse.Namespace) -> int:
    from rocketcae.sizing import size_stage_from_delta_v, burn_from_thrust, mixture_tank_volumes
    from rocketcae.propellants import get_pair

    s = size_stage_from_delta_v(args.dv, args.isp, args.payload, args.structure)
    if not s.success:
        print(f"FAILED: {s.message}")
        return 1
    print(f"Mass ratio m0/mf : {s.mass_ratio:.4f}")
    print(f"Propellant      : {s.propellant_mass_kg:.2f} kg")
    print(f"Inert           : {s.inert_mass_kg:.2f} kg")
    print(f"Gross           : {s.gross_mass_kg:.2f} kg")
    print(f"Prop MF         : {s.propellant_mass_fraction:.3f}")
    if args.thrust:
        b = burn_from_thrust(s.propellant_mass_kg, args.isp, args.thrust)
        if b.success:
            print(f"Burn time       : {b.burn_time_s:.2f} s @ {args.thrust:.0f} N")
            print(f"mdot            : {b.mdot_kg_s:.4f} kg/s")
    if args.pair:
        pair = get_pair(args.pair)
        of = args.of if args.of is not None else pair.of_default
        tanks = mixture_tank_volumes(
            s.propellant_mass_kg, of, pair.fuel.density_kg_m3, pair.oxidizer.density_kg_m3
        )
        print(f"Tank fuel       : {tanks['v_fuel_L']:.2f} L ({tanks['m_fuel_kg']:.2f} kg)")
        print(f"Tank oxidizer   : {tanks['v_oxidizer_L']:.2f} L ({tanks['m_oxidizer_kg']:.2f} kg)")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="rocketcae",
        description="RocketCAE — preliminary LRE trades via NASA CEA",
    )
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("list-pairs", help="List curated propellant pairs")
    s.set_defaults(func=cmd_list_pairs)

    s = sub.add_parser("run", help="Single CEA rocket evaluation")
    s.add_argument("--pair", help="Curated pair key (e.g. lox_rp1)")
    s.add_argument("--fuel", help="CEA fuel species name")
    s.add_argument("--oxidizer", help="CEA oxidizer species name")
    s.add_argument("--of", type=float, default=None, help="Oxidizer/fuel mass ratio")
    s.add_argument("--pc", type=float, default=50.0, help="Chamber pressure [bar]")
    s.add_argument("--eps", type=float, default=40.0, help="Nozzle area ratio Ae/At")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_run)

    s = sub.add_parser("sweep", help="Parameter sweep")
    s.add_argument("--pair", required=True)
    s.add_argument("--param", choices=["of", "pc", "eps"], default="of")
    s.add_argument("--min", type=float, default=None)
    s.add_argument("--max", type=float, default=None)
    s.add_argument("--n", type=int, default=15)
    s.add_argument("--of", type=float, default=None)
    s.add_argument("--pc", type=float, default=50.0)
    s.add_argument("--eps", type=float, default=40.0)
    s.add_argument("--out", default=None)
    s.set_defaults(func=cmd_sweep)

    s = sub.add_parser("optimize", help="Maximize Isp (or other) over O/F or O/F+Pc")
    s.add_argument("--pair", required=True)
    s.add_argument("--vars", choices=["of", "of_pc"], default="of")
    s.add_argument("--objective", choices=["isp", "isp_vac", "cstar", "density_isp"], default="isp")
    s.add_argument("--pc", type=float, default=50.0)
    s.add_argument("--eps", type=float, default=40.0)
    s.add_argument("--pc-min", type=float, default=20.0)
    s.add_argument("--pc-max", type=float, default=100.0)
    s.add_argument("--maxiter", type=int, default=12)
    s.set_defaults(func=cmd_optimize)

    s = sub.add_parser("rank", help="Rank all curated propellant pairs")
    s.add_argument("--pc", type=float, default=50.0)
    s.add_argument("--eps", type=float, default=40.0)
    s.add_argument("--out", default=None)
    s.set_defaults(func=cmd_rank)

    s = sub.add_parser("pareto", help="O/F Pareto front: max Isp vs min Tc")
    s.add_argument("--pair", required=True)
    s.add_argument("--pc", type=float, default=50.0)
    s.add_argument("--eps", type=float, default=40.0)
    s.add_argument("--n", type=int, default=21)
    s.set_defaults(func=cmd_pareto)

    
    s = sub.add_parser("validate", help="Run RP-1311 Example 8/13 validation vs NASA published output")
    s.add_argument(
        "--case",
        choices=["ex8", "ex13", "all", "samples", "full", "list"],
        default="all",
        help="ex8/ex13/all=numerical tables; samples=smoke 1-14; full=both; list=catalog",
    )
    s.set_defaults(func=cmd_validate)


    s = sub.add_parser("refs", help="List approximate real-engine Isp references")
    s.set_defaults(func=cmd_refs)

    s = sub.add_parser("size", help="Ideal stage sizing from Δv + Isp (no CEA)")
    s.add_argument("--dv", type=float, required=True, help="Delta-v [m/s]")
    s.add_argument("--isp", type=float, required=True, help="Specific impulse [s]")
    s.add_argument("--payload", type=float, default=100.0, help="Payload mass [kg]")
    s.add_argument("--structure", type=float, default=0.10, help="Structural fraction inert/(inert+prop)")
    s.add_argument("--thrust", type=float, default=None, help="Optional thrust [N] for burn time")
    s.add_argument("--pair", default=None, help="Optional pair for tank volume estimate")
    s.add_argument("--of", type=float, default=None)
    s.set_defaults(func=cmd_size)

    s = sub.add_parser("mission", help="CEA + sizing + nozzle + tanks + design brief")
    s.add_argument("--pair", default="lox_rp1")
    s.add_argument("--of", type=float, default=None)
    s.add_argument("--pc", type=float, default=50.0)
    s.add_argument("--eps", type=float, default=40.0)
    s.add_argument("--dv", type=float, default=3000.0, help="Target delta-v [m/s]")
    s.add_argument("--payload", type=float, default=100.0)
    s.add_argument("--structure", type=float, default=0.10)
    s.add_argument("--thrust", type=float, default=50000.0, help="Design thrust [N]")
    s.add_argument("--use-sl-isp", action="store_true", help="Use delivered Isp instead of vacuum")
    s.add_argument("--out", default="results/design_brief.md")
    s.set_defaults(func=cmd_mission)

    return p


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    code = args.func(args)
    raise SystemExit(code)


if __name__ == "__main__":
    main()

