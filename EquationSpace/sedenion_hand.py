"""sedenion_hand.py: exploratory (unregistered). Cayley-Dickson product (a,b)(c,d) = (ac - d*b, da + bc*), units e_i, e_i e_j = +-e_{i^j}.
   ValaQuenta/.venv/bin/python sedenion_hand.py"""
import numpy as np, itertools as it
def conj(x): y = -x.copy(); y[0] = x[0]; return y
def mul(x, y):
    n = len(x)
    if n == 1: return x * y
    h = n // 2; a, b, c, d = x[:h], x[h:], y[:h], y[h:]
    return np.concatenate([mul(a, c) - mul(conj(d), b), mul(d, a) + mul(b, conj(c))])
def unit(i, n=16): v = np.zeros(n); v[i] = 1; return v
N = 16
T = {}                                    # (i,j) -> (sign, k)
for i in range(N):
    for j in range(N):
        p = mul(unit(i), unit(j)); k = int(np.argmax(abs(p))); assert k == i ^ j and abs(p[k]) == 1; T[i, j] = (int(p[k]), k)
out = []
# 1. three fingers i,j,k = e1,e2,e4 (the XOR generators); the seven units they reach and the return
reach = {1, 2, 4}
ch = True
while ch:
    ch = False
    for a, b in it.product(list(reach), repeat=2):
        if a != b and (a ^ b) not in reach: reach.add(a ^ b); ch = True
out.append(f"1. units reached from e1,e2,e4 by products: {sorted(reach)} (7 imaginary units = Fano points); Fano lines (a,b,a^b) with a<b<a^b among 1..7: {[(a,b,a^b) for a in range(1,8) for b in range(a+1,8) if a^b>b]}")
# return test: i*j = +-k and (i*j)*k = -1
out.append(f"   e1*e2={T[1,2]}, e2*e4={T[2,4]}, e4*e1={T[4,1]}; (e1 e2) e4 = {T[T[1,2][1],4]} (a unit with sign): return to e0 with sign")
# 2. associativity of basis triples: octonion (indices<8) vs sedenion
def assoc(i, j, k):
    s1, a = T[i, j]; s2, b = T[a, k]; t1, c = T[j, k]; t2, d = T[i, c]
    return s1 * s2 * b == t1 * t2 * d and True and (s1 * s2 == t1 * t2)
for n in (4, 8, 16):
    tri = [t for t in it.product(range(1, n), repeat=3)]
    good = sum(assoc(*t) for t in tri)
    out.append(f"2. imaginary basis triples that associate in dim {n}: {good}/{len(tri)}")
# 3. zero divisors among D16 roots (+-e_i +-e_j) and among E8+E8 roots, via the real product
def vec(*pairs): v = np.zeros(N); [v.__setitem__(i, s) for i, s in pairs]; return v
D16 = [vec((i, s1), (j, s2)) for i in range(N) for j in range(i + 1, N) for s1 in (1, -1) for s2 in (1, -1)]
zd = [(r, s) for r in D16 for s in D16 if np.allclose(mul(r, s), 0)]
supp = lambda v: tuple(int(k) for k in np.nonzero(v)[0])
ass = sorted({supp(r) for r, s in zd})
out.append(f"3. D16 roots: {len(D16)}; ordered root pairs with product 0: {len(zd)}; distinct supports (assessors) among them: {len(ass)}; all low-high?: {all(a[0] < 8 <= a[1] for a in ass)}; with i in 1..7: {all(a[0] >= 1 for a in ass)}")
# E8 roots in each half
def e8_half():
    R = []
    for i in range(8):
        for j in range(i + 1, 8):
            for s1 in (1, -1):
                for s2 in (1, -1):
                    v = np.zeros(8); v[i] = s1; v[j] = s2; R.append(v)
    for signs in it.product((1, -1), repeat=8):
        if signs.count(-1) % 2 == 0: R.append(np.array(signs) / 2)
    return R
E8 = e8_half()
E8E8 = [np.concatenate([r, np.zeros(8)]) for r in E8] + [np.concatenate([np.zeros(8), r]) for r in E8]
zd2 = sum(1 for r in E8E8 for s in E8E8 if np.allclose(mul(r, s), 0))
out.append(f"   E8 roots {len(E8)}; E8+E8 roots {len(E8E8)}; ordered pairs with product 0 inside E8+E8: {zd2}")
# D16+ extra vectors: half-integer all (+-1/2)^16 with even minus signs: sample for zero-divisor pairs with D16 roots
rng = np.random.default_rng(0); hit = 0; tot = 0
for _ in range(2000):
    sg = rng.choice([-1, 1], 16)
    if (sg < 0).sum() % 2: sg[0] *= -1
    h = sg / 2
    for r in rng.choice(len(D16), 20, replace=False):
        tot += 1; hit += np.allclose(mul(D16[r], h), 0)
out.append(f"   D16+ glue vectors (+-1/2)^16 times a random D16 root: zero in {hit}/{tot} sampled pairs")
print("\n".join(out)); open("results_sedenion_hand_2026-11-20.txt", "w").write("\n".join(out) + "\n")
