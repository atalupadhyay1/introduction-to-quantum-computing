#!/usr/bin/env python3
"""
L04 -- Probability and statistics for quantum computing.

Course section: 3.2 (Introduction to Probability, Mutually Exclusive Events,
Independent Events, Manipulating Probabilities with Algebra, Venn Diagrams,
Conditional Probability, Introduction to Statistics, Random Variables, Mean,
Standard Deviation, Combinations of Random Variables, Correlation).

Run me::

    python labs/L04_probability_statistics/lab.py

What you will build
-------------------
* The algebra of probability: AND, OR, NOT, and the two special cases
  (mutually exclusive and independent).
* Random variables, expected value, variance and standard deviation.
* Correlation -- and the test that lets you *detect* entanglement:
  ``E[XY] != E[X]E[Y]``.
"""

from __future__ import annotations

import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "common"))

from qc101.labkit import Lab
from qc101 import probability as pr
from qc101 import viz

lab = Lab("L04", "Probability and statistics")
RNG = random.Random(31337)


# ---------------------------------------------------------------------------
lab.section("1. The algebra of probability")
# ---------------------------------------------------------------------------
lab.step("P(A or B) = P(A) + P(B) - P(A and B)")

p_a, p_b = 0.2, 0.3
p_ab = pr.p_independent(p_a, p_b)[0]
p_or = pr.p_or(p_a, p_b, p_ab)
lab.note(f"P(A) = {p_a}, P(B) = {p_b}, independent")
lab.note(f"P(A and B) = P(A)*P(B) = {p_ab:.4f}")
lab.note(f"P(A or B) = {p_a} + {p_b} - {p_ab:.4f} = {p_or:.4f}")
lab.check_close("independent P(A or B) = 0.44", p_or, 0.44, 1e-12)
lab.check_close("P(not A) = 1 - P(A)", pr.p_not(p_a), 0.8, 1e-12)

lab.step("Mutually exclusive events: P(A and B) = 0.")
p_ab_mx, p_or_mx = pr.p_mutually_exclusive(p_a, p_b)
lab.note(f"P(A and B) = {p_ab_mx}, P(A or B) = {p_or_mx:.4f}")
lab.check_close("mutually exclusive P(A or B) = P(A) + P(B)", p_or_mx, 0.5, 1e-12)

lab.step("Conditional probability: P(B|A) = P(A and B) / P(A)")
lab.check_close("P(B|A) with P(A and B)=0.12, P(A)=0.3", pr.p_conditional(0.12, 0.3), 0.4, 1e-12)
lab.note("This is the ratio of the 'A and B' region to the whole 'A' region in a Venn "
         "diagram -- the same picture the course draws.")


# ---------------------------------------------------------------------------
lab.section("2. Recovering P(A) from a decomposition")
# ---------------------------------------------------------------------------
lab.step("Alice's car: red or blue?")
p_a_and_b = 0.18      # red AND has a ticket
p_a_and_not_b = 0.22  # red AND no ticket
p_a = pr.p_from_joint(p_a_and_b, p_a_and_not_b)
lab.note(f"P(A and B) = {p_a_and_b}, P(A and not B) = {p_a_and_not_b}")
lab.note(f"P(A) = {p_a}")
lab.check_close("P(A) = P(A and B) + P(A and not B)", p_a, 0.40, 1e-12)
lab.note("A complete set of mutually exclusive events sums to 1 -- exactly like the "
         "measurement outcomes of a quantum state.")


# ---------------------------------------------------------------------------
lab.section("3. Random variables: mean, variance, standard deviation")
# ---------------------------------------------------------------------------
lab.step("A fair coin mapped to -1 (tails) and +1 (heads).")

fair = pr.coin(0.5, name="fair coin")
lab.show(fair.table())
lab.check_close("a fair coin has mean 0", fair.mean(), 0.0, 1e-12)
lab.check_close("a fair coin has standard deviation 1", fair.standard_deviation(), 1.0, 1e-12)

lab.step("A slightly loaded coin: P(heads) = 0.52.")
loaded = pr.coin(0.52, name="loaded coin")
lab.show(loaded.table())
lab.check_close("the mean is 0.04", loaded.mean(), 0.04, 1e-12)
lab.note("A mean of 0.04 instead of 0 is the *statistical fingerprint* of a loaded coin.  "
         "For qubits, the mean of repeated measurements is exactly this kind of evidence.")


# ---------------------------------------------------------------------------
lab.section("4. A loaded die")
# ---------------------------------------------------------------------------
lab.step("A die where 6 comes up 50% of the time.")

