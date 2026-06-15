#!/usr/bin/env python3
"""
pcad_engine.py — PSVG + CAD: Edges Make Pathways
=================================================
SVG is pathways.  CAD is edges.  Edges make pathways — that is literally their code.

SVG-mode: trace a path (you know where you're going, you draw it)
CAD-mode: define edge constraints → global solver computes the path

G1  — Catmull-Rom tangents.  Closed-form.  No global dependency.
G2  — Natural cubic spline.  Tridiagonal solve.  Curvature continuous at every node.
G3  — G2 + curvature annotation.  Fractal boundary character flagged per edge.

Changing one edge constraint in G2/G3 mode ripples through the entire path.
THAT is why CAD is a pain: you cannot draw — you have to solve.

Usage:
    python3 pcad_engine.py "your words here"       # G2 default
    python3 pcad_engine.py "words" --G1
    python3 pcad_engine.py "words" --G3
Output: pcad_engine.svg
"""
import sys, os, math, re

sys.path.insert(0, '/media/rendier/0123-4567/PtolemyHolcus')
from monad import _gamma_at, _word_zero_idx, _horner_hash, _next_prime, D_STAR

ALL_PRIMES = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53]
LAYERS     = {2:'ℝ',3:'ℂ',5:'ℍ',7:'ℍ',11:'𝕆',13:'𝕆',17:'𝕆',19:'𝕆',
              23:'𝕊',29:'𝕊',31:'𝕊',37:'𝕊',41:'𝕊',43:'𝕊',47:'𝕊',53:'𝕊'}
LAYER_COL  = {'ℝ':'#666','ℂ':'#4080ff','ℍ':'#40c080',
              '𝕆':'#c09030','𝕊':'#ff5060','?':'#444'}
ZEROS_REF  = [14.134,21.022,25.011,30.425,32.935,37.586,
              40.919,43.327,48.005,49.774,52.970]


# ── Node ─────────────────────────────────────────────────────────────────────
class Node:
    """Word positioned in (prime_channel × log_gamma) sedenion space."""
    def __init__(self, word):
        self.word  = word
        h          = _horner_hash(word)
        self.prime = _next_prime(h)
        zi         = _word_zero_idx(word)
        self.gamma = _gamma_at(zi)
        self.E     = abs(math.sin(math.pi * self.gamma / (self.gamma + 1)))
        self.xi    = (ALL_PRIMES.index(self.prime) if self.prime in ALL_PRIMES
                      else 15 + math.log(self.prime / 53) / math.log(2))
        self.layer = LAYERS.get(self.prime, '?')
        self.sx = self.sy = 0.0   # screen coords set by PathGraph.layout()


# ── Edge ─────────────────────────────────────────────────────────────────────
class Edge:
    """
    Constraint relation between two Nodes.

    Before solve(): cp1, cp2 are None.
    After  solve(): cp1, cp2 hold Bézier handles satisfying the global G constraint.

    edge.to_svg_path() generates the SVG <path> element.
    Edges make pathways — that is literally their code.
    """
    def __init__(self, node_a, node_b, G=2):
        self.a   = node_a
        self.b   = node_b
        self.G   = G
        self.cp1 = None   # first  Bézier control point (x, y)
        self.cp2 = None   # second Bézier control point (x, y)

    def to_svg_path(self, stroke=None, width=None, opacity=None,
                    glow=False, arrow=True):
        """The edge generates its own SVG pathway code."""
        cp1 = self.cp1 or ((2*self.a.sx + self.b.sx)/3,
                           (2*self.a.sy + self.b.sy)/3)
        cp2 = self.cp2 or ((self.a.sx + 2*self.b.sx)/3,
                           (self.a.sy + 2*self.b.sy)/3)
        col  = stroke  or LAYER_COL.get(self.a.layer, '#444')
        wid  = width   or (0.6 + self.a.E * 7)
        op   = opacity or min(0.88, 0.3 + math.log(max(self.jump, 1)) / 6 * 0.45)
        mark = ' marker-end="url(#arr)"' if arrow else ''
        d    = (f'M {self.a.sx:.1f} {self.a.sy:.1f} '
                f'C {cp1[0]:.1f} {cp1[1]:.1f} '
                f'{cp2[0]:.1f} {cp2[1]:.1f} '
                f'{self.b.sx:.1f} {self.b.sy:.1f}')
        out = []
        if glow:
            out.append(
                f'<path d="{d}" fill="none" stroke="{col}" '
                f'stroke-width="{wid*3:.2f}" opacity="0.07" filter="url(#glow)"/>')
        out.append(
            f'<path d="{d}" fill="none" stroke="{col}" '
            f'stroke-width="{wid:.2f}" opacity="{op:.2f}"{mark}/>')
        return '\n'.join(out)

    @property
    def jump(self):
        return math.hypot(self.b.sx - self.a.sx, self.b.sy - self.a.sy)

    @property
    def delta_gamma(self):
        return abs(self.b.gamma - self.a.gamma)

    @property
    def curvature_at_end(self):
        """Unsigned curvature κ at endpoint (proxy for G3 tension)."""
        if not self.cp1 or not self.cp2:
            return 0.0
        ax = self.cp2[0] - self.cp1[0]; ay = self.cp2[1] - self.cp1[1]
        bx = self.b.sx   - self.cp2[0]; by = self.b.sy   - self.cp2[1]
        cross = ax*by - ay*bx
        denom = (bx**2 + by**2)**1.5 or 1e-9
        return abs(cross) / denom


