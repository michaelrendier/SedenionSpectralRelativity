"""catalog_compression.py (2026-11-20, exploratory, unregistered): how compressible are the catalog words?  An adaptive order-k context model (Krichevsky-Trofimov estimator, alphabet {A,S,G,$} with $ = end of word)
gives the code length an arithmetic coder would reach: bits = sum of -log2 p(next symbol | last k symbols) (3Blue1Brown, 'Compression is intelligence', part 3).  Controls: the uniform code (2 bits per symbol over 4 symbols) and the same words
with their letters shuffled across the whole catalog (same letter counts and word lengths, no structure).  Words longer than 400 letters are skipped.   Run: ../.venv/bin/python catalog_compression.py"""
import csv, os, random, math, collections
CAT = os.path.expanduser("~/Projects/ThePlace/FourthAgePapers/EquationSpace/catalog")
def asg(w): return "".join(c for c in w if c in "ASG")
def load(fn, col): return [asg(r[col]) for r in csv.DictReader(open(f"{CAT}/{fn}"))]
def codelen(words, k):
    cnt = collections.defaultdict(lambda: [0.5, 0.5, 0.5, 0.5]); idx = {"A": 0, "S": 1, "G": 2, "$": 3}; bits = 0.0; n = 0
    for w in words:
        s = w + "$"; ctx = ""
        for ch in s:
            c = cnt[ctx[-k:] if k else ""]; bits -= math.log2(c[idx[ch]] / sum(c)); c[idx[ch]] += 1; ctx += ch; n += 1
    return bits, n
rng = random.Random(0)
def shuffled(words):
    letters = list("".join(words)); rng.shuffle(letters); out = []; p = 0
    for w in words: out.append("".join(letters[p:p + len(w)])); p += len(w)
    return out
for name, words in (("A: 65 Python (ASG word of each equation)", [w for w in load("archimedes_py.csv", "ass_word") if 0 < len(w) <= 400]),
                    ("B: 6,268 fractals (loop word)", [w for w in load("archimedes_ufm.csv", "loop_word") if 0 < len(w) <= 400])):
    uniq = sorted(set(words)); print(f"\n== {name}: {len(words)} words, {len(uniq)} distinct, mean length {sum(map(len, words))/len(words):.1f}")
    for label, W in (("all entries", words), ("distinct words", uniq)):
        for k in (0, 1, 2, 3, 4, 6):
            b, n = codelen(W, k); sh = [codelen(shuffled(W), k)[0] for _ in range(5)]
            print(f"   {label:15s} order {k}: {b/n:.3f} bits/symbol (uniform 2.000)   shuffled control {sum(sh)/5/n:.3f} +- {(sum((x-sum(sh)/5)**2 for x in sh)/4)**.5/n:.3f}   saving vs shuffled {(1-b/(sum(sh)/5))*100:5.1f}%")
