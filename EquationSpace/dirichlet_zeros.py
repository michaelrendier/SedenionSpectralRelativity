"""dirichlet_zeros.py (2026-11-20): zeros of the Dirichlet L-functions that govern the prime race mod 16, computed here (mpmath Hurwitz zeta), not looked up.
(Z/16)* = <-1> x <5> = C2 x C4.  A character is chi(-1) = +-1 and chi(5) = i^k.  Nonprincipal: k = 0, chi(-1) = -1 -> chi_-4 (conductor 4); k = 2, even -> chi_8; k = 2, odd -> chi_-8 (conductor 8);
k = 1, 3 with chi(-1) = +-1 -> four PRIMITIVE characters of conductor 16 with values in {+-1, +-i} (quarter turns).  Imprimitive ones have the same zeros as their primitive parent (chi(2) = 0).
Checks the zeros of L(s, chi_-4) against the published first values (6.0209489, 10.2437703, 12.9880980, 16.3426071, 18.2919930).  Run: ../.venv/bin/python dirichlet_zeros.py T   (default T = 70)"""
import sys, json, mpmath as mp
mp.mp.dps = 15; T = float(sys.argv[1]) if len(sys.argv) > 1 else 70.0
LOG = {1: (0, 0), 5: (0, 1), 9: (0, 2), 13: (0, 3), 15: (1, 0), 11: (1, 1), 7: (1, 2), 3: (1, 3)}      # n = (-1)^s 5^t mod 16
def make(sign, k): return {n: (sign ** s) * (1j ** (k * t)) for n, (s, t) in LOG.items()}
CHARS = {"chi_-4": (make(-1, 0), False), "chi_8": (make(+1, 2), False), "chi_-8": (make(-1, 2), False), "psi_even": (make(+1, 1), True), "psi_odd": (make(-1, 1), True)}
def L(s, chi):
    return sum(mp.mpc(v) * mp.zeta(s, mp.mpf(n) / 16) for n, v in chi.items()) * mp.mpf(16) ** (-s)
def zeros(chi, complex_char, T, step=0.25):
    lo = -T if complex_char else 0.0; ts = [lo + i * step for i in range(int((T - lo) / step) + 1)]; vals = [abs(L(mp.mpc(0.5, t), chi)) for t in ts]; out = []
    for i in range(1, len(ts) - 1):
        if vals[i] < vals[i - 1] and vals[i] < vals[i + 1] and vals[i] < 0.6:
            try:
                r = mp.findroot(lambda s: L(s, chi), mp.mpc(0.5, ts[i]), tol=1e-9, maxsteps=30)
                if abs(r.real - 0.5) < 1e-5 and abs(L(r, chi)) < 1e-6 and all(abs(r.imag - z) > 1e-4 for z in out): out.append(float(r.imag))
            except Exception: pass
    return sorted(out)
res = {}
for name, (chi, cx) in CHARS.items():
    z = zeros(chi, cx, T); res[name] = z; print(name, len(z), "zeros up to |t| <", T, "; first:", [round(x, 4) for x in z[:6]], flush=True)
ref = [6.0209489, 10.2437703, 12.9880980, 16.3426071, 18.2919930]; got = res["chi_-4"][:5]
print("chi_-4 check against the published values: max abs error", max(abs(a - b) for a, b in zip(got, ref)) if len(got) == 5 else "FEWER THAN 5 FOUND")
json.dump(res, open("results/dirichlet_zeros_mod16.json", "w"))
