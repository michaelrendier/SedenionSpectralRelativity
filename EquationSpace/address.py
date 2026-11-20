"""address.py: EquationSpace test 5, Part A (see 07_registered_grammar_catalog_address.md).  Address of a quantity = the 16-vector with e1..e7 = exponents over
(kg, m, s, A, K, mol, cd) (the order of GenerationalLineage units.py), all other components 0.  The 16-in 16-out operator is the Emerger's sigma_rb / emerge.
   ValaQuenta/.venv/bin/python address.py"""
import sys, os, itertools, json
sys.path.insert(0, os.path.expanduser("~/Projects/ThePlace")); sys.path.insert(0, os.path.expanduser("~/Projects/ThePlace/GenerationalLineage"))
from fractions import Fraction as Fr
from ValaQuenta.modules.emerger import maths as E
from engine.toolsets import units as U
Q = {"mass (inertia)": (1,0,0,0,0,0,0), "length": (0,1,0,0,0,0,0), "time": (0,0,1,0,0,0,0), "velocity": (0,1,-1,0,0,0,0), "acceleration": (0,1,-2,0,0,0,0),
     "momentum": (1,1,-1,0,0,0,0), "force N = m a": (1,1,-2,0,0,0,0), "energy J": (1,2,-2,0,0,0,0), "power W": (1,2,-3,0,0,0,0), "action J s": (1,2,-1,0,0,0,0),
     "pressure Pa": (1,-1,-2,0,0,0,0), "frequency Hz": (0,0,-1,0,0,0,0), "G (Newton)": (-1,3,-2,0,0,0,0),
     "entropy J/K": (1,2,-2,0,-1,0,0), "temperature K": (0,0,0,0,1,0,0), "molar entropy J/(K mol)": (1,2,-2,0,-1,-1,0), "amount mol": (0,0,0,0,0,1,0), "luminous cd": (0,0,0,0,0,0,1),
     "current A": (0,0,0,1,0,0,0), "charge C": (0,0,1,1,0,0,0), "voltage V": (1,2,-3,-1,0,0,0), "resistance Ohm": (1,2,-3,-2,0,0,0), "capacitance F": (-1,-2,4,2,0,0,0),
     "epsilon_0": (-1,-3,4,2,0,0,0), "mu_0": (1,1,-2,-2,0,0,0), "dimensionless": (0,0,0,0,0,0,0)}
MECH = [n for n, v in Q.items() if all(c == 0 for c in v[3:]) and any(v)]            # support within kg, m, s
def addr(vec, assign=None):
    a = assign or tuple(range(1, 8)); x = [Fr(0)] * 16
    for i, c in enumerate(vec): x[a[i]] = Fr(c)
    return x
def tilt_nonzero(x): s = E.sigma_rb(x); return sum(1 for t in s["tilt"] if t != 0), sum(1 for t in s["axis"] if t != 0)
print("== addresses of the registered assignment (kg,m,s,A,K,mol,cd) -> e1..e7")
print("%-26s %-22s %6s %6s %-8s %-5s %-5s" % ("quantity", "exponents", "tilt#", "axis#", "domain", "ZD", "equat"))
for n, v in Q.items():
    x = addr(v); tl, ax = tilt_nonzero(x); sup = frozenset(i for i in range(1, 16) if x[i] != 0)
    dom = E.domain_of(sup) if sup else "R"
    print("%-26s %-22s %6d %6d %-8s %-5s %-5s" % (n, str(v[:7]), tl, ax, dom, E.is_zero_divisor(x), E.on_zd_equator(x)))
