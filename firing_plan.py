#!/usr/bin/env python3
"""
firing_plan.py — Bracketings that carry firing orders (the plan layer of the
Recursive Bracketing & Firing-Order Engine)
==========================================================================
bracket_firing_engine.py walks the 31-node Cayley-Dickson block tree and fires
the SMALLER-norm child first.  That is ONE rule for choosing an order.  This
module makes the order itself a first-class part of the bracketing:

    PLAN     a Leaf (one operator), or a Bracket(children, order)
    ORDER    a permutation of 1..k written beside the bracket; entry i names
             the child that fires i-th.  (2, 1) on two children: the second
             child fires first, the first child fires second.  Same reading
             as GenerationalLineage.engine.bracketing_firing_order
             .apply_firing_order(written, order).
    NOTATION (A B | 2 1)      one bracket, two children, second fires first
             ((A B | 2 1) C)  a bracket inside a bracket; the inner one runs
                              as ONE operation in its own order, and the
                              outer order (default 1 2) sequences it against C

A bracket is an operation: its children, fired in its order, composed as
operators (first fired is applied first, so the bracket's matrix is
M_last · … · M_first).  The bracket then sits inside its parent as a single
operator.  Order matters exactly where the members do not commute — that is
the whole content of "firing order": operator order changes the output, as a
numerator driving a denominator differs from a denominator driving a
numerator.  Application order and traversal order are the same order; there
is no direction beyond "order arrived at".

THE TWO-OCTONION MODEL OF THE SEDENION (the worked example):
    a = (a1, a2),  R = L((a1, 0))  the real octonion half,
                   I = L((0, a2))  the imaginary octonion half,
    L_a = R + I   (sum: exact), and the bracket (R I | 2 1) fires I first and
    R second:  matrix R·I, against (R I) = I·R.  They differ by the
    commutator of the two halves.

Exact: every matrix is a Fraction list-of-lists built from emerger_spectrum's
`cd_mul` (the Cayley-Dickson convention named in bracket_firing_engine.py).
stdlib only; no numpy needed here.

    python3 firing_plan.py            # runs verify() and prints the worked example
"""
import itertools, math, os, sys
from fractions import Fraction as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from emerger_spectrum import cd_mul

Matrix = list


# ── exact matrix helpers ────────────────────────────────────────────────────
def _identity(n):
    return [[F(int(r == c)) for c in range(n)] for r in range(n)]


def _matmul(A, B):
    n = len(A)
    Bt = list(zip(*B))
    return [[sum((a * b for a, b in zip(row, col)), F(0)) for col in Bt] for row in A]


def _equal(A, B):
    return all(a == b for ra, rb in zip(A, B) for a, b in zip(ra, rb))


def _key(A):
    return tuple(tuple(r) for r in A)


def left_matrix(a):
    """L_a, exact: column k is a·e_k."""
    n = len(a)
    cols = [cd_mul(tuple(a), tuple(F(int(i == k)) for i in range(n))) for k in range(n)]
    return [[cols[k][r] for k in range(n)] for r in range(n)]


# ── the plan ────────────────────────────────────────────────────────────────
class Leaf:
    """one operator.  `matrix` is its operator reading (operator()); `vec` is its element reading
    (value()).  Either may be absent if only the other reading is used."""
    def __init__(self, name, matrix=None, vec=None):
        self.name, self.matrix, self.vec = name, matrix, vec

    def __repr__(self):
        return self.name


class Bracket:
    def __init__(self, children, order=None):
        k = len(children)
        order = tuple(range(1, k + 1)) if order is None else tuple(order)
        if sorted(order) != list(range(1, k + 1)):
            raise ValueError(f"order must be a permutation of 1..{k}, got {order}")
        self.children, self.order = list(children), order

    def fired(self):
        """the children in the order they fire"""
        return [self.children[i - 1] for i in self.order]

    def __repr__(self):
        return notation(self)


def notation(plan):
    if isinstance(plan, Leaf):
        return plan.name
    body = " ".join(notation(c) for c in plan.children)
    if plan.order != tuple(range(1, len(plan.children) + 1)):
        body += " | " + " ".join(str(i) for i in plan.order)
    return f"({body})"


def fire_sequence(plan):
    """leaf names in the exact order they fire, internal bracket orders included"""
    if isinstance(plan, Leaf):
        return [plan.name]
    return [name for c in plan.fired() for name in fire_sequence(c)]


def operator(plan):
    """the plan as ONE operator: fired children composed, first fired applied first"""
    if isinstance(plan, Leaf):
        return plan.matrix
    n = len(plan.children[0].matrix) if isinstance(plan.children[0], Leaf) else len(operator(plan.children[0]))
    M = _identity(n)
    for c in plan.fired():
        M = _matmul(operator(c), M)
    return M


