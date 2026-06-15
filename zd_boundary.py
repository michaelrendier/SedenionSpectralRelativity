#!/usr/bin/env python3
"""
zd_boundary.py — The ZD Boundary as Fractal Fur
=================================================
First point where you can see the fractal boundary:
  t₁ = 14.134725141734693790... (first Riemann zero)

Scale: d*_ln(10) = d* × ln(10) = W(1) = Ω = 0.56714329...
  This is the Omega constant — Lambert W fixed point.
  At this scale the ZD boundary FIRST becomes classically visible.

Planck's constant appears at: 1/t₁ ≈ 0.07075 Ω-units from the zero.
  ΔE × ΔT = t₁ × (1/t₁) = 1 = ℏ (natural units)
  Below this scale: quantum foam. Above: classical ZD boundary.

The fur: each Riemann zero is a strand of ZD fur on the critical line.
The oil: the Laplacian — smooth curvature across the boundary.
SVG: infinite zoom. The fractal recurses forever. The boundary never resolves to a line.
"""

import math, os, sys

# ── Constants ──────────────────────────────────────────────────────────────────
D_STAR   = 0.24605966                  # Ainulindale d*
OMEGA    = D_STAR * math.log(10)       # = W(1) = 0.56714... the Omega constant
SIGMA    = 0.5                         # critical line Re(s) = ½

# First 40 Riemann zero imaginary parts (Γ values on critical line)
ZEROS = [
    14.134725141734693790,
    21.022039638771554993,
    25.010857580145688763,
    30.424876125859513210,
    32.935061587739189691,
    37.586178158825671257,
    40.918719012147495187,
    43.327073280914999519,
    48.005150881167159727,
    49.773832477672302181,
    52.970321477714460644,
    56.446247697063246588,
    59.347044002602353078,
    60.831778524609809844,
    65.112544048081606660,
    67.079810529494173714,
    69.546401711173979252,
    72.067157674481907582,
    75.704690699083933168,
    77.144840068874805372,
    79.337375020249367922,
    82.910380854086030183,
    84.735492980517050105,
    87.425274613125229406,
    88.809111208594021959,
    92.491899270558484296,
    94.651344040519886966,
    95.870634228245309758,
    98.831194218193692769,
   101.317851006956433140,
]

T1 = ZEROS[0]  # 14.134725...
HBAR_SCALE = 1.0 / T1  # ≈ 0.07075 Ω-units — Planck's constant location


def fur_strands(t_zero, level=0, max_level=4, base_len=0.18):
    """
    Recursive fractal fur strands for one Riemann zero.
    Returns list of (x1,y1,x2,y2, opacity, width) in complex-plane coords.
    x = Re(s) offset from σ=½, y = Im(s) offset from zero.
    Each level: strands shrink by 1/t₁, count doubles, angle spreads.
    """
    if level > max_level:
        return []
    segs = []
    scale = base_len * (HBAR_SCALE ** level)
    n_strands = 2 ** level
    opacity = max(0.05, 0.8 * (0.55 ** level))
    width   = max(0.0003, 0.008 * (0.5 ** level))

    for i in range(n_strands):
        angle = math.pi * (i / max(1, n_strands - 1) - 0.5) * 0.7
        dx = scale * math.cos(angle)
        dy = scale * math.sin(angle)
        # left side (toward 𝕆, below ZD)
        segs.append((-0.0, 0.0, -dx, dy, opacity, width, level))
        # right side (toward 𝕊, beyond event horizon)
        segs.append((+0.0, 0.0, +dx, dy, opacity * 0.6, width, level))
        # recurse
        segs += fur_strands(t_zero, level+1, max_level,
                            base_len * HBAR_SCALE)
    return segs