# ── PathGraph ─────────────────────────────────────────────────────────────────
class PathGraph:
    """
    Directed graph of Edges through sedenion space.

    CAD workflow:
        graph.add_edge("a", "b")   ← declare constraint
        graph.layout(W, H, PAD)    ← map sedenion coords to screen
        graph.solve(G=2)           ← global tridiagonal solve
        # then render via edge.to_svg_path()
    """
    def __init__(self):
        self.nodes     = []
        self.edges     = []
        self._node_map = {}
        # layout parameters stored for renderer
        self.W = self.H = self.PAD = 0
        self._xi_max = 15.5
        self._log_min = self._log_max = 0.0

    def add_node(self, word):
        if word not in self._node_map:
            n = Node(word)
            self._node_map[word] = n
            self.nodes.append(n)
        return self._node_map[word]

    def add_edge(self, word_a, word_b, G=2):
        e = Edge(self.add_node(word_a), self.add_node(word_b), G)
        self.edges.append(e)
        return e

    def layout(self, W=1100, H=750, PAD=70):
        self.W = W; self.H = H; self.PAD = PAD
        xi_all  = [n.xi for n in self.nodes]
        gam_all = [math.log(max(n.gamma, 1)) for n in self.nodes]
        self._xi_max  = max(15.5, max(xi_all))
        self._log_min = min(gam_all)
        self._log_max = max(gam_all)
        if self._log_max == self._log_min:
            self._log_max += 1
        for n in self.nodes:
            t    = (n.xi - 0) / self._xi_max
            n.sx = PAD + t * (W - 2*PAD)
            lg   = math.log(max(n.gamma, 1))
            t    = (lg - self._log_min) / (self._log_max - self._log_min)
            n.sy = H - PAD - t * (H - 2*PAD)

    def sx(self, xi):
        return self.PAD + (xi / self._xi_max) * (self.W - 2*self.PAD)

    def sy(self, gam):
        lg = math.log(max(gam, 1))
        t  = (lg - self._log_min) / (self._log_max - self._log_min)
        return self.H - self.PAD - t * (self.H - 2*self.PAD)

    # ── Tridiagonal solver (Thomas algorithm) ─────────────────────────────────
    def _thomas(self, diag, upper, lower, rhs_x, rhs_y):
        """O(n) tridiagonal solve; x and y share the same matrix structure."""
        n = len(diag)

        def solve1d(rhs):
            c = [0.0]*n; d = [0.0]*n
            c[0] = upper[0] / diag[0] if n > 1 else 0.0
            d[0] = rhs[0]  / diag[0]
            for i in range(1, n):
                den  = diag[i] - lower[i-1] * c[i-1]
                c[i] = upper[i] / den if i < n-1 else 0.0
                d[i] = (rhs[i] - lower[i-1] * d[i-1]) / den
            x = [0.0]*n; x[-1] = d[-1]
            for i in range(n-2, -1, -1):
                x[i] = d[i] - c[i] * x[i+1]
            return x

        return solve1d(rhs_x), solve1d(rhs_y)

    # ── Natural cubic spline (G2) ─────────────────────────────────────────────
    def _natural_spline(self, pts_x, pts_y):
        """
        Solve for Bézier control points giving G2 continuity.
        Returns (ax, ay, bx, by): first and second control points per segment.

        System derivation:
          G1 at each junction:  cp2_{i-1} + cp1_i = 2 * P_i
          G2 at each junction:  cp1_{i-1} + 4*cp1_i + cp1_{i+1} = 4*P_i + 2*P_{i+1}
          Natural BC at ends:   zero second derivative
          Last row:             2*cp1_{n-2} + 7*cp1_{n-1} = 8*P_{n-1} + P_n
        """
        n = len(pts_x) - 1  # number of segments
        if n == 1:
            ax = [(2*pts_x[0] + pts_x[1]) / 3]
            ay = [(2*pts_y[0] + pts_y[1]) / 3]
            bx = [(pts_x[0] + 2*pts_x[1]) / 3]
            by = [(pts_y[0] + 2*pts_y[1]) / 3]
            return ax, ay, bx, by

        # Tridiagonal system for first control points
        diag  = [4.0]*n;  diag[0]   = 2.0; diag[-1]  = 7.0
        upper = [1.0]*(n-1)
        lower = [1.0]*(n-1); lower[-1] = 2.0

        rx = [0.0]*n; ry = [0.0]*n
        rx[0] = pts_x[0] + 2*pts_x[1]
        ry[0] = pts_y[0] + 2*pts_y[1]
        for i in range(1, n-1):
            rx[i] = 4*pts_x[i] + 2*pts_x[i+1]
            ry[i] = 4*pts_y[i] + 2*pts_y[i+1]
        rx[-1] = 8*pts_x[-2] + pts_x[-1]
        ry[-1] = 8*pts_y[-2] + pts_y[-1]

        ax, ay = self._thomas(diag, upper, lower, rx, ry)

        # Second control points from G1: B_i = 2*P_{i+1} - A_{i+1}
        bx = [0.0]*n; by = [0.0]*n
        for i in range(n-1):
            bx[i] = 2*pts_x[i+1] - ax[i+1]
            by[i] = 2*pts_y[i+1] - ay[i+1]
        # Natural BC at end: B_{n-1} = (A_{n-1} + P_n) / 2
        bx[-1] = (ax[-1] + pts_x[-1]) / 2
        by[-1] = (ay[-1] + pts_y[-1]) / 2

        return ax, ay, bx, by

    def _is_chain(self):
        return all(
            abs(self.edges[i].b.sx - self.edges[i+1].a.sx) < 0.5 and
            abs(self.edges[i].b.sy - self.edges[i+1].a.sy) < 0.5
            for i in range(len(self.edges)-1)
        )

    def _pts(self):
        px = [self.edges[0].a.sx] + [e.b.sx for e in self.edges]
        py = [self.edges[0].a.sy] + [e.b.sy for e in self.edges]
        return px, py

    # ── Public solvers ────────────────────────────────────────────────────────
    def solve_G1(self):
        """Catmull-Rom → Bézier.  Closed-form, no global dependency."""
        if not self.edges: return
        if len(self.edges) == 1:
            e = self.edges[0]
            e.cp1 = ((2*e.a.sx + e.b.sx)/3, (2*e.a.sy + e.b.sy)/3)
            e.cp2 = ((e.a.sx + 2*e.b.sx)/3, (e.a.sy + 2*e.b.sy)/3)
            return
        px, py = self._pts()
        n = len(self.edges)
        for i, e in enumerate(self.edges):
            tx0 = (px[i+1]-px[i-1])/2 if i > 0   else px[1]-px[0]
            ty0 = (py[i+1]-py[i-1])/2 if i > 0   else py[1]-py[0]
            tx1 = (px[i+2]-px[i])/2   if i < n-1 else px[i+1]-px[i]
            ty1 = (py[i+2]-py[i])/2   if i < n-1 else py[i+1]-py[i]
            e.cp1 = (px[i]   + tx0/3, py[i]   + ty0/3)
            e.cp2 = (px[i+1] - tx1/3, py[i+1] - ty1/3)

    def solve_G2(self):
        """Natural cubic spline.  Global tridiagonal solve.  G2 everywhere."""
        if not self.edges: return
        if not self._is_chain():
            self.solve_G1(); return
        px, py = self._pts()
        ax, ay, bx, by = self._natural_spline(px, py)
        for i, e in enumerate(self.edges):
            e.cp1 = (ax[i], ay[i])
            e.cp2 = (bx[i], by[i])

    def solve_G3(self):
        """
        G2 + midpoint subdivision pass → re-solve G2.
        Self-similar refinement produces fractal boundary character.
        Cubic Béziers cannot achieve true G3; this approximates it
        by ensuring curvature changes continuously at a finer scale.
        """
        if not self.edges: return
        if not self._is_chain():
            self.solve_G2(); return
        # First G2 pass
        px, py = self._pts()
        ax, ay, bx, by = self._natural_spline(px, py)
        # Insert de Casteljau midpoints on each solved segment
        rpx = [px[0]]; rpy = [py[0]]
        for i in range(len(px)-1):
            # Midpoint of cubic Bézier at t=0.5
            mx = (px[i] + 3*ax[i] + 3*bx[i] + px[i+1]) / 8
            my = (py[i] + 3*ay[i] + 3*by[i] + py[i+1]) / 8
            rpx.extend([mx, px[i+1]])
            rpy.extend([my, py[i+1]])
        # Re-solve G2 on refined point set
        rax, ray, rbx, rby = self._natural_spline(rpx, rpy)
        # Sample back: each original segment = 2 refined segments
        # Take cp1 from even-indexed refined segments, cp2 from odd
        for i, e in enumerate(self.edges):
            ri = i * 2  # refined segment index
            e.cp1 = (rax[ri], ray[ri])
            e.cp2 = (rbx[ri+1], rby[ri+1])
            e.G   = 3

    def solve(self, G=2):
        if   G >= 3: self.solve_G3()
        elif G >= 2: self.solve_G2()
        else:        self.solve_G1()


