#!/usr/bin/env python3
"""
fano_oscilloscope.py — The Wobble Between Fano and Sedenion
============================================================
A signal generator drives 16 oscillators (one per prime channel).
Project the 16D path DOWN to the Fano plane (𝕆, channels e4-e7).
The wobble = what the sedenion channels (e8-e15) are doing outside Fano space.

At ZD crossings: the Fano projection and the sedenion path diverge.
That divergence IS the zero-divisor fault — the cavitation — the wobble.

Input: any text. The P1 prime hash seeds each oscillator's phase.
Output: SVG showing:
  - Blue  path: Fano projection (𝕆 only, e4-e7, primes 11-19)
  - Red   path: full sedenion Lissajous (all 16 channels projected to 2D)
  - Gold  delta: the wobble = |sedenion - fano| at each t
  - Stars: ZD crossings (where wobble is locally maximal)
"""

import math, sys, os, hashlib

# ── Prime channels ─────────────────────────────────────────────────────────────
ALL_PRIMES  = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53]
FANO_PRIMES = [11, 13, 17, 19]                   # 𝕆 channels e4-e7
SED_PRIMES  = [23, 29, 31, 37, 41, 43, 47, 53]   # 𝕊 channels e8-e15

# ── P1-style phase seed from text ─────────────────────────────────────────────
def word_phase(word, p):
    """Hash word to a phase offset in [0, 2π] for prime p."""
    h = 0
    for ch in word:
        h = (h * 95 + (ord(ch) - 32)) & 0xFFFF
    return (h % p) / p * 2 * math.pi

def dirichlet_vector(text, primes, t, n_terms=32):
    """
    Compute a 2D Lissajous projection from the given prime channels.
    x = Σ_p Σ_i  i^(-½) · cos(2π·i·t/p + φ_p)   (first channel → x)
    y = Σ_p Σ_i  i^(-½) · sin(2π·i·t/p + φ_p)   (second channel → y)
    Phase φ_p is seeded by the text P1 hash.
    """
    words = text.lower().split() or ['null']
    x = y = 0.0
    for p in primes:
        phi = sum(word_phase(w, p) for w in words) / len(words)
        for i in range(1, n_terms + 1):
            amp = i ** -0.5
            freq = 2 * math.pi * i / p
            x += amp * math.cos(freq * t + phi)
            y += amp * math.sin(freq * t + phi)
    # Normalize by number of terms
    norm = len(primes) * sum((i ** -0.5) for i in range(1, n_terms + 1))
    return x / norm, y / norm

def sedenion_vector_2d(text, t, n_terms=32):
    """Full 16D path projected to 2D by pairing channels."""
    # Use ALL 16 prime channels, project pairs (p_2k, p_2k+1) → (x_k, y_k)
    # Then sum all (x_k, y_k) contributions with layer weighting
    x = y = 0.0
    words = text.lower().split() or ['null']
    for idx, p in enumerate(ALL_PRIMES):
        phi = sum(word_phase(w, p) for w in words) / len(words)
        weight = (idx + 1) ** -0.5  # higher channels slightly damped
        for i in range(1, n_terms + 1):
            amp = weight * i ** -0.5
            freq = 2 * math.pi * i / p
            if idx % 2 == 0:
                x += amp * math.cos(freq * t + phi)
            else:
                y += amp * math.sin(freq * t + phi)
    norm = sum((k + 1) ** -0.5 * sum(i ** -0.5 for i in range(1, n_terms + 1))
               for k in range(len(ALL_PRIMES)))
    return x / norm, y / norm

