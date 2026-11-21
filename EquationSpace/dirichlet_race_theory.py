"""dirichlet_race_theory.py (2026-11-20, exploratory, UNREGISTERED): the Rubinstein-Sarnak limiting distribution of the prime race mod 16, built from the zeros computed in dirichlet_zeros.py, against the actual primes up to 2e9.
E(x;q,a) = (log x / sqrt x)(phi(q) pi(x;q,a) - pi(x)).  Under GRH and Linear Independence of the zero ordinates (both ASSUMED, unproved):
   E(x;q,a) -> (1 - N(q,a)) - sum_{chi != chi0} conj(chi(a)) sum_{gamma} e^{i theta_gamma}/(1/2 + i gamma),   theta_gamma independent uniform,
N(q,a) = #{b mod q : b^2 = a}; real characters have zeros in +-gamma pairs (2 Re over gamma > 0); a complex pair (psi, conj psi) gives 2 Re over all gamma of psi.  Zeros are truncated at |t| < 70 (the tail adds variance, so
spreads are slightly under-stated).  Validation: q = 4 must give the known density 0.9959 for 'primes 3 mod 4 lead'.   Run: ../.venv/bin/python dirichlet_race_theory.py"""
import json, itertools, numpy as np
rng = np.random.default_rng(20261120)
Z = json.load(open("results/dirichlet_zeros_mod16.json")); D = np.load("results/prime_race_mod16.npz"); X, CNT, CL = D["x"], D["counts"], [int(c) for c in D["classes"]]
LOG = {1: (0, 0), 5: (0, 1), 9: (0, 2), 13: (0, 3), 15: (1, 0), 11: (1, 1), 7: (1, 2), 3: (1, 3)}
def chi(sign, k): return {n: (sign ** s) * (1j ** (k * t)) for n, (s, t) in LOG.items()}
CH = {"chi_-4": chi(-1, 0), "chi_8": chi(+1, 2), "chi_-8": chi(-1, 2), "psi_even": chi(+1, 1), "psi_odd": chi(-1, 1)}
REAL = ["chi_-4", "chi_8", "chi_-8"]; CPLX = ["psi_even", "psi_odd"]
Nsq = {a: sum(1 for b in range(16) if (b * b) % 16 == a) for a in CL}; mean = {a: 1 - Nsq[a] for a in CL}
def simulate(M, classes, realset, cplxset, chars, Nq):
    """M samples of E(a) for the given classes; returns array (M, len(classes))"""
    out = np.tile(np.array([1 - Nq[a] for a in classes], float), (M, 1))
    for nm in realset:
        g = np.array([z for z in Z[nm] if z > 0]); amp = 1 / (0.5 + 1j * g)
        for lo in range(0, M, 20000):
            n = min(20000, M - lo); th = rng.uniform(0, 2 * np.pi, (n, len(g))); s = 2 * np.real((np.exp(1j * th) * amp)).sum(1)
            out[lo:lo + n] -= s[:, None] * np.array([chars[nm][a].real for a in classes])[None, :]
    for nm in cplxset:
        g = np.array(Z[nm]); amp = 1 / (0.5 + 1j * g)
        for lo in range(0, M, 20000):
            n = min(20000, M - lo); th = rng.uniform(0, 2 * np.pi, (n, len(g))); s = (np.exp(1j * th) * amp).sum(1)      # complex sum
            out[lo:lo + n] -= 2 * np.real(np.conj(np.array([chars[nm][a] for a in classes]))[None, :] * s[:, None])
    return out
