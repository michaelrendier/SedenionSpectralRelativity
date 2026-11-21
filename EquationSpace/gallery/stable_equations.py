"""stable_equations.py (2026-11-20): the quantities, units and equations behind the Equation Space Gallery's F = ma tree and Units pages.
Quantity = a point in the 7-axis SI lattice (kg, m, s, A, K, mol, cd).  Equation = lhs = rhs over those quantities.
STABLE (the author's term, 2026-11-20: "whether or not terms cancel out", also "sane") is TESTED here as dimensional homogeneity: lhs and rhs have the same exponent vector and every
sum adds like with like.  Unstable permutations are kept on purpose: not every permutation of equation space is a static relationship.
ASS word of an equation (PROVISIONAL, THEORETICAL): post-order over the right-hand side, product = S, quotient = S G, derivative d/dt = A (the ADD generator D), sum = A, power n = S x (|n|-1) and G if n < 0, log = S.
The word is read through the Cayley-Dickson walk (equation_space.mul: ADD = e1, SCALE = e2, SIGN = e4) to a sedenion location +-e_k.  stdlib only."""
import sys, os
from fractions import Fraction as Fr
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, ".."))
import equation_space as Q
AX = ("kg", "m", "s", "A", "K", "mol", "cd")
def V(*v): return tuple(Fr(x) for x in (list(v) + [0] * 7)[:7])
# name: (symbol, unit, dims, domain, definition-expression or None)
QUANT = {
 "mass": ("m", "kg", V(1), "base", None), "length": ("x", "m", V(0, 1), "base", None), "time": ("t", "s", V(0, 0, 1), "base", None), "current": ("I", "A", V(0, 0, 0, 1), "base", None),
 "temperature": ("T", "K", V(0, 0, 0, 0, 1), "base", None), "amount": ("n", "mol", V(0, 0, 0, 0, 0, 1), "base", None), "luminous intensity": ("Iv", "cd", V(0, 0, 0, 0, 0, 0, 1), "base", None),
 "area": ("A", "m²", V(0, 2), "mechanics", ("pow", "length", 2)), "volume": ("Vol", "m³", V(0, 3), "mechanics", ("pow", "length", 3)), "frequency": ("f", "Hz", V(0, 0, -1), "mechanics", ("div", 1, "time")),
 "velocity": ("v", "m/s", V(0, 1, -1), "mechanics", ("ddt", "length")), "acceleration": ("a", "m/s²", V(0, 1, -2), "mechanics", ("ddt", "velocity")), "jerk": ("j", "m/s³", V(0, 1, -3), "mechanics", ("ddt", "acceleration")),
 "momentum": ("p", "kg m/s", V(1, 1, -1), "mechanics", ("mul", "mass", "velocity")), "force": ("F", "N", V(1, 1, -2), "mechanics", ("mul", "mass", "acceleration")),
 "energy": ("E", "J", V(1, 2, -2), "mechanics", ("mul", "force", "length")), "power": ("P", "W", V(1, 2, -3), "mechanics", ("div", "energy", "time")), "pressure": ("p_", "Pa", V(1, -1, -2), "mechanics", ("div", "force", "area")),
 "density": ("ρ", "kg/m³", V(1, -3), "mechanics", ("div", "mass", "volume")), "action": ("S_a", "J s", V(1, 2, -1), "mechanics", ("mul", "energy", "time")), "angular momentum": ("L", "kg m²/s", V(1, 2, -1), "mechanics", ("mul", "length", "momentum")),
 "impulse": ("J_", "N s", V(1, 1, -1), "mechanics", ("mul", "force", "time")), "spring constant": ("k", "N/m", V(1, 0, -2), "mechanics", ("div", "force", "length")), "gravitational constant": ("G", "m³/(kg s²)", V(-1, 3, -2), "constant", None),
 "charge": ("q", "C", V(0, 0, 1, 1), "electromagnetism", ("mul", "current", "time")), "voltage": ("V", "V", V(1, 2, -3, -1), "electromagnetism", ("div", "energy", "charge")), "resistance": ("R", "Ω", V(1, 2, -3, -2), "electromagnetism", ("div", "voltage", "current")),
 "capacitance": ("C", "F", V(-1, -2, 4, 2), "electromagnetism", ("div", "charge", "voltage")), "electric field": ("E_", "V/m", V(1, 1, -3, -1), "electromagnetism", ("div", "force", "charge")),
 "magnetic flux density": ("B", "T", V(1, 0, -2, -1), "electromagnetism", ("div", "force", ("mul", "charge", "velocity"))), "magnetic flux": ("Φ", "Wb", V(1, 2, -2, -1), "electromagnetism", ("mul", "voltage", "time")),
 "inductance": ("L_", "H", V(1, 2, -2, -2), "electromagnetism", ("div", "magnetic flux", "current")), "permittivity": ("ε0", "F/m", V(-1, -3, 4, 2), "constant", None), "permeability": ("μ0", "H/m", V(1, 1, -2, -2), "constant", None),
 "heat": ("Q", "J", V(1, 2, -2), "thermodynamics", None), "entropy": ("S", "J/K", V(1, 2, -2, 0, -1), "thermodynamics", ("div", "heat", "temperature")), "Boltzmann constant": ("k_B", "J/K", V(1, 2, -2, 0, -1), "constant", None),
 "molar gas constant": ("R_g", "J/(mol K)", V(1, 2, -2, 0, -1, -1), "constant", None), "specific heat": ("c", "J/(kg K)", V(0, 2, -2, 0, -1), "thermodynamics", None), "number of microstates": ("W", "1", V(), "thermodynamics", None),
}
def dims(e, env=QUANT):
    """-> (dims tuple, ok) ; ok False if a sum adds unlike quantities."""
    if isinstance(e, (int, float)) or e is None: return V(), True
    if isinstance(e, str): return env[e][2], True
    op = e[0]
    if op == "mul": a, ok1 = dims(e[1]); b, ok2 = dims(e[2]); return tuple(x + y for x, y in zip(a, b)), ok1 and ok2
    if op == "div":
        a, ok1 = dims(e[1]); b, ok2 = dims(e[2]); return tuple(x - y for x, y in zip(a, b)), ok1 and ok2
    if op == "ddt": a, ok = dims(e[1]); return tuple(x - y for x, y in zip(a, V(0, 0, 1))), ok
    if op == "pow": a, ok = dims(e[1]); return tuple(x * e[2] for x in a), ok
    if op == "add": a, ok1 = dims(e[1]); b, ok2 = dims(e[2]); return a, ok1 and ok2 and a == b
    if op == "log": a, ok = dims(e[1]); return V(), ok and a == V()
    raise ValueError(op)