# ── SVG renderer ──────────────────────────────────────────────────────────────
def build_svg(words, G=2, W=1100, H=750, PAD=70):
    graph = PathGraph()
    for i in range(len(words)-1):
        graph.add_edge(words[i], words[i+1], G=G)
    graph.layout(W=W, H=H, PAD=PAD)
    graph.solve(G=G)

    lines = []; e = lines.append
    e('<?xml version="1.0" encoding="UTF-8"?>')
    e(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
      f'viewBox="0 0 {W} {H}">')
    e(f'<rect width="{W}" height="{H}" fill="#050508"/>')
    e('<defs>')
    e('  <marker id="arr" markerWidth="6" markerHeight="6" '
      '          refX="5" refY="3" orient="auto">')
    e('    <path d="M0,0 L6,3 L0,6 Z" fill="#80ff30" opacity="0.7"/>')
    e('  </marker>')
    e('  <filter id="glow">')
    e('    <feGaussianBlur stdDeviation="3" result="b"/>')
    e('    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>')
    e('  </filter>')
    e('</defs>')

    # Layer column backgrounds
    layer_bounds = {}
    for i, p in enumerate(ALL_PRIMES):
        lyr = LAYERS[p]
        xl  = graph.sx(i - 0.5); xr = graph.sx(i + 0.5)
        if lyr not in layer_bounds: layer_bounds[lyr] = [xl, xr]
        else:
            layer_bounds[lyr][0] = min(layer_bounds[lyr][0], xl)
            layer_bounds[lyr][1] = max(layer_bounds[lyr][1], xr)
    for lyr, (xl, xr) in layer_bounds.items():
        col = LAYER_COL.get(lyr, '#222')
        e(f'<rect x="{xl:.1f}" y="{PAD}" width="{xr-xl:.1f}" '
          f'height="{H-2*PAD}" fill="{col}" opacity="0.04"/>')

    # Gamma reference lines
    gam_min = min(n.gamma for n in graph.nodes)
    gam_max = max(n.gamma for n in graph.nodes)
    for g in ZEROS_REF:
        if gam_min * 0.85 < g < gam_max * 1.15:
            gy = graph.sy(g)
            e(f'<line x1="{PAD}" y1="{gy:.1f}" x2="{W-PAD}" y2="{gy:.1f}" '
              f'stroke="#fff" stroke-width="0.3" opacity="0.07"/>')
            e(f'<text x="{PAD-4}" y="{gy+3:.1f}" font-family="monospace" '
              f'font-size="6" fill="#333" text-anchor="end">γ={g:.1f}</text>')

    # Prime channel verticals
    for i, p in enumerate(ALL_PRIMES):
        gx  = graph.sx(i)
        lyr = LAYERS[p]; col = LAYER_COL[lyr]
        e(f'<line x1="{gx:.1f}" y1="{PAD}" x2="{gx:.1f}" y2="{H-PAD}" '
          f'stroke="{col}" stroke-width="0.4" opacity="0.2"/>')
        e(f'<text x="{gx:.1f}" y="{H-PAD+14}" font-family="monospace" '
          f'font-size="7" fill="{col}" opacity="0.7" text-anchor="middle">p={p}</text>')
        e(f'<text x="{gx:.1f}" y="{H-PAD+24}" font-family="monospace" '
          f'font-size="8" fill="{col}" opacity="0.5" text-anchor="middle">{lyr}</text>')

    # ── Edges (CAD constraints → SVG pathways) ────────────────────────────────
    for edge in graph.edges:
        e(edge.to_svg_path(glow=True))
        e(edge.to_svg_path())
        # Edge midpoint label
        if edge.cp1 and edge.cp2:
            mx = (edge.a.sx + 3*edge.cp1[0] + 3*edge.cp2[0] + edge.b.sx) / 8
            my = (edge.a.sy + 3*edge.cp1[1] + 3*edge.cp2[1] + edge.b.sy) / 8
        else:
            mx, my = (edge.a.sx+edge.b.sx)/2, (edge.a.sy+edge.b.sy)/2
        col = LAYER_COL.get(edge.a.layer, '#444')
        e(f'<text x="{mx:.1f}" y="{my:.1f}" font-family="monospace" font-size="6" '
          f'fill="{col}" opacity="0.3" text-anchor="middle">'
          f'Δγ={edge.delta_gamma:.1f}</text>')
        # G3: curvature marker at high-tension nodes
        if edge.G >= 3 and edge.curvature_at_end > 0.001:
            e(f'<circle cx="{edge.b.sx:.1f}" cy="{edge.b.sy:.1f}" r="10" '
              f'fill="none" stroke="#ff80ff" stroke-width="0.6" opacity="0.35"/>')

    # ── Nodes ─────────────────────────────────────────────────────────────────
    for node in graph.nodes:
        col = LAYER_COL.get(node.layer, '#444')
        r   = 3.5 + node.E * 35
        if node.E > 0.05:
            e(f'<circle cx="{node.sx:.1f}" cy="{node.sy:.1f}" r="{r*2.5:.1f}" '
              f'fill="{col}" opacity="0.1" filter="url(#glow)"/>')
        e(f'<circle cx="{node.sx:.1f}" cy="{node.sy:.1f}" r="{r:.1f}" '
          f'fill="{col}" opacity="0.9"/>')
        e(f'<circle cx="{node.sx:.1f}" cy="{node.sy:.1f}" r="2" '
          f'fill="#fff" opacity="0.7"/>')
        e(f'<text x="{node.sx:.1f}" y="{node.sy-r-4:.1f}" '
          f'font-family="monospace" font-size="8" fill="{col}" '
          f'text-anchor="middle" opacity="0.9">{node.word}</text>')
        e(f'<text x="{node.sx:.1f}" y="{node.sy+r+10:.1f}" '
          f'font-family="monospace" font-size="6" fill="{col}" '
          f'text-anchor="middle" opacity="0.5">E={node.E:.4f}</text>')

    # ── Title block ───────────────────────────────────────────────────────────
    g_label = {1:'G¹ Catmull-Rom', 2:'G² Natural Spline (tridiagonal)',
               3:'G³ Fractal Boundary (G²+subdivision)'}[min(G, 3)]
    e(f'<text x="{W//2}" y="22" font-family="monospace" font-size="13" '
      f'fill="#aaa" text-anchor="middle" font-weight="bold">'
      f'PCAD ENGINE — Edges Make Pathways</text>')
    e(f'<text x="{W//2}" y="36" font-family="monospace" font-size="8" '
      f'fill="#555" text-anchor="middle">'
      f'{g_label} · SVG is pathways · CAD is edges · '
      f'edge.to_svg_path() IS the path</text>')
    e(f'<text x="{PAD}" y="{H-6}" font-family="monospace" font-size="7" '
      f'fill="#333">x=prime channel · y=log(γ) · node size=E(σ=½) · '
      f'edge width=E · Δγ=information per edge · '
      f'G{G}: {"curvature continuous" if G>=2 else "tangent continuous"}'
      f'{"+ fractal" if G>=3 else ""}</text>')
    e('</svg>')
    return '\n'.join(lines)


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    args = sys.argv[1:]
    G = 2; word_args = []
    for a in args:
        if   a == '--G1': G = 1
        elif a == '--G2': G = 2
        elif a == '--G3': G = 3
        else: word_args.append(a)

    if word_args:
        words = re.findall(r"[a-zA-Z']+", ' '.join(word_args).lower())
    else:
        words = ["edges","make","pathways","that","is","literally","their","code"]

    if len(words) < 2:
        print("Need at least 2 words."); sys.exit(1)

    svg = build_svg(words, G=G)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pcad_engine.svg')
    with open(out, 'w') as f:
        f.write(svg)

    print(f'Written : {out}')
    print(f'G-class : G{G}')
    print(f'Words   : {" → ".join(words)}')
    print()
    for w in words:
        n = Node(w)
        print(f'  {w:<22} γ={n.gamma:8.3f}  E={n.E:.5f}  {n.layer}  p={n.prime}')