# ---- validation: q = 4, 'primes 3 mod 4 lead'
c4 = {3: {3: -1, 1: 1}}; chi4 = {"chi_-4": {1: 1, 3: -1}}; N4 = {1: 2, 3: 0}
E4 = simulate(200000, [1, 3], ["chi_-4"], [], chi4, N4); p4 = float((E4[:, 1] > E4[:, 0]).mean())
print(f"q=4 validation: P(3 mod 4 leads) = {p4:.4f}   (Rubinstein-Sarnak 0.9959; zeros truncated at |t| < 70)")
# ---- q = 16
M = 400000; E = simulate(M, CL, REAL, CPLX, CH, Nsq); print("\nmod 16 limiting distribution: mean and sd of E(x;16,a), prediction (1 - N):")
res = {"validation_q4": p4, "classes": CL, "pred_mean": [mean[a] for a in CL], "pred_sd": [float(E[:, i].std()) for i in range(8)]}
for i, a in enumerate(CL): print(f"   class {a:>2d}: predicted mean {mean[a]:+d}   simulated mean {E[:, i].mean():+.3f}   sd {E[:, i].std():.3f}")
low = np.argsort(E, axis=1)                                                       # ascending: low[:,0] = lowest class
p_low = [float((low[:, 0] == i).mean()) for i in range(8)]; p_high = [float((low[:, -1] == i).mean()) for i in range(8)]
trip = lambda S: float(np.mean([set(CL[j] for j in row[:3]) == S for row in low[:100000]]))
gap = {1, 11, 15}; orbit = sorted({tuple(sorted((u * g) % 16 for g in gap)) for u in CL})
p_trip = {str(t): trip(set(t)) for t in orbit}
print("\nP(class is the LOWEST):", {CL[i]: round(p_low[i], 3) for i in range(8)}); print("P(class is the HIGHEST):", {CL[i]: round(p_high[i], 3) for i in range(8)})
print("P(the three lowest classes are exactly T) for the 8 images of the Niemeier gap {1,11,15} under the unit group:", {k: round(v, 4) for k, v in p_trip.items()})
allp = {}
for S in itertools.combinations(CL, 3): allp[S] = trip(set(S))
rank = sorted(allp.items(), key=lambda kv: -kv[1]); print("most probable 'three lowest' triples:", [(k, round(v, 4)) for k, v in rank[:4]], "| gap triple (1,11,15):", round(allp[(1, 11, 15)], 4), "rank", [k for k, _ in rank].index((1, 11, 15)) + 1, "of 56")
# ---- empirical, log-uniform in x (the density RS use)
pi = CNT.sum(1) + 1; Eemp = (np.log(X)[:, None] / np.sqrt(X)[:, None]) * (8 * CNT - pi[:, None]); sel = X >= 10 ** 5; Es = Eemp[sel]
print("\nempirical, 6,000 log-spaced x between 1e5 and 2e9: mean of E(x;16,a):", {CL[i]: round(float(Es[:, i].mean()), 2) for i in range(8)})
lw = np.argsort(Es, axis=1); e_low = [float((lw[:, 0] == i).mean()) for i in range(8)]; e_high = [float((lw[:, -1] == i).mean()) for i in range(8)]
e_trip = float(np.mean([set(CL[j] for j in row[:3]) == gap for row in lw]))
print("empirical P(lowest):", {CL[i]: round(e_low[i], 3) for i in range(8)}); print("empirical P(highest):", {CL[i]: round(e_high[i], 3) for i in range(8)}); print("empirical P(three lowest = {1,11,15}):", round(e_trip, 4))
o4 = (CNT[:, [CL.index(a) for a in (3, 7, 11, 15)]].sum(1) > CNT[:, [CL.index(a) for a in (1, 5, 9, 13)]].sum(1)); print("empirical: 3 mod 4 leads at", round(float(o4[sel].mean()) * 100, 2), "% of the log-spaced x from 1e5 to 2e9; at x = 2e9 the lead is", int(CNT[-1, [CL.index(a) for a in (3, 7, 11, 15)]].sum() - CNT[-1, [CL.index(a) for a in (1, 5, 9, 13)]].sum()))
# coarse curves for the gallery (E(x;16,a) at ~240 x) and summary
step = max(1, len(X) // 240); curves = {"x": [int(v) for v in X[::step]], "E": [[round(float(v), 3) for v in Eemp[::step, i]] for i in range(8)]}
res.update(dict(sim_p_lowest=p_low, sim_p_highest=p_high, emp_p_lowest=e_low, emp_p_highest=e_high, gap_triple_sim=allp[(1, 11, 15)], gap_triple_rank=[k for k, _ in rank].index((1, 11, 15)) + 1, gap_triple_emp=e_trip,
               emp_mean=[float(Es[:, i].mean()) for i in range(8)], mod4_emp_lead=float(o4[sel].mean()), curves=curves, N=int(X[-1]), zeros_T=70, samples=M))
json.dump(res, open("results/dirichlet_race_theory.json", "w"), default=lambda o: o.item()); print("\nwritten results/dirichlet_race_theory.json")
