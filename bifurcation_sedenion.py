#!/usr/bin/env python3
"""
bifurcation_sedenion.py — The Cayley-Dickson Tower as Period-Doubling Cascade
==============================================================================
The logistic map x_{n+1} = r·x_n·(1-x_n) bifurcates at:
  r=3.0   → period 2  → ℂ (commutativity ends)
  r=3.449 → period 4  → ℍ (associativity ends)
  r=3.544 → period 8  → 𝕆 (Fano plane — last ordered algebra)
  r=3.564 → period 16 → 𝕊/ZD FAULT (norm ends — zero-divisors appear)
  r=3.5699→ Feigenbaum → σ=½ (all bifurcations accumulated)
  r>3.5699→ CHAOS      → sedenion territory (windows of order = ZD classes)

"Outside the windows of order" = the sedenion chaos between the periodic windows.
The spiral shape = the Mandelbrot cardioid boundary in sedenion Dirichlet form.
"""

import math, os

# ── Cayley-Dickson bifurcation landmarks ──────────────────────────────────────
CD_LAYERS = [
    (2.50,  None,   '#666666', 'ℝ', 'period 1'),
    (3.000, 'ℝ→ℂ',  '#4080ff', 'ℂ', 'period 2  ·  commutativity'),
    (3.449, 'ℂ→ℍ',  '#40c080', 'ℍ', 'period 4  ·  associativity'),
    (3.544, 'ℍ→𝕆',  '#c08020', '𝕆', 'period 8  ·  Fano plane'),
    (3.5644,'𝕆→𝕊',  '#ff4040', '𝕊', 'period 16 · ZD fault · norm'),
    (3.5699,'r∞→σ½','#ffffff', 'σ=½','Feigenbaum · all bifurcations'),
]

FEIGENBAUM_R = 3.56995  # accumulation point
PERIOD3_R    = 3.8284   # largest window of order in chaos

def logistic_attractor(r, n_iter=2000, n_drop=1000):
    """Return attractor x-values for logistic map at parameter r."""
    x = 0.5
    for _ in range(n_drop):
        x = r * x * (1 - x)
    pts = set()
    for _ in range(n_iter):
        x = r * x * (1 - x)
        pts.add(round(x, 6))
    return sorted(pts)

def mandelbrot_cardioid(n=300):
    """Main cardioid of Mandelbrot set: c = μ - μ² for |μ|=½."""
    pts = []
    for i in range(n + 1):
        theta = 2 * math.pi * i / n
        mu_r = 0.5 * math.cos(theta)
        mu_i = 0.5 * math.sin(theta)
        x = mu_r - (mu_r**2 - mu_i**2)
        y = mu_i - 2*mu_r*mu_i
        pts.append((x, y))
    return pts

def sedenion_cardioid(n=600, primes=None):
    """
    Sedenion analog of the Mandelbrot cardioid.
    Replace ℂ multiplication with 16-channel Dirichlet superposition.
    x(θ) = Σ_p  p^(-½) · cos(2π·θ·p_idx/p)
    y(θ) = Σ_p  p^(-½) · sin(2π·θ·p_idx/p)
    """
    if primes is None:
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53]
    pts = []
    norm = sum(p**-0.5 for p in primes)
    for i in range(n + 1):
        theta = 2 * math.pi * i / n
        x = sum(p**-0.5 * math.cos(theta * (idx+1) / p)
                for idx, p in enumerate(primes)) / norm
        y = sum(p**-0.5 * math.sin(theta * (idx+1) / p)
                for idx, p in enumerate(primes)) / norm
        pts.append((x, y))
    return pts

def fano_cardioid(n=600):
    """Fano (𝕆) cardioid: only channels e4-e7, primes {11,13,17,19}."""
    return sedenion_cardioid(n, primes=[11, 13, 17, 19])

