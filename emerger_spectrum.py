#!/usr/bin/env python3
"""
emerger_spectrum.py — The Sedenion Bracketing Spectrograph
==========================================================
"factoral is the generalized, Spectral is Sedenion focused"  — Cody, 2026-09-01

The Emerger, rendered as a spectrograph.  Bracket a 16-channel sedenion path
five ways; the FIRING ORDER is the dispersion; each bracket is a BAND.

    {1:15}     the R | imaginary split            -> Re, N, conj, inverse
    {2:14}     the (e0,e8) doubling plane          -> the pointer z, |z| - Omega
    {8:8}      the  O ‖ZD‖ S  fault               -> |a|-|b| = distance from the
                                                     ZD equator (zd_boundary.py's
                                                     critical line), the sheet, J_2
    {4:4:4:4}  four H blocks                       -> four SU(2) phases, sigma_RB
                                                     tilt/axis, Sigma_tilt = net work
    {4:8:4}    the gain spectrum  0 / 1 / sqrt2    -> multiplicative role

This is a REFINEMENT of the repo's CD-tower layer table
(README:  R -> C -> H -> O ‖ZD‖ S).  {8:8} is the ZD fault itself.

e_0 (real) is the ANCHOR — the tilt to the i axis — never bracketed; every
imaginary group is paired against it.  The firing order can be canonical
(dependency) or sigma_RB-phased (Sigma_tilt rotates the entry into the 12-step
precession, 4 d* faces : 3 Lambert-W faces).

Input : any text (P1-style prime hash seeds the 16 channels), or --vec "e1+e10".
Output: a text spectrum + emerger_spectrum.svg  (bands x firing order).

stdlib only.  Exact ZD test via Fraction.  Generalized engine:
FactoralDecomposition/engine/emerger.py ; ValaQuenta/modules/emerger/.
"""
import sys, os, math
from fractions import Fraction as F

DIM = 16
D_STAR  = 0.24605966
OMEGA   = D_STAR * math.log(10)          # W(1) = 0.56714..., the Omega constant
SIGMA   = 0.5
PRIMES  = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53]

# CD-tower layers (README table) — the emerger brackets refine this
LAYERS = [("R", 1), ("C", 2), ("H", 4), ("O", 8), ("ZD fault", 8), ("S", 16)]


# ── Cayley-Dickson algebra (exact, Fraction) ──────────────────────────────────
def cd_conj(x):
    return (x[0],) + tuple(-c for c in x[1:])

def cd_mul(a, b):
    n = len(a)
    if n == 1:
        return (a[0] * b[0],)
    h = n // 2
    a1, a2, b1, b2 = a[:h], a[h:], b[:h], b[h:]
    c1 = tuple(p - q for p, q in zip(cd_mul(a1, b1), cd_mul(cd_conj(b2), a2)))
    c2 = tuple(p + q for p, q in zip(cd_mul(b2, a1), cd_mul(a2, cd_conj(b1))))
    return c1 + c2

def e(k):
    v = [F(0)] * DIM; v[k] = F(1); return tuple(v)

def left_matrix(a):
    cols = [cd_mul(a, e(k)) for k in range(DIM)]
    return [[cols[k][r] for k in range(DIM)] for r in range(DIM)]

def mat_rank(M):
    M = [row[:] for row in M]; rows = len(M); r = 0
    for c in range(len(M[0])):
        piv = next((i for i in range(r, rows) if M[i][c] != 0), None)
        if piv is None:
            continue
        M[r], M[piv] = M[piv], M[r]
        inv = M[r][c]; M[r] = [v / inv for v in M[r]]
        for i in range(rows):
            if i != r and M[i][c] != 0:
                f = M[i][c]; M[i] = [a - f * b for a, b in zip(M[i], M[r])]
        r += 1
        if r == rows:
            break
    return r

def is_zero_divisor(x):
    if all(c == 0 for c in x):
        return False
    return mat_rank(left_matrix(x)) < DIM

def norm_sq(x):
    return sum((c * c for c in x), F(0))

def on_zd_equator(x):
    a, b = x[:8], x[8:]
    na, nb = norm_sq(a), norm_sq(b)
    return a[0] == 0 and b[0] == 0 and na == nb and na != 0


