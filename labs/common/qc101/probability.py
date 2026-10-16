"""
Probability and statistics for quantum computing.

Covers Section 3.2 of QC101: probability of boolean expressions, mutually
exclusive and independent events, the algebra of probabilities, Venn
diagram reasoning, conditional probability, random variables, mean, variance,
standard deviation, combinations of random variables and correlation.
"""

from __future__ import annotations

import math
import random
from typing import Callable, Dict, List, Sequence, Tuple

__all__ = [
    "p_and",
    "p_or",
    "p_not",
    "p_mutually_exclusive",
    "p_independent",
    "p_from_joint",
    "p_conditional",
    "RandomVariable",
    "bernoulli",
    "dice",
    "coin",
    "mean",
    "variance",
    "standard_deviation",
    "correlation",
    "joint_distribution",
]


# --------------------------------------------------------------------------
# The algebra of probabilities
# --------------------------------------------------------------------------
def p_and(p_a: float, p_b: float, p_a_and_b: float | None = None) -> float:
    """
    ``P(A and B) = P(A) * P(B)`` when A and B are independent.

    If ``p_a_and_b`` is given it is returned unchanged (the general case).
    """
    if p_a_and_b is not None:
        return p_a_and_b
    return p_a * p_b


def p_or(p_a: float, p_b: float, p_a_and_b: float = 0.0) -> float:
    """
    The general addition rule: ``P(A or B) = P(A) + P(B) - P(A and B)``.

    For mutually exclusive events ``P(A and B) = 0`` so this reduces to
    ``P(A) + P(B)``.  For independent events it is
    ``P(A) + P(B) - P(A)*P(B)``.
    """
    return p_a + p_b - p_a_and_b


def p_not(p_a: float) -> float:
    """``P(not A) = 1 - P(A)``."""
    return 1.0 - p_a


def p_mutually_exclusive(p_a: float, p_b: float) -> Tuple[float, float]:
    """
    For mutually exclusive events: ``P(A and B) = 0`` and
    ``P(A or B) = P(A) + P(B)``.

    Returns ``(p_a_and_b, p_a_or_b)``.
    """
    return 0.0, p_a + p_b


def p_independent(p_a: float, p_b: float) -> Tuple[float, float]:
    """
    For independent events: ``P(A and B) = P(A)*P(B)`` and
    ``P(A or B) = P(A) + P(B) - P(A)*P(B)``.

    Returns ``(p_a_and_b, p_a_or_b)``.
    """
    p_ab = p_a * p_b
    return p_ab, p_a + p_b - p_ab


def p_from_joint(p_a_and_b: float, p_a_and_not_b: float) -> float:
    """
    Recover ``P(A)`` from a decomposition of the sample space.

    ``A`` splits into ``(A and B)`` and ``(A and not B)`` so
    ``P(A) = P(A and B) + P(A and not B)``.
    """
    return p_a_and_b + p_a_and_not_b


def p_conditional(p_a_and_b: float, p_a: float) -> float:
    """
    Conditional probability: ``P(B | A) = P(A and B) / P(A)``.
    """
    if p_a == 0:
        raise ZeroDivisionError("P(A) is zero, so P(B|A) is undefined")
    return p_a_and_b / p_a


# --------------------------------------------------------------------------
# Random variables
# --------------------------------------------------------------------------
class RandomVariable:
    """
    A discrete random variable: a mapping from outcome values to probabilities.

    >>> rv = RandomVariable({-1: 0.48, 1: 0.52})
    >>> round(rv.mean(), 2)
    0.04
    """

    def __init__(self, distribution: Dict[float, float], name: str = "X"):
        total = sum(distribution.values())
        if abs(total - 1.0) > 1e-9:
            raise ValueError(f"probabilities must sum to 1 (got {total})")
        self.distribution = dict(distribution)
        self.name = name

    # -- moments ----------------------------------------------------------
    def mean(self) -> float:
        """Expected value: ``E[X] = sum(x * P(x))``."""
        return sum(x * p for x, p in self.distribution.items())

    def variance(self) -> float:
        """``Var[X] = E[(X - mu)^2] = E[X^2] - mu^2``."""
        mu = self.mean()
        return sum((x - mu) ** 2 * p for x, p in self.distribution.items())

    def standard_deviation(self) -> float:
        """``sigma = sqrt(Var[X])``."""
        return math.sqrt(self.variance())

    def second_moment(self) -> float:
        """``E[X^2]``."""
        return sum(x * x * p for x, p in self.distribution.items())

    # -- sampling ---------------------------------------------------------
    def sample(self, n: int = 1, rng: random.Random | None = None) -> List[float]:
        """Draw ``n`` samples from the distribution."""
        rng = rng or random
        values = list(self.distribution.keys())
        weights = list(self.distribution.values())
        return rng.choices(values, weights=weights, k=n)

    # -- display ----------------------------------------------------------
    def table(self) -> str:
        """Render the distribution as an aligned text table."""
        lines = [f"{self.name}      p({self.name})", "--------  -----------"]
        for x in sorted(self.distribution):
            lines.append(f"{x:>8}  {self.distribution[x]:>10.4f}")
        lines.append("")
        lines.append(f"mean      = {self.mean():.4f}")
        lines.append(f"variance  = {self.variance():.4f}")
        lines.append(f"std dev   = {self.standard_deviation():.4f}")
        return "\n".join(lines)

    def __repr__(self) -> str:  # pragma: no cover - convenience
        return f"RandomVariable({self.distribution!r}, name={self.name!r})"


