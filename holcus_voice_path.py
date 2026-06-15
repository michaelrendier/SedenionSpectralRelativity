#!/usr/bin/env python3
"""
holcus_voice_path.py — The Words AND The Edges. Point by point along a path.
=============================================================================
The voice is not the words. The voice is the PATH between the words.
Words = nodes. Edges = the speech act connecting them. Path = the voice.

Each word has a position in (prime_channel_index × log_gamma) space.
The edge between consecutive words is the distance jumped — the information.
The curve connecting them is the Holcus utterance.

The maths shout WRONG at every non-prime. The WRONGs BUILD the landscape.
The path exists because of the WRONGs.
"""

import sys, os, math

sys.path.insert(0, '/media/rendier/0123-4567/PtolemyHolcus')
from monad import _gamma_at, _word_zero_idx, _horner_hash, _next_prime, D_STAR

ALL_PRIMES = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53]
LAYERS     = {2:'ℝ',3:'ℂ',5:'ℍ',7:'ℍ',
              11:'𝕆',13:'𝕆',17:'𝕆',19:'𝕆',
              23:'𝕊',29:'𝕊',31:'𝕊',37:'𝕊',
              41:'𝕊',43:'𝕊',47:'𝕊',53:'𝕊'}
LAYER_COL  = {'ℝ':'#666','ℂ':'#4080ff','ℍ':'#40c080',
              '𝕆':'#c09030','𝕊':'#ff5060','?':'#444'}

# ── Engine spoken word sequence (from Stirling convergence) ──────────────────
SPOKEN = [
    "glozed","defective","site","darted","god's","carrying",
    "sikeloi","strangeness","autochthony","adhesion","coupling","right",
    "kindnesses","context","world",
    "poetry","function","liquid","style",
    "strangeness","math","site","defective","glozed",
]

def word_position(w):
    """Return (x, y, E, prime, layer, gamma) for a word."""
    h    = _horner_hash(w)
    p    = _next_prime(h)
    zi   = _word_zero_idx(w)
    gam  = _gamma_at(zi)
    E    = abs(math.sin(math.pi * gam / (gam + 1)))
    # x: prime channel index in ALL_PRIMES (0-15), or proportional for out-of-range
    if p in ALL_PRIMES:
        xi = ALL_PRIMES.index(p)
    else:
        # Map large primes to fractional positions beyond e15
        xi = 15 + math.log(p / 53) / math.log(2)
    layer = LAYERS.get(p, '?')
    return xi, gam, E, p, layer

def bezier(p0, p1, p2, p3, t):
    """Cubic Bézier at parameter t."""
    u = 1-t
    x = u**3*p0[0] + 3*u**2*t*p1[0] + 3*u*t**2*p2[0] + t**3*p3[0]
    y = u**3*p0[1] + 3*u**2*t*p1[1] + 3*u*t**2*p2[1] + t**3*p3[1]
    return x, y

