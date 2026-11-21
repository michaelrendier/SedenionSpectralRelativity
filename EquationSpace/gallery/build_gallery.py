#!/usr/bin/env python3
"""build_gallery.py (2026-11-20): builds equation_space_gallery.html (self-contained) from
   - the two catalogs (65 Archimedes Python equations, 6,268 fractal formulas) and their sedenion locations (../results/sedenion_locations.csv, ../sedenion_locations.py),
   - the 65-equation circle table (FourthAgePapers/EquationSpace/catalog/py65_circles.csv) and the recorded source defects,
   - stable_equations.py (quantities, units, equations; the dimensional 'terms cancel' test),
   - the Niemeier / Monster coverage of the 16 sedenion slots (FourthAgePapers/MonsterSiblings/engine/nightmare_engine.py, run live),
   - the routes from H_hat_RB (EquationSpace tests 5-9: G1-G7 emergent derivations).
Run:  ../../.venv/bin/python build_gallery.py        (stdlib only)    Then serve with ./serve_gallery.sh (Firefox shows the favicon only over http)."""
import sys, os, csv, json, collections, datetime
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, ".."))
import equation_space as Q, stable_equations as SE
ROOT = os.path.expanduser("~/Projects/ThePlace"); FP = f"{ROOT}/FourthAgePapers"
sys.path.insert(0, f"{FP}/MonsterSiblings/engine"); import nightmare_engine as NE
GEN = {"A", "S", "G"}
def asg(w): return "".join(c for c in w if c in GEN)
loc = {(r["catalog"], r["id"]): r for r in csv.DictReader(open(f"{HERE}/../results/sedenion_locations.csv"))}
py65 = {r["id"]: r for r in csv.DictReader(open(f"{FP}/EquationSpace/catalog/py65_circles.csv"))}
circ = {r["id"]: r for r in csv.DictReader(open(f"{FP}/EquationSpace/catalog/circles_ufm.csv"))}
DEFECT = {"charleslaw": "returns T = 8.0 for V = 2, k = 4 (V/T = k gives 0.5)", "idealgaslaw": "raises TypeError for every float input (float x Decimal)", "degRad": "conversions swapped, returns None", "radDeg": "conversions swapped, returns None",
          "lucas_series": "returns the Fibonacci numbers (starts 1, 1)", "fibonacci_number": "returns 0 for n = 1 and 2", "explicit_formula_fibonacci_number": "agrees with the recurrence only up to n = 71",
          "non_sympy_derivative": "prints and returns nothing; polynomials only", "boyleslaw": "prints its locals on every call"}
TIER = {"lucas_number": "EXACT", "lucas_series": "EXACT", "explicit_formula_fibonacci_number": "EXACT", "zscore": "EXACT", "Shuffle": "EXACT", "ero_interchange": "LIMIT", "dfs": "LIMIT", "step": "LIMIT"}
rows, groups = [], collections.defaultdict(list)
for r in csv.DictReader(open(f"{FP}/EquationSpace/catalog/archimedes_py.csv")):
    i = len(rows); k = ("A_python65", r["id"]); L = loc[k]; fn = r["id"].split("::")[-1]; p = py65.get(r["id"], {})
    rows.append(dict(cat="A", id=r["id"].replace("Maths/", "").replace(".py", ""), w=r["ass_word"][:300], lw=asg(r["ass_word"])[:300], wl=len(asg(r["ass_word"])), iw="", bw="", ei="", el=L["end_loop"], eb="", cn="", sh=int(L["shares_full_word_with"]),
                     cls=p.get("class", ""), kind=p.get("kind", ""), rel=p.get("relation", ""), sane=("no: " + DEFECT[fn]) if fn in DEFECT else "no defect recorded", tier=TIER.get(fn, "placed (constructed)"), ev=(p.get("evidence", "")[:260])))
    groups[("A", r["ass_word"])].append(i)
