"""catalog.py: EquationSpace test 5, Part C.  Reduces each Archimedes equation to its ASS-word (ordered tier-0 roots of its primitives, by the roll-down of
add_scale_sign) and lines the words up with the firing-order space.  The placement is CONSTRUCTED (found in); the EMERGENT objects are those of grammar.py.
   python3 catalog.py     (system python, stdlib only)   writes catalog/*.csv"""
import ast, glob, os, re, csv, math, collections
ARCH = os.path.expanduser("~/Projects/ThePlace/PtolemyDesktop/Archimedes")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "catalog")
A, S, G = "A", "S", "G"      # ADD, SCALE, SIGN ; F = a function slot with no root (unknown), R = randomness
FUNC = {**{n: G for n in "sin cos tan sinh cosh tanh asin acos atan asinh acosh atanh cotan cotanh sec csc abs cabs conj flip real imag arg sign radians degrees".split()},
        **{n: S for n in "exp log log10 sqrt sqr recip pow cube ident exp2 hypot".split()},
        **{n: A for n in "round trunc floor ceil sum range len".split()}}
RAND = {"random", "rand", "gauss", "randint", "seed", "shuffle", "choice"}
def word_str(w): return "".join(w)

# ---------------- python
class V(ast.NodeVisitor):
    def __init__(self): self.w = []
    def visit_BinOp(self, n):
        self.visit(n.left); self.visit(n.right)
        self.w.append(A if isinstance(n.op, (ast.Add, ast.Sub, ast.Mod)) else S)
    def visit_UnaryOp(self, n): self.visit(n.operand); self.w.append(G if isinstance(n.op, (ast.USub, ast.Not, ast.Invert)) else A)
    def visit_Compare(self, n): self.generic_visit(n); self.w.append(G)
    def visit_BoolOp(self, n): self.generic_visit(n); self.w.append(G)
    def visit_If(self, n): self.visit(n.test); self.w.append(G); [self.visit(b) for b in n.body + n.orelse]
    def visit_IfExp(self, n): self.visit(n.test); self.w.append(G); self.visit(n.body); self.visit(n.orelse)
    def visit_While(self, n): self.visit(n.test); self.w.append(G); [self.visit(b) for b in n.body]
    def visit_For(self, n): self.visit(n.iter); self.w.append(A); [self.visit(b) for b in n.body]
    def visit_Call(self, n):
        for a in n.args: self.visit(a)
        nm = n.func.attr if isinstance(n.func, ast.Attribute) else (n.func.id if isinstance(n.func, ast.Name) else "?")
        self.w.append("R" if nm in RAND else FUNC.get(nm, "F"))
def py_catalog():
    rows = []
    MODS = "Calculus Combinatorics Constants Electromagnetism Factorial LinearAlgebra LorenzStirling Matrix StatisticsAndProbability Thermodynamics Trigonometry".split()
    files = [f"{ARCH}/Maths/{m}.py" for m in MODS] + glob.glob(f"{ARCH}/Maths/Sequences/*.py") + glob.glob(f"{ARCH}/Maths/Series/*.py")
    for f in files:
        if f.endswith("__init__.py") or not os.path.exists(f): continue
        try: tree = ast.parse(open(f, encoding="utf-8").read())
        except Exception: continue
        for n in ast.walk(tree):
            if isinstance(n, ast.FunctionDef) and not n.name.startswith("_") and len(list(ast.walk(n))) > 8:
                v = V(); [v.visit(b) for b in n.body]
                rows.append(("py", os.path.relpath(f, ARCH) + "::" + n.name, "".join(v.w)))
    return rows

# ---------------- ultra fractal
TOK = re.compile(r"[A-Za-z_][A-Za-z_0-9]*|\d+\.?\d*|<=|>=|==|!=|&&|\|\||[-+*/^|<>=(),]")
def ufm_formulas():
    out = []
    for f in sorted(glob.glob(f"{ARCH}/Maths/Formula/UFformulary/*.ufm")):
        txt = open(f, encoding="latin-1").read()
        for m in re.finditer(r"^([A-Za-z_][\w\-\s\(\)\.]*?)\s*\{\s*\n(.*?)^\}", txt, re.M | re.S):
            body = m.group(2)
            if "loop:" in body: out.append((os.path.basename(f) + "::" + m.group(1).strip(), body))
    return out
def section(body, name):
    m = re.search(r"^" + name + r":\s*\n(.*?)(?=^\w[\w ]*:\s*$|^default:|\Z)", body, re.M | re.S)
    return m.group(1) if m else ""
