# EquationSpace — sedenion input/output of Ĥ_RB, hyperindexing, address systems

Standing rule (Cody, 2026-11-20): all code dealing with the sedenion input or output of Ĥ_RB, sedenion hyperindexing and address systems lives in this repository.

These files are copies of the working versions in `FourthAgePapers/EquationSpace/` (the equation-space workbench), taken 2026-11-20:

| file | what |
|---|---|
| `equation_space.py` | the Cayley–Dickson product and walk (`mul`): words over A (e1), S (e2), G (e4) to (sign, index) |
| `address.py`, `word_address.py`, `address_discrimination.py` | address of a word; the walk address is faithful (3,461 of 3,461) |
| `walk.py`, `conjugates.py` | prefix-tree test of the walk; conjugate / non-conjugate pairs of the three generators |
| `grammar.py`, `catalog.py` | the ASS grammar and the equation catalogue (paths point at the Ainulindale/PtolemyDesktop checkouts) |
| `sedenion_hand.py` | Fano lines, associating triples, zero divisors among D16 roots (42 assessors), none in E8⊕E8 (exploratory, unregistered) |
| `results/` | recorded outputs |

New work from here is written here first. The scripts import each other by bare name: run from this directory.
