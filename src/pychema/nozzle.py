"""Nozzle wall contours: conical and Rao parabolic bell (CHEMA heritage).

Algorithm matches the CHEMA V7 MATLAB construction (80% Rao length fraction,
throat entrance arc 1.5 Rt, exit arc 0.382 Rt, parabolic bell). Coordinates
are SI meters with x=0 at the throat plane (positive aft).

References
----------
- Rao, G.V.R., "Exhaust Nozzle Contour for Optimum Thrust", Jet Propulsion, 1958
- Huzel & Huang, Modern Engineering for Design of Liquid-Propellant Rocket Engines
- CHEMA graduation project (Kul et al., 2017), MATLAB Rao implementation
- Pattern inspiration: openrocketengine nozzle export (MIT) — reimplemented here
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass
class NozzleContour:
    """Inner-wall contour: axial x [m], radius y [m]."""

    x: np.ndarray
    y: np.ndarray
    contour_type: str
    throat_radius_m: float
    exit_radius_m: float
    area_ratio: float
    bell_fraction: float
    length_m: float

    def to_csv(self, path: str | Path, include_header: bool = True) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            if include_header:
                f.write("x_m,y_m,x_mm,y_mm\n")
            for xi, yi in zip(self.x, self.y, strict=True):
                f.write(f"{xi:.8f},{yi:.8f},{xi * 1000:.6f},{yi * 1000:.6f}\n")
        return path

    def to_xyz_cad(self, path: str | Path, units: str = "mm") -> Path:
        """Export XYZ points for SolidWorks 'Curve Through XYZ Points'.

        Column order: X Y Z with Z=0 planar curve in XY (revolution axis = X).
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        scale = 1000.0 if units == "mm" else 1.0
        with path.open("w", encoding="utf-8") as f:
            for xi, yi in zip(self.x, self.y, strict=True):
                f.write(f"{xi * scale:.6f},{yi * scale:.6f},0.000000\n")
        return path

    def to_dataframe(self):
        import pandas as pd

        return pd.DataFrame(
            {
                "x_m": self.x,
                "y_m": self.y,
                "x_mm": self.x * 1000,
                "y_mm": self.y * 1000,
            }
        )


def conical_contour(
    throat_radius_m: float,
    area_ratio: float,
    half_angle_deg: float = 15.0,
    num_points: int = 80,
) -> NozzleContour:
    """Simple conical divergent nozzle (throat to exit only)."""
    if throat_radius_m <= 0 or area_ratio <= 1.0:
        raise ValueError("Need positive Rt and area_ratio > 1")
    re = throat_radius_m * np.sqrt(area_ratio)
    ln = (re - throat_radius_m) / np.tan(np.deg2rad(half_angle_deg))
    x = np.linspace(0.0, ln, num_points)
    y = throat_radius_m + x * np.tan(np.deg2rad(half_angle_deg))
    return NozzleContour(
        x=x,
        y=y,
        contour_type="conical",
        throat_radius_m=throat_radius_m,
        exit_radius_m=float(re),
        area_ratio=area_ratio,
        bell_fraction=1.0,
        length_m=float(ln),
    )


