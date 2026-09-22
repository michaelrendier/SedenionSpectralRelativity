# SedenionSpectralRelativity
The Universal Oscilloscope...and spectrograph.

**Universal Oscilloscope for the Cayley-Dickson Tower.**

Every algebraic layer carries information. Always. Two spectrographs read it:
`layer_spectrograph.py` shows what is present at each **CD layer** (ℝ/ℂ/ℍ/𝕆/𝕊); `emerger_spectrum.py` shows what emerges from each **bracketing** of the sedenion, in firing order.

## The 16D Oscilloscope — one instrument, every mode

`fano_oscilloscope.py` — Cody, 2026-09-22: *"this was the reason i wanted
the 16d oscilloscope."* Originally a single-purpose Fano-vs-Sedenion
wobble probe; now the dispatcher for every Sedenion Spectral Relativity
engine in this repo, `--mode` selecting the probe. Each non-`wobble` mode
delegates straight to its own already-verified module (imported, not
reimplemented) — this file adds selection, nothing else:

```bash
python3 fano_oscilloscope.py "your text here"                # wobble (default, needs text)
python3 fano_oscilloscope.py --mode bifurcation               # bracket_firing_engine.py
python3 fano_oscilloscope.py --mode crankshaft                # crankshaft_three_phase.py
python3 fano_oscilloscope.py --mode firing-circles            # prime_gauge_sedenion.py
python3 fano_oscilloscope.py --mode equation-space             # equation_space_engine.py
python3 fano_oscilloscope.py --mode hyper-linear               # hyper_linear_bridge.py
```

All six verified clean, same session, exit 0 each.

## The Architecture

The Cayley-Dickson tower: ℝ → ℂ → ℍ → 𝕆 ‖ZD‖ 𝕊

Each doubling introduces new algebraic structure and new prime channels:

| Layer | Dim | New channels | New structure lost |
|-------|-----|-------------|-------------------|
| ℝ | 1 | e0 (p=2) | — |
| ℂ | 2 | e1 (p=3) | — |
| ℍ | 4 | e2,e3 (p=5,7) | commutativity |
| 𝕆 | 8 | e4-e7 (p=11-19) | associativity |
| ‖ZD FAULT‖ | — | — | norm (zero-divisors appear) |
| 𝕊 | 16 | e8-e15 (p=23-53) | alternativity |

The zero-divisor boundary between 𝕆 and 𝕊 is simultaneously:
- A **fault** — where the algebra loses its norm
- A **function** — the origin point of the sedenion layer

**The shadow from above defines the layer below.** The sedenion structure is what makes the octonion structure possible. The octonion structure is what makes the quaternion structure possible. Reading downward is reading the chain of definition.

## The Spectrograph

`layer_spectrograph.py` computes a Dirichlet-weighted projection at σ=½:

```
x_k = Σ c_i · i^(-½) · cos(2π·i / p_k)
```

For each of the 16 prime channels p_k ∈ {2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53}.

Five stacked panels — one per algebraic layer — show:
- **Bars above baseline**: positive projection (J_red, Noether UP)
- **Bars below baseline**: negative projection (J_blue, Noether DOWN)
- **Bright bars**: channels NEW to this layer
- **Ghost bars**: channels inherited from layers below
- **ZD fault zone**: the boundary between 𝕆 and 𝕊 where L_dynamic fires
- **Shadow lines**: information flowing downward from 𝕊 to define 𝕆

L_dynamic = ∫J_red · J_blue ds = the action of traversal through the fault in both directions simultaneously.

## The Bracketing Spectrograph

`emerger_spectrum.py` — **The Emerger**, rendered as a spectrograph.
"factoral is the generalized, Spectral is Sedenion focused" (Cody, 2026-09-01).
This repo is the Sedenion-focused half.

`e_0` (real) is the **anchor** — the tilt to the *i* axis — never bracketed;
every imaginary group is paired against it. Bracket the 16-channel path five
ways. The **firing order** is the dispersion; each bracket is a **band**:

