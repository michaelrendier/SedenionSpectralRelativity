# SedenionSpectralRelativity
The Universal Oscilloscope...and spectrograph.

**Universal Oscilloscope for the Cayley-Dickson Tower.**

Every algebraic layer carries information. Always. Two spectrographs read it:
`layer_spectrograph.py` shows what is present at each **CD layer** (ℝ/ℂ/ℍ/𝕆/𝕊); `emerger_spectrum.py` shows what emerges from each **bracketing** of the sedenion, in firing order.

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

## Usage

```bash
python3 layer_spectrograph.py "your text here"     # outputs: layer_spectrograph.svg

python3 emerger_spectrum.py "your text here"       # P1 hash seeds 16 channels
python3 emerger_spectrum.py --vec "e1+e10"         # a raw sedenion
# outputs: emerger_spectrum.svg
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

## Related

- `PtolemyHolcus/monad.py`: P1 prime hash implementation (lines 127-205)
- `PtolemyHolcus/PtolC/ptol.c`: sedenion Dirichlet projection engine
- `Ainulindale/wiki/Claude.md`: record of how this was designed
- `FactoralDecomposition/engine/emerger.py`: the generalized bracketing engine (ascent dual of `lineage.py`)
- `ValaQuenta/modules/emerger/`: the Full-Engine-Protocol build
- `ValaQuenta/modules/box_kite/`: the exact PSL(2,7) ZD geometry (G₂ is the blow-up)