def ufm_word(src):
    src = "\n".join(l.split(";")[0] for l in src.split("\n"))
    toks = TOK.findall(src); w = []; prev = None; bars = 0
    for t in toks:
        tl = t.lower()
        if t in "+-" and t != "":
            unary = prev is None or prev in ("(", ",", "=", "+", "-", "*", "/", "^", "<", ">", "<=", ">=", "==", "!=", "&&", "||")
            w.append(G if (t == "-" and unary) else A)
        elif t in ("*", "/", "^"): w.append(S)
        elif t == "|": bars += 1; (w.append(G) if bars % 2 == 0 else None)
        elif t in ("<", ">", "<=", ">=", "==", "!=", "&&", "||") or tl in ("if", "elseif", "while"): w.append(G)
        elif tl in RAND: w.append("R")
        elif tl in FUNC: w.append(FUNC[tl])
        elif re.fullmatch(r"fn\d|fn_\w*", tl): w.append("F")
        prev = t
    return "".join(w)
def ufm_catalog():
    rows = []
    for name, body in ufm_formulas():
        loop = ufm_word(section(body, "loop")); bail = ufm_word(section(body, "bailout")); init = ufm_word(section(body, "init"))
        rows.append(("ufm", name, loop, bail, init))
    return rows

if __name__ == "__main__":
    P = py_catalog(); U = ufm_catalog()
    os.makedirs(OUT, exist_ok=True)
    with open(f"{OUT}/archimedes_py.csv", "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["kind", "id", "ass_word", "length", "ADD", "SCALE", "SIGN", "unknown_F", "random_R"])
        for k, i, wd in P: w.writerow([k, i, wd, len(wd), wd.count(A), wd.count(S), wd.count(G), wd.count("F"), wd.count("R")])
    with open(f"{OUT}/archimedes_ufm.csv", "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["kind", "id", "loop_word", "bailout_word", "init_word", "skeleton_key"])
        for k, i, lp, bl, ini in U: w.writerow([k, i, lp, bl, ini, lp + "|" + bl])
    print("py named equations: %d ; ufm formulas with a loop: %d" % (len(P), len(U)))
    # ---- C1 skeleton duplication
    keys = collections.Counter(lp + "|" + bl for _, _, lp, bl, _ in U); loops = collections.Counter(lp for _, _, lp, _, _ in U)
    print("C1 distinct (loop|bailout) skeletons: %d ; distinct loop words: %d ; duplication x%.1f" % (len(keys), len(loops), len(U) / len(keys)))
    print("   most common skeletons:", [(k, n) for k, n in keys.most_common(5)])
    # ---- C2 escape-time formulas have SIGN and ADD
    esc = [(lp, bl) for _, _, lp, bl, _ in U if bl]; both = sum(1 for lp, bl in esc if (G in lp + bl) and (A in lp))
    print("C2 formulas with a bailout section: %d ; with >=1 SIGN (anywhere) and >=1 ADD in the loop: %d (%.1f%%)" % (len(esc), both, 100 * both / max(1, len(esc))))
    sg = sum(1 for lp, bl in esc if G in bl); print("   with a SIGN primitive in the bailout itself: %d (%.1f%%) ; with an ADD in the loop: %d (%.1f%%)" % (sg, 100 * sg / len(esc), sum(1 for lp, _ in esc if A in lp), 100 * sum(1 for lp, _ in esc if A in lp) / len(esc)))
    # ---- C3 alignment with the firing-order space
    allwords = [wd for _, _, wd in P] + [lp for _, _, lp, _, _ in U]
    cat = lambda n: math.comb(2 * n, n) // (n + 1)
    byn = collections.defaultdict(set); freq = collections.Counter()
    for wd in allwords:
        core = "".join(c for c in wd if c in "ASG"); freq[core] += 1
        if 1 <= len(core) <= 8: byn[len(core)].add(core)
    print("C3 words by length n: occupied / 3^n possible / orderings-with-bracketings 3^n*Catalan(n-1)")
    for n in range(1, 9): print("   n=%d occupied %5d  of %6d  (%.3f%%)  ;  firing-order points %d" % (n, len(byn[n]), 3 ** n, 100 * len(byn[n]) / 3 ** n, 3 ** n * cat(n - 1)))
    L = collections.Counter(len("".join(c for c in wd if c in "ASG")) for wd in allwords); print("   length histogram (n: count):", dict(sorted(L.items())[:20]), "... max", max(L))
    tot = collections.Counter(); [tot.update("".join(c for c in wd if c in "ASG")) for wd in allwords]
    print("   root totals over all words: ADD %d SCALE %d SIGN %d (unknown-function slots %d, random %d)" % (tot["A"], tot["S"], tot["G"], sum(w.count("F") for w in allwords), sum(w.count("R") for w in allwords)))
