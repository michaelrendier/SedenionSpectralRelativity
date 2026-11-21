"""associator_address.py (2026-11-20, UNREGISTERED exploratory; motive: Gauss's Theorema Egregium, 9-maths video): is the END SLOT of a word's walk (extrinsic, a coordinate) improved by an INTRINSIC bracketing invariant?
A word's left-to-right product L(w) and right-to-left product R(w) differ exactly when the bracketing matters (the associator is the curvature, canonical maths 'CURVATURE = THE ASSOCIATOR').
Address 1 = L(w) alone (what the gallery uses).  Address 2 = the pair (L(w), R(w)).  Count how many distinct words each separates.   Run: ../.venv/bin/python associator_address.py"""
import csv, os, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); import equation_space as Q
GEN = {"A": 1, "S": 2, "G": 4}; CAT = os.path.join(HERE, "..", "..", "FourthAgePapers", "EquationSpace", "catalog")
def asg(w): return "".join(c for c in w if c in GEN)
def left(w):
    v = (1, 0)
    for c in w: v = Q.mul(v, (1, GEN[c]))
    return v
def right(w):
    v = (1, 0)
    for c in reversed(w): v = Q.mul((1, GEN[c]), v)
    return v
words = set()
for r in csv.DictReader(open(f"{CAT}/archimedes_py.csv")): words.add(asg(r["ass_word"]))
for r in csv.DictReader(open(f"{CAT}/archimedes_ufm.csv")):
    for k in ("init_word", "loop_word", "bailout_word"): words.add(asg(r[k]))
words.discard("")
L = {w: left(w) for w in words}; R = {w: right(w) for w in words}
n = len(words); curved = sum(1 for w in words if L[w] != R[w])
a1 = collections.Counter(L.values()); a2 = collections.Counter((L[w], R[w]) for w in words)
fmt = lambda e: ("+" if e[0] > 0 else "-") + "e%d" % e[1]
out = [f"distinct A/S/G words: {n}", f"words whose left and right bracketing disagree (curved): {curved} ({100*curved/n:.1f}%)",
       f"distinct addresses by L alone: {len(a1)} (of 16 signed slots possible 16)", f"distinct addresses by (L, R): {len(a2)} (up to 256)",
       f"largest class by L: {a1.most_common(1)[0][1]} words; by (L,R): {a2.most_common(1)[0][1]} words"]
# is L vs R disagreement just a sign flip, or a different slot?
same_slot = sum(1 for w in words if L[w] != R[w] and L[w][1] == R[w][1]); out.append(f"curved words where R differs only by sign: {same_slot} of {curved}")
by_len = collections.defaultdict(lambda: [0, 0])
for w in words: by_len[min(len(w), 12)][0] += 1; by_len[min(len(w), 12)][1] += L[w] != R[w]
out.append("curved fraction by word length: " + "  ".join(f"{k}{'+' if k == 12 else ''}:{100*v[1]/v[0]:.0f}%" for k, v in sorted(by_len.items())))
open(os.path.join(HERE, "results", "associator_address.txt"), "w").write("\n".join(out) + "\n"); print("\n".join(out))
