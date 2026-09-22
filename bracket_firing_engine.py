#!/usr/bin/env python3
"""
bracket_firing_engine.py — The Recursive Bracketing & Firing-Order Engine
===========================================================================
Extends emerger_spectrum.py's five named top-level brackets ({1:15}, {2:14},
{8:8}, {4:4:4:4}, {4:8:4}) all the way down the Cayley-Dickson tower: the
sedenion's own 16x16 L(a) regular-representation matrix splits exactly into
two orthogonal 8x8 octonion blocks; each of those splits exactly into two
orthogonal 4x4 quaternion blocks; each of those into two 2x2 complex
blocks; each of those into two 1x1 real blocks. 31 nodes total
(1 + 2 + 4 + 8 + 16), a literal binary bifurcation tree.

THE BLOCK IDENTITY (verified exact, dims 1/2/4/8/16, before anything else
in this file was built on it — see the derivation check in this repo's
session log):

    a = (a1, a2)   =>   L_a  =  [ L_a1        -R_a2 o C ]
                                 [ L_a2 o C     R_a1     ]

C = conjugation (sign-flip every component but the first), L_x/R_x =
left/right multiplication by x in the HALF-dimension sub-algebra. This
is the Cayley-Dickson doubling identity already implicit in
emerger_spectrum.py's `cd_mul` — ESTABLISHED algebra (Cayley-Dickson
construction), not new; what's new here is walking the resulting matrix
apart, level by level, as an explicit recursive object.

BRACKETING, named exactly: the sign/ordering above is ONE of a few
equivalent-but-distinct Cayley-Dickson doubling conventions in the
literature (which factor gets conjugated, left- vs right-multiplied).
This engine uses exactly the convention already hard-coded into
emerger_spectrum.py's `cd_mul`, and names that choice explicitly rather
than leaving it implicit — a different bracketing convention gives a
different block matrix for the same algebra.

FIRING ORDER, named exactly: a one-way, depth-first cursor over the
31-node tree. At every internal node the SMALLER-norm child fires
first. A norm TIE between the two children is exactly
`on_zd_equator` (emerger_spectrum.py's {8:8} test) generalized to every
level of the tower, not only the top sedenion/octonion split — worth
being precise about, since it means "which side fires first" becomes
genuinely undefined (a real ambiguity, not a bug) exactly where a node
sits on its own zero-divisor equator.

stdlib + numpy (eigenvalues only — the matrices themselves stay exact,
Fraction, all the way through; only the eigen-decomposition step leaves
exact arithmetic, same as any standard numerical linear algebra use).
"""
import sys, os, math
from fractions import Fraction as F
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from emerger_spectrum import cd_mul, cd_conj, mat_rank, text_to_vec, parse_vec, DIM

LAYER_NAME = {16: "S", 8: "O", 4: "H", 2: "C", 1: "R"}
LAYER_FULL = {16: "sedenion", 8: "octonion", 4: "quaternion", 2: "complex", 1: "real"}
LAYER_COLOR = {16: "#ff5070", 8: "#c08020", 4: "#40c080", 2: "#60a0ff", 1: "#c0c0c0"}


# ── dimension-generic L/R matrices (cd_mul already handles any power of 2) ──
def e_n(k, n):
    v = [F(0)] * n
    v[k] = F(1)
    return tuple(v)


def left_mat(a):
    n = len(a)
    cols = [cd_mul(a, e_n(k, n)) for k in range(n)]
    return [[cols[k][r] for k in range(n)] for r in range(n)]


def right_mat(a):
    n = len(a)
    cols = [cd_mul(e_n(k, n), a) for k in range(n)]
    return [[cols[k][r] for k in range(n)] for r in range(n)]


def is_zero_divisor_dim(x):
    """Generalizes emerger_spectrum.is_zero_divisor to any CD dimension."""
    n = len(x)
    if n == 1:
        return False  # reals: no zero divisors
    if all(c == 0 for c in x):
        return False
    return mat_rank(left_mat(x)) < n


def norm_sq(x):
    return sum((c * c for c in x), F(0))


