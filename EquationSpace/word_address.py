"""word_address.py: EXPLORATORY (post-hoc: chosen after seeing that the unit address of address.py collapses; not in 07_registered).
A word over the tier-0 generators (ADD, SCALE, SIGN) is read as a product of basis units, ADD = e1, SCALE = e2, SIGN = e4 (three independent index bits),
multiplied left to right in the Cayley-Dickson algebra: the value is +-e_k with k = XOR of the indices (set by the PARITY of the generator counts) and the sign set by the ORDER
(equation_space.TABLE).  The address of an equation = (sign, k): 16 indices x 2 signs.  Control: shuffle each word's letters (same counts, different order).
   ValaQuenta/.venv/bin/python word_address.py"""
import sys, os, csv, random, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import equation_space as Q
GEN = {"A": 1, "S": 2, "G": 4}
def address(word):
    v = (1, 0)
    for ch in word:
        if ch in GEN: v = Q.mul(v, (1, GEN[ch]))
    return v
rows = []
for fn, col in (("catalog/archimedes_ufm.csv", "loop_word"), ("catalog/archimedes_py.csv", "ass_word")):
    d = os.path.join(os.path.dirname(os.path.abspath(__file__)), fn)
    for r in csv.DictReader(open(d)): rows.append(r[col])
words = sorted({"".join(c for c in w if c in GEN) for w in rows if any(c in GEN for c in w)})
words = [w for w in words if 1 <= len(w) <= 400]            # the longest formulas make left-to-right products slow and add nothing
print("distinct ASS-words (length 1..400): %d" % len(words))
obs = collections.Counter(address(w) for w in words)
rnd = random.Random(3); null = collections.Counter()
for w in words:
    l = list(w); rnd.shuffle(l); null[address("".join(l))] += 1
idx_obs = collections.Counter(k for (s, k) in [address(w) for w in words]); idx_null = collections.Counter(k for (s, k) in [(0, 0)] * 0)
print("index k = XOR of generator indices (parity of counts) over words:", dict(sorted(idx_obs.items())))
sgn = collections.Counter(s for s, k in (address(w) for w in words)); print("sign over words (+1/-1):", dict(sgn))
print("occupied (sign,index) addresses: observed %d of 16 ; after shuffling each word's letters %d of 16" % (len(obs), len(null)))
print("address distribution (sign,index): observed", dict(sorted(obs.items(), key=lambda kv: -kv[1])[:16]))
print("                                   shuffled ", dict(sorted(null.items(), key=lambda kv: -kv[1])[:16]))
# is the sign (order) informative: how many words change address when their letters are shuffled?
changed = 0
for w in words:
    l = list(w); rnd.shuffle(l)
    if address("".join(l)) != address(w): changed += 1
print("words whose address changes when the order of their letters is shuffled: %d of %d (%.1f%%) ; the index never changes (parity of counts): %s" % (changed, len(words), 100 * changed / len(words), all(address("".join(random.sample(w, len(w))))[1] == address(w)[1] for w in words[:300])))
# the F = m a word in this reading: ADD, ADD, SCALE (D^2 then m)
for name, wd in (("F = m a  (D D, then m)", "AAS"), ("entropy  S = k ln W (count, then log)", "AS"), ("inertia (scale of the second derivative)", "SAA"), ("boost on the light cone (scale)", "S")):
    print("  %-44s word %-4s -> address %s" % (name, wd, address(wd)))
