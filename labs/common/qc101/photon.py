"""
Photon polarization: the experimental ground floor of quantum mechanics.

This is a faithful Python port of the Java simulators that ship with the
QC101 course (``PhotonPolarizationMeasurement`` and
``EntangledPhotonMeasurement``), extended with the classical Malus's-law
helpers used in Section 2.

Physics recap:

* Light is a stream of photons.  Each photon has a *polarization* -- the
  direction its electric field oscillates in.
* A **polarizing filter** at angle ``t`` transmits a photon whose
  polarization is aligned with ``t`` and blocks (or re-polarizes) one that
  is anti-aligned.  By Malus's law the *probability* of transmission is
  ``cos^2(theta_in - theta_filter)``.
* After the filter, the photon's polarization is **always** aligned with the
  filter (or exactly 90 degrees from it) -- the original angle is gone.
  That loss of information is what makes measurement irreversible, and it
  is the physical basis of the no-cloning theorem.
"""

from __future__ import annotations

import math
import random
from typing import Dict, List, Optional, Sequence, Tuple

__all__ = [
    "malus_transmission",
    "PhotonPolarizationMeasurement",
    "EntangledPhotonMeasurement",
    "filter_cascade",
    "FilterCascadeResult",
    "measurement_cascade",
    "polarization_basis",
]


def malus_transmission(theta_in: float, theta_filter: float) -> float:
    """
    Malus's law: the probability that a photon with polarization
    ``theta_in`` passes through a filter at ``theta_filter``.

    ``P = cos^2(theta_in - theta_filter)``
    """
    delta = math.radians(theta_in - theta_filter)
    return math.cos(delta) ** 2


def polarization_basis(theta: float) -> str:
    """Classify a polarization angle into one of four BB84 basis states."""
    t = theta % 180
    if abs(t - 0) < 1e-6 or abs(t - 180) < 1e-6:
        return "0 (horizontal)"
    if abs(t - 90) < 1e-6:
        return "1 (vertical)"
    if abs(t - 45) < 1e-6 or abs(t - 225) < 1e-6:
        return "+ (45 deg)"
    if abs(t - 135) < 1e-6 or abs(t - 315) < 1e-6:
        return "- (135 deg)"
    return f"other ({t:.2f} deg)"


class PhotonPolarizationMeasurement:
    """
    A single photon with a known polarization, measured by filters.

    The course's mapping is::

        qubit value 1 = "aligned"    (the filter's axis)
        qubit value 0 = "anti-aligned" (90 degrees from the filter's axis)

    ``measure_polarization`` returns ``True`` for aligned (1) and ``False``
    for anti-aligned (0), and *destroys* the original polarization angle.
    """

    def __init__(self, angle: float = 90.0, rng: random.Random | None = None):
        self.polarization_angle = float(angle)
        self.rng = rng or random.Random()

    def measure_polarization(self, angle: float) -> bool:
        """
        Measure the photon with a polarizer at ``angle``.

        Returns ``True`` if the photon came out aligned with the filter
        (qubit 1) and ``False`` if anti-aligned (qubit 0).  The photon's
        polarization is reset to the outcome, losing the previous angle.
        """
        p_align = malus_transmission(self.polarization_angle, angle)
        if self.rng.random() < p_align:
            self.polarization_angle = angle
            return True
        self.polarization_angle = angle + 90.0
        return False

    def measure_repeated(self, angle: float, n: int = 1000) -> Dict[str, float]:
        """
        Measure the *same* photon ``n`` times with the same filter.

        The first measurement is probabilistic; every later measurement is
        deterministic, because the photon is now aligned or anti-aligned
        with the filter.  This is the "measurement disturbs the state"
        demonstration from the course.
        """
        results: List[bool] = []
        for _ in range(n):
            results.append(self.measure_polarization(angle))
        ones = sum(1 for r in results if r)
        first = 1 if results[0] else 0
        return {
            "aligned": ones / n,
            "anti_aligned": (n - ones) / n,
            "first_outcome": first,
            "subsequent_stability": (
                1.0 if all(r == results[0] for r in results[1:]) else 0.0
            ),
        }

    def __repr__(self) -> str:  # pragma: no cover - convenience
        return f"PhotonPolarizationMeasurement(angle={self.polarization_angle})"