| bracket | reads |
|---|---|
| `{1:15}` | the ℝ \| imaginary split — Re, N, conj, inverse |
| `{2:14}` | the `(e0,e8)` doubling plane — the pointer `z`, `\|z\| − Ω` |
| `{8:8}` | **the `𝕆 ‖ZD‖ 𝕊` fault itself** — distance from the ZD equator (`zd_boundary.py`'s critical line), the sheet, `J_2`; **exact zero-divisor test** via rank-deficiency of `L_x` |
| `{4:4:4:4}` | four ℍ blocks — four SU(2) phases, `sigma_RB` tilt/axis, `Σtilt` = net work (`= 0 ⇔ σ = ½`) |
| `{4:8:4}` | the gain spectrum `0 / 1 / √2` — multiplicative role |

`sigma_RB`'s tilt-phase rotates the entry band into the 12-step precession
(4 d\* faces : 3 Lambert-W faces). It is a **refinement** of the CD-tower
layer table above — `{8:8}` is the ZD FAULT row.

Generalized engine: `FactoralDecomposition/engine/emerger.py`.
Full-Engine-Protocol build: `ValaQuenta/modules/emerger/`.
Prototype: `TuringStack/the_emerger.py`.

## The Recursive Bracketing & Firing-Order Engine

`bracket_firing_engine.py` — takes `emerger_spectrum.py`'s five NAMED
top-level brackets and follows the bifurcation all the way down instead of
stopping at five bands: the sedenion's own 16x16 `L(a)` matrix splits into
its **two orthogonal octonions**, each of which splits into its **two
orthogonal quaternions**, each into two complex pairs, each into two reals.
31 nodes total (`1+2+4+8+16`), a literal binary tree.

The split is an exact matrix identity, not an approximation — verified live,
every dimension of the tower, before anything was built on it:

```
a = (a1, a2)   =>   L_a = [ L_a1        -R_a2 o C ]
                           [ L_a2 o C     R_a1     ]
```

(`C` = conjugation, `L_x`/`R_x` = left/right multiplication in the
half-dimension sub-algebra.) **Bracketing**, named exactly rather than left
implicit: this sign/ordering is one of a few equivalent-but-distinct
Cayley-Dickson doubling conventions — the one already hard-coded into
`emerger_spectrum.py`'s `cd_mul`. **Firing order**, named exactly: a
one-way, depth-first cursor over the 31-node tree — at every split the
smaller-norm child fires first, and a norm TIE is exactly `on_zd_equator`
generalized to every level of the tower, not only the top `{8:8}` split.

**The fractal signal, chased and found:** every NONZERO node below dim 16
is provably an exact isometry (Hurwitz's theorem — ℝ, ℂ, ℍ, 𝕆 are the only
normed division algebras that exist), meaning `L_a`'s eigenvalues all share
one modulus at every layer except the sedenion root itself. Verified live
across random inputs and a sparse zero-divisor input; the one apparent
counterexample found while checking (`e1+e10`, several sub-dim-16 nodes
showing spread) traced back exactly to an all-zero sub-vector (`0/0`,
undefined, not a real violation) — a caught false alarm kept in the record
rather than quietly fixed and forgotten. **The sedenion root is the only
place in the whole tree where eigenvalue-modulus can spread at all — that
departure from a single value IS the zero-divisor fault, read directly off
the spectrum, not just off the rank test.**

## The Hyper-Linear Algebra Decomposition Bridge

`hyper_linear_bridge.py` — runs the same generic recipe (one SCALE-type
generator per basis position, composed with a position operator, read
spectrally) on two different algebras side by side: plain integer
multiplication (self-contained here, mirroring
`GenerationalLineage/engine/toolsets/hyper_linear.py` exactly — no
cross-repo import, per this project's own module-independence rule) and
the sedenion `L_a` tower (`bracket_firing_engine.py`, above).

**The honest contrast it reports:** ℤ under `a*b` can never fault under
this recipe — the integers have no zero divisors, structurally, not
measured per-input. The sedenion tower faults in exactly one place (the
root, dim 16) and is provably as clean as ℤ's own multiplication
everywhere below that (Hurwitz). Same recipe, one algebra that never
breaks and one that breaks in exactly one spot.

## The Crankshaft, Three-Phase

`crankshaft_three_phase.py` — the box-kite's own 3-fold rotation, found and
verified rather than assumed: each box-kite's 6 Assessors split into 3
"reversal-pair" lobes (its 3 non-edges), and cyclically permuting those
lobes is a genuine order-3 graph automorphism that commutes with the
box-kite's own vibrational Laplacian — a real symmetry, not a relabelling.
That rotation is the crankshaft (Wankel framing: 3 lobes turning past one
fixed housing). Because it commutes with the Laplacian, it acts *within*
each vibrational eigenspace, and diagonalizing it there assigns every mode
a phase — literally 3-phase, cube roots of unity, checked not assumed:

    lambda=0  (e0's zero mode, 1-dim):  phase 0 deg only
    lambda=4  (3-fold degenerate):      the full 3-phase set: 0, +120, -120 deg
    lambda=6  (2-fold degenerate):      the two moving phases only, no 0 deg

Identical on all 7 struts, verified live. See
`marrais_boxkite_catalog.txt` (`VAPMIP/`) for the established object this
is built on.

## The Prime Gauge Field, in the Sedenion

`prime_gauge_sedenion.py` — how the sedenion describes and is influenced
by `ValaQuenta/modules/prime_gauge_field/`'s `Γ(s)=(s−1)/(s+1)`. Four
checked results:

1. **Containment** — every `span(e0, e_k)`, `k=1..15`, is a literal,
   closed copy of ℂ inside the sedenion (`e_k²=-e0`, verified). `Γ`
   embeds unchanged into any one; Hurwitz guarantees an exact isometry
   there, so nothing sedenion-specific happens in a single copy.
2. **The symmetric superposition** — a real negative result. Spreading
   the same `Γ(s)` identically across all 15 imaginary directions never
   produces a zero divisor, for any `s` tested — too symmetric to hit
   the thin zero-divisor locus.
3. **The Assessor embedding** — the real positive finding. Embedding
   `Γ(s)` into an actual Assessor plane fires (becomes an exact zero
   divisor) exactly when `Γ(s)` lands on a diagonal ray — pulled back
   through `Γ`'s own inverse Möbius map, an **exact circle** in the
   `s`-plane: `center=i, radius=√2`, verified to `1e-15`. The Assessor's
   *other* sign gives a **second** circle, `center=-i`, found via
   `equation_space_engine.py`'s gradient walk landing there and checked
   rather than dismissed — see `firing_circle_minus()`.
4. **Influence is the curvature, not the membership test** — `Γ`'s own
   curvature `F(s)` (no sedenion reference in its definition) correlates
   with `|∇ρ(s)|` (how fast the embedded sedenion approaches its own
   zero-divisor locus) at **Pearson ≈0.97–0.98**, and the firing circle
   is a genuine **fold/caustic** (`ρ/|dr| → ` the same nonzero constant
   from both sides — linear, not quadratic falloff), confirmed via
   `equation_space_engine.py`'s `classify_singularity()`. The circle
   passes exactly through both `Γ`'s zero (`s=1`, which is also ζ's own
   pole) and `Γ`'s pole (`s=-1`); its center (`i`) and radius (`√2=|1+i|`)
   are exactly Fermat's two-square data for the prime 2.

## Equation Space — steering by a collapse function's own gradient

`equation_space_engine.py` — companion to
`GenerationalLineage/engine/toolsets/equation_space.py`, same mechanism,
this repo's own `ρ` (the sedenion's zero-divisor proximity from
`prime_gauge_sedenion.py`, not the cheap `Γ`-diagonal proxy). `descend()`
reads `ρ` and its gradient at one point (free); `build_up()` walks from a
start point to `ρ=0` by gradient descent (expensive here — a 16×16
eigenproblem per step) and genuinely can fail to converge.
`classify_singularity()` distinguishes a fold (caustic) from a smooth
minimum; `steering_correlation()` checks whether an independent, cheap
compass predicts the costly gradient. Both circles found this way match
the ones found independently in `prime_gauge_sedenion.py` — two unrelated
methods, same two answers.

## Usage

```bash
python3 layer_spectrograph.py "your text here"     # outputs: layer_spectrograph.svg

python3 emerger_spectrum.py "your text here"       # P1 hash seeds 16 channels
python3 emerger_spectrum.py --vec "e1+e10"         # a raw sedenion
# outputs: emerger_spectrum.svg

python3 bracket_firing_engine.py "your text here"  # full 31-node bifurcation tree
python3 bracket_firing_engine.py --vec "e1+e10"    # a raw sedenion
# outputs: bracket_firing_engine.svg

python3 hyper_linear_bridge.py                     # integers vs sedenions, side by side

python3 crankshaft_three_phase.py                  # the box-kite's own 3-phase rotation, all 7 struts

python3 prime_gauge_sedenion.py                     # containment, superposition, both firing circles, influence
python3 equation_space_engine.py                    # steering by rho's gradient -- the sedenion instance
```

## Observations

**"O Captain My Captain"**: ℝ and ℂ negative, 𝕊 fully positive, peaks at e11 (p=37)

**"Michael Rendier He who is like God Wandering"**: 𝕊 layer 2× stronger than O Captain, same peak channel — the name has deeper sedenion resonance

**"primes are words the shadow from above defines the layer below"**: saturates e15 (p=53), keeps climbing — the statement about itself reaches the highest prime

## Origin

Designed during a session on 2026-06-14 in which:
- The user stated: *primes are words*
- Claude derived: the P1 prime hash (Horner → prime → Riemann zero index → σ=½)
- The layer spectrograph grew from the question: *when does computation START?*
- Answer: when the shadow from above touches the zero-divisor fault below, and L_dynamic fires through the singularity

The spectrograph is the universal oscilloscope for that event.

## Notebooks

`notebooks/01_hyper_linear_algebra_decomposition.ipynb` — the sedenion side
of the hyper-linear algebra decomposition (see below), executed live: the
31-node bifurcation tree, its firing order, the Hurwitz isometry check per
layer, and the integer/sedenion bridge script's output, all real, captured
output, nothing pasted in unexecuted.

## Related

- `PtolemyHolcus/monad.py`: P1 prime hash implementation (lines 127-205)
- `PtolemyHolcus/PtolC/ptol.c`: sedenion Dirichlet projection engine
- `Ainulindale/wiki/Claude.md`: record of how this was designed
- `FactoralDecomposition/engine/emerger.py`: the generalized bracketing engine (ascent dual of `lineage.py`)
- `ValaQuenta/modules/emerger/`: the Full-Engine-Protocol build
- `ValaQuenta/modules/box_kite/`: the exact PSL(2,7) ZD geometry (G₂ is the blow-up)
- `GenerationalLineage/engine/toolsets/hyper_linear.py`: the integer side of
  `hyper_linear_bridge.py` — same recipe (SCALE generator + position
  operator + spectral read), run on `a*b` instead of `L_a`