def value(plan):
    """the ELEMENT reading: a bracket is the algebra product of its fired children, folded left to
    right in firing order ((f1 f2) f3 …); nested brackets give the other groupings.  Unlike
    operator(), this is non-associative in the sedenions, so here the bracketing itself matters."""
    if isinstance(plan, Leaf):
        return tuple(plan.vec)
    kids = [value(c) for c in plan.fired()]
    acc = kids[0]
    for k in kids[1:]:
        acc = tuple(cd_mul(acc, k))
    return acc


def apply_plan(plan, x):
    M = operator(plan)
    return tuple(sum((m * v for m, v in zip(row, x)), F(0)) for row in M)


def parse(text, leaves):
    """'((A B | 2 1) C)' with leaves = {name: matrix} -> plan.  Whitespace-separated tokens."""
    toks = text.replace("(", " ( ").replace(")", " ) ").replace("|", " | ").split()
    pos = 0

    def group():
        nonlocal pos
        assert toks[pos] == "("; pos += 1
        kids, order = [], None
        while toks[pos] != ")":
            if toks[pos] == "(":
                kids.append(group())
            elif toks[pos] == "|":
                pos += 1; order = []
                while toks[pos] != ")":
                    order.append(int(toks[pos])); pos += 1
            else:
                kids.append(Leaf(toks[pos], leaves[toks[pos]])); pos += 1
        pos += 1
        return Bracket(kids, order)
    plan = group()
    assert pos == len(toks), "trailing tokens"
    return plan


# ── counting and enumeration ────────────────────────────────────────────────
def count_plans(n, kind="nary"):
    """How many plans over n leaves written in order.  kind:
         'flat'    one bracket, all n leaves, any order                      n!
         'binary'  every bracket has two children: Catalan(n-1) shapes, 2 orders per bracket
         'nary'    every bracket has ≥2 children and its own k! orders (ordered Schröder shapes)"""
    if kind == "flat":
        return math.factorial(n)
    if kind == "binary":
        return math.comb(2 * (n - 1), n - 1) // n * 2 ** (n - 1)
    T = {1: 1}

    def f(s, j):                      # ways to cut s leaves into j consecutive parts, each part a plan
        if j == 1:
            return T[s]
        return sum(T[p] * f(s - p, j - 1) for p in range(1, s - j + 2))
    for m in range(2, n + 1):
        T[m] = sum(f(m, j) * math.factorial(j) for j in range(2, m + 1))
    return T[n]


def binary_plans(leaves):
    """every binary bracketing of the leaves, written order kept, both orders at each bracket"""
    n = len(leaves)
    if n == 1:
        yield leaves[0]; return
    for cut in range(1, n):
        for L in binary_plans(leaves[:cut]):
            for R in binary_plans(leaves[cut:]):
                for order in ((1, 2), (2, 1)):
                    yield Bracket([L, R], order)


def permuted_shapes(leaves):
    """every binary tree shape over every ordering of the leaves, each bracket in written order.
    Reaches groupings a written-order plan cannot (e.g. (A C) B); for 3 leaves: 6 × 2 = 12."""
    for perm in itertools.permutations(leaves):
        yield from (p for p in binary_plans(list(perm)) if _is_default(p))


def _is_default(p):
    return isinstance(p, Leaf) or (p.order == (1, 2) and all(_is_default(c) for c in p.children))


def flat_plans(leaves):
    for order in itertools.permutations(range(1, len(leaves) + 1)):
        yield Bracket(list(leaves), order)


def distinct_results(plans):
    """{operator: [plans that produce it]} — how many different things the orders make available"""
    out = {}
    for p in plans:
        out.setdefault(_key(operator(p)), []).append(notation(p))
    return out


# ── the sedenion plans ──────────────────────────────────────────────────────
def two_octonion_leaves(a):
    """a = (a1, a2): R = L((a1,0)) real octonion half, I = L((0,a2)) imaginary octonion half"""
    h = len(a) // 2
    real = tuple(a[:h]) + (F(0),) * h
    imag = (F(0),) * h + tuple(a[h:])
    return Leaf("R", left_matrix(real)), Leaf("I", left_matrix(imag))


def two_octonions(a, order=(1, 2)):
    """the bracket of the two octonion halves, fired in `order`; (2, 1) = imaginary first, real second"""
    R, I = two_octonion_leaves(a)
    return Bracket([R, I], order)


def policy_written(node_vec, kids):
    return (1, 2)


def policy_reversed(node_vec, kids):
    return (2, 1)


def policy_smaller_norm(node_vec, kids):
    """the existing engine's rule: the smaller-norm child fires first; a tie breaks left"""
    nl, nr = (sum((c * c for c in k), F(0)) for k in kids)
    return (1, 2) if nl <= nr else (2, 1)