# ── sigma_RB : tilt (Scale) and axis (Flow) ──────────────────────────────────
def sigma_rb(x):
    def g(i):
        return x[(i + 8) % DIM]
    tilt = [x[k] * x[k ^ 4] + g(k) * g(k ^ 4) for k in range(DIM)]
    axis = [g(k) * x[k ^ 4] - x[k] * g(k ^ 4) for k in range(DIM)]
    return sum(tilt, F(0)), sum(axis, F(0))

def firing_phase(sigma_tilt):
    a = sigma_tilt if sigma_tilt >= 0 else -sigma_tilt
    u = (sigma_tilt / (1 + a) + 1) / 2
    step12 = int(u * 12)
    step12 = 0 if step12 < 0 else (11 if step12 > 11 else step12)
    return step12, step12 % 5


# ── the five brackets ────────────────────────────────────────────────────────
CANONICAL = ["{1:15}", "{2:14}", "{8:8}", "{4:4:4:4}", "{4:8:4}"]
GAIN = {0: "annihilator (0)", 1: "unit (1, NOW)", 2: "amplifier (sqrt2)"}


def band_readout(name, x):
    """One band's emergent readout + a scalar 'line strength' for the SVG."""
    fx = [float(c) for c in x]
    if name == "{1:15}":
        return {"Re": fx[0], "N": float(norm_sq(x))}, abs(fx[0])
    if name == "{2:14}":
        rz, iz = fx[0], fx[8]
        mz = (rz * rz + iz * iz) ** 0.5
        return {"z": (rz, iz), "|z|-Omega": mz - OMEGA}, mz
    if name == "{8:8}":
        na = float(norm_sq(x[:8])) ** 0.5
        nb = float(norm_sq(x[8:])) ** 0.5
        return {"|a|-|b|": na - nb, "on_zd_equator": on_zd_equator(x),
                "is_zero_divisor": is_zero_divisor(x)}, abs(na - nb)
    if name == "{4:4:4:4}":
        st, sa = sigma_rb(x)
        return {"Sigma_tilt": float(st), "Sigma_axis": float(sa),
                "sigma=1/2": st == 0}, abs(float(st))
    if name == "{4:8:4}":
        g0 = sum(fx[i] ** 2 for i in (4, 5, 6, 7))
        g1 = sum(fx[i] ** 2 for i in (1, 2, 3, 8, 9, 10, 11))
        g2 = sum(fx[i] ** 2 for i in (12, 13, 14, 15))
        cls = GAIN[max(((g0, 0), (g1, 1), (g2, 2)))[1]]
        return {"gain_class": cls}, max(g0, g1, g2)
    return {}, 0.0


def spectrum(x, mode="sigma_rb"):
    st, _ = sigma_rb(x)
    step12, entry = firing_phase(st)
    order = [CANONICAL[(entry + i) % 5] for i in range(5)] if mode == "sigma_rb" else CANONICAL[:]
    bands = []
    for i, name in enumerate(order):
        readout, strength = band_readout(name, x)
        bands.append({"pos": i, "band": name, "readout": readout, "strength": strength})
    return {"Sigma_tilt": float(st), "precession_step_of_12": step12,
            "entry": entry, "order": order, "bands": bands}


# ── text -> 16-vector (P1-style prime hash, cf. fano_oscilloscope.py) ─────────
def text_to_vec(text):
    def word_phase(word, p):
        h = 0
        for ch in word:
            h = (h * 95 + (ord(ch) - 32)) & 0xFFFF
        return (h % p) / p
    parts = text.split() or [text]
    acc = [0.0] * DIM
    for k, p in enumerate(PRIMES):
        for w in parts:
            acc[k] += math.cos(2 * math.pi * word_phase(w, p)) / (k + 1) ** 0.5
    n = math.sqrt(sum(c * c for c in acc)) or 1.0
    return tuple(F(round(c / n, 9)).limit_denominator(10 ** 6) for c in acc)


def parse_vec(spec):
    acc = [F(0)] * DIM
    for tok in spec.replace(" ", "").replace("-", "+-").split("+"):
        if not tok:
            continue
        sign = F(-1) if tok.startswith("-") else F(1)
        tok = tok.lstrip("-")
        if "*e" in tok:
            c, idx = tok.split("*e"); acc[int(idx)] += sign * F(c)
        elif tok.startswith("e"):
            acc[int(tok[1:])] += sign
        else:
            acc[0] += sign * F(tok)
    return tuple(acc)


