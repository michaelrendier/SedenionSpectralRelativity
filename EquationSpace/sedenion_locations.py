"""sedenion_locations.py (2026-11-20): the sedenion LOCATION of every equation in the two catalogs, and whether it is unique.
Catalog A = the 65 Archimedes Python equations (one ASS-word each).  Catalog B = the 6,268 Universal-Fractal formulas (three words each: init, loop, bailout).
A word over A, S, G (ADD = e1, SCALE = e2, SIGN = e4) is a walk through the sedenion basis: the partial products left to right (equation_space.mul); its END POINT is +-e_k.
F (unknown function slot) and R (random) have no index and are skipped.  This reads the SOURCE shape of an equation (a constructed placement), not a derivation.
Reads ../../FourthAgePapers/EquationSpace/catalog/*.csv.   Run:  ../.venv/bin/python sedenion_locations.py   (stdlib only)
Writes results/sedenion_locations.csv and results/sedenion_locations_summary.txt"""
import sys, os, csv, collections, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import equation_space as Q
CAT = os.path.join(HERE, "..", "..", "FourthAgePapers", "EquationSpace", "catalog")
GEN = {"A": 1, "S": 2, "G": 4}
def asg(w): return "".join(c for c in w if c in GEN)
cache = {}
def walk_end(w):
    """(end_sign, end_index, head) of the ASG letters of w; head = first 12 partial products."""
    if w in cache: return cache[w]
    v = (1, 0); head = []
    for i, ch in enumerate(w):
        v = Q.mul(v, (1, GEN[ch]))
        if i < 12: head.append(("+" if v[0] > 0 else "-") + "e%d" % v[1])
    cache[w] = (v[0], v[1], " ".join(head)); return cache[w]
def fmt(e): return ("+" if e[0] > 0 else "-") + "e%d" % e[1]
rows = []
for r in csv.DictReader(open(f"{CAT}/archimedes_py.csv")):
    w = asg(r["ass_word"]); e = walk_end(w) if w else None
    rows.append(dict(catalog="A_python65", id=r["id"], full_word=r["ass_word"], init="", loop=w, bailout="", len_loop=len(w), end_loop=fmt(e) if e else "", walk_head=e[2] if e else "", end_init="", end_bailout=""))
circ = {r["id"]: r for r in csv.DictReader(open(f"{CAT}/circles_ufm.csv"))}
for r in csv.DictReader(open(f"{CAT}/archimedes_ufm.csv")):
    wi, wl, wb = asg(r["init_word"]), asg(r["loop_word"]), asg(r["bailout_word"])
    ei, el, eb = (walk_end(w) if w else None for w in (wi, wl, wb))
    c = circ.get(r["id"], {})
    rows.append(dict(catalog="B_fractal6268", id=r["id"], full_word=r["init_word"] + "|" + r["loop_word"] + "|" + r["bailout_word"], init=wi if len(wi) <= 60 else wi[:57] + "...", loop=wl if len(wl) <= 60 else wl[:57] + "...", bailout=wb if len(wb) <= 60 else wb[:57] + "...",
                     len_loop=len(wl), end_init=fmt(ei) if ei else "", end_loop=fmt(el) if el else "", end_bailout=fmt(eb) if eb else "", walk_head=el[2] if el else "", circle_number=c.get("circle_number", "")))
# uniqueness: how many other entries share this entry's complete word set
key = collections.Counter(r["full_word"] for r in rows)
for r in rows: r["shares_full_word_with"] = key[r["full_word"]] - 1
cols = ["catalog", "id", "len_loop", "end_init", "end_loop", "end_bailout", "circle_number", "shares_full_word_with", "walk_head", "init", "loop", "bailout"]
os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
with open(os.path.join(HERE, "results", "sedenion_locations.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, cols, extrasaction="ignore"); w.writeheader(); w.writerows(rows)
out = []
for cat in ("A_python65", "B_fractal6268"):
    R = [r for r in rows if r["catalog"] == cat]; n = len(R)
    out.append(f"== catalog {cat}: {n} entries")
    has = [r for r in R if r["end_loop"]]; out.append(f"   entries with a loop/ASG walk: {len(has)}; empty (no A/S/G letter, so NO sedenion location): {n - len(has)}")
    c = collections.Counter(r["end_loop"] for r in has); idx = collections.Counter(int(r["end_loop"][2:]) for r in has)
    out.append("   END POINT of the loop word, by index (0..15): " + ", ".join(f"e{k}:{idx.get(k,0)}" for k in range(16)))
    out.append(f"   distinct end points used: {len(c)} of 32 (+-e0..e15); of the 16 reachable by A,S,G (8 indices x 2 signs): {len(c)}")
    out.append(f"   in the Niemeier blind spots {{e1, e11, e15}}: e1 holds {idx.get(1,0)} entries; e11 and e15 are indices >= 8 and hold {idx.get(11,0)+idx.get(15,0)} (A, S, G cannot reach them without a fourth generator K = e8)")
    out.append(f"   odd (prime-sector) indices e1,e3,e5,e7: {sum(idx.get(k,0) for k in (1,3,5,7))} entries; even: {sum(idx.get(k,0) for k in (0,2,4,6))}")
    shared = [r for r in R if r["shares_full_word_with"] > 0]
    out.append(f"   entries whose COMPLETE word set is shared with at least one other entry: {len(shared)} ({len(shared)/n*100:.1f}%); entries with a location of their own: {n-len(shared)}")
    if cat == "B_fractal6268":
        trip = collections.Counter((r["end_init"], r["end_loop"], r["end_bailout"]) for r in R)
        out.append(f"   the three END POINTS (init, loop, bailout) together: {len(trip)} distinct triples for {n} entries (largest bucket {trip.most_common(1)[0][1]})")
        cn = collections.Counter(r["circle_number"] for r in R if r["circle_number"]); out.append("   circle number of the loop element: " + ", ".join(f"{k}:{v}" for k, v in sorted(cn.items())))
    out.append("")
txt = "\n".join(out); print(txt); open(os.path.join(HERE, "results", "sedenion_locations_summary.txt"), "w").write(txt)
