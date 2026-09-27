#!/usr/bin/env python3
"""
sedenion_spin_wobble.py — Spin and Wobble, Embedded in the 16 Prime Channels
=============================================================================
Sedenion form of ValaQuenta/modules/spectral_primes/ and GenerationalLineage/
engine/toolsets/spectral_primes.py (2026-09-26). Same construction this repo
already uses everywhere else: the 16 sedenion channels e0..e15 mapped onto
the 16 primes {2,3,...,53} (README's own CD-tower table), one value per
channel, embedded and read with this repo's own verified machinery
(cd_mul/e from emerger_spectrum.py, left_mat/is_zero_divisor_dim from
bracket_firing_engine.py) -- no new algebra, only a new question asked of it,
same convention as prime_gauge_sedenion.py.

THE QUESTION: spin (theta'(t), the smooth non-resonant carrier) and wobble
(the minor-loop fluctuation that classically carries the primes) are the
same construction's two rotations. Embedded one value per prime channel,
do they look structurally different in the sedenion -- does wobble sit
closer to the zero-divisor locus (the primes' own structure showing up as
algebraic fault) while spin, being prime-blind by construction, sits
farther from it?

RESULT (computed, 2026-09-26): split verdict, reported as found.
  - CONFIRMED, the claim this file actually rests on: wobble genuinely
    differentiates primes from their non-prime neighbours once embedded --
    mean |local jump-rate| at the 16 primes is 5.04, at the non-prime
    probes (p+0.5, never a prime) is 1.53. Spin carries no such
    differentiation by construction (it never targets a prime, only uses
    p as a height).
  - NOT CONFIRMED: the secondary hypothesis that this shows up as a
    zero-divisor-locus contrast. Both the spin-vector and the wobble-
    vector are non-zero-divisors, both have exactly 3 distinct eigenvalue
    magnitudes (neither is an isometry). Embedding a value per channel
    this way does not, by itself, push the prime-resonant vector any
    closer to the ZD fault than the prime-blind one -- a real negative
    result on that specific question, not smoothed into the first one.

Module independence (this repo's convention, per hyper_linear_bridge.py's
own note): the zero table is a small, literal, frozen set (mpmath, dps=20,
2026-09-26) -- not re-derived here, not cross-imported from ValaQuenta.

stdlib + numpy only.
"""
import math
import cmath
import os
import sys
from fractions import Fraction as F

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from emerger_spectrum import cd_mul, e as e_of, PRIMES
from bracket_firing_engine import left_mat, is_zero_divisor_dim, norm_sq

DIM = 16
assert len(PRIMES) == DIM

# Same frozen zero table as GenerationalLineage/engine/toolsets/spectral_primes.py
ZEROS = [
    14.134725141734695, 21.022039638771556, 25.01085758014569,
    30.424876125859512, 32.93506158773919, 37.586178158825675,
    40.9187190121475, 43.327073280915, 48.00515088116716,
    49.7738324776723, 52.970321477714464, 56.44624769706339,
    59.34704400260235, 60.83177852460981, 65.1125440480816,
    67.07981052949417, 69.54640171117398, 72.0671576744819,
    75.70469069908393, 77.1448400688748, 79.33737502024937,
    82.91038085408603, 84.73549298051705, 87.42527461312523,
    88.80911120763446,
]


# ── spin: theta'(t) evaluated at each prime channel's own height ───────────

def theta_prime(t: float) -> float:
    return 0.5 * math.log(t / (2 * math.pi))


def spin_channel_values() -> list:
    """theta'(p) at t=p for each prime channel. Prime-BLIND by construction
    -- p is used only as a height, not as a resonance target -- so this
    should vary smoothly with p (log-like), never spiking AT primes vs
    nearby non-primes."""
    return [theta_prime(p) for p in PRIMES]


# ── wobble: local jump-rate of the truncated psi(x) reconstruction ────────

def psi_reconstructed(x: float, n_zeros: int = len(ZEROS)) -> float:
    smooth = x - math.log(2 * math.pi) - 0.5 * math.log(1 - x ** -2)
    osc = 0.0
    for gamma in ZEROS[:n_zeros]:
        rho = complex(0.5, gamma)
        term = (x ** 0.5) * cmath.exp(1j * gamma * math.log(x)) / rho
        osc += 2 * term.real
    return smooth - osc


def local_jump_rate(x: float, eps: float = 0.01) -> float:
    """(psi(x+eps) - psi(x-eps)) / (2*eps) -- the reconstruction's local
    slope. Expect this to be LARGE right at a prime (where the true step
    function jumps by ln(p)) and small between primes."""
    return (psi_reconstructed(x + eps) - psi_reconstructed(x - eps)) / (2 * eps)


def wobble_channel_values() -> list:
    """Local jump-rate of the reconstruction AT each prime channel -- this
    is where the primes' own structure should show up as differentiation
    between channels, unlike spin."""
    return [local_jump_rate(float(p)) for p in PRIMES]


# ── embedding + the sedenion read ──────────────────────────────────────────

def embed(values: list) -> tuple:
    """One value per channel, e_k <- values[k], rounded to a rational for
    exact rank testing (same convention as prime_gauge_sedenion.py's
    embed_c_copy)."""
    return tuple(F(round(v, 6)).limit_denominator(10 ** 6) for v in values)


def sedenion_report(values: list, label: str) -> dict:
    x = embed(values)
    zd = is_zero_divisor_dim(x)
    L = left_mat(x)
    Lf = np.array([[float(c) for c in row] for row in L])
    eigs = np.linalg.eigvals(Lf)
    mags = sorted(set(round(abs(z), 4) for z in eigs))
    return {
        "label": label,
        "values_range": (min(values), max(values)),
        "values_stdev": float(np.std(values)),
        "is_zero_divisor": zd,
        "n_distinct_eigenvalue_magnitudes": len(mags),
        "is_isometry": len(mags) == 1,
        "eigenvalue_magnitudes": mags,
    }


def prime_vs_nonprime_contrast() -> dict:
    """Direct check that wobble actually differentiates primes from their
    non-prime neighbours (the structural claim this whole file rests on),
    not asserted -- computed."""
    prime_rates = [abs(local_jump_rate(float(p))) for p in PRIMES]
    nonprime_probe = [p + 0.5 for p in PRIMES]  # midpoint to next integer, never a prime
    nonprime_rates = [abs(local_jump_rate(x)) for x in nonprime_probe]
    return {
        "mean_abs_jump_rate_at_primes": sum(prime_rates) / len(prime_rates),
        "mean_abs_jump_rate_at_nonprime_probes": sum(nonprime_rates) / len(nonprime_rates),
        "primes_differentiated": (sum(prime_rates) / len(prime_rates)) >
                                  (sum(nonprime_rates) / len(nonprime_rates)),
    }


def full_report() -> dict:
    spin_vals = spin_channel_values()
    wobble_vals = wobble_channel_values()
    return {
        "spin": sedenion_report(spin_vals, "spin (theta' at each prime channel)"),
        "wobble": sedenion_report(wobble_vals, "wobble (local jump-rate at each prime channel)"),
        "contrast": prime_vs_nonprime_contrast(),
    }


if __name__ == "__main__":
    r = full_report()
    for key in ("spin", "wobble"):
        d = r[key]
        print(f"\n=== {d['label']} ===")
        for k, v in d.items():
            if k != "label":
                print(f"  {k}: {v}")
    print("\n=== prime vs non-prime contrast (wobble only — the claim this rests on) ===")
    for k, v in r["contrast"].items():
        print(f"  {k}: {v}")
