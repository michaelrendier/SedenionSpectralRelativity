"""chebyshev_mod16.py (2026-11-20, exploratory, unregistered): Chebyshev's bias for the primes, checked against the video's numbers (mod 4) and extended to the odd residue classes mod 16,
the classes the Niemeier/Monster engine reads as the 'prime sector' (Niemeier gap {1, 11, 15}).  stdlib only, bytearray sieve to N.   Run: ../.venv/bin/python chebyshev_mod16.py"""
import sys, math
N = 10 ** 8
sv = bytearray([1]) * (N + 1); sv[0] = sv[1] = 0
for i in range(2, int(N ** .5) + 1):
    if sv[i]: sv[i * i::i] = bytearray(len(range(i * i, N + 1, i)))
pr = [i for i in range(2, N + 1) if sv[i]]; print("primes up to 1e8:", len(pr))
# mod 4 race, as in the video
c1 = c3 = 0; first_blue = None; lead_orange = lead_blue = tie = 0; checks = {}
j = 0; npr = len(pr)
for x in range(3, N + 1):
    while j < npr and pr[j] <= x:
        p = pr[j]; j += 1
        if p % 4 == 1: c1 += 1
        elif p % 4 == 3: c3 += 1
    if x in (10, 100, 1000, 10 ** 4, 10 ** 5, 10 ** 6, 10 ** 7, 10 ** 8): checks[x] = (c3, c1)
    if c1 > c3 and first_blue is None: first_blue = x
    if c3 > c1: lead_orange += 1
    elif c1 > c3: lead_blue += 1
    else: tie += 1
print("mod 4  (orange = 3 mod 4, blue = 1 mod 4):"); [print(f"   x={x:>9,d}: 3 mod 4 = {a:>8,d}   1 mod 4 = {b:>8,d}   lead {a-b:+d}") for x, (a, b) in sorted(checks.items())]
tot = lead_orange + lead_blue + tie; print(f"   first blue lead at x = {first_blue:,d}; limits 3..1e8: orange leads {lead_orange/tot*100:.3f}%, blue {lead_blue/tot*100:.3f}%, ties {tie/tot*100:.3f}%   (the video: 99.966% / about 0.03%)")
# mod 16 classes
cls = [1, 3, 5, 7, 9, 11, 13, 15]; cnt = {a: 0 for a in cls}
for p in pr:
    if p % 2: cnt[p % 16] += 1
SQ = {a for a in cls if any((x * x) % 16 == a for x in range(16))}
print("mod 16 odd classes, primes up to 1e8 (squares of odd numbers are 1 or 9):"); 
for a in sorted(cls, key=lambda a: -cnt[a]): print(f"   {a:>2d} mod 16: {cnt[a]:>9,d}   {'square class' if a in SQ else 'non-residue'}{'   <- Niemeier gap slot' if a in (1,11,15) else ''}")
mean = sum(cnt.values()) / 8; print("   deviation from equal share (counts - mean):", {a: int(cnt[a] - mean) for a in cls})
print("   squares classes {1,9} versus the six non-residues: mean deficit of the square classes =", int(mean - (cnt[1] + cnt[9]) / 2))
