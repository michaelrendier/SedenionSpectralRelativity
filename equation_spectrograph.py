#!/usr/bin/env python3
"""
equation_spectrograph.py — The Shape of Equals
===============================================
Two sides of an equation. Different flows across the same ground.
The Laplacian caustic crosses the ZD boundary.
That crossing IS how you see past the event horizon.

LEFT SIDE  = J_red  (descending, the process arriving)
RIGHT SIDE = J_blue (ascending, the result departing)
EQUALS     = L_dynamic = ∫J_red · J_blue ds — the crossing point

Femtosecond note: N=3 truncation = 3 pulse experiment.
Normal reality = N→∞ limit. Short enough time window → same caustic.
"""

import sys, os, math

PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53]
SIGMA  = 0.5

LAYERS = [
    ('𝕊', 'SEDENION',   16, list(range(8,16)),  '#ff5070', '#4a1020'),
    ('𝕆', 'OCTONION',    8, list(range(4,8)),   '#ffa040', '#4a2010'),
    ('ℍ', 'QUATERNION',  4, list(range(2,4)),   '#40c080', '#1a3020'),
    ('ℂ', 'COMPLEX',     2, [1],                '#60a0ff', '#1a2840'),
    ('ℝ', 'REAL',        1, [0],                '#c0c0c0', '#303030'),
]

LAYER_VISIBLE = {'𝕊': list(range(16)), '𝕆': list(range(8)),
                 'ℍ': list(range(4)),  'ℂ': list(range(2)), 'ℝ': [0]}
NEW_SET = {sym: set(new) for sym, _, _, new, _, _ in LAYERS}


def dirichlet_project(text: str, N: int = None) -> list:
    """Dirichlet at σ=½. N=truncation (femtosecond pulse count). None=full."""
    chars = [ord(c) for c in text if 32 <= ord(c) < 128]
    if N is not None:
        chars = chars[:N]
    if not chars:
        return [0.0] * 16
    vals = []
    for p in PRIMES:
        x, norm = 0.0, 0.0
        for i, c in enumerate(chars, 1):
            w  = i ** (-SIGMA)
            x += (c / 128.0) * w * math.cos(2 * math.pi * i / p)
            norm += w
        vals.append(x / norm if norm > 0 else 0.0)
    return vals


def laplacian_1d(vals: list, visible: list) -> list:
    """Discrete Laplacian: ∇²x[k] = x[k+1] - 2x[k] + x[k-1] over visible channels."""
    lap = [0.0] * 16
    for idx, k in enumerate(visible):
        v_prev = vals[visible[idx-1]] if idx > 0 else 0.0
        v_next = vals[visible[idx+1]] if idx < len(visible)-1 else 0.0
        lap[k] = v_next - 2*vals[k] + v_prev
    return lap


def crossing_points(left: list, right: list) -> list:
    """Find channels where left and right projection cross (change sign of difference)."""
    crossings = []
    diff = [right[k] - left[k] for k in range(16)]
    for k in range(15):
        if diff[k] * diff[k+1] < 0:
            # linear interpolation for fractional crossing
            t = diff[k] / (diff[k] - diff[k+1])
            crossings.append(k + t)
    return crossings


