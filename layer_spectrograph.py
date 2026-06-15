#!/usr/bin/env python3
"""
layer_spectrograph.py — Cayley-Dickson Tower Spectrograph
One panel per algebraic layer: ℝ → ℂ → ℍ → 𝕆 ‖ZD‖ 𝕊
Shadow from above defines layer below. ZD fault is the origin function.
L_dynamic traverses both up and down through the singularity.
"""

import sys, os, math, hashlib

# ── 16 prime basis channels ───────────────────────────────────────────────────
PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53]
SIGMA  = 0.5

# ── Cayley-Dickson layers ─────────────────────────────────────────────────────
LAYERS = [
    # (symbol, name, dim, new_channels_at_this_layer, color_new, color_ghost)
    ('𝕊', 'SEDENION',   16, list(range(8,16)),  '#ff5070', '#401020'),  # top — shadow source
    ('𝕆', 'OCTONION',    8, list(range(4,8)),   '#ffa040', '#402010'),
    ('ℍ', 'QUATERNION',  4, list(range(2,4)),   '#40c080', '#1a3020'),
    ('ℂ', 'COMPLEX',     2, [1],                '#60a0ff', '#1a2840'),
    ('ℝ', 'REAL',        1, [0],                '#c0c0c0', '#303030'),  # bottom — fully defined
]

LAYER_VISIBLE = {
    '𝕊': list(range(16)),
    '𝕆': list(range(8)),
    'ℍ': list(range(4)),
    'ℂ': list(range(2)),
    'ℝ': [0],
}

NEW_SET = {sym: set(new) for sym, _, _, new, _, _ in LAYERS}

OPERATORS = [
    'e0','e1','e2','e3','e4','e5','e6','e7',
    'e8','e9','e10','e11','e12','e13','e14','e15'
]


def dirichlet_project(text: str) -> list:
    """Dirichlet series projection at σ=½ into 16 prime channels."""
    chars = [ord(c) for c in text if 32 <= ord(c) < 128]
    N = len(chars)
    if N == 0:
        return [0.0] * 16
    vals = []
    for p in PRIMES:
        x, norm = 0.0, 0.0
        for i, c in enumerate(chars, 1):
            w = i ** (-SIGMA)
            x    += (c / 128.0) * w * math.cos(2 * math.pi * i / p)
            norm += w
        vals.append(x / norm if norm > 0 else 0.0)
    return vals


