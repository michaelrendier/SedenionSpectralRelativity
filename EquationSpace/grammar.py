"""grammar.py: EquationSpace test 5, Part G (see 07_registered_grammar_catalog_address.md).  Every check is symbolic and exact.
   ValaQuenta/.venv/bin/python grammar.py"""
import sympy as sp
x = sp.Symbol("x", positive=True); lam, s, k, h, t = sp.symbols("lambda s k h t")
f = sp.Function("f")
D = lambda g: sp.diff(g, x)                  # generator of ADD
TH = lambda g: x * sp.diff(g, x)             # generator of SCALE: theta = x D
Pp = lambda g: g.subs(x, -x)                 # SIGN: parity
out = {}
# G1: [theta, D] = -D ; theta = i x p with p = -i D  (Berry-Keating xp)
g1 = sp.simplify(TH(D(f(x))) - D(TH(f(x))) + D(f(x)))
bk = sp.simplify(TH(f(x)) - sp.I * (x * (-sp.I * D(f(x)))))
out["G1"] = (g1 == 0 and bk == 0, "[theta,D] f + D f = %s ; theta f - i(x p)f = %s" % (g1, bk))
# G2: P D P = -D ; [P, theta] = 0
g2a = sp.simplify(Pp(D(Pp(f(x)))) + D(f(x)))
g2b = sp.simplify(Pp(TH(f(x))) - TH(Pp(f(x))))
out["G2"] = (g2a == 0 and g2b == 0, "P D P f + D f = %s ; [P,theta] f = %s" % (g2a, g2b))
# G3: eigen-equations
lm = sp.Symbol("lam", real=True); sx = sp.Symbol("s", real=True)   # run 1 left s complex and sympy split the solution into re/im parts: a harness issue, kept as run 1
e1 = sp.dsolve(sp.Eq(D(f(x)), lm * f(x)), f(x)); e2 = sp.dsolve(sp.Eq(TH(f(x)), sx * f(x)), f(x))
ok3 = (sp.simplify(e1.rhs - sp.Symbol("C1") * sp.exp(lm * x)) == 0) and (sp.simplify(e2.rhs - sp.Symbol("C1") * x ** sx) == 0)
out["G3"] = (ok3, "D f = lam f -> %s ; theta f = s f -> %s ; P f = +-f -> even / odd" % (e1, e2))
# G4: flows
test = sp.sin(x) + x ** 3; N = 12
tay = sum(h ** n * sp.diff(test, x, n) / sp.factorial(n) for n in range(N + 1))
r4a = sp.simplify(sp.series(test.subs(x, x + h), h, 0, N + 1).removeO() - tay)
th_n = lambda n: (lambda g: g)(test) if n == 0 else None
cur = test; dil = test
for n in range(1, 9): cur = TH(cur); dil += t ** n * cur / sp.factorial(n)
r4b = sp.simplify(sp.series(test.subs(x, sp.exp(t) * x), t, 0, 9).removeO() - dil)
out["G4"] = (r4a == 0 and r4b == 0, "exp(hD) f = f(x+h) residual %s ; exp(t theta) f = f(e^t x) residual %s (orders %d, 8)" % (r4a, r4b, N))
# G5: entropy from additivity
y = sp.Symbol("y", positive=True); xp_ = sp.Symbol("xp", positive=True); F = sp.Function("F")
cond = sp.diff(F(xp_ * y), y).subs(y, 1)          # d/dy F(xy) at y = 1  = x F'(x)
ode = sp.Eq(xp_ * sp.diff(F(xp_), xp_), k)       # x F' = F'(1) = k
sol = sp.dsolve(ode, F(xp_)); fn = sol.rhs.subs(sp.Symbol("C1"), 0)
resid = sp.simplify(sp.expand_log(fn.subs(xp_, xp_ * y) - fn.subs(xp_, xp_) - fn.subs(xp_, y), force=True))
out["G5"] = (resid == 0 and sp.simplify(fn - k * sp.log(xp_)) == 0, "d/dy F(xy)|_{y=1} = x F'(x) = F'(1) ; solution %s ; additivity residual %s (S = k ln W is the form forced by multiplicative counts)" % (fn, resid))
# G6: inertia, Buckingham over (kg, m, s)
M = sp.Matrix([[1, 1, 0, 0], [1, 0, 1, 0], [-2, 0, 0, 1]]).T.T   # columns F, m, x, t ; rows kg, m, s
Fv, mv, xv, tv = (1, 1, -2), (1, 0, 0), (0, 1, 0), (0, 0, 1)
DM = sp.Matrix([[Fv[i], mv[i], xv[i], tv[i]] for i in range(3)])
ns = DM.nullspace(); basis = [list(v / v[[i for i in range(4) if v[i] != 0][0]]) for v in ns]
out["G6"] = (DM.rank() == 3 and len(ns) == 1 and list(ns[0].T / (ns[0][0])) == [1, -1, -1, 2], "rank %d, nullity %d, basis %s -> F t^2/(m x) = k ; with a = D^2 x: F = k m a" % (DM.rank(), len(ns), list(ns[0].T / ns[0][0])))
# G7: wp closed under SCALE (weights 4, 6) and SIGN; Laurent coefficients from the first integral
g2s, g3s = sp.symbols("g2 g3"); P0, P1, P2 = sp.symbols("P0 P1 P2")
Q0, Q1, Q2 = lam ** 2 * P0, lam ** 3 * P1, lam ** 4 * P2               # Q = lam^2 P(lam x) and its derivatives
ode_res = lambda a, b, c, g2: c - 6 * a ** 2 + g2 / 2
fi_res = lambda a, b, g2, g3: b ** 2 - 4 * a ** 3 + g2 * a + g3
r_ode = sp.simplify(ode_res(Q0, Q1, Q2, lam ** 4 * g2s) - lam ** 4 * ode_res(P0, P1, P2, g2s))
r_fi = sp.simplify(fi_res(Q0, Q1, lam ** 4 * g2s, lam ** 6 * g3s) - lam ** 6 * fi_res(P0, P1, g2s, g3s))
a2, a4, a6 = sp.symbols("a2 a4 a6"); Pser = 1 / x ** 2 + a2 * x ** 2 + a4 * x ** 4 + a6 * x ** 6
fi = sp.series(sp.diff(Pser, x) ** 2 - 4 * Pser ** 3 + g2s * Pser + g3s, x, 0, 5).removeO()
cs = sp.solve([sp.expand(fi).coeff(x, n) for n in (-2, 0, 2)], [a2, a4, a6], dict=True)
lau = cs[0] if cs else {}
ok7 = r_ode == 0 and r_fi == 0 and sp.simplify(lau.get(a2, 0) - g2s / 20) == 0 and sp.simplify(lau.get(a4, 0) - g3s / 28) == 0 and sp.simplify(lau.get(a6, 0) - g2s ** 2 / 1200) == 0
out["G7"] = (ok7, "SCALE weights (4,6): ode residual %s, first-integral residual %s ; SIGN: even ; Laurent %s" % (r_ode, r_fi, {str(a): sp.simplify(v) for a, v in lau.items()}))
for n, (ok, msg) in out.items(): print(n, "PASS" if ok else "FAIL", "|", msg)
print("all pass:", all(ok for ok, _ in out.values()))