def word(e):
    if isinstance(e, (int, float, str)) or e is None: return ""
    op = e[0]
    if op == "mul": return word(e[1]) + word(e[2]) + "S"
    if op == "div": return word(e[1]) + word(e[2]) + "SG"
    if op == "ddt": return word(e[1]) + "A"
    if op == "add": return word(e[1]) + word(e[2]) + "A"
    if op == "pow": n = int(e[2]); return word(e[1]) + "S" * (abs(n) - 1) + ("G" if n < 0 else "")
    if op == "log": return word(e[1]) + "S"
    raise ValueError(op)
def names(e, out=None):
    out = [] if out is None else out
    if isinstance(e, str): out.append(e)
    elif isinstance(e, tuple):
        for x in e[1:]:
            if isinstance(x, (str, tuple)): names(x, out)
    return out
GEN = {"A": 1, "S": 2, "G": 4}
def walk_end(w):
    v = (1, 0); head = []
    for ch in w:
        v = Q.mul(v, (1, GEN[ch])); head.append(("+" if v[0] > 0 else "-") + "e%d" % v[1])
    return v, head
# id, display, lhs quantity (name), rhs expression, domain, note.  The first two are the author's two roots.
EQ = [
 ("F=ma", "F = m a", "force", ("mul", "mass", "acceleration"), "mechanics", "ROOT of the F = ma tree (emergent form: G6, SCALE-covariance over kg, m, s)"),
 ("S=Q/T", "S = Q / T", "entropy", ("div", "heat", "temperature"), "thermodynamics", "ROOT of the entropy tree (the author wrote S = Q/t; read here as the Clausius entropy; its forced form S = k ln W is G5)"),
 ("S=klnW", "S = k_B ln W", "entropy", ("mul", "Boltzmann constant", ("log", "number of microstates")), "thermodynamics", "G5: f(xy) = f(x) + f(y) forces f = k ln x"),
 ("v=dx/dt", "v = dx/dt", "velocity", ("ddt", "length"), "mechanics", ""), ("a=dv/dt", "a = dv/dt", "acceleration", ("ddt", "velocity"), "mechanics", ""), ("j=da/dt", "j = da/dt", "jerk", ("ddt", "acceleration"), "mechanics", ""),
 ("p=mv", "p = m v", "momentum", ("mul", "mass", "velocity"), "mechanics", ""), ("F=dp/dt", "F = dp/dt", "force", ("ddt", "momentum"), "mechanics", "second route to force: lands on the same point as F = m a"),
 ("E=Fx", "E = F x", "energy", ("mul", "force", "length"), "mechanics", "work"), ("P=E/t", "P = E / t", "power", ("div", "energy", "time"), "mechanics", ""), ("P=Fv", "P = F v", "power", ("mul", "force", "velocity"), "mechanics", ""),
 ("p=F/A", "p = F / A", "pressure", ("div", "force", "area"), "mechanics", ""), ("rho=m/V", "ρ = m / Vol", "density", ("div", "mass", "volume"), "mechanics", ""), ("S=Et", "S_a = E t", "action", ("mul", "energy", "time"), "mechanics", "same dimensions as angular momentum"),
 ("L=xp", "L = x p", "angular momentum", ("mul", "length", "momentum"), "mechanics", "same dimensions as action"), ("J=Ft", "J = F t", "impulse", ("mul", "force", "time"), "mechanics", ""), ("J=dp", "J = Δp", "impulse", "momentum", "mechanics", "impulse-momentum theorem"),
 ("KE", "E = ½ m v²", "energy", ("mul", ("mul", "mass", "velocity"), "velocity"), "mechanics", "the ½ is dimensionless"), ("Hooke", "F = k x", "force", ("mul", "spring constant", "length"), "mechanics", ""),
 ("Newton-G", "F = G m m / x²", "force", ("div", ("mul", "gravitational constant", ("mul", "mass", "mass")), ("pow", "length", 2)), "mechanics", "Newton's gravitation"),
 ("w=2pif", "ω = 2π f", "frequency", "frequency", "mechanics", "angular frequency has the dimensions of frequency (radian is dimensionless)"),
 ("q=It", "q = I t", "charge", ("mul", "current", "time"), "electromagnetism", ""), ("V=E/q", "V = E / q", "voltage", ("div", "energy", "charge"), "electromagnetism", "energy per charge"), ("Ohm", "V = I R", "voltage", ("mul", "current", "resistance"), "electromagnetism", ""),
 ("P=IV", "P = I V", "power", ("mul", "current", "voltage"), "electromagnetism", ""), ("C=q/V", "C = q / V", "capacitance", ("div", "charge", "voltage"), "electromagnetism", ""),
 ("F=qE", "F = q E_", "force", ("mul", "charge", "electric field"), "electromagnetism", "the force on a charge in a field, in newtons"),
 ("wire", "F = q V / x", "force", ("div", ("mul", "charge", "voltage"), "length"), "electromagnetism", "THE NEWTON THREAD: the force on one electron in a wire of length x at voltage V, in newtons (the 1967 electronics text)"),
 ("Lorentz-B", "F = q v B", "force", ("mul", ("mul", "charge", "velocity"), "magnetic flux density"), "electromagnetism", ""), ("Coulomb", "F = q q / (ε0 x²)", "force", ("div", ("mul", "charge", "charge"), ("mul", "permittivity", ("pow", "length", 2))), "electromagnetism", "up to the dimensionless 1/4π"),
 ("flux", "Φ = V t", "magnetic flux", ("mul", "voltage", "time"), "electromagnetism", ""), ("ind", "L_ = Φ / I", "inductance", ("div", "magnetic flux", "current"), "electromagnetism", ""),
 ("E=kT", "E = k_B T", "energy", ("mul", "Boltzmann constant", "temperature"), "thermodynamics", "energy per mode"), ("Q=mcT", "Q = m c T", "heat", ("mul", ("mul", "mass", "specific heat"), "temperature"), "thermodynamics", ""),
 ("gas", "p Vol = n R_g T", ("mul", "pressure", "volume"), ("mul", ("mul", "amount", "molar gas constant"), "temperature"), "thermodynamics", "ideal gas law (a relation: any one variable can be solved for)"),
 # deliberate unstable permutations: terms that do not cancel
 ("x:F=mv", "F = m v", "force", ("mul", "mass", "velocity"), "unstable", "UNSTABLE: mass × velocity is momentum"), ("x:E=Ft", "E = F t", "energy", ("mul", "force", "time"), "unstable", "UNSTABLE: force × time is impulse"),
 ("x:V=I/R", "V = I / R", "voltage", ("div", "current", "resistance"), "unstable", "UNSTABLE: current / resistance is a conductance times current ... not a voltage"), ("x:P=Et", "P = E t", "power", ("mul", "energy", "time"), "unstable", "UNSTABLE: energy × time is action"),
 ("x:F=ma+v", "F = m a + v", "force", ("add", ("mul", "mass", "acceleration"), "velocity"), "unstable", "UNSTABLE: adds a force to a velocity (terms that cannot cancel)"), ("x:S=Qt", "S = Q t", "entropy", ("mul", "heat", "time"), "unstable", "UNSTABLE: heat × time is not entropy; entropy needs Q / T"),
 ("x:a=Fm", "a = F m", "acceleration", ("mul", "force", "mass"), "unstable", "UNSTABLE: force × mass has no standard name"),
]
def build():
    qs = []
    for n, (sym, unit, d, dom, defn) in QUANT.items():
        if defn is not None:
            dd, ok = dims(defn); assert ok and dd == d, ("definition does not match", n, dd, d)
        qs.append(dict(name=n, symbol=sym, unit=unit, dims=[str(x) for x in d], domain=dom, defined_by=names(defn) if defn else [], definition=repr(defn) if defn else ""))
    eqs = []
    for id_, disp, lhs, rhs, dom, note in EQ:
        l, okl = dims(lhs) if isinstance(lhs, tuple) else (QUANT[lhs][2], True); r, okr = dims(rhs)
        stable = bool(okl and okr and l == r)
        w = word(rhs); (v, head) = walk_end(w) if w else ((1, 0), [])
        used = sorted(set(names(rhs)) | (set(names(lhs)) if isinstance(lhs, tuple) else {lhs}))
        eqs.append(dict(id=id_, display=disp, lhs=lhs if isinstance(lhs, str) else disp.split("=")[0].strip(), rhs_names=sorted(set(names(rhs))), uses=used, domain=dom, note=note, stable=stable,
                        lhs_dims=[str(x) for x in l], rhs_dims=[str(x) for x in r], reason=("terms cancel: both sides are " + dims_str(l)) if stable else ("terms do not cancel: left " + dims_str(l) + " , right " + dims_str(r) + ("" if okr else " (and a sum adds unlike quantities)")),
                        word=w, end=("+" if v[0] > 0 else "-") + "e%d" % v[1], walk=" ".join(head[:24])))
    return qs, eqs
def dims_str(d): return " ".join(f"{a}^{x}" for a, x in zip(AX, d) if x != 0) or "dimensionless"
if __name__ == "__main__":
    qs, eqs = build(); print(len(qs), "quantities;", len(eqs), "equations;", sum(e["stable"] for e in eqs), "stable;", sum(not e["stable"] for e in eqs), "unstable")
    for e in eqs: print(f"{'OK ' if e['stable'] else 'BAD'} {e['id']:10s} {e['display']:22s} word {e['word']:10s} end {e['end']:4s} {'' if e['stable'] else e['reason'][:80]}")