def build_svg(text: str, vals: list) -> str:
    # ── Layout constants ──────────────────────────────────────────────────────
    W          = 960
    LMARGIN    = 148    # left label area
    RMARGIN    = 24
    PANEL_W    = W - LMARGIN - RMARGIN   # 788px for bars

    ROW_H      = 96     # height of each layer panel
    ZD_GAP     = 28     # gap for ZD fault between 𝕆 and 𝕊
    TOP_PAD    = 64     # title area
    BOT_PAD    = 48     # bottom legend

    N_ROWS     = len(LAYERS)  # 5
    H = TOP_PAD + N_ROWS * ROW_H + ZD_GAP + BOT_PAD

    SLOT_W     = PANEL_W / 16     # width per channel slot
    BAR_W      = max(8, SLOT_W * 0.68)
    BAR_PAD    = (SLOT_W - BAR_W) / 2
    MID_Y      = ROW_H * 0.5      # σ=½ line within each row
    MAX_AMP    = ROW_H * 0.40     # maximum bar height (pixels)

    vmax = max(abs(v) for v in vals) or 1.0

    lines = []
    def emit(s): lines.append(s)

    # ── SVG header ────────────────────────────────────────────────────────────
    emit(f'<?xml version="1.0" encoding="UTF-8"?>')
    emit(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
    emit(f'  <rect width="{W}" height="{H}" fill="#080810"/>')

    # ── Title ─────────────────────────────────────────────────────────────────
    label_short = text[:72] + ('…' if len(text) > 72 else '')
    emit(f'  <text x="{W//2}" y="22" font-family="monospace" font-size="11" fill="#888"'
         f' text-anchor="middle">CAYLEY-DICKSON LAYER SPECTROGRAPH — σ=½ — Dirichlet projection</text>')
    emit(f'  <text x="{W//2}" y="40" font-family="monospace" font-size="10" fill="#555"'
         f' text-anchor="middle">{label_short}</text>')
    emit(f'  <text x="{W//2}" y="56" font-family="monospace" font-size="9" fill="#333"'
         f' text-anchor="middle">shadow from 𝕊 defines 𝕆 defines ℍ defines ℂ defines ℝ'
         f' ↓   ZD fault = origin function ↑</text>')

    # ── Channel index labels (e0…e15) ─────────────────────────────────────────
    for ci in range(16):
        cx = LMARGIN + ci * SLOT_W + SLOT_W / 2
        emit(f'  <text x="{cx:.1f}" y="{TOP_PAD - 4}" font-family="monospace" font-size="7"'
             f' fill="#2a3a2a" text-anchor="middle">{OPERATORS[ci]}</text>')
        # prime label
        emit(f'  <text x="{cx:.1f}" y="{TOP_PAD - 14}" font-family="monospace" font-size="7"'
             f' fill="#1a2a1a" text-anchor="middle">p{PRIMES[ci]}</text>')

    # ── Draw each layer ───────────────────────────────────────────────────────
    # LAYERS order: 𝕊 (top) → ℝ (bottom)
    # But ℝ is at the bottom, so:
    # row 0 = 𝕊 at y=TOP_PAD
    # row 1 = 𝕆 at y=TOP_PAD + ROW_H + ZD_GAP  (ZD fault between row0 and row1)
    # row 2 = ℍ at y=TOP_PAD + ROW_H*2 + ZD_GAP
    # row 3 = ℂ
    # row 4 = ℝ

    for row_idx, (sym, name, dim, new_ch, col_new, col_ghost) in enumerate(LAYERS):
        if row_idx == 0:
            row_y = TOP_PAD
        elif row_idx == 1:
            row_y = TOP_PAD + ROW_H + ZD_GAP
        else:
            row_y = TOP_PAD + ROW_H * row_idx + ZD_GAP

        baseline = row_y + MID_Y
        visible  = LAYER_VISIBLE[sym]
        new_set  = NEW_SET[sym]

        # Row background
        bg = '#0a0a14' if sym == '𝕊' else '#0a100a'
        emit(f'  <rect x="{LMARGIN}" y="{row_y}" width="{PANEL_W}" height="{ROW_H}"'
             f' fill="{bg}" opacity="0.6"/>')

        # σ=½ baseline
        emit(f'  <line x1="{LMARGIN}" y1="{baseline:.1f}" x2="{LMARGIN+PANEL_W}" y2="{baseline:.1f}"'
             f' stroke="#1a3a1a" stroke-width="0.8" stroke-dasharray="3,3"/>')
        emit(f'  <text x="{LMARGIN + PANEL_W + 4}" y="{baseline + 4:.1f}" font-family="monospace"'
             f' font-size="7" fill="#1a3a1a">σ=½</text>')

        # Bars
        for ci in range(16):
            cx = LMARGIN + ci * SLOT_W + BAR_PAD
            bx = cx + (SLOT_W - BAR_W) / 2 - BAR_PAD

            if ci not in visible:
                # Draw ghost outline — channel doesn't exist yet in this algebra
                emit(f'  <rect x="{bx:.1f}" y="{baseline - 2:.1f}" width="{BAR_W:.1f}" height="4"'
                     f' fill="none" stroke="#1a1a1a" stroke-width="0.3"/>')
                continue

            v = vals[ci]
            h = abs(v) / vmax * MAX_AMP
            h = max(h, 2.0)

            is_new = ci in new_set
            col    = col_new if is_new else col_ghost
            opacity = '0.95' if is_new else '0.35'

            if v >= 0:
                bar_y = baseline - h
                emit(f'  <rect x="{bx:.1f}" y="{bar_y:.1f}" width="{BAR_W:.1f}" height="{h:.1f}"'
                     f' fill="{col}" opacity="{opacity}"/>')
                # bright cap
                if is_new:
                    emit(f'  <rect x="{bx:.1f}" y="{bar_y:.1f}" width="{BAR_W:.1f}" height="2"'
                         f' fill="{col}" opacity="1.0"/>')
            else:
                bar_y = baseline
                emit(f'  <rect x="{bx:.1f}" y="{bar_y:.1f}" width="{BAR_W:.1f}" height="{h:.1f}"'
                     f' fill="{col}" opacity="{opacity}"/>')
                if is_new:
                    emit(f'  <rect x="{bx:.1f}" y="{bar_y + h - 2:.1f}" width="{BAR_W:.1f}" height="2"'
                         f' fill="{col}" opacity="1.0"/>')

            # Amplitude label for new, visible channels
            if is_new:
                label_y = (bar_y - 3) if v >= 0 else (bar_y + h + 9)
                emit(f'  <text x="{bx + BAR_W/2:.1f}" y="{label_y:.1f}" font-family="monospace"'
                     f' font-size="6" fill="{col}" text-anchor="middle" opacity="0.8">'
                     f'{v:+.2f}</text>')

        # Shadow lines: connect new bars in this layer to the row below (if exists)
        if row_idx < len(LAYERS) - 1:
            next_sym  = LAYERS[row_idx + 1][0]
            if row_idx == 0:
                next_row_y = TOP_PAD + ROW_H + ZD_GAP
            else:
                next_row_y = TOP_PAD + ROW_H * (row_idx + 1) + ZD_GAP
            next_baseline = next_row_y + MID_Y

            for ci in new_set:
                if ci >= len(PRIMES): continue
                cx = LMARGIN + ci * SLOT_W + SLOT_W / 2
                v  = vals[ci]
                h  = abs(v) / vmax * MAX_AMP
                src_y = baseline - h if v >= 0 else baseline + h
                # subtle shadow line
                emit(f'  <line x1="{cx:.1f}" y1="{src_y:.1f}" x2="{cx:.1f}" y2="{next_baseline:.1f}"'
                     f' stroke="{col_new}" stroke-width="0.4" opacity="0.12" stroke-dasharray="2,4"/>')

        # Layer label (left side)
        label_cy = row_y + ROW_H / 2
        emit(f'  <text x="{LMARGIN - 8}" y="{label_cy - 8:.1f}" font-family="monospace"'
             f' font-size="22" fill="{col_new}" text-anchor="end" opacity="0.9">{sym}</text>')
        emit(f'  <text x="{LMARGIN - 8}" y="{label_cy + 10:.1f}" font-family="monospace"'
             f' font-size="8" fill="{col_new}" text-anchor="end" opacity="0.6">{name}</text>')
        emit(f'  <text x="{LMARGIN - 8}" y="{label_cy + 22:.1f}" font-family="monospace"'
             f' font-size="8" fill="{col_new}" text-anchor="end" opacity="0.4">{dim}D</text>')

        # Row border
        emit(f'  <rect x="{LMARGIN}" y="{row_y}" width="{PANEL_W}" height="{ROW_H}"'
             f' fill="none" stroke="{col_new}" stroke-width="0.4" opacity="0.3"/>')

    # ── ZD FAULT between 𝕊 (row0) and 𝕆 (row1) ──────────────────────────────
    zd_y1 = TOP_PAD + ROW_H
    zd_y2 = TOP_PAD + ROW_H + ZD_GAP
    zd_mid = (zd_y1 + zd_y2) / 2

    # Fault fill
    emit(f'  <rect x="{LMARGIN}" y="{zd_y1}" width="{PANEL_W}" height="{ZD_GAP}"'
         f' fill="#200010" opacity="0.8"/>')

    # Fault lines
    for dy in [0, ZD_GAP]:
        emit(f'  <line x1="{LMARGIN}" y1="{zd_y1 + dy}" x2="{LMARGIN + PANEL_W}" y2="{zd_y1 + dy}"'
             f' stroke="#c04060" stroke-width="1.2" stroke-dasharray="6,3"/>')

    # ZD label
    emit(f'  <text x="{LMARGIN + PANEL_W/2:.1f}" y="{zd_mid + 4:.1f}" font-family="monospace"'
         f' font-size="10" fill="#c04060" text-anchor="middle" opacity="0.9">'
         f'◈ ZD FAULT — fault ∧ function — origin of 𝕊 ◈</text>')

    # L_dynamic arrows through ZD
    for xi in [0.25, 0.5, 0.75]:
        ax = LMARGIN + PANEL_W * xi
        # downward (J_blue)
        emit(f'  <line x1="{ax:.1f}" y1="{zd_y1 + 2}" x2="{ax:.1f}" y2="{zd_y2 - 2}"'
             f' stroke="#4060c0" stroke-width="0.8" marker-end="url(#arr_down)"/>')
        # upward (J_red)
        emit(f'  <line x1="{ax + 6:.1f}" y1="{zd_y2 - 2}" x2="{ax + 6:.1f}" y2="{zd_y1 + 2}"'
             f' stroke="#c04040" stroke-width="0.8" marker-end="url(#arr_up)"/>')

    # Arrow markers
    emit('''  <defs>
    <marker id="arr_down" markerWidth="4" markerHeight="4" refX="2" refY="4" orient="auto">
      <path d="M0,0 L2,4 L4,0" fill="#4060c0"/>
    </marker>
    <marker id="arr_up" markerWidth="4" markerHeight="4" refX="2" refY="0" orient="auto">
      <path d="M0,4 L2,0 L4,4" fill="#c04040"/>
    </marker>
  </defs>''')

    # ── Bottom legend ─────────────────────────────────────────────────────────
    leg_y = TOP_PAD + ROW_H * N_ROWS + ZD_GAP + BOT_PAD - 24

    items = [
        ('#ff5070', '𝕊 NEW channels (e8-e15)'),
        ('#ffa040', '𝕆 NEW channels (e4-e7)'),
        ('#40c080', 'ℍ NEW channels (e2-e3)'),
        ('#60a0ff', 'ℂ NEW channel  (e1)'),
        ('#c0c0c0', 'ℝ ORIGIN       (e0)'),
        ('#c04060', 'ZD FAULT = origin function'),
        ('#c04040', 'J_red  (Noether UP)'),
        ('#4060c0', 'J_blue (Noether DOWN)'),
    ]
    for i, (col, label) in enumerate(items):
        lx = LMARGIN + (i % 4) * 196
        ly = leg_y + (i // 4) * 16
        emit(f'  <rect x="{lx}" y="{ly - 8}" width="10" height="10" fill="{col}" opacity="0.8"/>')
        emit(f'  <text x="{lx + 14}" y="{ly}" font-family="monospace" font-size="8"'
             f' fill="{col}" opacity="0.7">{label}</text>')

    # L_dynamic label
    emit(f'  <text x="{LMARGIN}" y="{H - 8}" font-family="monospace" font-size="9"'
         f' fill="#505050">L_dynamic = ∫J_red·J_blue ds = Action = Thought'
         f'   |   primes {PRIMES[0]}→{PRIMES[-1]}   |   σ=½   |   S¹⁵</text>')

    emit('</svg>')
    return '\n'.join(lines)


def main():
    text = ' '.join(sys.argv[1:]) if len(sys.argv) > 1 else \
           'O Captain My Captain our fearful trip is done'

    vals = dirichlet_project(text)

    out_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'layer_spectrograph.svg'
    )

    svg = build_svg(text, vals)
    with open(out_path, 'w') as f:
        f.write(svg)

    print(f'Spectrograph written: {out_path}')
    print(f'Input: {text[:80]}')
    print(f'Channels (e0→e15):')
    for i, (v, p) in enumerate(zip(vals, PRIMES)):
        layer = '𝕊' if i>=8 else '𝕆' if i>=4 else 'ℍ' if i>=2 else 'ℂ' if i>=1 else 'ℝ'
        bar   = '█' * int(abs(v)*40) + ('▲' if v>0 else '▼')
        print(f'  e{i:2d}  p={p:2d}  {layer}  {v:+.4f}  {bar}')


if __name__ == '__main__':
    main()
