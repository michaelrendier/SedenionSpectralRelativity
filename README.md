# SedenionSpectralRelativity
The Universal Oscilloscope...and spectrograph.

**Universal Oscilloscope for the Cayley-Dickson Tower.**

Every algebraic layer carries information. Always. The spectrograph shows what is present at each layer for any input — language, genome, mathematics, music, name.

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

## Usage

```bash
python3 layer_spectrograph.py "your text here"
# outputs: layer_spectrograph.svg
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