# A1
mech_zero = all(tilt_nonzero(addr(Q[n])) == (0, 0) for n in MECH); nonmech = [n for n in Q if n not in MECH and any(Q[n]) and any(Q[n][:3]) and any(Q[n][3:])]
print("\nA1 mechanical quantities with tilt=axis=0:", mech_zero, "(%d of them)" % len(MECH))
print("   mixed quantities (kg/m/s together with A,K,mol,cd):", {n: tilt_nonzero(addr(Q[n])) for n in nonmech})
# A2 control over 5040 assignments
cnt_all = 0; cnt_total = 0; per = []
for perm in itertools.permutations(range(1, 8)):
    ok = all(tilt_nonzero(addr(Q[n], perm)) == (0, 0) for n in MECH); cnt_total += 1; cnt_all += ok
    per.append(sum(1 for n in Q if any(Q[n]) and tilt_nonzero(addr(Q[n], perm))[0] > 0))
print("\nA2 assignments of the 7 base units to e1..e7: %d ; mechanical quantities all tilt-null in %d of them (%.1f%%)" % (cnt_total, cnt_all, 100 * cnt_all / cnt_total))
obs = sum(1 for n in Q if any(Q[n]) and tilt_nonzero(addr(Q[n]))[0] > 0)
print("   quantities with non-zero tilt: registered assignment %d ; over all assignments min %d, mean %.2f, max %d ; fraction of assignments with count <= registered: %.1f%%" % (obs, min(per), sum(per) / len(per), max(per), 100 * sum(1 for p in per if p <= obs) / len(per)))
# A3 the F = ma address as input
x = addr(Q["force N = m a"]); em = E.emerge(x)
print("\nA3 F = m a address:", [str(c) for c in x[:8]], "...")
print("   zero divisor:", E.is_zero_divisor(x), "| on ZD equator:", E.on_zd_equator(x), "| domain_of {1,2,3}:", E.domain_of(frozenset((1, 2, 3))), "| gain_class:", E.gain_class(x))
sr = E.sigma_rb(x); print("   sigma_rb: sigma_is_half", sr["sigma_is_half"], " T1_holds", sr["T1_holds"], " Sigma_tilt", sr["Sigma_tilt"], " Sigma_axis", sr["Sigma_axis"])
fo = em["firing_order"]; print("   emerge: input_norm %.6f ; firing_order %s" % (float(em["input_norm"]), {k: (v if not isinstance(v, (list, dict)) else str(v)[:90]) for k, v in fo.items()}))
print("   steps:", [(s_["bracket"], s_["tier"]) for s_ in em["steps"]])
# neighbours: how does the output change as the address changes by one step of each iterator (+-1 in an exponent)?
print("\n   one iterator step (exponent +-1) from the F = m a address, and what emerge/sigma_rb says:")
for i, nm in enumerate("kg m s A K mol cd".split()):
    for d in (1, -1):
        v = list(Q["force N = m a"]); v[i] += d; y = addr(tuple(v)); tl, ax = tilt_nonzero(y); sup = frozenset(j for j in range(1, 16) if y[j] != 0)
        print("     %-3s %+d -> %-22s tilt# %d axis# %d domain %s ZD %s" % (nm, d, tuple(v), tl, ax, E.domain_of(sup) if sup else "R", E.is_zero_divisor(y)))
# emergent objects of Part G with their addresses
print("\nPart G emergent objects and their addresses (dimension of the quantity each defines):")
G = {"inertia m (G6)": (1,0,0,0,0,0,0), "force F = k m a (G6)": (1,1,-2,0,0,0,0), "entropy S = k ln W (G5)": (1,2,-2,0,-1,0,0), "D = d/dx (ADD generator)": (0,-1,0,0,0,0,0), "theta = x D (SCALE generator)": (0,0,0,0,0,0,0),
     "wp (potential; 1/length^2)": (0,-2,0,0,0,0,0), "g2 (1/length^4)": (0,-4,0,0,0,0,0), "g3 (1/length^6)": (0,-6,0,0,0,0,0), "boost / Doppler factor": (0,0,0,0,0,0,0)}
for n, v in G.items():
    x = addr(v); tl, ax = tilt_nonzero(x); sup = frozenset(j for j in range(1, 16) if x[j] != 0); print("  %-32s %-22s tilt# %d axis# %d domain %s" % (n, str(v), tl, ax, E.domain_of(sup) if sup else "R"))
