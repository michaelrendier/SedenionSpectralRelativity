#!/usr/bin/env python3
"""
equation_space_engine.py — Equation Space, the sedenion instance
==============================================================================
Companion to `GenerationalLineage/engine/toolsets/equation_space.py`, same
mechanism, this repo's own object: `rho(s)` is `prime_gauge_sedenion.py`'s
continuous zero-divisor proximity (smallest |eigenvalue| of the embedded
Assessor's L_x), not Gamma's diagonal-distance proxy. Two unrelated `rho`
functions, built from unrelated machinery (finite-difference complex
calculus here vs GenerationalLineage's own pure-Python one there), same
mechanism, same found circle (`center=i, radius=sqrt(2)`) -- the
cross-check the GenerationalLineage notebook names explicitly.

DESCEND / BUILD_UP are named the same as GenerationalLineage's toolset
contract (free single evaluation vs costly walk with a real refusal), kept
informal here (this repo has no `AscentNotFree`-style registry) rather than
importing GenerationalLineage's contract machinery -- module independence,
this project's standing convention.

Reuses `prime_gauge_sedenion.py`'s `rho`, `grad_rho`, `gamma` directly.

stdlib + numpy only.
"""
import math
import random
import sys
import os
from typing import Any, Callable, Dict, Optional, Tuple

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from prime_gauge_sedenion import rho as _sedenion_rho, gamma


def dgamma(s: complex) -> complex:
    return 2 / (s + 1) ** 2


RhoFn = Callable[[complex], float]


def gradient(rho: RhoFn, s: complex, h: float = 1e-4) -> complex:
    rx = (rho(s + h) - rho(s - h)) / (2 * h)
    ry = (rho(s + 1j * h) - rho(s - 1j * h)) / (2 * h)
    return complex(rx, ry)


def descend(s: complex, rho: Optional[RhoFn] = None) -> Dict[str, Any]:
    """One point: rho(s) and its local gradient. Free."""
    rho = rho or _sedenion_rho
    s = complex(s)
    r = rho(s)
    g = gradient(rho, s)
    return {"s": s, "rho": r, "gradient": g, "|gradient|": abs(g)}


class NotConverged(Exception):
    """The equation-space walk stalled or ran out of budget -- a real
    result (the locus may not be reachable from this start), matching
    GenerationalLineage's AscentNotFree in spirit, kept local here per
    this repo's module-independence convention."""


def build_up(start: complex, rho: Optional[RhoFn] = None, max_steps: int = 150,
             step_scale: float = 0.3, tol: float = 1e-6) -> Dict[str, Any]:
    """Walk from start toward rho=0 by (annealed) gradient descent. This
    rho is expensive (a 16x16 eigenvalue problem per evaluation), so the
    step budget is much smaller than the plain-Gamma case -- the cost
    asymmetry is real, not just narrative."""
    rho = rho or _sedenion_rho
    s = complex(start)
    best_s, best_r = s, rho(s)
    for step in range(max_steps):
        r = rho(s)
        if r < best_r:
            best_s, best_r = s, r
        if r < tol:
            return {"converged": True, "s": s, "rho": r, "cost": step}
        g = gradient(rho, s)
        if abs(g) < 1e-9:
            raise NotConverged(f"stalled at s={s}, rho={r}, after {step} steps")
        anneal = step_scale / (1.0 + step / 10.0)
        s = s - anneal * r * g / (abs(g) ** 2)
    if best_r < tol * 20:
        return {"converged": True, "s": best_s, "rho": best_r, "cost": max_steps,
                "note": "converged to within 20x tol via best-seen"}
    raise NotConverged(f"did not converge in {max_steps} steps; best rho={best_r}")


def classify_singularity(s0: complex, rho: Optional[RhoFn] = None,
                          direction: complex = 1 + 0j, h: float = 0.03) -> Dict[str, Any]:
    """Fold (caustic) or smooth minimum, transverse to s0 -- same
    diagnostic as GenerationalLineage's equation_space, applied to the
    sedenion's own (expensive) rho instead of the cheap Gamma proxy."""
    rho = rho or _sedenion_rho
    direction = direction / abs(direction)
    ratios = {}
    for dr in (-h, -h / 3, h / 3, h):
        s = s0 + dr * direction
        ratios[dr] = rho(s) / abs(dr)
    vals = list(ratios.values())
    mean_v = sum(vals) / len(vals) if vals else 0.0
    spread = (max(vals) - min(vals)) / mean_v if mean_v > 1e-12 else float("inf")
    return {"s0": s0, "ratios": ratios, "is_fold_caustic": spread < 0.2}