d = pr.dice(6, loaded={6: 0.5}, name="loaded die")
lab.show(d.table())
lab.check_close("the mean of the loaded die is 4.5", d.mean(), 4.5, 1e-12)
fair_die = pr.dice(6, name="fair die")
lab.check_close("a fair die has mean 3.5", fair_die.mean(), 3.5, 1e-12)
lab.note("Two dice can have the same mean and completely different behaviour -- that is "
         "why the course insists on looking at the *spread* as well.")


# ---------------------------------------------------------------------------
lab.section("5. Beyond the mean: variance and standard deviation")
# ---------------------------------------------------------------------------
lab.step("Compare a coin (values -1/+1) and a die (values 1..6) by their spread.")

lab.show(viz.kv_table({
    "fair coin mean": round(fair.mean(), 4),
    "fair coin std dev": round(fair.standard_deviation(), 4),
    "fair die mean": round(fair_die.mean(), 4),
    "fair die std dev": round(fair_die.standard_deviation(), 4),
}))
lab.check("the die has a larger spread than the coin",
          fair_die.standard_deviation() > fair.standard_deviation())


# ---------------------------------------------------------------------------
lab.section("6. Combinations of random variables")
# ---------------------------------------------------------------------------
lab.step("Add a coin and a die: the mean of the sum is the sum of the means.")

coin_samples = fair.sample(20000, RNG)
die_samples = fair_die.sample(20000, RNG)
sums = [c + x for c, x in zip(coin_samples, die_samples)]
lab.check_close("mean(coin + die) = mean(coin) + mean(die)",
                pr.mean(sums), fair.mean() + fair_die.mean(), 0.15)
lab.note("This linearity of the expected value is why quantum expectation values are "
         "so easy to compute: <psi|A|psi> is linear in the operator.")


# ---------------------------------------------------------------------------
lab.section("7. Correlation: the entanglement test")
# ---------------------------------------------------------------------------
lab.step("Independent variables: E[XY] = E[X]E[Y].")

x = fair.sample(20000, RNG)
y = fair_die.sample(20000, RNG)
e_xy = pr.mean([a * bb for a, bb in zip(x, y)])
e_x, e_y = pr.mean(x), pr.mean(y)
lab.note(f"E[X] = {e_x:.4f}, E[Y] = {e_y:.4f}")
lab.note(f"E[XY] = {e_xy:.4f}, E[X]E[Y] = {e_x * e_y:.4f}")
lab.check_close("independent variables satisfy E[XY] = E[X]E[Y]", e_xy, e_x * e_y, 0.05)

lab.step("Perfectly correlated variables: Y = X.")
y2 = list(x)
e_xy2 = pr.mean([a * bb for a, bb in zip(x, y2)])
lab.note(f"E[XY] = {e_xy2:.4f} vs E[X]E[Y] = {pr.mean(x) * pr.mean(y2):.4f}")
lab.check("perfectly correlated variables break E[XY] = E[X]E[Y]",
          abs(e_xy2 - pr.mean(x) * pr.mean(y2)) > 0.05)
lab.note("This is the exact test used in lab L12 to *prove* that a pair of photons is "
         "entangled: the joint product of the outcomes does not factorise.")

lab.step("Pearson correlation on the same data.")
lab.note(f"corr(independent) = {pr.correlation(x, y):+.4f}")
lab.note(f"corr(identical)   = {pr.correlation(x, y2):+.4f}")
lab.check("independent samples have near-zero correlation", abs(pr.correlation(x, y)) < 0.05)
lab.check("identical samples have correlation 1", abs(pr.correlation(x, y2) - 1.0) < 1e-9)


# ---------------------------------------------------------------------------
lab.section("8. The Born rule as a probability distribution")
# ---------------------------------------------------------------------------
lab.step("The measurement probabilities of a quantum state must sum to one.")

from qc101 import quantum as q

sv = q.StateVector.zero(2).apply_single(q.H, 0).apply_cnot(0, 1)
probs = sv.probabilities()
lab.note(f"state: {sv.to_dirac()}")
lab.show(viz.table(["basis state", "probability"], list(zip(sv.basis_labels(), probs))))
lab.check_close("probabilities sum to 1", sum(probs), 1.0, 1e-12)
lab.check("a complete set of mutually exclusive outcomes", all(p >= 0 for p in probs))
lab.note("The Born rule turns a quantum state into a probability distribution, and the "
         "distribution over a complete basis always sums to one.")


if __name__ == "__main__":
    sys.exit(lab.finish())
