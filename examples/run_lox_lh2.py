"""Example: single LOX/LH2 evaluation (NASA RP-1311 style)."""

from pychema.cea_runner import run_from_pair


def main() -> None:
    r = run_from_pair("lox_lh2", of_ratio=5.55, pc_bar=53.3172, area_ratio=25.0)
    assert r.success, r.message
    print(f"Isp = {r.isp_s:.2f} s, Isp_vac = {r.isp_vac_s:.2f} s, Tc = {r.tc_k:.0f} K, c* = {r.cstar_m_s:.0f} m/s")


if __name__ == "__main__":
    main()