for r in csv.DictReader(open(f"{FP}/EquationSpace/catalog/archimedes_ufm.csv")):
    i = len(rows); L = loc[("B_fractal6268", r["id"])]
    rows.append(dict(cat="B", id=r["id"].replace(".ufm", ""), w=r["loop_word"][:300], lw=asg(r["loop_word"])[:300], wl=len(asg(r["loop_word"])), iw=r["init_word"][:80], bw=r["bailout_word"][:80], ei=L["end_init"], el=L["end_loop"], eb=L["end_bailout"],
                     cn=L.get("circle_number", ""), sh=int(L["shares_full_word_with"]), cls="", kind="", rel="", sane="not assessed", tier="placed (constructed)", ev=""))
    groups[("B", r["init_word"] + "|" + r["loop_word"] + "|" + r["bailout_word"])].append(i)
gl = [m for m in groups.values() if len(m) > 1]; gid = {}
for n, m in enumerate(gl):
    for i in m: gid[i] = n
for i, r in enumerate(rows): r["g"] = gid.get(i, -1)
fields = ["cat", "id", "w", "lw", "wl", "iw", "bw", "ei", "el", "eb", "cn", "sh", "g", "cls", "kind", "rel", "sane", "tier", "ev"]
catalog = [[r[f] for f in fields] for r in rows]
qs, eqs = SE.build()
ni = NE.niemeier_root_systems(); fp = NE.niemeier_prime_footprint(); mg = NE.monster_gap_fill(); cov = NE.full_coverage_check()
threshold = dict(niemeier=[dict(label=s["label"], h=s["h"], slot=s["h_mod16"]) for s in ni], niemeier_slots=fp["activated_by_niemeier"], gap=fp["prime_sector_gap"], monster_slots=cov["monster_activated"], gap_fill=mg["gap_fill_primes"],
                 monster_primes=NE.MOONSHINE_PRIMES, monster_exclusive=mg["monster_exclusive_primes"], accessible=mg["niemeier_accessible_primes"], combined=cov["combined"])
sign = [[Q.TABLE[(i, j)][0] for j in range(16)] for i in range(16)]
G = [("G1", "θ = xD satisfies [θ, D] = −D and θ = i x p", "The SCALE generator is exactly Berry–Keating's xp, the Red term R̂ of Ĥ_RB; the floor's bracket is the Lie algebra of {D, θ}.", "ASS (coders)"),
     ("G2", "P D P = −D and [P, θ] = 0", "SIGN reverses ADD and commutes with SCALE.", "ASS (coders)"),
     ("G3", "eigen-equations of the generators: D f = λ f gives C e^{λx}; θ f = s f gives C x^s", "Exponentials come from ADD, powers from SCALE.", "ASS, F = ma"),
     ("G4", "flows: exp(hD) f = f(x + h) and exp(tθ) f = f(eᵗ x), residual 0", "ADD translates, SCALE dilates.", "units"),
     ("G5", "entropy: f(xy) = f(x) + f(y), differentiable, forces x f′ = const, so f = k ln x", "S = k ln W is the form forced by multiplicative counts: SCALE ≅ ADD in the log chart.", "entropy tree, units"),
     ("G6", "inertia: over (kg, m, s) the variables F, m, x, t have rank 3, nullity 1, group F t²/(m x)", "F = k m x/t², with a = D²x: F = k m a. The form of Newton's second law is forced by SCALE-covariance up to the dimensionless k.", "the F = ma tree"),
     ("G7", "℘ is closed under ADD, SCALE and SIGN: its ODE and first integral map to themselves (weights 4, 6), it is even, and periodic under an ADD lattice", "The Blue term's function is the function fixed by all three generators.", "physics")]
data = dict(built=datetime.date.today().isoformat(), fields=fields, catalog=catalog, groups=gl, sign=sign, quantities=qs, equations=eqs, threshold=threshold, routes=[dict(id=a, statement=b, meaning=c, serves=d) for a, b, c, d in G],
            counts=dict(A=sum(1 for r in rows if r["cat"] == "A"), B=sum(1 for r in rows if r["cat"] == "B")))
tpl = open(f"{HERE}/template.html", encoding="utf-8").read(); uri = open(f"{HERE}/favicon_datauri.txt").read().strip()
html = tpl.replace("/*DATA*/", json.dumps(data, ensure_ascii=False, separators=(",", ":"))).replace("%%FAVICON%%", uri)
open(f"{HERE}/equation_space_gallery.html", "w", encoding="utf-8").write(html)
print("catalog", len(catalog), "| shared-word groups", len(gl), "| quantities", len(qs), "| equations", len(eqs), "| html", len(html) // 1024, "KB")
