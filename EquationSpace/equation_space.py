"""equation_space.py: the sign-space of basis-unit words over the Cayley-Dickson algebra (EquationSpace stub, 2026-11-19).
A point is (word, bracketing); its value is (sign, index) because a product of basis units is +-e_k with k the XOR of the indices.
Uses ValaQuenta.modules.emerger.maths.cd_mul (exact Fractions); the 16x16 table is built once from it.
   ValaQuenta/.venv/bin/python equation_space.py"""
import sys, os, math, itertools, random
sys.path.insert(0, os.path.expanduser("~/Projects/ThePlace"))
from fractions import Fraction as F
from ValaQuenta.modules.emerger import maths as E

def _basis(i): v = [F(0)]*16; v[i] = F(1); return v
TABLE = {}
for a in range(16):
    for b in range(16):
        p = E.cd_mul(_basis(a), _basis(b)); k = [j for j, x in enumerate(p) if x != 0]
        assert len(k) == 1 and abs(p[k[0]]) == 1 and k[0] == a ^ b       # +-e_(a xor b), exactly
        TABLE[(a, b)] = (int(p[k[0]]), a ^ b)

def mul(x, y):
    """(sign, index) times (sign, index)."""
    s, k = TABLE[(x[1], y[1])]; return (x[0]*y[0]*s, k)

def bracketings(word):
    """All values (sign, index) of the word over every full binary bracketing: a list of length Catalan(n-1), in a fixed order."""
    if len(word) == 1: return [(1, word[0])]
    return [mul(L, R) for k in range(1, len(word)) for L in bracketings(word[:k]) for R in bracketings(word[k:])]

def catalan(n): return math.comb(2*n, n)//(n+1)

def eq1():
    """For distinct imaginary a, b, c: (ab)c vs a(bc) -- same sign iff c = a xor b (closed, classed H)? Returns counts."""
    out = dict(triples=0, closed=0, assoc=0, closed_and_assoc=0, closed_not_assoc=0, open_and_assoc=0, H_class=0, H_agrees=0)
    for a, b, c in itertools.permutations(range(1, 16), 3):
        L, R = bracketings((a, b, c)); assoc = (L == R); closed = (c == a ^ b or a == b ^ c or b == a ^ c)
        out["triples"] += 1; out["closed"] += closed; out["assoc"] += assoc
        out["closed_and_assoc"] += closed and assoc; out["closed_not_assoc"] += closed and not assoc; out["open_and_assoc"] += (not closed) and assoc
        h = E.domain_of(frozenset((a, b, c))) == "H"; out["H_class"] += h; out["H_agrees"] += (h == assoc)
    return out

def eq2(n, trials, seed=0):
    rnd = random.Random(seed); dist = {}; worst = 0
    for _ in range(trials):
        w = tuple(rnd.randrange(1, 16) for _ in range(n)); v = bracketings(w)
        d = len(set(v)); dist[d] = dist.get(d, 0) + 1; worst = max(worst, d)
    return dist, worst

def eq3(n, trials, seed=1):
    rnd = random.Random(seed); pats = set(); tot = 0
    for _ in range(trials):
        w = tuple(rnd.randrange(1, 16) for _ in range(n)); tot += len({s for s, _ in bracketings(w)}); pats.add(tuple(s for s, _ in bracketings(w)))
    return tot/trials, len(pats)

if __name__ == "__main__":
    print("table built, all 256 products are +-e_(a xor b): True")
    print("EQ1", eq1())
    for n in range(3, 8):
        t = 20000 if n <= 6 else 5000; dist, worst = eq2(n, t); m, npat = eq3(n, 2000)
        print("EQ2 n=%d words=%d distinct values histogram %s worst=%d | EQ3 Catalan=%d mean distinct sign-patterns=%.3f (sign patterns seen: %d)" % (n, t, dict(sorted(dist.items())), worst, catalan(n-1), m, npat))