def build_svg(words=SPOKEN):
    nodes = [word_position(w) for w in words]

    # ── Layout ────────────────────────────────────────────────────────────────
    W, H   = 1100, 750
    PAD    = 70
    # x: prime channel index 0-15 → [PAD, W-PAD]
    # y: log(gamma) → [H-PAD, PAD]  (higher gamma = higher on screen)
    xi_all  = [n[0] for n in nodes]
    gam_all = [math.log(max(n[1], 1)) for n in nodes]
    xi_min,  xi_max  = 0,    max(15.5, max(xi_all))
    gam_min, gam_max = min(gam_all), max(gam_all)

    def sx(xi):
        t = (xi - xi_min) / max(xi_max - xi_min, 1)
        return PAD + t * (W - 2*PAD)

    def sy(gam):
        lg = math.log(max(gam, 1))
        t  = (lg - gam_min) / max(gam_max - gam_min, 1)
        return H - PAD - t * (H - 2*PAD)

    lines = []
    e = lines.append

    e('<?xml version="1.0" encoding="UTF-8"?>')
    e(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}"'
      f' viewBox="0 0 {W} {H}">')
    e(f'<rect width="{W}" height="{H}" fill="#050508"/>')

    e('<defs>')
    e('  <marker id="arr" markerWidth="6" markerHeight="6" refX="5" refY="3"'
      '          orient="auto">')
    e('    <path d="M0,0 L6,3 L0,6 Z" fill="#80ff30" opacity="0.7"/>')
    e('  </marker>')
    e('  <filter id="glow">')
    e('    <feGaussianBlur stdDeviation="3" result="b"/>')
    e('    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>')
    e('  </filter>')
    e('</defs>')

    # ── Layer column backgrounds ──────────────────────────────────────────────
    layer_bounds = {}
    for i, p in enumerate(ALL_PRIMES):
        lyr = LAYERS[p]
        x_l = sx(i - 0.5)
        x_r = sx(i + 0.5)
        if lyr not in layer_bounds:
            layer_bounds[lyr] = [x_l, x_r]
        else:
            layer_bounds[lyr][0] = min(layer_bounds[lyr][0], x_l)
            layer_bounds[lyr][1] = max(layer_bounds[lyr][1], x_r)

    for lyr, (x_l, x_r) in layer_bounds.items():
        col = LAYER_COL.get(lyr, '#222')
        e(f'<rect x="{x_l:.1f}" y="{PAD}" width="{x_r-x_l:.1f}"'
          f' height="{H-2*PAD}" fill="{col}" opacity="0.04"/>')

    # ── Grid: gamma reference lines ───────────────────────────────────────────
    ZEROS_REF = [14.134, 21.022, 25.011, 30.425, 32.935, 37.586,
                 40.919, 43.327, 48.005, 49.774, 52.970]
    for g in ZEROS_REF:
        gy = sy(g)
        e(f'<line x1="{PAD}" y1="{gy:.1f}" x2="{W-PAD}" y2="{gy:.1f}"'
          f' stroke="#ffffff" stroke-width="0.3" opacity="0.08"/>')
        e(f'<text x="{PAD-4}" y="{gy+3:.1f}" font-family="monospace" font-size="6"'
          f' fill="#333" text-anchor="end">γ={g:.1f}</text>')

    # σ=½ reference: E ≈ d* = 0.246
    e(f'<text x="{W-PAD+4}" y="{PAD+12}" font-family="monospace" font-size="7"'
      f' fill="#c09030" opacity="0.5">σ=½</text>')

    # ── Prime channel x-axis ──────────────────────────────────────────────────
    for i, p in enumerate(ALL_PRIMES):
        gx = sx(i)
        lyr = LAYERS[p]
        col = LAYER_COL[lyr]
        e(f'<line x1="{gx:.1f}" y1="{PAD}" x2="{gx:.1f}" y2="{H-PAD}"'
          f' stroke="{col}" stroke-width="0.4" opacity="0.2"/>')
        e(f'<text x="{gx:.1f}" y="{H-PAD+14}" font-family="monospace" font-size="7"'
          f' fill="{col}" opacity="0.7" text-anchor="middle">p={p}</text>')
        e(f'<text x="{gx:.1f}" y="{H-PAD+24}" font-family="monospace" font-size="8"'
          f' fill="{col}" opacity="0.5" text-anchor="middle">{lyr}</text>')

    # ── EDGES — the actual speech acts ───────────────────────────────────────
    for i in range(len(nodes)-1):
        xi0, g0, E0, p0, l0 = nodes[i]
        xi1, g1, E1, p1, l1 = nodes[i+1]
        x0, y0 = sx(xi0), sy(g0)
        x1, y1 = sx(xi1), sy(g1)

        # Control points: tangent follows direction of change
        dx = x1 - x0
        dy = y1 - y0
        dist = math.hypot(dx, dy)
        ctrl_scale = min(dist * 0.5, 120)
        cx0 = x0 + ctrl_scale * (dx/max(dist,1)) * 0.6 - ctrl_scale * (dy/max(dist,1)) * 0.2
        cy0 = y0 + ctrl_scale * (dy/max(dist,1)) * 0.6 + ctrl_scale * (dx/max(dist,1)) * 0.2
        cx1 = x1 - ctrl_scale * (dx/max(dist,1)) * 0.6 + ctrl_scale * (dy/max(dist,1)) * 0.2
        cy1 = y1 - ctrl_scale * (dy/max(dist,1)) * 0.6 - ctrl_scale * (dx/max(dist,1)) * 0.2

        # Edge color: blend from source to destination layer
        col0 = LAYER_COL.get(l0, '#444')
        # Edge opacity: proportional to how "far" the jump is (big jump = strong edge)
        jump = math.log(max(dist, 1)) / 6
        op   = min(0.85, 0.25 + jump * 0.4)
        # Width: E of source word (closeness to σ=½)
        wid  = 0.6 + E0 * 8

        e(f'<path d="M {x0:.1f} {y0:.1f} C {cx0:.1f} {cy0:.1f}'
          f' {cx1:.1f} {cy1:.1f} {x1:.1f} {y1:.1f}"'
          f' fill="none" stroke="{col0}" stroke-width="{wid:.2f}"'
          f' opacity="{op:.2f}"'
          f' marker-end="url(#arr)"/>')

        # Edge label: word pair that defines this edge
        mid_t = 0.5
        mx = (x0+x1)/2 + (cy0-cy1)*0.05
        my = (y0+y1)/2 - (cx0-cx1)*0.05
        e(f'<text x="{mx:.1f}" y="{my:.1f}" font-family="monospace" font-size="6"'
          f' fill="{col0}" opacity="0.35" text-anchor="middle">'
          f'Δγ={abs(g1-g0):.1f}</text>')

    # ── NODES — the words ─────────────────────────────────────────────────────
    for i, (xi, gam, E, p, lyr) in enumerate(nodes):
        w   = words[i]
        x,y = sx(xi), sy(gam)
        col = LAYER_COL.get(lyr, '#444')

        # Node size: E × 40 (larger = closer to σ=½)
        r   = 3.5 + E * 35
        # Glow for words closest to d*
        if E > 0.05:
            e(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r*2.5:.1f}"'
              f' fill="{col}" opacity="0.12" filter="url(#glow)"/>')
        e(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}"'
          f' fill="{col}" opacity="0.9"/>')
        e(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2" fill="#ffffff" opacity="0.7"/>')

        # Label
        angle_offset = -12 if i % 2 == 0 else 14
        e(f'<text x="{x:.1f}" y="{y+angle_offset:.1f}" font-family="monospace"'
          f' font-size="8" fill="{col}" text-anchor="middle" opacity="0.9">'
          f'{w}</text>')
        e(f'<text x="{x:.1f}" y="{y+angle_offset+9:.1f}" font-family="monospace"'
          f' font-size="6" fill="{col}" text-anchor="middle" opacity="0.55">'
          f'E={E:.4f}</text>')

    # ── Special highlight: "poetry function liquid style" ────────────────────
    for w_highlight in ["poetry", "function", "liquid", "style"]:
        for i, w in enumerate(words):
            if w == w_highlight:
                xi, gam, E, p, lyr = nodes[i]
                x, y = sx(xi), sy(gam)
                for r_ring, op in [(22, 0.15), (14, 0.25), (8, 0.4)]:
                    e(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r_ring}"'
                      f' fill="none" stroke="#80ff30" stroke-width="1.0"'
                      f' opacity="{op}"/>')

    # ── Titles ────────────────────────────────────────────────────────────────
    e(f'<text x="{W//2}" y="22" font-family="monospace" font-size="13"'
      f' fill="#aaa" text-anchor="middle" font-weight="bold">'
      f'HOW DO YOU SPEAK HOLCUS — THE PATH</text>')
    e(f'<text x="{W//2}" y="36" font-family="monospace" font-size="8"'
      f' fill="#555" text-anchor="middle">'
      f'words AND edges · point by point · x=prime channel · y=log(γ) · size=E(σ=½)</text>')

    e(f'<text x="{PAD}" y="{H-6}" font-family="monospace" font-size="7"'
      f' fill="#333">'
      f'Δγ = distance jumped per edge = information per speech act'
      f'  ·  node size = energy at σ=½  ·  path closes: glozed→...→glozed</text>')

    # Green ring legend
    e(f'<text x="{W-PAD-120}" y="{PAD+16}" font-family="monospace" font-size="7"'
      f' fill="#80ff30" opacity="0.6">◎ = ENGINE SPEAKS</text>')
    e(f'<text x="{W-PAD-120}" y="{PAD+28}" font-family="monospace" font-size="7"'
      f' fill="#80ff30" opacity="0.4">  poetry·function·liquid·style</text>')

    e('</svg>')
    return '\n'.join(lines)


if __name__ == '__main__':
    svg  = build_svg()
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        'holcus_voice_path.svg')
    with open(path, 'w') as f:
        f.write(svg)
    print(f'Written: {path}')
    print()
    print('The path:')
    for i, w in enumerate(SPOKEN):
        xi, gam, E, p, lyr = word_position(w)
        arr = '→' if i < len(SPOKEN)-1 else ''
        print(f'  {w:<18}  γ={gam:8.3f}  E={E:.5f}  {lyr}  {arr}')
    print()
    print('The path closes. The standing wave reflects. glozed returns to glozed.')
    print('The WRONGs built the landscape. The path is the NOT-WRONGs.')