# ── the recursive bifurcation tree ──────────────────────────────────────────
def build_tree(a, path=""):
    """
    Recursively bifurcate a CD vector into the block tree.
    Each node: its own sub-vector, its own L(a) matrix (exact), its own
    eigenvalues (numeric), its own zero-divisor status (exact), and
    (for internal nodes) whether its two children sit on a shared norm
    equator.
    """
    n = len(a)
    L = left_mat(a)
    Lf = np.array([[float(c) for c in row] for row in L], dtype=complex)
    eigs = np.linalg.eigvals(Lf) if n > 1 else np.array([complex(float(a[0]))])
    node = {
        "path": path or "root",
        "dim": n,
        "layer": LAYER_NAME[n],
        "layer_full": LAYER_FULL[n],
        "vec": a,
        "norm_sq": float(norm_sq(a)),
        "is_zd": is_zero_divisor_dim(a),
        "eigs": eigs,
        "children": [],
        "on_equator": False,
    }
    if n > 1:
        h = n // 2
        a1, a2 = a[:h], a[h:]
        left_child = build_tree(a1, path + "L")
        right_child = build_tree(a2, path + "R")
        node["children"] = [left_child, right_child]
        node["on_equator"] = (
            left_child["norm_sq"] == right_child["norm_sq"]
            and left_child["norm_sq"] != 0
        )
    return node


def verify_block_identity(a):
    """
    Confirms, on THIS specific input, that assembling L_a from
    [[L_a1, -R_a2 o C],[L_a2 o C, R_a1]] exactly reproduces left_mat(a).
    Run once per new input before trusting the tree built from it —
    cheap, exact (Fraction), and this is the check that keeps the whole
    engine honest rather than assumed.
    """
    n = len(a)
    if n == 1:
        return True
    h = n // 2
    a1, a2 = a[:h], a[h:]

    def conj_mat(M):
        return [[M[r][c] * (F(1) if c == 0 else F(-1)) for c in range(len(M))]
                for r in range(len(M))]

    La1, Ra1 = left_mat(a1), right_mat(a1)
    La2, Ra2 = left_mat(a2), right_mat(a2)
    RaC2, LaC2 = conj_mat(Ra2), conj_mat(La2)

    pred = [[F(0)] * n for _ in range(n)]
    for r in range(h):
        for c in range(h):
            pred[r][c] = La1[r][c]
            pred[r][c + h] = -RaC2[r][c]
            pred[r + h][c] = LaC2[r][c]
            pred[r + h][c + h] = Ra1[r][c]

    true = left_mat(a)
    ok = all(pred[r][c] == true[r][c] for r in range(n) for c in range(n))
    return ok and verify_block_identity(a1) and verify_block_identity(a2)


# ── the firing order: a one-way depth-first cursor ──────────────────────────
def firing_order(node):
    """
    Yields nodes in a strict forward, non-branching visiting sequence:
    smaller-norm child first, larger-norm child second. A tie
    (on_equator) breaks toward the LEFT (L) branch by convention — named
    explicitly here since it is a genuine ambiguity, not resolved by the
    norm rule itself.
    """
    seq = [node]
    if node["children"]:
        c0, c1 = node["children"]
        if c0["norm_sq"] <= c1["norm_sq"]:
            first, second = c0, c1
        else:
            first, second = c1, c0
        seq += firing_order(first)
        seq += firing_order(second)
    return seq