def rao_bell_contour(
    throat_radius_m: float,
    area_ratio: float,
    bell_fraction: float = 0.8,
    theta_n_deg: float = 40.0,
    n_fc: int = 20,
    n_sc: int = 12,
    n_bell: int = 60,
    include_chamber: bool = False,
    contraction_ratio: float = 4.0,
) -> NozzleContour:
    """Rao-style parabolic bell nozzle (CHEMA / classic 80%-bell construction).

    Parameters
    ----------
    throat_radius_m
        Throat radius Rt [m]
    area_ratio
        Ae/At
    bell_fraction
        Fraction of 15° conical length (0.8 = classic 80% bell)
    theta_n_deg
        Inflection angle after throat (CHEMA default 40°)
    include_chamber
        If True, prepend a short cylindrical chamber + convergent arc
    contraction_ratio
        Ac/At when chamber is included
    """
    rt = float(throat_radius_m)
    eps = float(area_ratio)
    if rt <= 0 or eps <= 1.0:
        raise ValueError("Need positive Rt and area_ratio > 1")
    if not (0.5 <= bell_fraction <= 1.0):
        raise ValueError("bell_fraction typically in [0.5, 1.0]")

    re = rt * np.sqrt(eps)
    # Length of 80% (or f%) bell relative to 15° cone
    ln = bell_fraction * (np.sqrt(eps) - 1.0) * rt / np.tan(np.deg2rad(15.0))
    theta_n = np.deg2rad(theta_n_deg)

    # --- First curve (entrance / upstream of throat): R = 1.5 Rt ---
    # CHEMA: from -3π/4 to -π/2
    theta_fc = np.linspace(-0.75 * np.pi, -0.5 * np.pi, n_fc)
    r_fc = 1.5 * rt
    x_fc = np.cos(theta_fc) * r_fc
    y_fc = np.sin(theta_fc) * r_fc + (r_fc + rt)

    # --- Second curve (downstream throat): R = 0.382 Rt ---
    theta_sc = np.linspace(-0.5 * np.pi, theta_n - 0.5 * np.pi, n_sc)
    r_sc = 0.382 * rt
    x_sc = np.cos(theta_sc) * r_sc
    y_sc = np.sin(theta_sc) * r_sc + (r_sc + rt)

    # --- Parabolic bell: x = a y^2 + b y + c ---
    x_tc = np.cos(theta_n - 0.5 * np.pi) * r_sc
    y_tc = np.sin(theta_n - 0.5 * np.pi) * r_sc + (r_sc + rt)
    # Match: at (x_tc, y_tc), slope = tan(theta_n); at exit y=re, x=Ln
    # matrix from CHEMA: [y^2, y, 1; y_e^2, y_e, 1; 2y, 1, 0] * [a;b;c] = [x; Ln; 1/tan]
    A = np.array(
        [
            [y_tc**2, y_tc, 1.0],
            [re**2, re, 1.0],
            [2.0 * y_tc, 1.0, 0.0],
        ],
        dtype=float,
    )
    rhs = np.array([x_tc, ln, 1.0 / np.tan(theta_n)], dtype=float)
    a, b, c = np.linalg.solve(A, rhs)
    y_bell = np.linspace(y_tc, re, n_bell)
    x_bell = a * y_bell**2 + b * y_bell + c

    # Shift so throat (min radius) is near x=0: throat is end of FC / start of SC
    x_div = np.concatenate([x_fc, x_sc, x_bell])
    y_div = np.concatenate([y_fc, y_sc, y_bell])
    # Find throat index (minimum y)
    i_th = int(np.argmin(y_div))
    x_div = x_div - x_div[i_th]

    xs = [x_div]
    ys = [y_div]

    if include_chamber:
        rc = rt * np.sqrt(contraction_ratio)
        # cylindrical chamber length ~ empirical CHEMA-ish L_c from Dt
        dt_cm = 2.0 * rt * 100.0
        # LCCM [cm] formula from CHEMA, then m
        lccm = np.exp(0.029 * np.log(dt_cm) ** 2 + 0.47 * np.log(dt_cm) + 1.94)
        lc = max(lccm / 100.0, 2.0 * rt)
        x0 = float(x_div[0])
        # cylinder from x0-lc to x0, radius rc
        x_cyl = np.linspace(x0 - lc, x0, 15)
        y_cyl = np.full_like(x_cyl, rc)
        xs.insert(0, x_cyl)
        ys.insert(0, y_cyl)

    x = np.concatenate(xs)
    y = np.concatenate(ys)
    # Deduplicate near-identical points
    keep = np.ones(len(x), dtype=bool)
    keep[1:] = np.sqrt(np.diff(x) ** 2 + np.diff(y) ** 2) > 1e-9
    x, y = x[keep], y[keep]

    return NozzleContour(
        x=x,
        y=y,
        contour_type="rao_bell" if not include_chamber else "rao_bell_with_chamber",
        throat_radius_m=rt,
        exit_radius_m=float(re),
        area_ratio=eps,
        bell_fraction=bell_fraction,
        length_m=float(x[-1] - x[0]),
    )


def contour_from_throat_area(
    throat_area_m2: float,
    area_ratio: float,
    kind: str = "rao",
    **kwargs,
) -> NozzleContour:
    rt = float(np.sqrt(throat_area_m2 / np.pi))
    if kind == "conical":
        return conical_contour(rt, area_ratio, **{k: v for k, v in kwargs.items() if k in ("half_angle_deg", "num_points")})
    return rao_bell_contour(rt, area_ratio, **kwargs)