class FilterCascadeResult:
    """
    The outcome of pushing photons through a sequence of polarizers.

    Attributes
    ----------
    stage_transmission:
        Conditional transmission at each filter, ``T_k`` -- the fraction
        of the photons that *reached* filter ``k`` that get through it.
    cumulative_transmission:
        Fraction of the *original* photons that make it past filter ``k``.
    final_angle:
        The polarization angle of the surviving photons.
    """

    def __init__(
        self,
        stage_transmission: List[float],
        cumulative_transmission: List[float],
        final_angle: float,
    ):
        self.stage_transmission = stage_transmission
        self.cumulative_transmission = cumulative_transmission
        self.final_angle = final_angle

    def __str__(self) -> str:
        lines = ["stage   conditional   cumulative"]
        for i, (s, c) in enumerate(zip(self.stage_transmission, self.cumulative_transmission), 1):
            lines.append(f"  {i}      {s:>8.4f}     {c:>8.4f}")
        lines.append(f"surviving polarization: {self.final_angle:.1f} deg")
        return "\n".join(lines)


def filter_cascade(
    photon_angle: float,
    filter_angles: Sequence[float],
    shots: int = 2000,
    rng: random.Random | None = None,
) -> FilterCascadeResult:
    """
    Run photons through a sequence of polarizers, in the **Malus's law
    (polarizer) model**.

    A real polarizer transmits the component of the light parallel to its
    axis and absorbs the rest, so every photon that survives filter ``f``
    comes out polarized along ``f``.

    ``T_k = cos^2(theta_{k-1} - theta_k)`` where ``theta_0`` is the
    incoming angle.

    >>> r = filter_cascade(90.0, [45.0, 45.0, 90.0])
    >>> [round(t, 2) for t in r.stage_transmission]
    [0.5, 1.0, 0.5]
    >>> [round(t, 2) for t in r.cumulative_transmission]
    [0.5, 0.5, 0.25]

    The classic surprise: inserting a 45 degree filter *between* two
    vertical filters changes the outcome, because the first 45 degree
    filter destroys the information about the original polarization and
    leaves the light in a *new*, well-defined direction.
    """
    rng = rng or random
    stage_t: List[float] = []
    cumulative: List[float] = []
    survivors = shots
    current = photon_angle
    for f in filter_angles:
        p = malus_transmission(current, f)
        passed = sum(1 for _ in range(survivors) if rng.random() < p)
        stage_t.append(p)
        cumulative.append(passed / shots if shots else 0.0)
        survivors = passed
        current = f  # transmitted photons are re-polarized along the filter axis
    return FilterCascadeResult(stage_t, cumulative, current)


def measurement_cascade(
    photon_angle: float,
    filter_angles: Sequence[float],
    shots: int = 2000,
    rng: random.Random | None = None,
) -> FilterCascadeResult:
    """
    The same cascade, but measured with the **qubit model** used in the
    course: each filter measures the photon in the {aligned,
    anti-aligned} basis, and afterwards the photon's state is either
    aligned with that filter or exactly 90 degrees from it.

    This is the model implemented by the course's Java simulator
    ``PhotonPolarizationMeasurement``.  Each stage reports the
    probability that the photon came out *aligned* with that filter
    (qubit value 1).

    One photon is pushed through the *whole* chain, then the chain is
    repeated ``shots`` times -- this is the "sequential filters" experiment.

    >>> r = measurement_cascade(90.0, [45.0, 45.0, 90.0])
    >>> [round(t, 2) for t in r.stage_transmission]
    [0.5, 0.5, 0.5]
    """
    rng = rng or random
    aligned_counts = [0] * len(filter_angles)
    last_angle = photon_angle
    for _ in range(shots):
        p = PhotonPolarizationMeasurement(photon_angle, rng)
        for k, f in enumerate(filter_angles):
            if p.measure_polarization(f):
                aligned_counts[k] += 1
        last_angle = p.polarization_angle
    stage_t = [c / shots if shots else 0.0 for c in aligned_counts]
    cumulative: List[float] = []
    running = 1.0
    for t in stage_t:
        running *= t
        cumulative.append(running)
    return FilterCascadeResult(stage_t, cumulative, last_angle)