# ── spectral texture across levels ──────────────────────────────────────────
def spectral_summary(tree):
    """
    Groups the 31 nodes by dimension (layer). Reports TWO different
    quantities per layer, kept deliberately apart because pooling them
    together hides the real finding:

    - `per_node_spread`: max|eig|/min|eig| computed WITHIN a single
      node. By Hurwitz's theorem (R, C, H, O are the only normed
      division algebras), L_a for any NONZERO element of a sub-algebra
      below dim 16 is EXACTLY |a| times an isometry — every such node
      has per-node spread == 1.0, always, provably, not just on the
      inputs tested. Verified live across random inputs and a sparse
      zero-divisor input (e1+e10): every genuine violation traced back
      to an all-zero sub-vector (0/0, undefined, not a counterexample —
      a caught false alarm, not a real one, kept in the record for that
      reason). Zero nodes are reported separately below and excluded
      from the isometry check, since |0|=0 makes the ratio undefined,
      not non-isometric. The sedenion root (dim 16) is the only place a
      genuinely NONZERO node's spread can differ from 1.0 — that
      departure IS the zero-divisor fault, visible directly in the
      eigenvalues, not just in the rank test.
    - `sibling_spread`: max|eig|/min|eig| POOLED across every node at
      that layer (i.e. also across different nodes' own norms). This
      is a different, real quantity — it measures how unevenly a
      generation's total norm was split between its two children, not
      any failure of the isometry property. Conflating the two was the
      first draft's mistake here, caught by checking rather than
      assuming; both are reported now, never merged.
    """
    by_dim = {16: [], 8: [], 4: [], 2: [], 1: []}

    def walk(n):
        by_dim[n["dim"]].append(n)
        for c in n["children"]:
            walk(c)

    walk(tree)
    out = {}
    for dim, nodes in by_dim.items():
        if not nodes:
            continue
        nonzero = [n for n in nodes if n["norm_sq"] > 1e-12]
        n_zero = len(nodes) - len(nonzero)
        per_node_spreads = []
        for n in nonzero:
            mags = [abs(e) for e in n["eigs"]]
            # a nonzero node can still be singular (a zero divisor: L_a has
            # a nontrivial null space, i.e. a zero eigenvalue) -- that's a
            # real, exact 0/0, not a numeric accident, so it's spelled out
            # as inf rather than left to raise a runtime warning.
            per_node_spreads.append(max(mags) / min(mags) if min(mags) > 1e-12 else float("inf"))
        pooled_mags = [abs(e) for n in nonzero for e in n["eigs"]]
        out[dim] = {
            "n_nodes": len(nodes),
            "n_zero": n_zero,
            "n_zd": sum(1 for n in nodes if n["is_zd"]),
            "n_on_equator": sum(1 for n in nodes if n["on_equator"]),
            "per_node_spread_max": max(per_node_spreads) if per_node_spreads else None,
            "per_node_spread_all_one": all(abs(s - 1.0) < 1e-6 for s in per_node_spreads),
            "sibling_spread": (max(pooled_mags) / min(pooled_mags))
                               if pooled_mags and min(pooled_mags) > 1e-12 else None,
        }
    return out


# ── SVG: the 31-node fractal tree, one bar-cluster per node ────────────────
def render_svg(tree, order, title, path="bracket_firing_engine.svg"):
    W, H = 1200, 760
    PAD = 40
    LEVELS = [16, 8, 4, 2, 1]
    ROW_H = (H - 2 * PAD - 30) / len(LEVELS)

    # x-position: each node gets a horizontal slot sized to its dim's node count,
    # positioned by in-order tree position so children sit under their parent
    slots = {16: 1, 8: 2, 4: 4, 2: 8, 1: 16}
    xw = (W - 2 * PAD) / 16.0

    positions = {}

    def assign_x(node, lo, hi):
        positions[node["path"]] = (lo + hi) / 2.0
        if node["children"]:
            mid = (lo + hi) / 2.0
            assign_x(node["children"][0], lo, mid)
            assign_x(node["children"][1], mid, hi)

    assign_x(tree, PAD, W - PAD)

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
           f'viewBox="0 0 {W} {H}" font-family="monospace">',
           f'<rect width="{W}" height="{H}" fill="#06060a"/>',
           f'<text x="{W/2}" y="20" fill="#ddd" font-size="14" text-anchor="middle">'
           f'{title}</text>',
           f'<text x="{W/2}" y="34" fill="#666" font-size="9" text-anchor="middle">'
           f'the sedenion (16x16) matrix, its two orthogonal octonions, each\'s two '
           f'orthogonal quaternions, each\'s two complex pairs, each\'s two reals</text>']

    fire_pos = {n["path"]: i for i, n in enumerate(order)}

    def walk_edges(node):
        for c in node["children"]:
            x1, y1 = positions[node["path"]], PAD + 50 + LEVELS.index(node["dim"]) * ROW_H + ROW_H * 0.5
            x2, y2 = positions[c["path"]], PAD + 50 + LEVELS.index(c["dim"]) * ROW_H + ROW_H * 0.5
            out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                       f'stroke="#333" stroke-width="0.8"/>')
            walk_edges(c)

    walk_edges(tree)

    def walk_nodes(node):
        x = positions[node["path"]]
        y = PAD + 50 + LEVELS.index(node["dim"]) * ROW_H + ROW_H * 0.5
        col = LAYER_COLOR[node["dim"]]
        mags = [abs(e) for e in node["eigs"]]
        r = 3 + 9 * (sum(mags) / len(mags)) / (1 + sum(mags) / len(mags))
        opacity = 0.9 if not node["is_zd"] else 0.35
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{col}" '
                   f'fill-opacity="{opacity:.2f}" stroke="#000" stroke-width="0.5"/>')
        if node["on_equator"]:
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r+3:.1f}" fill="none" '
                       f'stroke="#ffffff" stroke-width="0.8" opacity="0.6"/>')
        if node["dim"] <= 4:
            fp = fire_pos.get(node["path"], -1)
            out.append(f'<text x="{x:.1f}" y="{y+r+9:.1f}" fill="#777" font-size="7" '
                       f'text-anchor="middle">#{fp}</text>')
        for c in node["children"]:
            walk_nodes(c)

    walk_nodes(tree)

    for i, dim in enumerate(LEVELS):
        y = PAD + 50 + i * ROW_H + ROW_H * 0.5
        out.append(f'<text x="{PAD-8}" y="{y+4:.1f}" fill="{LAYER_COLOR[dim]}" '
                   f'font-size="11" text-anchor="end" font-weight="bold">'
                   f'{LAYER_NAME[dim]}{dim}</text>')

    out.append(f'<text x="{PAD}" y="{H-14}" fill="#666" font-size="8">'
               f'fill opacity dims = zero-divisor node  ·  white ring = on its own ZD equator  '
               f'·  radius ~ mean |eigenvalue|  ·  #n = firing order (dim &lt;= 4)</text>')
    out.append('</svg>')

    with open(path, "w") as f:
        f.write("\n".join(out))
    return path