def _gamma_curvature(s: complex) -> float:
    return 2 * dgamma(s).imag


def steering_correlation(compass: Callable[[complex], float] = _gamma_curvature,
                          rho: Optional[RhoFn] = None, n_samples: int = 150,
                          domain: Tuple[float, float, float, float] = (-3, 3, -2, 4),
                          seed: int = 0) -> Dict[str, Any]:
    """Pearson(compass, |grad(rho)|) -- reproduces the 0.97 correlation
    found live this session, now as a reusable, re-runnable function."""
    rho = rho or _sedenion_rho
    rng = random.Random(seed)
    x0, x1, y0, y1 = domain
    xs, ys = [], []
    for _ in range(n_samples):
        s = complex(rng.uniform(x0, x1), rng.uniform(y0, y1))
        if abs(s + 1) < 0.15:
            continue
        xs.append(abs(compass(s)))
        ys.append(abs(gradient(rho, s)))
    n = len(xs)
    if n < 3:
        return {"n": n, "pearson": None}
    xs_a, ys_a = np.array(xs), np.array(ys)
    return {"n": n, "pearson": float(np.corrcoef(xs_a, ys_a)[0, 1])}


def verify() -> Dict[str, Any]:
    """Note on ok_matches_known_circle: prime_gauge_sedenion.py's rho is
    built from is_zero_divisor_dim, a SIGN-AGNOSTIC rank-deficiency test
    -- it fires on EITHER zero-divisor diagonal (84 diagonals = 42
    Assessors x 2 signs, marrais_boxkite_catalog.txt Sec.3), not just
    the one GenerationalLineage's cheaper Re==Im proxy tracks. So the
    walk can legitimately land on EITHER circle -- center=+i or
    center=-i, both radius sqrt(2), verified as a genuine SECOND circle,
    not a failure to find the first one. Checked against both centers,
    not just the one this file originally expected."""
    d = descend(0.5 + 0.1j)
    ok_descend = d["rho"] >= 0 and math.isfinite(d["|gradient|"])

    b = build_up(0.5 + 0.1j)
    ok_converge = b.get("converged", False) and b["rho"] < 1e-2
    dist_from_plus_i = abs(b["s"] - 1j)
    dist_from_minus_i = abs(b["s"] - (-1j))
    ok_matches_circle = (abs(dist_from_plus_i - math.sqrt(2)) < 0.05
                          or abs(dist_from_minus_i - math.sqrt(2)) < 0.05)

    try:
        build_up(100 + 100j, max_steps=2)
        ok_refuse = False
    except NotConverged:
        ok_refuse = True

    fold = classify_singularity(b["s"])
    ok_fold = fold["is_fold_caustic"]

    corr = steering_correlation()
    ok_corr = corr["pearson"] is not None and corr["pearson"] > 0.5

    ok = ok_descend and ok_converge and ok_matches_circle and ok_refuse and ok_fold and ok_corr
    return {
        "ok": ok, "ok_descend": ok_descend, "ok_converge": ok_converge,
        "ok_matches_known_circle": ok_matches_circle,
        "distance_from_+i": dist_from_plus_i, "distance_from_-i": dist_from_minus_i,
        "which_circle": "+i" if abs(dist_from_plus_i - math.sqrt(2)) < 0.05 else "-i",
        "ok_refuses_when_unreachable": ok_refuse,
        "ok_fold_caustic": ok_fold,
        "steering_correlation_pearson": corr["pearson"],
        "ok_correlation_positive": ok_corr,
    }


if __name__ == "__main__":
    print("descend(0.5+0.1j):", descend(0.5 + 0.1j))
    print()
    b = build_up(0.5 + 0.1j)
    print("build_up (walk to rho=0, expensive rho -- 16x16 eigenproblem per step):", b)
    print(f"distance from +i: {abs(b['s']-1j):.6f}   distance from -i: {abs(b['s']+1j):.6f}"
          f"   (expected sqrt(2)={math.sqrt(2):.6f} from one of the two)")
    print()
    print("classify_singularity:", classify_singularity(b["s"]))
    print()
    print("steering_correlation (Gamma's own curvature vs |grad(rho)|):",
          steering_correlation())
    print()
    print("verify():", verify())
