"""conjugates.py (registered in 09, X1-X7).  ValaQuenta/.venv/bin/python conjugates.py"""
import sys, os, csv, re, numpy as np
here = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(11)
x = np.linspace(-40, 40, 40001); dx = x[1] - x[0]
def D(f): return np.gradient(f, dx)
def ip(f, g): return np.sum(np.conj(f) * g) * dx
def ev(op, f): return ip(f, op(f)).real
def spread(op, f):
    m = ev(op, f); g = op(f) - m * f; return np.sqrt(abs(ip(g, g).real))
def norm(f): return f / np.sqrt(ip(f, f).real)
p  = lambda f: -1j * D(f)
X  = lambda f: x * f
th = lambda f: -0.5j * (x * D(f) + D(x * f))            # symmetrised dilation generator (x p + p x)/2
Pf = lambda f: f[::-1]
# X1
g = norm(np.exp(-x**2 / 2 + 0j)); print("X1 (x,p) gaussian: dx*dp = %.6f" % (spread(X, g) * spread(p, g)))
# X2: u = ln x on x>0 ; lognormal packet psi(x) = x^{-1/2} exp(-(ln x)^2/4) exp(i k ln x); theta = -i(x d/dx + 1/2) ; u-conjugate
xp = np.exp(np.linspace(-12, 12, 60001)); u = np.log(xp); du = u[1] - u[0]
for k in (0.0, 3.0):
    psi = np.exp(-u**2 / 4) * np.exp(1j * k * u)           # in the u chart (unitary map psi(x)=x^{-1/2} f(ln x))
    psi = psi / np.sqrt(np.sum(abs(psi)**2) * du)
    thp = -1j * np.gradient(psi, du)                       # theta in the u chart = -i d/du
    mu = np.sum(u * abs(psi)**2) * du; su = np.sqrt(np.sum((u - mu)**2 * abs(psi)**2) * du)
    mt = (np.sum(np.conj(psi) * thp) * du).real; st = np.sqrt(abs(np.sum(abs(thp - mt * psi)**2) * du))
    print("X2 (u=ln x, theta) lognormal k=%g: du*dtheta = %.6f" % (k, su * st))
# X3: Robertson for (theta, p) over random states; the bound is (1/2)|<[theta,p]>| and [theta,p] = i p
worst = 1e9; best = 0; viol = 0; ratios = []
for _ in range(200):
    a, b, c, d = rng.normal(size=4); s0 = rng.uniform(0.6, 2.5); m = rng.uniform(-2, 2)
    f = norm(np.exp(-(x - m)**2 / (2 * s0**2) * (1 + 0.5j * a) + 1j * (b * x + c * x**2 / 8) + 0j) * (1 + 0.3 * d * x))
    lhs = spread(th, f) * spread(p, f); rhs = 0.5 * abs(ev(p, f))
    ratios.append(lhs / rhs if rhs > 1e-9 else np.inf)
    if lhs < rhs * (1 - 1e-3): viol += 1
r = np.array([q for q in ratios if np.isfinite(q)]); print("X3 (theta,p): states %d, violations of dtheta*dp >= |<p>|/2: %d, min ratio lhs/bound = %.4f, 5th pct %.3f" % (len(ratios), viol, r.min(), np.percentile(r, 5)))
# squeezed saturation: complex gaussian exp(-(1/2)(a - i b) x^2 + i k x), exact: look at best ratio via scan of (s0, chirp)
best = 1e9
for s0 in np.linspace(0.5, 3, 11):
    for ch in np.linspace(-3, 3, 13):
        for k in (1.0, 2.0, 4.0):
            f = norm(np.exp(-x**2 / (2 * s0**2) + 1j * ch * x**2 / 2 + 1j * k * x)); rr = spread(th, f) * spread(p, f) / (0.5 * abs(ev(p, f)))
            best = min(best, rr)
print("X3 best ratio over gaussian chirped family: %.4f" % best)
# X4: (P,p) anticommute
f = norm(np.exp(-x**2 / 2) * (1 + 0.5 * x) + 0j); ac = ip(f, Pf(p(f)) + p(Pf(f))); print("X4 <{P,p}> = %.2e (anticommute), <p> for even state = %.2e" % (abs(ac), abs(ev(p, norm(np.exp(-x**2 / 2) + 0j)))))
# X5: (theta,P) commute: apply both orders to an odd-or-even test function with power-like profile
f = norm(np.exp(-x**2 / 2) * x**3 + 0j); c1 = th(Pf(f)); c2 = Pf(th(f)); print("X5 || theta P f - P theta f || = %.2e" % np.sqrt(abs(ip(c1 - c2, c1 - c2))))
# X6: catalog words: affine composition  A: x->x+1, S: x->2x, G: x->-x ; reversed word differs?
def val(w):
    a, b = 1.0, 0.0
    for ch in w:
        if ch == "A": b += 1
        elif ch == "S": a *= 2; b *= 2
        elif ch == "G": a, b = -a, -b
    return (a, b)
rows = []
for fn, col in (("catalog/archimedes_ufm.csv", "loop_word"), ("catalog/archimedes_py.csv", "ass_word")):
    for r_ in csv.DictReader(open(os.path.join(here, fn))): rows.append(r_[col])
words = sorted({"".join(c for c in w if c in "ASG") for w in rows}); words = [w for w in words if "A" in w and "S" in w and len(w) <= 60]
sens = sum(val(w) != val(w[::-1]) for w in words); print("X6 words with A and S (len<=60): %d ; order-sensitive under reversal: %d (%.1f%%)" % (len(words), sens, 100 * sens / len(words)))
# commuting pairs among distinct letters: A,G anticommute; S,G commute; A,S -> [S,A]=A
for a_, b_ in (("A", "S"), ("A", "G"), ("S", "G")):
    print("   %s%s vs %s%s : %s" % (a_, b_, b_, a_, "equal" if val(a_ + b_) == val(b_ + a_) else ("opposite-sign translation" if val(a_ + b_) == tuple(-t for t in val(b_ + a_)) else "different")))
# X7 names
pat = re.compile(r"fourier|fft|laplace|mellin|wavelet|uncertain|heisenberg|conjug|dual|transform", re.I); hits = []
for fn in ("catalog/archimedes_py.csv", "catalog/archimedes_ufm.csv"):
    for r_ in csv.DictReader(open(os.path.join(here, fn))):
        if pat.search(r_["id"]): hits.append(r_["id"])
print("X7 catalog ids naming a transform/conjugate pair: %d" % len(hits)); print("   ", hits[:25])
