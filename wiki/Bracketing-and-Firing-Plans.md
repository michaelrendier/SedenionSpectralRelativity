# Bracketing and Firing Plans — brackets that carry firing orders

**Updated 2026-10-21.** Code: `firing_plan.py` (new), `bracket_firing_engine.py` (`plan_of_tree`, plan line in `main`). Notebook: `notebooks/02_bracketing_firing_plans.ipynb` (executed). Standalone port: `GenerationalLineage/engine/bracketing_firing_order.py` (tool 4). Everything below is `:CALCULATED` (exact `Fraction`, `emerger_spectrum.cd_mul`), and `python3 firing_plan.py` re-runs all 15 checks.

## What changed

The old engine fired the smaller-norm child first at every bracket: one rule for choosing an order. The order is now part of the bracket, written beside it, so any rule (or any hand-chosen order) is expressible, and a bracket runs as one operation inside its parent in its own order.

| notation | reading |
|---|---|
| `(A B)` | one bracket; default order `1 2`: `A` fires first |
| `(R I \| 2 1)` | the second child (`I`, imaginary octonion) fires first, the first (`R`, real octonion) second |
| `((A B \| 2 1) C \| 2 1)` | inner bracket runs as ONE operation in its own order; the outer order puts `C` first, then that whole operation. Fires `C B A` |

An order is a permutation of `1..k`; entry *i* names the child that fires *i*-th (the same reading as `GenerationalLineage.engine.bracketing_firing_order.apply_firing_order`).

## Meaning

Firing order acknowledges that the order operators are used in changes the output, as a numerator driving a denominator differs from a denominator driving a numerator. Application order and traversal order are the same order in different terms; "direction" in higher maths is *order arrived at*, nothing more.

Two readings of a bracket, kept apart:

- **Operator reading** (`operator`, `apply_plan`): fired children composed as matrices, first fired applied first; a bracket's matrix is `M_last · … · M_first`. Matrix composition is associative, so regrouping at the default order changes nothing; **only the firing order changes the result**.
- **Element reading** (`value`): the bracket is the algebra product of its fired children, folded left to right. The sedenion product is not associative, so here **the bracketing itself changes the result** (checked: `((B A) C)` ≠ `(B (A C))`).

## Measured

| result | value |
|---|---|
| two-octonion sedenion, `a = (1,2,0,1,0,0,3,0,0,1,0,0,2,0,0,1)`: `L_a = R + I` exactly | True |
| `(R I) = I·R` and `(R I \| 2 1) = R·I`; they differ in | 72 of 256 matrix entries |
| orders agree when the imaginary half is zero | True |
| plans over n leaves, `flat` (n!), `binary` (Catalan(n−1)·2^(n−1)), `nary` (every bracket ≥ 2 children, k! orders) | n = 2: 2, 2, 2 · n = 3: 6, 8, 14 · n = 4: 24, 40, 124 · n = 5: 120, 224, 1 244 · n = 6: 720, 1 344, 13 488 |
| orders reached by written-order binary plans | 6 of 6, **22 of 24**, **90 of 120** for n = 3, 4, 5 (the separable permutations; `2 4 1 3` and `3 1 4 2` are unreachable) |
| every triple of slots (circle elements 3/5 + 4/5 e_k, exact), every shape over every ordering, element reading | 35 triples → 6 results, 168 → 8, 252 → 12: the ring-circle tables reproduced through the plan engine |
| the old rule (`smaller norm first`, tie left) written as a plan (`policy_smaller_norm`) | leaf firing order identical to `firing_order()` |

The old engine's tree, norms and spectra are unchanged. For `e1+e10` its order reads:
`((((e0 e1) (e2 e3) | 2 1) ((e4 e5) (e6 e7)) | 2 1) (((e8 e9) (e10 e11 | 2 1)) ((e12 e13) (e14 e15)) | 2 1))`

## Limits and open

- `component_plan` is the **product reading** of a vector (leaves `L(a_k e_k)`, identity where `a_k = 0`); it is not `L_a`, which is the **sum** of the leaves. The additive merge of the two halves (`L_a = R + I`) is not a firing: there is no order in a sum. If a plan needs "fire and add", that is a different bracket kind and is not built.
- The notation has brackets of any size, but the emerger's five named brackets (`{1:15}`, `{2:14}`, `{8:8}`, `{4:4:4:4}`, `{4:8:4}`) are not yet written as plans with their legal orders (`emerger.legal_orders`).
- Order-of-application with inverses (`a·b⁻¹` against `b⁻¹·a`, "numerator drives denominator") is not a leaf flag yet; a leaf can carry any matrix, including an inverse, so it is expressible, not packaged.
- Positions are 1-based, as in `apply_firing_order`.

Related: `Ring-Circle-Operators.md` (what each slot produces under these brackets and orders), `GenerationalLineage/wiki/Firing-Plans.md`.