def component_plan(a, policy=policy_written, lo=0, hi=None):
    """The full Cayley-Dickson tree as a plan: leaves are the 16 single-component operators
    L(a_k e_k) (identity where a_k = 0, so an absent component is neutral), brackets are the
    halving of the index range, and `policy(vec, (left_vec, right_vec))` names each bracket's
    order.  This is the 'product reading' of a vector; it is NOT L_a (L_a is the SUM of the
    leaves).  The old engine's rule is policy_smaller_norm."""
    n = len(a)
    hi = n if hi is None else hi
    if hi - lo == 1:
        v = tuple(F(a[lo]) if i == lo else F(0) for i in range(n))
        return Leaf(f"e{lo}", left_matrix(v) if a[lo] != 0 else _identity(n))
    mid = (lo + hi) // 2
    kids = [component_plan(a, policy, lo, mid), component_plan(a, policy, mid, hi)]
    return Bracket(kids, policy(tuple(a[lo:hi]), (tuple(a[lo:mid]), tuple(a[mid:hi]))))


# ── self-check ──────────────────────────────────────────────────────────────
def verify():
    import random
    random.seed(7)
    res = {}
    a = tuple(F(random.randint(-3, 3)) for _ in range(16))
    R, I = two_octonion_leaves(a)
    La = left_matrix(a)
    res["L_a = R + I"] = all(La[r][c] == R.matrix[r][c] + I.matrix[r][c] for r in range(16) for c in range(16))
    p12, p21 = two_octonions(a, (1, 2)), two_octonions(a, (2, 1))
    res["(R I) = I·R"] = _equal(operator(p12), _matmul(I.matrix, R.matrix))
    res["(R I | 2 1) = R·I"] = _equal(operator(p21), _matmul(R.matrix, I.matrix))
    res["order matters for a generic sedenion"] = not _equal(operator(p12), operator(p21))
    res["fire sequence (2,1) = I then R"] = fire_sequence(p21) == ["I", "R"]
    # a bracket inside a bracket runs as one operation in its own order
    A, B, C = (Leaf(n, left_matrix(tuple(F(int(i == k)) for i in range(16)))) for n, k in (("A", 1), ("B", 2), ("C", 12)))
    inner = Bracket([A, B], (2, 1)); outer = Bracket([inner, C], (2, 1))
    res["nested firing sequence"] = fire_sequence(outer) == ["C", "B", "A"]
    res["nested = C then (B then A)"] = _equal(operator(outer), _matmul(_matmul(A.matrix, B.matrix), C.matrix))
    res["parse round trip"] = notation(parse("((A B | 2 1) C | 2 1)", {"A": A.matrix, "B": B.matrix, "C": C.matrix})) == "((A B | 2 1) C | 2 1)"
    res["count flat 3"] = count_plans(3, "flat") == 6
    res["count binary 3"] = count_plans(3, "binary") == len(list(binary_plans([A, B, C]))) == 8
    res["count nary 3"] = count_plans(3, "nary") == 8 + 6 and count_plans(2, "nary") == 2
    # operator reading is associative: regrouping at default order never changes it; element reading is not
    E1, E2, E3 = (Leaf(n, vec=tuple(F(int(i == k)) for i in range(16))) for n, k in (("A", 1), ("B", 10), ("C", 12)))
    M1, M2, M3 = (Leaf(l.name, matrix=left_matrix(l.vec)) for l in (E1, E2, E3))
    res["operator reading: regrouping keeps the result"] = _equal(operator(Bracket([Bracket([M1, M2]), M3])), operator(Bracket([M1, Bracket([M2, M3])])))
    res["element reading: some regrouping changes the result"] = any(
        value(Bracket([Bracket([x, y]), z])) != value(Bracket([x, Bracket([y, z])]))
        for x, y, z in itertools.permutations([E1, E2, E3]))
    res["written-order binary plans reach the separable permutations (6, 22, 90)"] = [
        len({tuple(fire_sequence(p)) for p in binary_plans([Leaf(str(i)) for i in range(n)])}) for n in (3, 4, 5)] == [6, 22, 90]
    # the old engine's rule is one policy: leaf order equals bracket_firing_engine.firing_order's leaves
    from bracket_firing_engine import build_tree, firing_order
    v = tuple(F(random.randint(-4, 4)) for _ in range(16))
    old = [int(n["path"].replace("L", "0").replace("R", "1"), 2) for n in firing_order(build_tree(v)) if n["dim"] == 1]
    new = [int(s[1:]) for s in fire_sequence(component_plan(v, policy_smaller_norm))]
    res["policy_smaller_norm reproduces the old firing order"] = old == new
    return res


if __name__ == "__main__":
    for k, ok in verify().items():
        print(("PASS " if ok else "FAIL ") + k)
    a = tuple(F(x) for x in (1, 2, 0, 1, 0, 0, 3, 0, 0, 1, 0, 0, 2, 0, 0, 1))
    R, I = two_octonion_leaves(a)
    d = [[operator(two_octonions(a, (1, 2)))[r][c] - operator(two_octonions(a, (2, 1)))[r][c] for c in range(16)] for r in range(16)]
    print("\nthe two-octonion sedenion  a = (a1, a2):")
    print("  plan (R I)       fires R first, I second:", notation(two_octonions(a, (1, 2))))
    print("  plan (R I | 2 1) fires I first, R second:", notation(two_octonions(a, (2, 1))))
    print("  entries where the two orders differ:", sum(1 for r in d for x in r if x != 0), "of 256")
