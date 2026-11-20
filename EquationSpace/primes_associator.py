"""primes_associator.py (exploratory, unregistered): (1) Conway's FRACTRAN PRIMEGAME as a recursive input-output cycle that outputs the primes;
(2) the Fano position of the ADD/SCALE/SIGN generators e1,e2,e4 and their associator.
   python3 primes_associator.py"""
from fractions import Fraction
import numpy as np, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# (1) FRACTRAN: n -> n * (first fraction that gives an integer); the output n is the next input.
PRIME = [Fraction(a, b) for a, b in [(17, 91), (78, 85), (19, 51), (23, 38), (29, 33), (77, 29), (95, 23), (77, 19), (1, 17), (11, 13), (13, 11), (15, 14), (15, 2), (55, 1)]]
n = 2; primes = []; steps = 0
while len(primes) < 12:
    for f in PRIME:
        m = n * f
        if m.denominator == 1: n = int(m); break
    steps += 1
    if n & (n - 1) == 0 and n > 2:
        e = n.bit_length() - 1
        if not primes or e > primes[-1]: primes.append(e)
print("FRACTRAN powers of 2 (exponents), in order:", primes, "after", steps, "iterations")
# Erato / Euclid recursion with the list fed back
ps = []; m = 2
while len(ps) < 12:
    if all(m % p for p in ps): ps.append(m)
    m += 1
print("sieve with its own output as input:        ", ps)
# (2) e1, e2, e4: not a Fano line; associator
def conj(x): y = -x.copy(); y[0] = x[0]; return y
def mul(x, y):
    k = len(x)
    if k == 1: return x * y
    h = k // 2; a, b, c, d = x[:h], x[h:], y[:h], y[h:]
    return np.concatenate([mul(a, c) - mul(conj(d), b), mul(d, a) + mul(b, conj(c))])
u = lambda i, k=8: np.eye(k)[i]
for name, (i, j, k) in {"(e1,e2,e4) = (A,S,G)": (1, 2, 4), "(e1,e2,e3) = a Fano line": (1, 2, 3)}.items():
    left = mul(mul(u(i), u(j)), u(k)); right = mul(u(i), mul(u(j), u(k)))
    print(f"{name}: (xy)z = {np.round(left,3).tolist()}  x(yz) = {np.round(right,3).tolist()}  associator norm {np.linalg.norm(left-right):.1f}")
sq = [(i, mul(u(i, 16), u(i, 16))[0]) for i in (1, 2, 4, 8)]
print("squares of A, S, G, K=e8 (real part):", sq)