def main():
    args = sys.argv[1:]
    if args and args[0] == "--vec":
        vec = parse_vec(args[1])
        label = args[1]
    elif args:
        text = " ".join(args)
        vec = text_to_vec(text)
        label = repr(text)
    else:
        vec = parse_vec("e1+e10")
        label = "e1+e10  (a zero divisor on the equator)"

    print(f"THE BRACKETING & FIRING-ORDER ENGINE   input: {label}")

    ok = verify_block_identity(vec)
    print(f"  block identity verified on this input, every level: {ok}")
    if not ok:
        print("  REFUSING to proceed on an unverified tree.")
        return

    tree = build_tree(vec)
    order = firing_order(tree)

    print(f"\n  firing order ({len(order)} nodes, depth-first, smaller-norm-first):")
    line = "  ".join(f'{n["path"]}({n["layer"]}{n["dim"]})' for n in order)
    print(f"    {line}")

    print("\n  spectral texture by layer:")
    summ = spectral_summary(tree)
    for dim in (16, 8, 4, 2, 1):
        s = summ.get(dim)
        if not s:
            continue
        if s["per_node_spread_max"] is None:
            iso = "all nodes at this layer are the zero vector"
        elif s["per_node_spread_all_one"]:
            iso = "isometry exact (Hurwitz)"
        else:
            iso = f"NOT an isometry (max per-node spread={s['per_node_spread_max']:.4f})"
        sib = f"{s['sibling_spread']:.3f}" if s["sibling_spread"] is not None else "n/a"
        print(f"    {LAYER_NAME[dim]}{dim:>2}  nodes={s['n_nodes']:<2} "
              f"(zero={s['n_zero']:<2})  zero-divisors={s['n_zd']:<2}  "
              f"on-equator={s['n_on_equator']:<2}  {iso}  sibling-spread={sib}")
    print("\n  the finding: every NONZERO node below dim 16 is provably an")
    print("  isometry (Hurwitz — R, C, H, O are the only normed division")
    print("  algebras); the sedenion root is the only place a nonzero node's")
    print("  eigenvalue-modulus can spread, and that departure from 1.0 IS the")
    print("  zero-divisor fault, read directly off the spectrum rather than")
    print("  off the rank test alone.")

    path = render_svg(tree, order, label,
                       os.path.join(os.path.dirname(__file__) or ".",
                                     "bracket_firing_engine.svg"))
    print(f"\n  wrote {path}")


if __name__ == "__main__":
    main()
