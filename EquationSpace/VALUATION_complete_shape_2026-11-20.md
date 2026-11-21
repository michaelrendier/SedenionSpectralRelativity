# Valuation: does the Equation Space work support "Ĥ_RB is The Complete Shape of Mathematics"? (2026-11-20)

> **Assistant note.** Written by a transformer language model (Claude Sonnet 5.5) at the author's request, using only results already in `FourthAgePapers/EquationSpace` (tests 1–9), the Niemeier/Monster engine, and the catalogs. The author's claim is an *assumption*; this document values it against the data and adds no claim of its own. Tier labels: `ESTABLISHED`, `THEORETICAL`, `INTERPRETATION`, `CONJECTURE`, `OPEN`; `:CALCULATED` where a number was computed. Failed results stay.

## 1. The claim, made testable
"Ĥ_RB is the Complete Shape of Mathematics" is not testable as written. Equation Space can only test **operational** versions, each with a control. The scale used below:

| mark | meaning |
|---|---|
| **T** | a theorem or exact derivation: true, but no significance figure applies; also asks whether it is *specific* to Ĥ_RB |
| **σ** | a statistical result against a stated null (one-sided normal σ from the p-value) |
| **0σ / N** | non-discriminating: the control gives the same answer |
| **P** | placement (constructed): a reading of the source, not evidence |
| **OPEN** | not tested |

## 2. The valuation, sub-claim by sub-claim
| # | sub-claim | evidence in this work | control / null | result |
|---|---|---|---|---|
| 1 | The three generators close: ADD = D, SCALE = θ = xD, SIGN = P | [θ, D] = −D, P D P = −D, [P, θ] = 0 (G1, G2), exact, symbolic | none needed | **T**. This is the Lie algebra of the affine group of the line extended by parity. It is **not specific to Ĥ_RB**: any framework with translation, dilation and reflection has it. |
| 2 | Textbook structures are derivable from the generators | G1–G7 pass (xp, SIGN/ADD, eigen-forms, flows, entropy form, F = k m a, ℘ closure) | G6 is the Buckingham π theorem, G5 is Cauchy's functional equation, G7 is the homogeneity of the ℘ ODE | **T**, with **zero novelty** (the record says none is new to the literature). Tests 3 and 4 gave the **same classification for the control operators as for Ĥ_RB**: **0σ discrimination**. |
| 3 | The catalogs are "in" Ĥ_RB | 65 + 6,268 equations placed as A/S/G words | shuffling a word's letters leaves the address distribution unchanged; the unit address collapses (19 of 25 quantities on one value) | **P**. Placement reads operator counts from source; any grammar can do that. **Not evidence.** |
| 4 | Words carry information about behaviour | NMI(word class, circle kind) = 0.293 against a null 95th percentile of 0.261; 5,000 shuffles, p = 0.006 | shuffled null | **≈ 2.5σ**, weak: the only significant association in the work (EquationSpace test 8) |
| 5 | The hyperindex points at each equation | walk address is faithful to the *word* (3,461 of 3,461) | words per equation | **Not supported**: 20% of each catalog shares its complete word set; the end points use 15–16 of 32 values; 193 entries have no letter; nothing lands above e7 |
| 6 | Niemeier ∪ Monster cover all 16 sedenion slots (the threshold) | the Niemeier gap {1, 11, 15} is an algebraic theorem; the 15 moonshine primes cover the gap | chance that 15 random primes cover those three residues mod 16: **0.59 exact, 0.65–0.71 by simulation** | **T** for the gap; the covering is **≈ 0.4–0.5σ**: expected by chance more often than not. The author's own corrections stand (covering, not bijection; mod 10, 12, 14 also leave one gap, also covered). The unification reading is an **INTERPRETATION**. |
| 7 | Units are in Ĥ_RB | unit group ℤ⁷ as the log chart of SCALE; rank/nullity = dimensional analysis | the 16-vector encoding does not discriminate (A2: the registered assignment sits at the 22.9th percentile of 5,040; 0.7σ, not extreme) | **INTERPRETATION**, 0σ for the encoding |
| 8 | New content: an interface operator, equations outside the literature | searched | none found | **OPEN, negative so far** |
| 9 | Completeness of reach | A, S, G reach indices 0–7 only; the catalogs occupy 2.3% of the possible words at length 8 (153 of 6,561) | none | the three generators reach **half** the sedenion slots; the other half needs a fourth generator K, undefined. A **measured limit** on the reach of {A, S, G}. |

Registered predictions, selected from the records: test 5 C1 failed (4,500 loop skeletons against ≤ 2,500); test 6 W3 failed (prefix tree ratio 0.79); test 7 P3 (order-sensitivity 42%) and C2 (mod-4 returns 54.6%) failed; test 8 had 17 predictions and 3 failed; test 9 Q4 failed on its own tolerance and was re-run, labelled. The failures are in the record.

## 3. Verdict
- **Is Ĥ_RB the Complete Shape of Mathematics, according to the Equation Space work?** **Not established, and not discriminated.** The data are consistent with it and equally consistent with "the three generators of the affine group with parity, plus placement". No test so far separates Ĥ_RB from its controls, so the honest valuation of the *completeness* claim is **≈ 0σ**: an assumption, tier **CONJECTURE**.
- **What is solid:** the closure of the generators; seven exact textbook derivations; the catalog and location infrastructure; one weak significant association (≈ 2.5σ); the Niemeier gap theorem.
- **What the data say against completeness *as currently built*:** reach is half the slots; 20% of equations are not uniquely addressed; units collapse; no new equation found.
- **Does the name stack up?** "The Complete Shape of Mathematics" is, in the project's own registry, the title of the **Circle Atlas** paper (`FourthAgePapers/TheInterface`), and the author's rule is to be hesitant using it elsewhere. For Equation Space, a descriptive title is supportable by the data now ("Equation Space: what the three generators of Ĥ_RB place, derive and cannot reach"); the grand title is supportable only as the *assumption under test* (`CONJECTURE`), with the tests below.

## 4. What would raise the valuation (register predictions before running)
1. **Held-out corpus.** Sample, blind, a few hundred equations not used to build the catalogs. Predict the fraction that are dimensionally stable *and* have a derivation route from {D, θ, P} by the G-recipe; run the same recipe with a control algebra (the affine group alone; a random three-generator algebra). Completeness gains weight only if Ĥ_RB's number exceeds the controls'.
2. **Ĥ_RB-specific content.** Find a derivation that needs Ĥ_RB's own terms (the R̂, ∂̂, B̂ structure, σ_RB), not just the three generators, and fails for the control.
3. **K.** Assign K from behaviour (more data first, as agreed), then predict whether the 191 + 2 empty entries and the e8–e15 half fill, and whether e11 and e15 (the Niemeier blind spots) receive entries. A fourth generator that fills them would be a real test; one that does not would be a limit.
4. **A falsifier.** State a class of stable, sane equations that, if found provably unreachable by {D, θ, P, K}, would limit completeness. The author's observation that a fourth independent operator would change Fermat's theorem is the kind of statement to formalise.
5. **Uniqueness.** Extend the address (identity of the unknown-function slots, parameters) until collisions fall below a registered threshold; then "points at each equation" can be tested.