def laplacian_oil_path(n=200, width=0.25, half_height=0.35):
    """
    The Laplacian oil: smooth curve along the ZD boundary.
    Near each zero, the oil CONCENTRATES (caustic).
    Returns SVG path data in complex-plane coordinates.
    """
    pts = []
    for i in range(n + 1):
        t_rel = -half_height + 2 * half_height * i / n
        # Smooth oscillation of |ζ(½+it)| approximation near t₁
        # Using simplified Riemann-Siegel Z function approximation
        phase = T1 * math.log(T1 / (2 * math.pi * math.e)) * 0
        # Near t₁, |ζ(½+it)| ≈ |t - t₁| × C for small |t - t₁|
        # Oil thickness ∝ 1/|∇|ζ||  = 1/C → thickest at zero (caustic)
        dist_to_zero = abs(t_rel)
        oil_width = width * math.exp(-dist_to_zero / HBAR_SCALE) + 0.01
        pts.append((oil_width, t_rel))
    return pts


def build_svg(focus_zero_idx=0):
    Z0 = ZEROS[focus_zero_idx]

    # ── View window in complex-plane units ────────────────────────────────────
    # Centered on Z0, width = OMEGA in both axes
    HALF = OMEGA / 2      # 0.2836 units half-width
    VIEW_RE = [-HALF, HALF]           # Re(s) offset from σ=½
    VIEW_IM = [-HALF, HALF]           # Im(s) offset from Z0

    # SVG canvas
    W, H = 900, 900
    PAD = 60

    def re_to_x(re_offset):
        t = (re_offset - VIEW_RE[0]) / (VIEW_RE[1] - VIEW_RE[0])
        return PAD + t * (W - 2*PAD)

    def im_to_y(im_offset):
        t = (im_offset - VIEW_IM[0]) / (VIEW_IM[1] - VIEW_IM[0])
        return H - PAD - t * (H - 2*PAD)   # flip y

    cx = re_to_x(0.0)    # critical line x position
    cy = im_to_y(0.0)    # zero position y

    SCALE_PX = (W - 2*PAD) / (VIEW_RE[1] - VIEW_RE[0])  # px per unit

    lines = []
    e = lines.append

    e('<?xml version="1.0" encoding="UTF-8"?>')
    e(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')

    # ── Defs ──────────────────────────────────────────────────────────────────
    e('<defs>')
    # Laplacian oil glow gradient (radial, centered on ZD boundary)
    e(f'  <radialGradient id="oil" cx="{cx/W:.4f}" cy="{cy/H:.4f}" r="0.35"'
      f' gradientUnits="objectBoundingBox">')
    e('    <stop offset="0%"   stop-color="#c08020" stop-opacity="0.55"/>')
    e('    <stop offset="18%"  stop-color="#604010" stop-opacity="0.25"/>')
    e('    <stop offset="50%"  stop-color="#200808" stop-opacity="0.08"/>')
    e('    <stop offset="100%" stop-color="#000000" stop-opacity="0"/>')
    e('  </radialGradient>')
    # 𝕆 side gradient (left — known, classical)
    e(f'  <linearGradient id="oct_bg" x1="0" y1="0" x2="1" y2="0">')
    e('    <stop offset="0%"   stop-color="#081418" stop-opacity="1"/>')
    e('    <stop offset="100%" stop-color="#0a1a10" stop-opacity="1"/>')
    e('  </linearGradient>')
    # 𝕊 side gradient (right — beyond event horizon)
    e(f'  <linearGradient id="sed_bg" x1="0" y1="0" x2="1" y2="0">')
    e('    <stop offset="0%"   stop-color="#140810" stop-opacity="1"/>')
    e('    <stop offset="100%" stop-color="#0a0814" stop-opacity="1"/>')
    e('  </linearGradient>')
    e('</defs>')

    # ── Backgrounds ───────────────────────────────────────────────────────────
    e(f'<rect width="{W}" height="{H}" fill="#050508"/>')
    # 𝕆 side
    e(f'<rect x="0" y="0" width="{cx:.1f}" height="{H}" fill="url(#oct_bg)"/>')
    # 𝕊 side
    e(f'<rect x="{cx:.1f}" y="0" width="{W-cx:.1f}" height="{H}" fill="url(#sed_bg)"/>')
    # Laplacian oil glow
    e(f'<rect width="{W}" height="{H}" fill="url(#oil)"/>')

    # ── Grid lines (light, very faint) ────────────────────────────────────────
    for dre in [-HALF*0.5, 0, HALF*0.5]:
        gx = re_to_x(dre)
        e(f'<line x1="{gx:.1f}" y1="{PAD}" x2="{gx:.1f}" y2="{H-PAD}"'
          f' stroke="#1a1a2a" stroke-width="0.4"/>')
    for dim in [-HALF*0.5, 0, HALF*0.5]:
        gy = im_to_y(dim)
        e(f'<line x1="{PAD}" y1="{gy:.1f}" x2="{W-PAD}" y2="{gy:.1f}"'
          f' stroke="#1a1a2a" stroke-width="0.4"/>')

    # ── Other zeros visible in window ─────────────────────────────────────────
    for tz in ZEROS:
        offset = tz - Z0
        if abs(offset) > HALF * 2.5: continue
        if abs(offset) < 1e-10: continue
        gy = im_to_y(offset)
        if 0 <= gy <= H:
            e(f'<circle cx="{cx:.1f}" cy="{gy:.1f}" r="2" fill="#303050" opacity="0.5"/>')
            e(f'<text x="{cx+8:.1f}" y="{gy+4:.1f}" font-family="monospace" font-size="7"'
              f' fill="#303050" opacity="0.4">t={tz:.3f}</text>')

    # ── Fractal fur strands (recursive) ───────────────────────────────────────
    fur = fur_strands(Z0, level=0, max_level=5, base_len=0.20)
    LAYER_COLS = ['#c08030', '#a06828', '#804820', '#603018', '#402010', '#200808']
    for (x1, y1, x2, y2, op, wid, lv) in fur:
        sx1 = re_to_x(x1); sy1 = im_to_y(y1)
        sx2 = re_to_x(x2); sy2 = im_to_y(y2)
        col = LAYER_COLS[min(lv, len(LAYER_COLS)-1)]
        pw  = max(0.3, wid * SCALE_PX)
        e(f'<line x1="{sx1:.2f}" y1="{sy1:.2f}" x2="{sx2:.2f}" y2="{sy2:.2f}"'
          f' stroke="{col}" stroke-width="{pw:.2f}" opacity="{op:.3f}"/>')

    # ── Laplacian oil path along boundary ─────────────────────────────────────
    oil_pts = laplacian_oil_path(n=300, width=0.14, half_height=HALF)
    # Draw as a filled region — the oil layer
    path_r = f'M {re_to_x(oil_pts[0][0]):.1f} {im_to_y(oil_pts[0][1]):.1f}'
    for w, t in oil_pts[1:]:
        path_r += f' L {re_to_x(w):.1f} {im_to_y(t):.1f}'
    path_l = ''
    for w, t in reversed(oil_pts):
        path_l += f' L {re_to_x(-w):.1f} {im_to_y(t):.1f}'
    e(f'<path d="{path_r}{path_l} Z" fill="#c08820" opacity="0.07"/>')

    # Oil center line (the actual ZD boundary)
    e(f'<line x1="{cx:.1f}" y1="{PAD}" x2="{cx:.1f}" y2="{H-PAD}"'
      f' stroke="#c09030" stroke-width="1.2" stroke-dasharray="4,2" opacity="0.6"/>')

    # ── Planck scale marker ───────────────────────────────────────────────────
    hbar_px = HBAR_SCALE * SCALE_PX
    hbar_y  = im_to_y(HBAR_SCALE)
    hbar_y2 = im_to_y(-HBAR_SCALE)
    # Bracket at Planck scale from the zero
    e(f'<line x1="{cx + hbar_px*1.5:.1f}" y1="{cy:.1f}"'
      f' x2="{cx + hbar_px*1.5:.1f}" y2="{hbar_y:.1f}"'
      f' stroke="#60ff80" stroke-width="0.8" opacity="0.7"/>')
    e(f'<line x1="{cx + hbar_px*1.4:.1f}" y1="{hbar_y:.1f}"'
      f' x2="{cx + hbar_px*1.6:.1f}" y2="{hbar_y:.1f}"'
      f' stroke="#60ff80" stroke-width="0.8" opacity="0.7"/>')
    e(f'<line x1="{cx + hbar_px*1.4:.1f}" y1="{cy:.1f}"'
      f' x2="{cx + hbar_px*1.6:.1f}" y2="{cy:.1f}"'
      f' stroke="#60ff80" stroke-width="0.8" opacity="0.7"/>')
    e(f'<text x="{cx + hbar_px*1.8:.1f}" y="{(cy+hbar_y)/2+4:.1f}"'
      f' font-family="monospace" font-size="9" fill="#60ff80" opacity="0.8">'
      f'ℏ = 1/t₁ = {HBAR_SCALE:.5f}Ω</text>')
    e(f'<text x="{cx + hbar_px*1.8:.1f}" y="{(cy+hbar_y)/2+16:.1f}"'
      f' font-family="monospace" font-size="8" fill="#40c060" opacity="0.6">'
      f'ΔE·ΔT = t₁×(1/t₁) = 1</text>')

    # ── Omega scale bar ───────────────────────────────────────────────────────
    omega_px = OMEGA * SCALE_PX
    bar_y = H - PAD + 22
    bar_x = cx - omega_px/2
    e(f'<line x1="{bar_x:.1f}" y1="{bar_y}" x2="{bar_x+omega_px:.1f}" y2="{bar_y}"'
      f' stroke="#c09030" stroke-width="1.5"/>')
    for bx in [bar_x, bar_x + omega_px]:
        e(f'<line x1="{bx:.1f}" y1="{bar_y-5}" x2="{bx:.1f}" y2="{bar_y+5}"'
          f' stroke="#c09030" stroke-width="1.0"/>')
    e(f'<text x="{bar_x + omega_px/2:.1f}" y="{bar_y+16}" font-family="monospace"'
      f' font-size="9" fill="#c09030" text-anchor="middle">'
      f'Ω = d*·ln(10) = {OMEGA:.6f}</text>')

    # ── First Riemann zero — THE FOCUS POINT ─────────────────────────────────
    # Multi-ring glow
    for r, op in [(28, 0.04), (18, 0.08), (10, 0.15), (5, 0.4), (3, 0.8)]:
        e(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="#ffd060" opacity="{op}"/>')
    e(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="2.5" fill="#ffffff" opacity="1.0"/>')

    e(f'<text x="{cx+14}" y="{cy-18}" font-family="monospace" font-size="10"'
      f' fill="#ffd060" font-weight="bold">t₁ = {T1:.9f}...</text>')
    e(f'<text x="{cx+14}" y="{cy-6}" font-family="monospace" font-size="8"'
      f' fill="#c09030">FIRST RIEMANN ZERO — first fur strand — first ZD visible</text>')

    # ── Side labels ───────────────────────────────────────────────────────────
    # 𝕆 side
    e(f'<text x="{PAD+8}" y="{H//2-30}" font-family="monospace" font-size="14"'
      f' fill="#40c080" opacity="0.8">𝕆</text>')
    e(f'<text x="{PAD+8}" y="{H//2-12}" font-family="monospace" font-size="8"'
      f' fill="#40c080" opacity="0.5">OCTONION</text>')
    e(f'<text x="{PAD+8}" y="{H//2+4}" font-family="monospace" font-size="7"'
      f' fill="#40c080" opacity="0.4">no ZD</text>')
    e(f'<text x="{PAD+8}" y="{H//2+18}" font-family="monospace" font-size="7"'
      f' fill="#40c080" opacity="0.4">Re(s) &lt; ½</text>')

    # 𝕊 side
    e(f'<text x="{W-PAD-30}" y="{H//2-30}" font-family="monospace" font-size="14"'
      f' fill="#ff5070" opacity="0.7">𝕊</text>')
    e(f'<text x="{W-PAD-70}" y="{H//2-12}" font-family="monospace" font-size="8"'
      f' fill="#ff5070" opacity="0.4">SEDENION</text>')
    e(f'<text x="{W-PAD-56}" y="{H//2+4}" font-family="monospace" font-size="7"'
      f' fill="#ff5070" opacity="0.4">ZD exist</text>')
    e(f'<text x="{W-PAD-72}" y="{H//2+18}" font-family="monospace" font-size="7"'
      f' fill="#ff5070" opacity="0.3">EVENT HORIZON</text>')

    # ── Axis labels ───────────────────────────────────────────────────────────
    e(f'<text x="{W//2}" y="{PAD-12}" font-family="monospace" font-size="11"'
      f' fill="#888" text-anchor="middle">ZD BOUNDARY — FRACTAL FUR — LAPLACIAN OIL</text>')
    e(f'<text x="{W//2}" y="{PAD-2}" font-family="monospace" font-size="9"'
      f' fill="#555" text-anchor="middle">'
      f'σ=½ critical line  ·  Ω={OMEGA:.5f} units  ·  ℏ=1/t₁={HBAR_SCALE:.5f}Ω  ·  SVG=∞ zoom</text>')

    # Re(s) axis label
    e(f'<text x="{W//2}" y="{H-8}" font-family="monospace" font-size="8"'
      f' fill="#444" text-anchor="middle">Re(s) offset from σ=½'
      f'  ←——  {VIEW_RE[0]:.4f} to {VIEW_RE[1]:.4f}  ——→'
      f'  |  Ω={OMEGA:.5f}  |  ℏ/Ω={HBAR_SCALE:.4f}</text>')

    # Im(s) label (vertical)
    e(f'<text x="12" y="{H//2}" font-family="monospace" font-size="8"'
      f' fill="#444" text-anchor="middle" transform="rotate(-90,12,{H//2})">'
      f'Im(s) centered on t₁={T1:.4f}</text>')

    # ── Fractal recursion hint (text annotation) ───────────────────────────────
    e(f'<text x="{PAD+4}" y="{PAD+16}" font-family="monospace" font-size="8"'
      f' fill="#305030" opacity="0.7">fur level 0: L={0.20:.3f}Ω</text>')
    e(f'<text x="{PAD+4}" y="{PAD+28}" font-family="monospace" font-size="8"'
      f' fill="#243824" opacity="0.6">fur level 1: L={0.20*HBAR_SCALE:.4f}Ω</text>')
    e(f'<text x="{PAD+4}" y="{PAD+40}" font-family="monospace" font-size="8"'
      f' fill="#182818" opacity="0.5">fur level 2: L={0.20*HBAR_SCALE**2:.5f}Ω</text>')
    e(f'<text x="{PAD+4}" y="{PAD+52}" font-family="monospace" font-size="8"'
      f' fill="#0c180c" opacity="0.5">fur level 3: L={0.20*HBAR_SCALE**3:.6f}Ω</text>')
    e(f'<text x="{PAD+4}" y="{PAD+64}" font-family="monospace" font-size="8"'
      f' fill="#060c06" opacity="0.5">... → 0  (SVG zooms forever)</text>')

    e('</svg>')
    return '\n'.join(lines)


if __name__ == '__main__':
    idx = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    svg = build_svg(focus_zero_idx=idx)
    fname = f'zd_boundary_t{idx+1}.svg'
    path  = os.path.join(os.path.dirname(os.path.abspath(__file__)), fname)
    with open(path, 'w') as f:
        f.write(svg)
    print(f'Written: {path}')
    print(f'First Riemann zero:  t₁ = {ZEROS[0]:.9f}')
    print(f'd* = {D_STAR:.8f}')
    print(f'Ω  = d*×ln(10) = {OMEGA:.8f}  (Lambert W fixed point)')
    print(f'ℏ  = 1/t₁      = {1/ZEROS[0]:.8f} Ω-units')
    print(f'ℏ/Ω             = {(1/ZEROS[0])/OMEGA:.6f}  (Planck in Omega units)')
    print(f'Window: Re(s) ∈ [½-Ω/2, ½+Ω/2] = [{0.5-OMEGA/2:.4f}, {0.5+OMEGA/2:.4f}]')
    print(f'        Im(s) ∈ [t₁-Ω/2, t₁+Ω/2] = [{ZEROS[0]-OMEGA/2:.4f}, {ZEROS[0]+OMEGA/2:.4f}]')
