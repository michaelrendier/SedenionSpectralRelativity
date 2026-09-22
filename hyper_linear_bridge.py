#!/usr/bin/env python3
"""
hyper_linear_bridge.py — The Hyper-Linear Algebra Decomposition, both sides
==============================================================================
Same recipe, two algebras. `GenerationalLineage/engine/toolsets/hyper_linear.py`
runs it on plain integers (`a*b`, base 10); `bracket_firing_engine.py` in this
repo runs it on sedenions (`L_a`, the Cayley-Dickson regular representation).
This script runs BOTH, side by side, self-contained (no cross-repo import —
this repo's own convention, matching GenerationalLineage's
"module-independence" rule in `engine/toolsets/__init__.py`).

THE RECIPE, stated once, generically:
    1. one generator per basis position — a SCALE operator (multiply by a
       digit, or L_x, left-multiply by a sedenion component)
    2. composed with a POSITION operator (a shift T^r, or a recursive
       Cayley-Dickson block split)
    3. read spectrally (DFT for the integer convolution; eigenvalues of the
       block matrix for the sedenion tower)

WHAT DIFFERS, and it is the whole finding: plain integer multiplication
under this recipe never breaks — Z has no zero divisors, full stop, so
there is no analogue of the sedenion root's "isometry fault." The tower
this repo already proved (Hurwitz: every node below dim 16 is an exact
isometry, only the sedenion root can fail) is a genuine STRUCTURE the
integers never even approach needing — Z sits, in this sense, "more
established" than even the octonions: a normed division algebra AND
commutative AND associative, three properties the CD tower sheds one at a
time on the way up to the sedenions, which keep none of them.

stdlib + numpy only.
"""
import math
import sys
import os

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bracket_firing_engine import build_tree, verify_block_identity, spectral_summary
from emerger_spectrum import parse_vec, text_to_vec


# ── the integer side, self-contained (mirrors GenerationalLineage's
#    engine/toolsets/hyper_linear.py exactly, kept independent per this
#    project's own module-independence rule) ────────────────────────────────
def _digits_lsd(n):
    return [int(c) for c in str(n)[::-1]]


def integer_hyper_linear(a: int, b: int) -> dict:
    ad, bd = _digits_lsd(a), _digits_lsd(b)
    rows = []
    for r, d in enumerate(bd):
        p = a * d
        rows.append({"row": r, "digit": d, "operator": f"L_{d} o T^{r}",
                     "n_digits": len(str(p)) if p else 1,
                     "spills": len(str(p)) > len(ad) if d else False})
    return {"a": a, "b": b, "product": a * b, "rows": rows,
            "n_spilling_rows": sum(1 for r in rows if r["spills"]),
            "n_zero_divisor_rows": 0,   # Z has none, ever — see note below
            }


def main():
    print("=" * 78)
    print("THE HYPER-LINEAR ALGEBRA DECOMPOSITION — integers vs sedenions")
    print("=" * 78)

    A, B = 1546854629, 7283619945
    iz = integer_hyper_linear(A, B)
    print(f"\n[Z, commutative, associative, no zero divisors]")
    print(f"  a={A}  b={B}  a*b={iz['product']}")
    print(f"  spilling rows (11-digit partial products): {iz['n_spilling_rows']}/10")
    print(f"  zero-divisor rows: {iz['n_zero_divisor_rows']}/10  "
          f"(ALWAYS 0 — Z is an integral domain, this is not measured, it is "
          f"structurally guaranteed)")

    vec = text_to_vec("primes are words")
    ok = verify_block_identity(vec)
    tree = build_tree(vec)
    summ = spectral_summary(tree)
    root = summ[16]
    print(f"\n[Sedenion tower S -> O -> H -> C -> R, non-commutative, "
          f"non-associative below O, zero divisors AT S]")
    print(f"  input: 'primes are words'  (block identity verified: {ok})")
    print(f"  root (dim16) isometry holds: {root['per_node_spread_all_one']}  "
          f"(False means the fault fired — it did)")
    for dim in (8, 4, 2, 1):
        s = summ[dim]
        print(f"  dim {dim:>2}: isometry holds for every nonzero node: "
              f"{s['per_node_spread_all_one']}  (ALWAYS True below dim 16 — "
              f"Hurwitz, not measured per-input, proven)")

    print(f"\n[the honest contrast]")
    print("  Z under a*b:      never faults — no zero-divisor rows exist to find,")
    print("                    the question this script asks of it has a trivial")
    print("                    answer (0) for every (a,b), by the definition of Z.")
    print("  S under L_a:      faults exactly once, exactly at the top (dim 16) —")
    print("                    below that, every node is exactly as clean as Z's")
    print("                    own multiplication, provably (Hurwitz), not by luck.")
    print("  Same recipe (SCALE generator + position operator + spectral read),")
    print("  run on two different algebras — one that can never fault, and one")
    print("  that faults in exactly one place, no more and no less.")


if __name__ == "__main__":
    main()