def build_svg(text="What is 1 plus 1", n_steps=1200):
    T_MAX = 2 * math.pi * 53   # one full revolution of slowest oscillator

    # ── Compute paths ─────────────────────────────────────────────────────────
    ts = [T_MAX * k / n_steps for k in range(n_steps + 1)]

    fano_path = [dirichlet_vector(text, FANO_PRIMES, t) for t in ts]
    sed_path  = [sedenion_vector_2d(text, t) for t in ts]

    # Wobble: L2 distance between the two paths at each t
    wobble = [math.hypot(s[0]-f[0], s[1]-f[1]) for f, s in zip(fano_path, sed_path)]
    max_wob = max(wobble) or 1e-9

    # ZD crossings: local maxima of wobble (wobble > 0.6 × max)
    zd_crossings = []
    for i in range(1, n_steps):
        if wobble[i] > wobble[i-1] and wobble[i] > wobble[i+1]:
            if wobble[i] > 0.55 * max_wob:
                zd_crossings.append(i)

    # ── SVG layout ────────────────────────────────────────────────────────────
    W, H = 1200, 680
    PAD  = 50

    # Three panels: [Fano] [Sedenion] [Wobble over time]
    PW = (W - 4*PAD) // 3  # panel width
    PH = H - 2*PAD          # panel height

    def to_screen(x, y, ox, oy, scale=1.0):
        return (ox + x * scale * PW * 0.45,
                oy - y * scale * PH * 0.45)

    cx1 = PAD + PW // 2
    cx2 = PAD * 2 + PW + PW // 2
    cx3 = PAD * 3 + 2*PW + PW // 2
    cy  = PAD + PH // 2

    lines = []
    e = lines.append

    e('<?xml version="1.0" encoding="UTF-8"?>')
    e(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
      f'viewBox="0 0 {W} {H}">')
    e(f'<rect width="{W}" height="{H}" fill="#060609"/>')

    # ── Panel borders ─────────────────────────────────────────────────────────
    for cx, label, sublabel in [
        (cx1, '𝕆 FANO PROJECTION', 'channels e4-e7  ·  primes {11,13,17,19}'),
        (cx2, '𝕊 SEDENION PATH',   'all 16 channels  ·  primes {2,...,53}'),
        (cx3, 'WOBBLE  Δ(t)',       '|sedenion − fano|  ·  ZD crossings = ★'),
    ]:
        bx = cx - PW//2
        e(f'<rect x="{bx}" y="{PAD}" width="{PW}" height="{PH}"'
          f' fill="none" stroke="#1a1a2a" stroke-width="0.5"/>')
        e(f'<text x="{cx}" y="{PAD-14}" font-family="monospace" font-size="11"'
          f' fill="#aaa" text-anchor="middle" font-weight="bold">{label}</text>')
        e(f'<text x="{cx}" y="{PAD-3}" font-family="monospace" font-size="8"'
          f' fill="#555" text-anchor="middle">{sublabel}</text>')

    # ── Draw Fano path ────────────────────────────────────────────────────────
    def path_svg(pts, cx, cy, color, stroke_w=0.9, scale=1.0, opacity=1.0):
        d = ''
        for i, (x, y) in enumerate(pts):
            sx, sy = to_screen(x, y, cx, cy, scale)
            d += f'{"M" if i==0 else "L"} {sx:.2f} {sy:.2f} '
        return (f'<path d="{d.strip()}" fill="none" stroke="{color}"'
                f' stroke-width="{stroke_w}" opacity="{opacity}"/>')

    e(path_svg(fano_path, cx1, cy, '#4080ff', stroke_w=1.0))
    e(path_svg(sed_path,  cx2, cy, '#ff5060', stroke_w=1.0))

    # In panel 2: overlay fano as ghost
    e(path_svg(fano_path, cx2, cy, '#2040a0', stroke_w=0.5, opacity=0.4))

    # In panel 1: overlay sedenion as ghost
    e(path_svg(sed_path, cx1, cy, '#601030', stroke_w=0.5, opacity=0.3))

    # ── Draw wobble time series ───────────────────────────────────────────────
    wob_d = ''
    bx3 = cx3 - PW//2
    for i, w in enumerate(wobble):
        wx = bx3 + PAD//2 + (PW - PAD) * i / n_steps
        wy = (PAD + PH) - (PH - PAD) * (w / max_wob)
        wob_d += f'{"M" if i==0 else "L"} {wx:.1f} {wy:.1f} '
    e(f'<path d="{wob_d}" fill="none" stroke="#c09030" stroke-width="0.8"/>')

    # ZD crossing markers on wobble panel
    for idx in zd_crossings[:20]:
        wx = bx3 + PAD//2 + (PW - PAD) * idx / n_steps
        wy = (PAD + PH) - (PH - PAD) * (wobble[idx] / max_wob)
        e(f'<text x="{wx:.1f}" y="{wy-4:.1f}" font-family="monospace"'
          f' font-size="9" fill="#ff8040" text-anchor="middle" opacity="0.8">★</text>')

    # ZD crossing markers ON the lissajous panels
    for idx in zd_crossings[:15]:
        fx, fy = fano_path[idx]
        sx_f, sy_f = to_screen(fx, fy, cx1, cy)
        e(f'<circle cx="{sx_f:.1f}" cy="{sy_f:.1f}" r="3.5" fill="none"'
          f' stroke="#ff8040" stroke-width="0.8" opacity="0.7"/>')

        sx2v, sy2v = to_screen(*sed_path[idx], cx2, cy)
        e(f'<circle cx="{sx2v:.1f}" cy="{sy2v:.1f}" r="3.5" fill="none"'
          f' stroke="#ff8040" stroke-width="0.8" opacity="0.7"/>')

    # ── Crosshairs ────────────────────────────────────────────────────────────
    for cx in [cx1, cx2]:
        e(f'<line x1="{cx}" y1="{PAD}" x2="{cx}" y2="{PAD+PH}"'
          f' stroke="#1a1a28" stroke-width="0.4" stroke-dasharray="2,3"/>')
        e(f'<line x1="{cx-PW//2}" y1="{cy}" x2="{cx+PW//2}" y2="{cy}"'
          f' stroke="#1a1a28" stroke-width="0.4" stroke-dasharray="2,3"/>')

    # ── Stats ─────────────────────────────────────────────────────────────────
    e(f'<text x="{PAD}" y="{H-8}" font-family="monospace" font-size="8"'
      f' fill="#444">Input: "{text}"'
      f'  ·  max wobble = {max_wob:.4f}'
      f'  ·  ZD crossings (wobble peaks) = {len(zd_crossings)}'
      f'  ·  oscillators: {n_steps} steps over T=2π×53</text>')

    # ── Wobble value label ────────────────────────────────────────────────────
    mid_wob = wobble[n_steps//2]
    e(f'<text x="{cx3}" y="{PAD + PH - 8}" font-family="monospace" font-size="8"'
      f' fill="#c09030" text-anchor="middle">'
      f'max={max_wob:.4f}  ·  mean={sum(wobble)/len(wobble):.4f}</text>')

    e('</svg>')
    return '\n'.join(lines), len(zd_crossings), max_wob


if __name__ == '__main__':
    text = ' '.join(sys.argv[1:]) if len(sys.argv) > 1 else "What is 1 plus 1"
    svg, n_zd, mw = build_svg(text)
    safe = text[:30].replace(' ', '_').replace('/', '_')
    fname = f'fano_wobble_{safe}.svg'
    path  = os.path.join(os.path.dirname(os.path.abspath(__file__)), fname)
    with open(path, 'w') as f:
        f.write(svg)
    print(f'Written: {path}')
    print(f'ZD crossings (wobble peaks): {n_zd}')
    print(f'Max wobble:  {mw:.6f}')
    print(f'Is the wobble noticeable? {"YES — clearly visible" if mw > 0.1 else "subtle"}')
