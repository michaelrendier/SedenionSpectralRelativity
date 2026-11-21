"""prime_race_counts.py (2026-11-20): pi(x; 16, a) for every odd class a, at 6,000 log-spaced x from 10^3 to N, by a numpy segmented sieve (also pi(x), pi(x; 4, a), pi(x; 8, a) follow from the classes).
Writes results/prime_race_mod16.npz.  Run: ../.venv/bin/python prime_race_counts.py N   (default 2e9; about a minute per 10^9)"""
import sys, time, numpy as np
N = int(float(sys.argv[1])) if len(sys.argv) > 1 else 2_000_000_000
xs = np.unique(np.exp(np.linspace(np.log(1000), np.log(N), 6000)).astype(np.int64)); xs[-1] = N
CL = np.array([1, 3, 5, 7, 9, 11, 13, 15]); counts = np.zeros((len(xs), 8), dtype=np.int64); two = np.zeros(len(xs), dtype=np.int64)
r = int(N ** 0.5) + 1; sm = np.ones(r + 1, bool); sm[:2] = False
for i in range(2, int(r ** .5) + 1):
    if sm[i]: sm[i * i::i] = False
base = np.nonzero(sm)[0]; SEG = 1 << 24; run = np.zeros(8, dtype=np.int64); run2 = 0; t0 = time.time(); k = 0
for lo in range(0, N + 1, SEG):
    hi = min(lo + SEG, N + 1); seg = np.ones(hi - lo, bool)
    if lo == 0: seg[:2] = False
    for p in base:
        if p * p >= hi: break
        s = max(p * p, ((lo + p - 1) // p) * p); seg[s - lo::p] = False
    pr = np.nonzero(seg)[0] + lo; cls = pr % 16
    while k < len(xs) and xs[k] < hi:                                  # samples inside this segment
        idx = np.searchsorted(pr, xs[k], side="right"); c = np.bincount(cls[:idx], minlength=16)[CL]; counts[k] = run + c; two[k] = run2 + (1 if lo == 0 and xs[k] >= 2 else (1 if lo > 0 and False else 0)); k += 1
    run += np.bincount(cls, minlength=16)[CL]
    if lo == 0: run2 = 1                                                # the prime 2 (class 2 mod 16 is not an odd class)
    if (lo // SEG) % 20 == 0: print(f"{hi:>13,d} {time.time()-t0:5.0f}s", flush=True)
np.savez("results/prime_race_mod16.npz", x=xs, counts=counts, classes=CL)
print("done; pi(N) odd primes =", int(counts[-1].sum()), "+ the prime 2")
