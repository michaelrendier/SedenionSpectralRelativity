"""address_discrimination.py: can the 16-out result of the Emerger tell the quantities apart?  (follows address.py)"""
import sys, os, collections, random
sys.path.insert(0, os.path.expanduser("~/Projects/ThePlace")); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import address as A
from ValaQuenta.modules.emerger import maths as E
def out_key(x):
    s = E.sigma_rb(x); fo = E.emerge(x)["firing_order"]
    return (tuple(map(str, s["tilt"])), tuple(map(str, s["axis"])), E.gain_class(x), str(fo.get("precession_step_of_12")), str(fo.get("entry_bracket_index")), str(fo.get("canonical")))
groups = collections.defaultdict(list)
for n, v in A.Q.items():
    if any(v): groups[out_key(A.addr(v))].append(n)
print("\n== distinct 16-out results among the %d named quantities: %d" % (sum(len(g) for g in groups.values()), len(groups)))
for k, g in sorted(groups.items(), key=lambda kv: -len(kv[1])): print("  ", len(g), g)
rnd = random.Random(5); keys = collections.Counter(); N = 2000
for _ in range(N): keys[out_key(A.addr(tuple(rnd.randint(-3, 3) for _ in range(7))))] += 1
print("== %d random exponent vectors in [-3,3]^7: %d distinct 16-out results (largest class %d)" % (N, len(keys), keys.most_common(1)[0][1]))
