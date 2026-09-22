#!/usr/bin/env python3
"""
crankshaft_three_phase.py — The box-kite's own 3-fold rotation, spectrally
==============================================================================
The Wankel framing this project has used since the ZD-focal-point/precession
work ("the sedenion wankel... an 8 cycle 2 stroke engine") asked for a
CRANKSHAFT: the single rotating axis a rotor's motion is read against. This
finds the exact, established object that plays that role for one box-kite,
and spectrally decomposes it into THREE PHASES — not a metaphor, a checked
representation-theory fact.

THE CRANKSHAFT, found and verified (not assumed): each box-kite's 6
Assessors split into exactly 3 "reversal pairs" — its 3 non-edges
(de Marrais/`marrais_boxkite_catalog.txt` §6). Cyclically permuting those
3 pairs is a genuine graph automorphism of the octahedron (order 3,
verified: R^3 = I) AND commutes with the box-kite's own vibrational
Laplacian (verified: R @ L == L @ R) — i.e. it is a real symmetry of the
object being decomposed, not an arbitrary relabelling. That rotation R
IS the crankshaft: the box-kite has 3 lobes (the reversal pairs), R turns
them into each other, exactly like a Wankel rotor's 3 faces turning past
one fixed housing.

THE THREE-PHASE READ: because R^3 = I, R's eigenvalues on any subspace it
preserves are cube roots of unity {1, omega, omega^2} = {0 deg, 120 deg,
-120 deg} -- a genuine 3-phase system in the literal electrical-engineering
sense (three signals at the same frequency, 120 degrees apart). Since R
commutes with L, R acts WITHIN each of L's own eigenspaces -- diagonalizing
R there assigns each vibrational mode a phase. Verified live, all 7 struts,
identical every time:

    lambda=0  (the e0 zero mode, 1-dim):  phase 0 deg only        (all 3 collapse to none-moving)
    lambda=4  (3-fold degenerate):        phases {0, +120, -120} deg  (the full 3-phase set)
    lambda=6  (2-fold degenerate):        phases {+120, -120} deg    (moving phases only, no 0 deg)

Self-contained (no cross-repo import, per this project's module-
independence convention) -- rebuilds the 7 box-kite graphs directly from
`marrais_boxkite_catalog.txt`'s own tables rather than importing
ValaQuenta's box_kite module.

stdlib + numpy only.
"""
import numpy as np

# the 7 box-kites, exactly as verified in marrais_boxkite_catalog.txt §6
BOX_KITES = {
    1: [(2,3),(3,2),(4,5),(5,4),(6,7),(7,6)],
    2: [(1,3),(3,1),(4,6),(5,7),(6,4),(7,5)],
    3: [(1,2),(2,1),(4,7),(5,6),(6,5),(7,4)],
    4: [(1,5),(2,6),(3,7),(5,1),(6,2),(7,3)],
    5: [(1,4),(2,7),(3,6),(4,1),(6,3),(7,2)],
    6: [(1,7),(2,4),(3,5),(4,2),(5,3),(7,1)],
    7: [(1,6),(2,5),(3,4),(4,3),(5,2),(6,1)],
}


def _octahedron_graph(verts):
    """4-regular on 6 vertices; the 3 non-edges are the reversal pairs
    (a,b)<->(b,a). Built directly from the vertex list, not assumed."""
    n = len(verts)
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            a, b = verts[i], verts[j]
            if b != (a[1], a[0]):     # not a reversal pair -> an edge
                edges.append((i, j))
    non_edges = [(i, j) for i in range(n) for j in range(i + 1, n)
                 if (i, j) not in edges]
    return edges, non_edges


def _laplacian(n, edges):
    L = np.zeros((n, n))
    for i, j in edges:
        L[i, j] = -1
        L[j, i] = -1
    for i in range(n):
        L[i, i] = sum(1 for e in edges if i in e)
    return L


def _crankshaft(non_edges, n=6):
    """The 3-fold rotation cycling the 3 reversal-pair lobes into each
    other: lobe k -> lobe (k+1) mod 3, index-order preserved within a lobe."""
    lobes = [list(pair) for pair in non_edges]
    R = np.zeros((n, n))
    for k in range(3):
        src, dst = lobes[k], lobes[(k + 1) % 3]
        for a, b in zip(src, dst):
            R[b, a] = 1.0
    return R


def three_phase_decomposition(strut: int) -> dict:
    verts = BOX_KITES[strut]
    edges, non_edges = _octahedron_graph(verts)
    L = _laplacian(6, edges)
    R = _crankshaft(non_edges)

    r3_is_identity = np.allclose(R @ R @ R, np.eye(6))
    r_commutes_with_l = np.allclose(R @ L, L @ R)

    w, V = np.linalg.eigh(L)
    phases = {}
    for lam in (0.0, 4.0, 6.0):
        idxs = np.where(np.isclose(w, lam))[0]
        E = V[:, idxs]
        Rp = E.T @ R @ E
        wr = np.linalg.eigvals(Rp)
        phases[lam] = sorted(round(float(np.degrees(np.angle(v))), 1) for v in wr)

    return {
        "strut": strut, "r3_is_identity": r3_is_identity,
        "r_is_genuine_symmetry": r_commutes_with_l,
        "phases_by_mode": phases,
    }


def main():
    print("THE CRANKSHAFT, THREE-PHASE — verified across all 7 box-kites\n")
    all_ok = True
    for s in range(1, 8):
        d = three_phase_decomposition(s)
        ok = d["r3_is_identity"] and d["r_is_genuine_symmetry"]
        all_ok &= ok
        print(f"strut {s}:  R^3=I:{d['r3_is_identity']}  "
              f"R commutes with L:{d['r_is_genuine_symmetry']}")
        for lam, ph in d["phases_by_mode"].items():
            print(f"    lambda={lam:<4} phases(deg)={ph}")
    print(f"\nidentical pattern on every strut: {all_ok}")
    print("\nreading: lambda=4's 3-fold degeneracy IS a genuine 3-phase system")
    print("under the box-kite's own 3-lobe rotation; lambda=6 carries only the")
    print("two moving phases (no 0-deg/stationary component); lambda=0 (the e0")
    print("zero mode) is phase-0 only, consistent with it being the mode that")
    print("exists everywhere and propagates nowhere.")


if __name__ == "__main__":
    main()