def bernoulli(p: float = 0.5, name: str = "X") -> RandomVariable:
    """Bernoulli distribution: 0 with probability ``1-p`` and 1 with probability ``p``."""
    return RandomVariable({0: 1.0 - p, 1: p}, name=name)


def coin(p_head: float = 0.5, name: str = "X") -> RandomVariable:
    """A coin mapping heads to +1 and tails to -1 (the course convention)."""
    return RandomVariable({-1: 1.0 - p_head, 1: p_head}, name=name)


def dice(sides: int = 6, loaded: Dict[int, float] | None = None, name: str = "X") -> RandomVariable:
    """
    A die.  ``loaded`` optionally overrides some face probabilities; the
    remaining probability mass is spread uniformly over the other faces.
    """
    if loaded is None:
        loaded = {}
    dist: Dict[int, float] = {}
    remaining = 1.0 - sum(loaded.values())
    other = [f for f in range(1, sides + 1) if f not in loaded]
    share = remaining / len(other) if other else 0.0
    for f in range(1, sides + 1):
        dist[f] = loaded.get(f, share)
    return RandomVariable(dist, name=name)


# --------------------------------------------------------------------------
# Module-level moment helpers
# --------------------------------------------------------------------------
def mean(values: Sequence[float]) -> float:
    """Arithmetic mean of a sample."""
    values = list(values)
    if not values:
        raise ValueError("mean of an empty sample is undefined")
    return sum(values) / len(values)


def variance(values: Sequence[float], ddof: int = 0) -> float:
    """
    Variance of a sample.  ``ddof=0`` (default) uses the population formula
    ``E[(X-mu)^2]``; ``ddof=1`` uses the unbiased sample estimator.
    """
    values = list(values)
    n = len(values)
    if n - ddof <= 0:
        raise ValueError("not enough data points")
    mu = mean(values)
    return sum((v - mu) ** 2 for v in values) / (n - ddof)


def standard_deviation(values: Sequence[float], ddof: int = 0) -> float:
    """Standard deviation: ``sqrt(variance)``."""
    return math.sqrt(variance(values, ddof))


def correlation(x: Sequence[float], y: Sequence[float]) -> float:
    """
    Pearson correlation coefficient of two samples, in ``[-1, 1]``.

    ``0`` means uncorrelated (which for the *mean* test means independent),
    ``+1`` perfect positive, ``-1`` perfect negative.
    """
    x, y = list(x), list(y)
    if len(x) != len(y):
        raise ValueError("samples must have equal length")
    if len(x) < 2:
        raise ValueError("need at least two samples")
    mx, my = mean(x), mean(y)
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    if sxx == 0 or syy == 0:
        return 0.0
    return sxy / math.sqrt(sxx * syy)


def joint_distribution(
    rv_x: RandomVariable,
    rv_y: RandomVariable,
    independent: bool = True,
) -> Dict[Tuple[float, float], float]:
    """
    Joint distribution of two random variables.

    When ``independent`` is True the product rule is used, otherwise the
    maximum-entropy-free "shared" coupling is not assumed and the caller
    should build the table explicitly.  This helper exists to make the
    ``E[XY] = E[X]E[Y]`` test concrete.
    """
    if not independent:
        raise ValueError("only the independent case is modelled by this helper")
    return {
        (x, y): px * py
        for x, px in rv_x.distribution.items()
        for y, py in rv_y.distribution.items()
    }