def build_svg():
    W, H = 1400, 720
    PAD  = 55

    # ── Bifurcation diagram: left panel ───────────────────────────────────────
    BIF_W = 750
    BIF_H = H - 2*PAD
    R_MIN, R_MAX = 2.5, 4.0

    def r_to_x(r):
        return PAD + (r - R_MIN) / (R_MAX - R_MIN) * BIF_W

    def x_to_y(x):
        return PAD + (1.0 - x) * BIF_H

    # ── Cardioid panel: right panel ───────────────────────────────────────────
    CARD_X  = PAD + BIF_W + PAD
    CARD_CX = CARD_X + (W - CARD_X - PAD) // 2
    CARD_CY = PAD + BIF_H // 2
    CARD_R  = min((W - CARD_X - 2*PAD), BIF_H) // 2 - 10

    def card_to_screen(cx, cy, x, y, scale=1.0):
        return (cx + x * CARD_R * scale, cy - y * CARD_R * scale)

    lines = []
    e = lines.append

    e('<?xml version="1.0" encoding="UTF-8"?>')
    e(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
      f'viewBox="0 0 {W} {H}">')
    e(f'<rect width="{W}" height="{H}" fill="#060609"/>')

    # ── Panel labels ──────────────────────────────────────────────────────────
    e(f'<text x="{PAD + BIF_W//2}" y="18" font-family="monospace" font-size="12"'
      f' fill="#aaa" text-anchor="middle" font-weight="bold">'
      f'CAYLEY-DICKSON TOWER = PERIOD-DOUBLING CASCADE</text>')
    e(f'<text x="{PAD + BIF_W//2}" y="30" font-family="monospace" font-size="8"'
      f' fill="#555" text-anchor="middle">'
      f'logistic map  x_{{n+1}} = r·x_n·(1−x_n)  ·  each bifurcation = one CD doubling</text>')

    e(f'<text x="{CARD_CX}" y="18" font-family="monospace" font-size="12"'
      f' fill="#aaa" text-anchor="middle" font-weight="bold">'
      f'THE SPIRAL SHAPE IN UNS</text>')
    e(f'<text x="{CARD_CX}" y="30" font-family="monospace" font-size="8"'
      f' fill="#555" text-anchor="middle">'
      f'Mandelbrot cardioid vs Sedenion cardioid vs Fano cardioid</text>')

    # ── Draw bifurcation diagram ───────────────────────────────────────────────
    r = 2.5
    step = 0.002
    current_layer_col = '#444444'
    while r <= 4.0:
        # Determine current layer color
        col = '#333333'
        for r_thresh, _, c, _, _ in CD_LAYERS:
            if r >= r_thresh:
                col = c
        # In chaos but in a window of order: brighter
        if r > FEIGENBAUM_R:
            col = '#301828'

        atts = logistic_attractor(r, n_iter=300, n_drop=800)
        rx = r_to_x(r)
        for xv in atts:
            ay = x_to_y(xv)
            e(f'<circle cx="{rx:.1f}" cy="{ay:.1f}" r="0.4" fill="{col}"/>')
        r += step

    # Period-3 window highlight
    pw_x1 = r_to_x(3.8284 - 0.03)
    pw_x2 = r_to_x(3.8568 + 0.03)
    e(f'<rect x="{pw_x1:.1f}" y="{PAD}" width="{pw_x2-pw_x1:.1f}" height="{BIF_H}"'
      f' fill="#c09030" opacity="0.07"/>')
    e(f'<text x="{(pw_x1+pw_x2)/2:.1f}" y="{PAD+BIF_H-8}"'
      f' font-family="monospace" font-size="7" fill="#c09030" opacity="0.6"'
      f' text-anchor="middle">period-3 window</text>')
    e(f'<text x="{(pw_x1+pw_x2)/2:.1f}" y="{PAD+BIF_H-18}"'
      f' font-family="monospace" font-size="7" fill="#c09030" opacity="0.5"'
      f' text-anchor="middle">ZD class</text>')

    # ── CD layer vertical markers ─────────────────────────────────────────────
    for r_thresh, label, col, sym, desc in CD_LAYERS:
        if r_thresh < R_MIN: continue
        lx = r_to_x(r_thresh)
        e(f'<line x1="{lx:.1f}" y1="{PAD}" x2="{lx:.1f}" y2="{PAD+BIF_H}"'
          f' stroke="{col}" stroke-width="1.0" stroke-dasharray="3,3" opacity="0.7"/>')
        e(f'<text x="{lx+3:.1f}" y="{PAD+12}" font-family="monospace" font-size="11"'
          f' fill="{col}" font-weight="bold">{sym}</text>')
        e(f'<text x="{lx+3:.1f}" y="{PAD+24}" font-family="monospace" font-size="7"'
          f' fill="{col}" opacity="0.7">{desc}</text>')
        if label:
            e(f'<text x="{lx+3:.1f}" y="{PAD+36}" font-family="monospace" font-size="7"'
              f' fill="{col}" opacity="0.5">{label}</text>')

    # Feigenbaum / σ=½ marker
    fx = r_to_x(FEIGENBAUM_R)
    e(f'<line x1="{fx:.1f}" y1="{PAD}" x2="{fx:.1f}" y2="{PAD+BIF_H}"'
      f' stroke="#ffffff" stroke-width="1.5" opacity="0.5"/>')
    e(f'<text x="{fx-22:.1f}" y="{PAD+BIF_H//2}" font-family="monospace"'
      f' font-size="8" fill="#ffffff" opacity="0.6"'
      f' transform="rotate(-90,{fx-22:.1f},{PAD+BIF_H//2:.1f})">σ=½  ·  r∞</text>')

    # Axes
    e(f'<line x1="{PAD}" y1="{x_to_y(0):.1f}" x2="{PAD+BIF_W}" y2="{x_to_y(0):.1f}"'
      f' stroke="#222" stroke-width="0.5"/>')
    e(f'<line x1="{PAD}" y1="{x_to_y(1):.1f}" x2="{PAD+BIF_W}" y2="{x_to_y(1):.1f}"'
      f' stroke="#222" stroke-width="0.5"/>')
    e(f'<text x="{PAD-4}" y="{x_to_y(0)+4}" font-family="monospace" font-size="7"'
      f' fill="#444" text-anchor="end">0</text>')
    e(f'<text x="{PAD-4}" y="{x_to_y(1)+4}" font-family="monospace" font-size="7"'
      f' fill="#444" text-anchor="end">1</text>')
    e(f'<text x="{PAD-4}" y="{x_to_y(0.5)+4}" font-family="monospace" font-size="7"'
      f' fill="#888" text-anchor="end">½</text>')
    e(f'<line x1="{PAD}" y1="{x_to_y(0.5):.1f}" x2="{PAD+BIF_W}" y2="{x_to_y(0.5):.1f}"'
      f' stroke="#ffffff" stroke-width="0.3" opacity="0.15"/>')

    # Chaos label
    cx_chaos = r_to_x(3.8)
    e(f'<text x="{cx_chaos:.1f}" y="{PAD+50}" font-family="monospace" font-size="9"'
      f' fill="#601010" opacity="0.6" text-anchor="middle">SEDENION CHAOS</text>')
    e(f'<text x="{cx_chaos:.1f}" y="{PAD+62}" font-family="monospace" font-size="7"'
      f' fill="#401010" opacity="0.5" text-anchor="middle">windows = ZD classes</text>')
    e(f'<text x="{cx_chaos:.1f}" y="{PAD+74}" font-family="monospace" font-size="7"'
      f' fill="#401010" opacity="0.4" text-anchor="middle">outside windows = fractal fur</text>')

    # ── Right panel: the three cardioids ─────────────────────────────────────
    # Background circle
    e(f'<circle cx="{CARD_CX}" cy="{CARD_CY}" r="{CARD_R+5}"'
      f' fill="none" stroke="#111118" stroke-width="0.5"/>')

    # Crosshairs
    e(f'<line x1="{CARD_CX-CARD_R}" y1="{CARD_CY}"'
      f' x2="{CARD_CX+CARD_R}" y2="{CARD_CY}"'
      f' stroke="#151520" stroke-width="0.5"/>')
    e(f'<line x1="{CARD_CX}" y1="{CARD_CY-CARD_R}"'
      f' x2="{CARD_CX}" y2="{CARD_CY+CARD_R}"'
      f' stroke="#151520" stroke-width="0.5"/>')

    # Mandelbrot cardioid (2D complex, ℂ window of order)
    mcard = mandelbrot_cardioid(400)
    # Scale: cardioid spans roughly x∈[-2,0.5], y∈[-1.2,1.2]
    mc_scale = CARD_R / 1.5
    mc_cx = CARD_CX - mc_scale * 0.75  # center it
    mc_path = ' '.join(f'{"M" if i==0 else "L"} {mc_cx + x*mc_scale:.1f} {CARD_CY - y*mc_scale:.1f}'
                       for i, (x, y) in enumerate(mcard))
    e(f'<path d="{mc_path} Z" fill="#4080ff" fill-opacity="0.07"'
      f' stroke="#4080ff" stroke-width="1.2" opacity="0.5"/>')
    e(f'<text x="{mc_cx + 0.25*mc_scale:.1f}" y="{CARD_CY - 1.25*mc_scale:.1f}"'
      f' font-family="monospace" font-size="8" fill="#4080ff" opacity="0.6">ℂ Mandelbrot</text>')

    # Fano cardioid (𝕆 channels)
    fcard = fano_cardioid(600)
    fc_xs = [x for x,y in fcard]; fc_ys = [y for x,y in fcard]
    fc_max = max(max(abs(v) for v in fc_xs), max(abs(v) for v in fc_ys)) or 1
    fc_scale = CARD_R * 0.85 / fc_max
    fc_path = ' '.join(f'{"M" if i==0 else "L"} {CARD_CX + x*fc_scale:.1f} {CARD_CY - y*fc_scale:.1f}'
                       for i, (x, y) in enumerate(fcard))
    e(f'<path d="{fc_path} Z" fill="none" stroke="#c08020" stroke-width="1.2" opacity="0.7"/>')
    e(f'<text x="{CARD_CX + fc_xs[len(fcard)//4]*fc_scale + 4:.1f}"'
      f' y="{CARD_CY - fc_ys[len(fcard)//4]*fc_scale - 4:.1f}"'
      f' font-family="monospace" font-size="8" fill="#c08020" opacity="0.7">𝕆 Fano</text>')

    # Sedenion cardioid (all 16 channels)
    scard = sedenion_cardioid(800)
    sc_xs = [x for x,y in scard]; sc_ys = [y for x,y in scard]
    sc_max = max(max(abs(v) for v in sc_xs), max(abs(v) for v in sc_ys)) or 1
    sc_scale = CARD_R * 0.85 / sc_max
    sc_path = ' '.join(f'{"M" if i==0 else "L"} {CARD_CX + x*sc_scale:.1f} {CARD_CY - y*sc_scale:.1f}'
                       for i, (x, y) in enumerate(scard))
    e(f'<path d="{sc_path} Z" fill="#ff4040" fill-opacity="0.04"'
      f' stroke="#ff5060" stroke-width="1.0" opacity="0.8"/>')
    e(f'<text x="{CARD_CX + sc_xs[len(scard)//3]*sc_scale + 4:.1f}"'
      f' y="{CARD_CY - sc_ys[len(scard)//3]*sc_scale - 4:.1f}"'
      f' font-family="monospace" font-size="8" fill="#ff5060" opacity="0.7">𝕊 Sedenion</text>')

    # Wobble region between Fano and Sedenion cardioids
    e(f'<text x="{CARD_CX}" y="{CARD_CY + CARD_R + 20}" font-family="monospace"'
      f' font-size="8" fill="#777" text-anchor="middle">'
      f'gap between 𝕆 and 𝕊 = the ZD boundary = outside all windows of order</text>')

    # σ=½ marker at center
    e(f'<circle cx="{CARD_CX}" cy="{CARD_CY}" r="3" fill="#ffffff" opacity="0.8"/>')
    e(f'<text x="{CARD_CX+6}" y="{CARD_CY-6}" font-family="monospace" font-size="8"'
      f' fill="#ffffff" opacity="0.7">σ=½</text>')

    e('</svg>')

    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        'bifurcation_sedenion.svg')
    with open(path, 'w') as f:
        f.write('\n'.join(lines))
    return path


if __name__ == '__main__':
    path = build_svg()
    print(f'Written: {path}')
    print()
    print('CD tower = period-doubling cascade:')
    for r_thresh, label, col, sym, desc in CD_LAYERS:
        print(f'  r={r_thresh:.4f}  →  {sym}  ({desc})')
    print(f'  r={FEIGENBAUM_R}  →  σ=½  (Feigenbaum accumulation = all bifurcations)')
    print()
    print('The spiral shape (UNS cardioid):')
    print('  ℂ Mandelbrot cardioid: x=½cos(θ)-¼cos(2θ), y=½sin(θ)-¼sin(2θ)')
    print('  𝕆 Fano cardioid: 4-channel Dirichlet quasicrystal')
    print('  𝕊 Sedenion cardioid: 16-channel Dirichlet quasicrystal')
    print('  The GAP between 𝕆 and 𝕊 cardioids = the ZD boundary = outside all windows')