class EntangledPhotonMeasurement:
    """
    A pair of photons described by the four amplitudes
    ``(p00, p01, p10, p11)``.

    The Bell state used in the course is
    ``(|00> + |11>)/sqrt(2)`` -- amplitudes ``(0.7071, 0, 0, 0.7071)``.

    Measurement uses the Born rule: the probability of an outcome is the
    *square of the amplitude of the joint projection*, which is why the
    code sums products of amplitudes before squaring.
    """

    def __init__(self, p00: float, p01: float, p10: float, p11: float, rng: random.Random | None = None):
        self.p00, self.p01, self.p10, self.p11 = p00, p01, p10, p11
        total = p00**2 + p01**2 + p10**2 + p11**2
        if not (0.99 <= total <= 1.01):
            raise ValueError(f"probabilities must add up to 1 (got {total})")
        self.m1angle = 90.0
        self.m2angle = 90.0
        self.rng = rng or random.Random()

    # -- state helpers ----------------------------------------------------
    def set_independent_photon_angles(self, angle1: float, angle2: float) -> None:
        """Model two *independent* (unentangled) photons with these angles."""
        r1 = math.radians(angle1)
        r2 = math.radians(angle2)
        self.p00 = math.cos(r1) * math.cos(r2)
        self.p01 = math.cos(r1) * math.sin(r2)
        self.p10 = math.sin(r1) * math.cos(r2)
        self.p11 = math.sin(r1) * math.sin(r2)

    def set_measurement_angles(self, angle1: float, angle2: float) -> None:
        """Set the orientation of the two measurement filters."""
        self.m1angle = angle1
        self.m2angle = angle2

    def _outcome_probabilities(self) -> Dict[str, float]:
        """Born-rule probabilities of the four joint outcomes."""
        r1 = math.radians(self.m1angle)
        r2 = math.radians(self.m2angle)
        m00 = math.cos(r1) * math.cos(r2)
        m01 = math.cos(r1) * math.sin(r2)
        m10 = math.sin(r1) * math.cos(r2)
        m11 = math.sin(r1) * math.sin(r2)

        def sq(v: float) -> float:
            return v * v

        p11 = sq(self.p00 * m00 + self.p01 * m01 + self.p10 * m10 + self.p11 * m11)
        # 01: rotate the first measurement by 90 degrees
        r1b = math.radians(self.m1angle + 90)
        m00b, m01b = math.cos(r1b) * math.cos(r2), math.cos(r1b) * math.sin(r2)
        m10b, m11b = math.sin(r1b) * math.cos(r2), math.sin(r1b) * math.sin(r2)
        p01 = sq(self.p00 * m00b + self.p01 * m01b + self.p10 * m10b + self.p11 * m11b)
        # 10: rotate the second measurement by 90 degrees
        r2b = math.radians(self.m2angle + 90)
        m00c, m01c = math.cos(r1) * math.cos(r2b), math.cos(r1) * math.sin(r2b)
        m10c, m11c = math.sin(r1) * math.cos(r2b), math.sin(r1) * math.sin(r2b)
        p10 = sq(self.p00 * m00c + self.p01 * m01c + self.p10 * m10c + self.p11 * m11c)
        # 00: rotate both
        m00d = math.cos(r1b) * math.cos(r2b)
        m01d = math.cos(r1b) * math.sin(r2b)
        m10d = math.sin(r1b) * math.cos(r2b)
        m11d = math.sin(r1b) * math.sin(r2b)
        p00 = sq(self.p00 * m00d + self.p01 * m01d + self.p10 * m10d + self.p11 * m11d)
        return {"00": p00, "01": p01, "10": p10, "11": p11}

    def report_measurement_probability(self) -> str:
        """
        Report the four joint outcome probabilities plus the conditional
        probabilities ``P(photon1 | photon2)`` that expose entanglement.
        """
        probs = self._outcome_probabilities()
        lines = [f"Measurement angles: {self.m1angle:.2f} deg, {self.m2angle:.2f} deg"]
        for key in ("00", "01", "10", "11"):
            lines.append(f"  P({key}) = {probs[key]:.4f}")
        p01, p10, p11, p00 = probs["01"], probs["10"], probs["11"], probs["00"]
        if p01 + p11 > 1e-5:
            lines.append(f"  P(photon1=1 | photon2=1) = {p11 / (p01 + p11):.4f}")
        if p10 + p00 > 1e-5:
            lines.append(f"  P(photon1=1 | photon2=0) = {p10 / (p10 + p00):.4f}")
        if p10 + p11 > 1e-5:
            lines.append(f"  P(photon2=1 | photon1=1) = {p11 / (p10 + p11):.4f}")
        if p01 + p00 > 1e-5:
            lines.append(f"  P(photon2=1 | photon1=0) = {p01 / (p01 + p00):.4f}")
        return "\n".join(lines)

    def perform_measurement(self) -> str:
        """
        Perform one joint measurement.

        The outcome collapses the pair: the photons become independent
        (product) states with definite polarizations.
        """
        probs = self._outcome_probabilities()
        r = self.rng.random()
        if r < probs["00"]:
            outcome = "00"
            a1, a2 = self.m1angle + 90, self.m2angle + 90
        elif r < probs["00"] + probs["01"]:
            outcome = "01"
            a1, a2 = self.m1angle + 90, self.m2angle
        elif r < probs["00"] + probs["01"] + probs["10"]:
            outcome = "10"
            a1, a2 = self.m1angle, self.m2angle + 90
        else:
            outcome = "11"
            a1, a2 = self.m1angle, self.m2angle
        self.set_independent_photon_angles(a1, a2)
        return (
            f"Measured {outcome}\n"
            f"After measurement, the photon angles are {a1:.2f} and {a2:.2f} "
            f"and the photon state is {self.p00:.2f} {self.p01:.2f} {self.p10:.2f} {self.p11:.2f}"
        )