# ── SVG spectrograph : bands x firing order ─────────────────────────────────
def render_svg(spec, title, path="emerger_spectrum.svg"):
    W, H = 900, 360
    x0, y0, bw, bh = 70, 40, 150, 46
    colors = {"{1:15}": "#c0c0c0", "{2:14}": "#60a0ff", "{8:8}": "#ff5070",
              "{4:4:4:4}": "#40c080", "{4:8:4}": "#ffa040"}
    strengths = [b["strength"] for b in spec["bands"]] or [1.0]
    smax = max(strengths) or 1.0
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
           f'viewBox="0 0 {W} {H}" font-family="monospace">',
           f'<rect width="{W}" height="{H}" fill="#0a0a12"/>',
           f'<text x="{x0}" y="24" fill="#ddd" font-size="14">{title}  '
           f'(Sigma_tilt={spec["Sigma_tilt"]:+.4f}, precession {spec["precession_step_of_12"]}/12)</text>']
    for b in spec["bands"]:
        cx = x0 + b["pos"] * (bw + 8)
        alpha = 0.25 + 0.75 * (b["strength"] / smax)
        col = colors.get(b["band"], "#888")
        out.append(f'<rect x="{cx}" y="{y0}" width="{bw}" height="{bh}" '
                   f'fill="{col}" fill-opacity="{alpha:.2f}" stroke="#222"/>')
        out.append(f'<text x="{cx + 6}" y="{y0 + 18}" fill="#000" font-size="12" '
                   f'font-weight="bold">{b["band"]}</text>')
        rd = "  ".join(f'{k}={v}' for k, v in list(b["readout"].items())[:2])
        out.append(f'<text x="{cx + 6}" y="{y0 + 36}" fill="#111" font-size="9">{rd[:26]}</text>')
        out.append(f'<text x="{cx + bw/2}" y="{y0 + bh + 16}" fill="#888" '
                   f'font-size="10" text-anchor="middle">fire {b["pos"]+1}</text>')
    # the ZD equator marker on the {8:8} band
    for b in spec["bands"]:
        if b["band"] == "{8:8}" and b["readout"].get("on_zd_equator"):
            cx = x0 + b["pos"] * (bw + 8)
            out.append(f'<text x="{cx + bw/2}" y="{y0 - 6}" fill="#ff5070" '
                       f'font-size="11" text-anchor="middle">ON THE ZD EQUATOR</text>')
    # the CD-tower layer strip this refines
    ly = y0 + bh + 60
    out.append(f'<text x="{x0}" y="{ly}" fill="#666" font-size="10">'
               f'refines the CD tower:  R -&gt; C -&gt; H -&gt; O &#8214;ZD&#8214; S</text>')
    out.append('</svg>')
    with open(path, "w") as f:
        f.write("\n".join(out))
    return path


def main():
    args = sys.argv[1:]
    mode = "sigma_rb"
    if args and args[0] == "--canonical":
        mode = "canonical"; args = args[1:]
    if args and args[0] == "--vec":
        vec = parse_vec(args[1]); label = args[1]
    elif args:
        text = " ".join(args); vec = text_to_vec(text); label = repr(text)
    else:
        vec = parse_vec("e1+e10"); label = "e1+e10  (a zero divisor on the equator)"

    spec = spectrum(vec, mode=mode)
    print(f"THE SEDENION BRACKETING SPECTROGRAPH   input: {label}")
    print(f"  Sigma_tilt = {spec['Sigma_tilt']:+.6f}   precession step "
          f"{spec['precession_step_of_12']}/12   entry band #{spec['entry']}")
    print(f"  firing order ({mode}):  {'  ->  '.join(spec['order'])}")
    print()
    for b in spec["bands"]:
        print(f"  [{b['pos']+1}] {b['band']:<10}  strength={b['strength']:.4g}")
        for k, v in b["readout"].items():
            print(f"        {k} = {v}")
    path = render_svg(spec, label, os.path.join(os.path.dirname(__file__) or ".",
                                                "emerger_spectrum.svg"))
    print(f"\n  wrote {path}")


if __name__ == "__main__":
    main()