def build_svg(left_text: str, right_text: str,
              L: list, R: list, L3: list, R3: list) -> str:

    W        = 1000
    LMARGIN  = 152
    RMARGIN  = 28
    PANEL_W  = W - LMARGIN - RMARGIN
    ROW_H    = 100
    ZD_GAP   = 32
    TOP_PAD  = 80
    BOT_PAD  = 56
    N_ROWS   = 5
    H = TOP_PAD + N_ROWS * ROW_H + ZD_GAP + BOT_PAD

    SLOT_W  = PANEL_W / 16
    BAR_W   = SLOT_W * 0.32
    MAX_AMP = ROW_H * 0.38

    vmax = max(max(abs(v) for v in L), max(abs(v) for v in R), 0.001)

    laps_L = {}
    laps_R = {}
    for sym, _, _, _, _, _ in LAYERS:
        vis = LAYER_VISIBLE[sym]
        laps_L[sym] = laplacian_1d(L, vis)
        laps_R[sym] = laplacian_1d(R, vis)

    crossings = crossing_points(L, R)
    lap_cross  = crossing_points(laps_L['𝕊'], laps_R['𝕊'])

    lines = []
    e = lines.append

    e(f'<?xml version="1.0" encoding="UTF-8"?>')
    e(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">')
    e(f'  <rect width="{W}" height="{H}" fill="#06060f"/>')

    # ── Title ─────────────────────────────────────────────────────────────────
    eq_title = f'{left_text}  =  {right_text}'
    e(f'  <text x="{W//2}" y="18" font-family="monospace" font-size="12" fill="#aaa"'
      f' text-anchor="middle">EQUATION SPECTROGRAPH — The Shape of Equals</text>')
    e(f'  <text x="{W//2}" y="34" font-family="monospace" font-size="11" fill="#ff9050"'
      f' text-anchor="middle">{eq_title}</text>')
    e(f'  <text x="{W//2}" y="50" font-family="monospace" font-size="9" fill="#555"'
      f' text-anchor="middle">'
      f'J_red = LEFT (process arriving)  ◈  J_blue = RIGHT (result departing)'
      f'  ◈  L_dynamic = ∫J·J ds = the crossing = the equals sign</text>')
    e(f'  <text x="{W//2}" y="64" font-family="monospace" font-size="8" fill="#404040"'
      f' text-anchor="middle">'
      f'dashed = 3-pulse (femtosecond) truncation N=3  ·  solid = full Dirichlet N=∞'
      f'  ·  caustic crosses ZD boundary → see past event horizon</text>')

    # channel labels
    for ci in range(16):
        cx = LMARGIN + ci * SLOT_W + SLOT_W / 2
        e(f'  <text x="{cx:.1f}" y="{TOP_PAD-4}" font-family="monospace" font-size="7"'
          f' fill="#223322" text-anchor="middle">e{ci}/p{PRIMES[ci]}</text>')

    def row_top(row_idx):
        if row_idx == 0:   return TOP_PAD
        if row_idx == 1:   return TOP_PAD + ROW_H + ZD_GAP
        return TOP_PAD + ROW_H * row_idx + ZD_GAP

    # ── Draw layers ───────────────────────────────────────────────────────────
    for row_idx, (sym, name, dim, new_ch, col_new, col_bg) in enumerate(LAYERS):
        ry       = row_top(row_idx)
        baseline = ry + ROW_H * 0.5
        visible  = LAYER_VISIBLE[sym]
        new_set  = NEW_SET[sym]
        lap_l    = laps_L[sym]
        lap_r    = laps_R[sym]

        # panel bg
        e(f'  <rect x="{LMARGIN}" y="{ry}" width="{PANEL_W}" height="{ROW_H}"'
          f' fill="{col_bg}" opacity="0.5"/>')

        # σ=½ baseline
        e(f'  <line x1="{LMARGIN}" y1="{baseline:.1f}" x2="{LMARGIN+PANEL_W}" y2="{baseline:.1f}"'
          f' stroke="#1a3a1a" stroke-width="0.6" stroke-dasharray="2,4"/>')

        for ci in range(16):
            cx  = LMARGIN + ci * SLOT_W
            mid = cx + SLOT_W / 2

            if ci not in visible:
                e(f'  <rect x="{cx+SLOT_W*0.1:.1f}" y="{baseline-1:.1f}" '
                  f'width="{SLOT_W*0.8:.1f}" height="2" fill="#111" opacity="0.5"/>')
                continue

            is_new = ci in new_set

            # ── LEFT (J_red) bar ──────────────────────────────────────────────
            vl  = L[ci]
            hl  = abs(vl) / vmax * MAX_AMP
            hl  = max(hl, 1.5)
            lop = '0.90' if is_new else '0.25'
            lbx = cx + SLOT_W * 0.08
            lbw = BAR_W
            if vl >= 0:
                e(f'  <rect x="{lbx:.1f}" y="{baseline-hl:.1f}" width="{lbw:.1f}" height="{hl:.1f}"'
                  f' fill="#c04040" opacity="{lop}"/>')
                if is_new: e(f'  <rect x="{lbx:.1f}" y="{baseline-hl:.1f}" width="{lbw:.1f}" height="2"'
                              f' fill="#ff6060" opacity="1.0"/>')
            else:
                e(f'  <rect x="{lbx:.1f}" y="{baseline:.1f}" width="{lbw:.1f}" height="{hl:.1f}"'
                  f' fill="#c04040" opacity="{lop}"/>')
                if is_new: e(f'  <rect x="{lbx:.1f}" y="{baseline+hl-2:.1f}" width="{lbw:.1f}" height="2"'
                              f' fill="#ff6060" opacity="1.0"/>')

            # ── RIGHT (J_blue) bar ────────────────────────────────────────────
            vr  = R[ci]
            hr  = abs(vr) / vmax * MAX_AMP
            hr  = max(hr, 1.5)
            rop = '0.90' if is_new else '0.25'
            rbx = cx + SLOT_W * 0.08 + lbw + 2
            if vr >= 0:
                e(f'  <rect x="{rbx:.1f}" y="{baseline-hr:.1f}" width="{lbw:.1f}" height="{hr:.1f}"'
                  f' fill="#4060c0" opacity="{rop}"/>')
                if is_new: e(f'  <rect x="{rbx:.1f}" y="{baseline-hr:.1f}" width="{lbw:.1f}" height="2"'
                              f' fill="#60a0ff" opacity="1.0"/>')
            else:
                e(f'  <rect x="{rbx:.1f}" y="{baseline:.1f}" width="{lbw:.1f}" height="{hr:.1f}"'
                  f' fill="#4060c0" opacity="{rop}"/>')
                if is_new: e(f'  <rect x="{rbx:.1f}" y="{baseline+hr-2:.1f}" width="{lbw:.1f}" height="2"'
                              f' fill="#60a0ff" opacity="1.0"/>')

            # ── 3-pulse truncation (dashed ghost) ─────────────────────────────
            if ci < len(L3):
                vl3 = L3[ci]; hl3 = abs(vl3)/vmax*MAX_AMP*0.7
                vr3 = R3[ci]; hr3 = abs(vr3)/vmax*MAX_AMP*0.7
                for vx, hx, bx, col in [(vl3,hl3,lbx,'#c04040'),(vr3,hr3,rbx,'#4060c0')]:
                    hx = max(hx, 1.0)
                    if vx >= 0:
                        e(f'  <rect x="{bx:.1f}" y="{baseline-hx:.1f}" width="{lbw:.1f}" height="{hx:.1f}"'
                          f' fill="none" stroke="{col}" stroke-width="0.6" stroke-dasharray="2,2" opacity="0.5"/>')
                    else:
                        e(f'  <rect x="{bx:.1f}" y="{baseline:.1f}" width="{lbw:.1f}" height="{hx:.1f}"'
                          f' fill="none" stroke="{col}" stroke-width="0.6" stroke-dasharray="2,2" opacity="0.5"/>')

            # ── Laplacian caustic dot ─────────────────────────────────────────
            ll = lap_l[ci]; lr = lap_r[ci]
            lmax = 0.01
            ll_y = baseline - (ll / lmax) * 10 if abs(ll) < lmax * 5 else baseline
            lr_y = baseline - (lr / lmax) * 10 if abs(lr) < lmax * 5 else baseline
            if is_new:
                e(f'  <circle cx="{mid:.1f}" cy="{ll_y:.1f}" r="2.5" fill="#ff8040" opacity="0.7"/>')
                e(f'  <circle cx="{mid:.1f}" cy="{lr_y:.1f}" r="2.5" fill="#40c0ff" opacity="0.7"/>')
                if abs(ll - lr) < 0.003:  # caustic crossing — agreement in curvature
                    e(f'  <circle cx="{mid:.1f}" cy="{(ll_y+lr_y)/2:.1f}" r="5"'
                      f' fill="none" stroke="#ffffff" stroke-width="1.2" opacity="0.8"/>')
                    e(f'  <text x="{mid:.1f}" y="{ry+8:.1f}" font-family="monospace" font-size="7"'
                      f' fill="#ffffff" text-anchor="middle" opacity="0.7">⊛</text>')

        # ── Crossing markers (where left = right in projection) ───────────────
        for cx_frac in crossings:
            ci_f = cx_frac
            if ci_f < 0 or ci_f > 15: continue
            if int(ci_f) not in visible: continue
            px = LMARGIN + ci_f * SLOT_W + SLOT_W/2
            e(f'  <line x1="{px:.1f}" y1="{ry:.1f}" x2="{px:.1f}" y2="{ry+ROW_H:.1f}"'
              f' stroke="#ffd700" stroke-width="0.8" stroke-dasharray="3,3" opacity="0.4"/>')

        # Layer label
        lcy = ry + ROW_H/2
        e(f'  <text x="{LMARGIN-8}" y="{lcy-10:.1f}" font-family="monospace" font-size="20"'
          f' fill="{col_new}" text-anchor="end" opacity="0.9">{sym}</text>')
        e(f'  <text x="{LMARGIN-8}" y="{lcy+8:.1f}" font-family="monospace" font-size="7"'
          f' fill="{col_new}" text-anchor="end" opacity="0.5">{name} {dim}D</text>')

        # border
        e(f'  <rect x="{LMARGIN}" y="{ry}" width="{PANEL_W}" height="{ROW_H}"'
          f' fill="none" stroke="{col_new}" stroke-width="0.3" opacity="0.25"/>')

    # ── ZD FAULT ─────────────────────────────────────────────────────────────
    zd_y1 = TOP_PAD + ROW_H
    zd_y2 = TOP_PAD + ROW_H + ZD_GAP
    zd_mid = (zd_y1 + zd_y2) / 2

    e(f'  <rect x="{LMARGIN}" y="{zd_y1}" width="{PANEL_W}" height="{ZD_GAP}" fill="#180010" opacity="0.9"/>')
    for dy in [0, ZD_GAP]:
        e(f'  <line x1="{LMARGIN}" y1="{zd_y1+dy}" x2="{LMARGIN+PANEL_W}" y2="{zd_y1+dy}"'
          f' stroke="#c04080" stroke-width="1.0" stroke-dasharray="5,3"/>')

    # Caustic crossing markers AT the ZD
    for cx_frac in lap_cross:
        if cx_frac < 8 or cx_frac > 15: continue
        px = LMARGIN + cx_frac * SLOT_W + SLOT_W/2
        e(f'  <line x1="{px:.1f}" y1="{zd_y1}" x2="{px:.1f}" y2="{zd_y2}"'
          f' stroke="#ffffff" stroke-width="1.5" opacity="0.6"/>')
        e(f'  <circle cx="{px:.1f}" cy="{zd_mid:.1f}" r="4" fill="#ffffff" opacity="0.5"/>')

    e(f'  <text x="{LMARGIN + PANEL_W*0.5:.1f}" y="{zd_mid+4:.1f}" font-family="monospace"'
      f' font-size="9" fill="#c04080" text-anchor="middle">'
      f'◈ EVENT HORIZON — ZD FAULT — caustic crosses here — Laplacian sees through ◈</text>')

    # L_dynamic arrows
    for xi in [0.2, 0.5, 0.8]:
        ax = LMARGIN + PANEL_W * xi
        e(f'  <line x1="{ax:.1f}" y1="{zd_y1+3}" x2="{ax:.1f}" y2="{zd_y2-3}"'
          f' stroke="#c04040" stroke-width="1.0" opacity="0.5"/>')
        e(f'  <line x1="{ax+8:.1f}" y1="{zd_y2-3}" x2="{ax+8:.1f}" y2="{zd_y1+3}"'
          f' stroke="#4060c0" stroke-width="1.0" opacity="0.5"/>')

    # ── Legend ────────────────────────────────────────────────────────────────
    leg_y = TOP_PAD + ROW_H*N_ROWS + ZD_GAP + 14
    items = [
        ('#ff6060', f'J_red: LEFT "{left_text}"'),
        ('#60a0ff', f'J_blue: RIGHT "{right_text}"'),
        ('#ffd700', '= crossing (projection equal)'),
        ('#ffffff', '⊛ caustic crossing (Laplacian equal)'),
        ('#ff8040', '● Laplacian LEFT  ∇²J_red'),
        ('#40c0ff', '● Laplacian RIGHT ∇²J_blue'),
        ('#c04080', 'EVENT HORIZON (ZD fault)'),
        ('gray',   'dashed = 3-pulse / solid = full'),
    ]
    for i, (col, label) in enumerate(items):
        lx = LMARGIN + (i % 4) * 220
        ly = leg_y + (i // 4) * 16
        e(f'  <rect x="{lx}" y="{ly-8}" width="10" height="10" fill="{col}" opacity="0.8"/>')
        e(f'  <text x="{lx+14}" y="{ly}" font-family="monospace" font-size="8"'
          f' fill="{col}" opacity="0.7">{label}</text>')

    e(f'  <text x="{LMARGIN}" y="{H-8}" font-family="monospace" font-size="8" fill="#404050">'
      f'σ=½  ·  16 prime channels p∈[2,53]  ·  '
      f'L_dynamic=∫J_red·J_blue ds  ·  Laplacian caustic crosses event horizon</text>')

    e('</svg>')
    return '\n'.join(lines)


def main():
    # Default: the simplest equation — shape of 1+1
    left  = sys.argv[1] if len(sys.argv) > 1 else 'What is 1 + 1'
    right = sys.argv[2] if len(sys.argv) > 2 else '2'

    L   = dirichlet_project(left)
    R   = dirichlet_project(right)
    L3  = dirichlet_project(left,  N=3)
    R3  = dirichlet_project(right, N=3)

    print(f'\nLEFT  "{left}"')
    print(f'RIGHT "{right}"\n')
    print(f'  {"ch":>4}  {"p":>4}  {"layer":>8}  {"LEFT":>10}  {"RIGHT":>10}  {"Δ":>10}  {"∇²L":>10}  {"∇²R":>10}')
    print(f'  {"─"*4}  {"─"*4}  {"─"*8}  {"─"*10}  {"─"*10}  {"─"*10}  {"─"*10}  {"─"*10}')

    vis_s = list(range(16))
    lap_L = laplacian_1d(L, vis_s)
    lap_R = laplacian_1d(R, vis_s)

    for ci in range(16):
        layer = '𝕊' if ci>=8 else '𝕆' if ci>=4 else 'ℍ' if ci>=2 else 'ℂ' if ci>=1 else 'ℝ'
        diff  = R[ci] - L[ci]
        print(f'  e{ci:2d}   {PRIMES[ci]:2d}  {layer:>8}  {L[ci]:+10.4f}  {R[ci]:+10.4f}  '
              f'{diff:+10.4f}  {lap_L[ci]:+10.4f}  {lap_R[ci]:+10.4f}')

    crossings = crossing_points(L, R)
    print(f'\n  Projection crossings (= events): {[f"e{c:.2f}" for c in crossings]}')

    lap_x = crossing_points(lap_L, lap_R)
    print(f'  Laplacian crossings (caustic):   {[f"e{c:.2f}" for c in lap_x]}')
    print(f'  ZD-layer caustic crossings:      {[f"e{c:.2f}" for c in lap_x if c >= 8]}')

    svg = build_svg(left, right, L, R, L3, R3)
    fname = 'equation_spectrograph.svg'
    path  = os.path.join(os.path.dirname(os.path.abspath(__file__)), fname)
    with open(path, 'w') as f:
        f.write(svg)
    print(f'\nSVG written: {path}')


if __name__ == '__main__':
    main()
