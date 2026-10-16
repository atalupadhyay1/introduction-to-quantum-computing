# API reference -- the shared `qc101` library

Every lab in this repository is built on one small, dependency-free Python
package:

```
labs/common/qc101/
    complexnum.py    complex arithmetic
    boolean.py       Boolean algebra, truth tables, logic gates
    probability.py   probability rules, random variables, statistics
    linalg.py        matrices, vectors, eigenvalues, the Kronecker product
    quantum.py       qubit states, gates, multi-qubit systems, entanglement
    photon.py        photon polarization and the Malus cascade
    bb84.py          the BB84 protocol and the QBER
    viz.py           ASCII tables, bar charts, histograms, Bloch spheres
    labkit.py        the Lab harness the labs are written against
    selftest.py      167 self-checks for the library itself
```

It deliberately avoids numpy and Qiskit, so the *maths* labs run in any
Python 3.8+ environment.  The Qiskit-based labs (L14-L17) import Qiskit
directly.

## The `Lab` harness

Every lab is written against `qc101.labkit.Lab`:

```python
from qc101.labkit import Lab

lab = Lab("L01", "Quantum computing versus classical computing")

lab.section("1. A heading")
lab.step("What you are about to do")
lab.note("An aside")
lab.show("some output")
lab.check("a claim that must be true", condition, "detail on failure")
lab.check_close("a numeric claim", got, expected, tol=1e-6)
lab.check_equal("an exact claim", got, expected)

if __name__ == "__main__":
    sys.exit(lab.finish())
```

`lab.finish()` prints the summary and returns the exit code: 0 if every
check passed, 1 otherwise.  That is what `tools/labcheck.py` relies on.


## `qc101.complexnum`

Complex-number arithmetic: addition, multiplication, division, conjugate, modulus, polar form.

### `add(a: 'complex', b: 'complex') -> 'complex'`

Return ``a + b``.

### `conjugate(z: 'complex') -> 'complex'`

Return the complex conjugate ``a - bi``.

### `div(a: 'complex', b: 'complex') -> 'complex'`

Divide ``a / b`` using the complex-conjugate method.

### `div_real(z: 'complex', k: 'float') -> 'complex'`

Divide a complex number by a non-zero real scalar.

### `euler(r: 'float', theta: 'float') -> 'complex'`

Euler's formula: ``r * e^(i*theta) = r*(cos(theta) + i*sin(theta))``.

### `format_list(values: 'Iterable[complex]', places: 'int' = 4) -> 'str'`

Render an iterable of complex numbers as a bracketed list.

### `from_polar(r: 'float', theta: 'float') -> 'complex'`

Convert polar form ``(r, theta)`` back to ``a + bi``.

### `magnitude(z: 'complex') -> 'float'`

Return ``|z| = sqrt(a^2 + b^2)``.

### `mul(a: 'complex', b: 'complex') -> 'complex'`

Multiply two complex numbers, treating ``i`` as an unknown with ``i**2 = -1``.

### `mul_real(k: 'float', z: 'complex') -> 'complex'`

Multiply a complex number by a real scalar: ``k * (a + bi) = ka + kbi``.

### `nth_roots(z: 'complex', n: 'int') -> 'List[complex]'`

Return the ``n`` distinct ``n``-th roots of ``z``.

### `polar_pretty(z: 'complex', places: 'int' = 4) -> 'str'`

Render a complex number in polar form, e.g. ``1.414 e^(i*0.7854)``.

### `power(z: 'complex', exponent: 'float') -> 'complex'`

Complex exponentiation via polar form: ``z**p = r**p * e^(i*p*theta)``.

### `pretty(z: 'complex', places: 'int' = 4) -> 'str'`

Render a complex number in the familiar ``a + bi`` style used in the course.

### `sqrt_i() -> 'Tuple[complex, complex]'`

The two square roots of ``i``:

### `squared_magnitude(z: 'complex') -> 'float'`

Return ``|z|^2 = a^2 + b^2`` (equivalently ``z * conj(z)``).

### `sub(a: 'complex', b: 'complex') -> 'complex'`

Return ``a - b``.

### `to_polar(z: 'complex') -> 'Tuple[float, float]'`

Convert ``a + bi`` to polar form ``(r, theta)``.

## `qc101.boolean`

Boolean algebra: truth tables, expressions, and the classical logic gates.

### `AND(a: 'Bit', b: 'Bit') -> 'Bit'`

AND gate: 1 only when both inputs are 1.

### `NAND(a: 'Bit', b: 'Bit') -> 'Bit'`

NAND gate: NOT(AND(a, b)). A universal gate.

### `NOR(a: 'Bit', b: 'Bit') -> 'Bit'`

NOR gate: NOT(OR(a, b)).

### `NOT(a: 'Bit') -> 'Bit'`

NOT gate: flips the bit.

### `OR(a: 'Bit', b: 'Bit') -> 'Bit'`

OR gate: 1 when at least one input is 1.

### `XOR(a: 'Bit', b: 'Bit') -> 'Bit'`

Exclusive OR: 1 exactly when the two inputs differ.

### `and_from_or_not(a: 'Bit', b: 'Bit') -> 'Bit'`

AND built only from OR and NOT gates.

### `bit_frequency(bits: 'Iterable[Bit]') -> 'float'`

Fraction of 1-bits in a sequence (the mean of a Bernoulli variable).

### `decrypt(cipher: 'Sequence[Bit]', key: 'Sequence[Bit]') -> 'str'`

Decrypt an XOR cipher by XOR-ing with the same shared secret again.

### `encrypt(message: 'str', key: 'Sequence[Bit]') -> 'List[Bit]'`

Encrypt a text message with XOR against a shared secret bit sequence.

### `hamming_distance(a: 'Sequence[Bit]', b: 'Sequence[Bit]') -> 'int'`

Number of positions where two equal-length bit strings differ.

### `nand_to_and(a: 'Bit', b: 'Bit') -> 'Bit'`

AND built from a single NAND gate: ``AND = NOT(NAND)``.

### `nand_to_not(a: 'Bit') -> 'Bit'`

NOT built from a NAND gate: ``NOT A = NAND(A, A)``.

### `nand_to_or(a: 'Bit', b: 'Bit') -> 'Bit'`

OR built from NAND gates: ``OR = NAND(NOT A, NOT B)``.

### `one_time_pad_decrypt(cipher: 'Sequence[Bit]', pad: 'Sequence[Bit]') -> 'str'`

Decrypt a one-time pad message.

### `one_time_pad_encrypt(message: 'str', rng: 'random.Random | None' = None) -> 'Tuple[List[Bit], List[Bit]]'`

Encrypt with a *fresh random* one-time pad.

### `render_truth_table(fn: 'Expr', inputs: 'Sequence[str]' = ('A', 'B'), output: 'str' = 'OUT') -> 'str'`

Render a truth table as a nicely aligned text table.

### `truth_table(fn: 'Expr', inputs: 'Sequence[str]' = ('A', 'B')) -> 'List[Tuple[Tuple[Bit, ...], Bit]]'`

Build the truth table of a boolean function.

### `xor_bitstrings(a: 'Sequence[Bit]', b: 'Sequence[Bit]') -> 'List[Bit]'`

Element-wise XOR of two bit sequences.

## `qc101.probability`

Probability rules, discrete random variables and descriptive statistics.

### `bernoulli(p: 'float' = 0.5, name: 'str' = 'X') -> 'RandomVariable'`

Bernoulli distribution: 0 with probability ``1-p`` and 1 with probability ``p``.

### `coin(p_head: 'float' = 0.5, name: 'str' = 'X') -> 'RandomVariable'`

A coin mapping heads to +1 and tails to -1 (the course convention).

### `correlation(x: 'Sequence[float]', y: 'Sequence[float]') -> 'float'`

Pearson correlation coefficient of two samples, in ``[-1, 1]``.

### `dice(sides: 'int' = 6, loaded: 'Dict[int, float] | None' = None, name: 'str' = 'X') -> 'RandomVariable'`

A die.  ``loaded`` optionally overrides some face probabilities; the remaining probability mass is spread uniformly over the other faces.

### `joint_distribution(rv_x: 'RandomVariable', rv_y: 'RandomVariable', independent: 'bool' = True) -> 'Dict[Tuple[float, float], float]'`

Joint distribution of two random variables.

### `mean(values: 'Sequence[float]') -> 'float'`

Arithmetic mean of a sample.

### `p_and(p_a: 'float', p_b: 'float', p_a_and_b: 'float | None' = None) -> 'float'`

``P(A and B) = P(A) * P(B)`` when A and B are independent.

### `p_conditional(p_a_and_b: 'float', p_a: 'float') -> 'float'`

Conditional probability: ``P(B | A) = P(A and B) / P(A)``.

### `p_from_joint(p_a_and_b: 'float', p_a_and_not_b: 'float') -> 'float'`

Recover ``P(A)`` from a decomposition of the sample space.

### `p_independent(p_a: 'float', p_b: 'float') -> 'Tuple[float, float]'`

For independent events: ``P(A and B) = P(A)*P(B)`` and ``P(A or B) = P(A) + P(B) - P(A)*P(B)``.

### `p_mutually_exclusive(p_a: 'float', p_b: 'float') -> 'Tuple[float, float]'`

For mutually exclusive events: ``P(A and B) = 0`` and ``P(A or B) = P(A) + P(B)``.

### `p_not(p_a: 'float') -> 'float'`

``P(not A) = 1 - P(A)``.

### `p_or(p_a: 'float', p_b: 'float', p_a_and_b: 'float' = 0.0) -> 'float'`

The general addition rule: ``P(A or B) = P(A) + P(B) - P(A and B)``.

### `standard_deviation(values: 'Sequence[float]', ddof: 'int' = 0) -> 'float'`

Standard deviation: ``sqrt(variance)``.

### `variance(values: 'Sequence[float]', ddof: 'int' = 0) -> 'float'`

Variance of a sample.  ``ddof=0`` (default) uses the population formula ``E[(X-mu)^2]``; ``ddof=1`` uses the unbiased sample estimator.

### `class RandomVariable(distribution: 'Dict[float, float]', name: 'str' = 'X')`

A discrete random variable: a mapping from outcome values to probabilities.

- `mean(self) -> 'float'` — Expected value: ``E[X] = sum(x * P(x))``.
- `sample(self, n: 'int' = 1, rng: 'random.Random | None' = None) -> 'List[float]'` — Draw ``n`` samples from the distribution.
- `second_moment(self) -> 'float'` — ``E[X^2]``.
- `standard_deviation(self) -> 'float'` — ``sigma = sqrt(Var[X])``.
- `table(self) -> 'str'` — Render the distribution as an aligned text table.
- `variance(self) -> 'float'` — ``Var[X] = E[(X - mu)^2] = E[X^2] - mu^2``.

## `qc101.linalg`

Matrices and vectors: products, adjoints, inverses, eigenvalues, and the Kronecker product.

### `add(a: 'Matrix', b: 'Matrix') -> 'Matrix'`

Element-wise addition.

### `adjoint(m: 'Matrix') -> 'Matrix'`

The adjoint (dagger): transpose of the complex conjugate.

### `conjugate(m: 'Matrix') -> 'Matrix'`

Complex-conjugate every element.

### `determinant(m: 'Matrix') -> 'complex'`

Determinant via cofactor expansion (fine for the small matrices used here).

### `dims(m: 'Matrix') -> 'Tuple[int, int]'`

Return ``(rows, cols)`` of a matrix.

### `eigenpairs_2x2(m: 'Matrix') -> 'List[Tuple[complex, Vector]]'`

Return ``[(eigenvalue, eigenvector), ...]`` for a 2x2 matrix.

### `eigenvalues_2x2(m: 'Matrix') -> 'List[complex]'`

Eigenvalues of a 2x2 matrix from the characteristic polynomial ``lambda^2 - tr(A) lambda + det(A) = 0``.

### `format_matrix(m: 'Matrix', fmt: 'str' = '{:>8.3f}') -> 'str'`

Render a matrix as an aligned text table (real and imaginary parts).

### `hermitian_eigenvalues(m: 'Matrix', max_sweeps: 'int' = 100) -> 'List[float]'`

Eigenvalues of a **Hermitian** matrix (A = A^dagger), returned as real numbers sorted in increasing order.

### `identity(n: 'int') -> 'Matrix'`

The n x n identity matrix.

### `inner_product(a: 'Vector', b: 'Vector') -> 'complex'`

The conjugate inner product ``<a|b> = sum_i conj(a_i) * b_i``.

### `inverse(m: 'Matrix') -> 'Matrix'`

Matrix inverse via Gauss-Jordan elimination with partial pivoting.

### `is_hermitian(m: 'Matrix', tol: 'float' = 1e-09) -> 'bool'`

True when ``A^dagger = A``.

### `is_identity(m: 'Matrix', tol: 'float' = 1e-09) -> 'bool'`

True when the matrix equals the identity matrix.

### `is_square(m: 'Matrix') -> 'bool'`

True when the matrix has as many rows as columns.

### `is_unitary(m: 'Matrix', tol: 'float' = 1e-09) -> 'bool'`

True when ``A^dagger A = I``.

### `jacobi_eigenvalues_real(a: 'List[List[float]]', max_sweeps: 'int' = 100, tol: 'float' = 1e-14) -> 'List[float]'`

Eigenvalues of a **real symmetric** matrix, by the Jacobi method.

### `kron(a: 'Matrix', b: 'Matrix') -> 'Matrix'`

Kronecker (tensor) product -- the operation that composes qubit states.

### `matrix_equals(a: 'Matrix', b: 'Matrix', tol: 'float' = 1e-09) -> 'bool'`

Element-wise comparison with a tolerance.

### `mul(a: 'Matrix', b: 'Matrix') -> 'Matrix'`

Matrix multiplication, row-by-column.

### `outer_product(a: 'Vector', b: 'Vector') -> 'Matrix'`

The outer product ``|a><b|`` as a matrix.

### `power_iteration(m: 'Matrix', v0: 'Vector | None' = None, iterations: 'int' = 500, tol: 'float' = 1e-12) -> 'Tuple[complex, Vector]'`

Dominant eigenpair of a matrix by power iteration.

### `rref(m: 'Matrix') -> 'Matrix'`

Reduced row echelon form (used for linear-dependency checks).

### `scale(k: 'complex', m: 'Matrix') -> 'Matrix'`

Multiply every element of the matrix by the scalar ``k``.

### `sub(a: 'Matrix', b: 'Matrix') -> 'Matrix'`

Element-wise subtraction.

### `transpose(m: 'Matrix') -> 'Matrix'`

Interchange rows and columns.

### `zeros(rows: 'int', cols: 'int') -> 'Matrix'`

A rows x cols matrix of zeros.

## `qc101.quantum`

The quantum model: qubit states, the standard gates, multi-qubit systems and entanglement.

### `apply_gate(sv: 'StateVector', gate: 'Matrix', qubit: 'int') -> 'StateVector'`

Functional form of ``StateVector.apply_single``.

### `bell_state() -> 'StateVector'`

The Bell state ``(|00> + |11>)/sqrt(2)`` -- a maximally entangled pair.

### `bra(bitstring: 'str') -> 'str'`

Render a bra: ``bra("10")`` -> ``'<10|'``.

### `braket(left: 'str', right: 'str') -> 'str'`

Render a matrix element: ``braket("0", "1")`` -> ``'<0|1>'``.

### `entanglement_entropy(sv: 'StateVector') -> 'float'`

Von Neumann entropy of the first half of the system.

### `ghz_state(n_qubits: 'int' = 3) -> 'StateVector'`

The GHZ state ``(|00...0> + |11...1>)/sqrt(2)``.

### `is_entangled(sv: 'StateVector') -> 'bool'`

True when the state cannot be written as a product of two subsystems.

### `ket(bitstring: 'str') -> 'str'`

Render a basis state in Dirac notation: ``ket("10")`` -> ``'|10>'``.

### `class StateVector(amplitudes: 'Sequence[complex]')`

A quantum state of ``n`` qubits, stored as a list of ``2**n`` amplitudes.

- `apply_cnot(self, control: 'int', target: 'int') -> "'StateVector'"` — Apply a CNOT gate.
- `apply_single(self, gate: 'Matrix', qubit: 'int') -> "'StateVector'"` — Apply a single-qubit gate to ``qubit``.
- `apply_three(self, gate: 'Matrix', q1: 'int', q2: 'int', q3: 'int') -> "'StateVector'"` — Apply a three-qubit gate acting on ``(q1, q2, q3)`` in that order.
- `apply_toffoli(self, control1: 'int', control2: 'int', target: 'int') -> "'StateVector'"` — Apply a CCNOT (Toffoli) gate.
- `apply_two(self, gate: 'Matrix', control: 'int', target: 'int') -> "'StateVector'"` — Apply a two-qubit gate with the given control and target qubits.
- `basis_labels(self) -> 'List[str]'` — The bit string label of each basis state, in state-vector order.
- `copy(self) -> "'StateVector'"` — A deep copy of this state.
- `density_matrix(self) -> 'Matrix'` — The density matrix ``|psi><psi|`` of the pure state.
- `entropy(self) -> 'float'` — The von Neumann entropy of the reduced state (0 for a product state).
- `from_basis(index: 'int', n_qubits: 'int') -> "'StateVector'"` — A basis state given by its integer index.
- `from_bitstring(bits: 'str') -> "'StateVector'"` — A basis state given by a bit string, e.g. ``"10"``.
- `histogram(self, rng: 'random.Random | None' = None, shots: 'int' = 1000) -> 'Dict[str, int]'` — Sample the state ``shots`` times and return a bitstring histogram.
- `is_normalized(self, tol: 'float' = 1e-09) -> 'bool'` — True when the total probability is 1.
- `measure(self, rng: 'random.Random | None' = None) -> "Tuple[int, 'StateVector']"` — Measure the whole system.
- `measure_qubit(self, qubit: 'int', rng: 'random.Random | None' = None) -> "Tuple[int, 'StateVector']"` — Measure a *single* qubit (and collapse only that qubit's dimension).
- `one(n_qubits: 'int' = 1) -> "'StateVector'"` — The state with the *last* qubit set to one: ``|00...1>``.
- `probabilities(self) -> 'List[float]'` — Measurement probabilities: ``|amplitude|^2`` for each basis state.
- `probability_table(self) -> 'str'` — A text table of basis states and their probabilities.
- `random(n_qubits: 'int' = 1, rng: 'random.Random | None' = None) -> "'StateVector'"` — A uniformly random pure state (Haar-random via normalised Gaussians).
- `to_dirac(self, threshold: 'float' = 1e-06) -> 'str'` — Render the state in Dirac notation, dropping negligible terms.
- `zero(n_qubits: 'int' = 1) -> "'StateVector'"` — The all-zeros state ``|00...0>``.

## `qc101.photon`

Photon polarization: Malus's law, the polarization cascade and single-photon states.

### `filter_cascade(photon_angle: 'float', filter_angles: 'Sequence[float]', shots: 'int' = 2000, rng: 'random.Random | None' = None) -> 'FilterCascadeResult'`

Run photons through a sequence of polarizers, in the **Malus's law (polarizer) model**.

### `malus_transmission(theta_in: 'float', theta_filter: 'float') -> 'float'`

Malus's law: the probability that a photon with polarization ``theta_in`` passes through a filter at ``theta_filter``.

### `measurement_cascade(photon_angle: 'float', filter_angles: 'Sequence[float]', shots: 'int' = 2000, rng: 'random.Random | None' = None) -> 'FilterCascadeResult'`

The same cascade, but measured with the **qubit model** used in the course: each filter measures the photon in the {aligned, anti-aligned} basis, and afterwards the photon's state is either aligned with that filter or exactly 90 degrees from it.

### `polarization_basis(theta: 'float') -> 'str'`

Classify a polarization angle into one of four BB84 basis states.

### `class EntangledPhotonMeasurement(p00: 'float', p01: 'float', p10: 'float', p11: 'float', rng: 'random.Random | None' = None)`

A pair of photons described by the four amplitudes ``(p00, p01, p10, p11)``.

- `perform_measurement(self) -> 'str'` — Perform one joint measurement.
- `report_measurement_probability(self) -> 'str'` — Report the four joint outcome probabilities plus the conditional probabilities ``P(photon1 | photon2)`` that expose entanglement.
- `set_independent_photon_angles(self, angle1: 'float', angle2: 'float') -> 'None'` — Model two *independent* (unentangled) photons with these angles.
- `set_measurement_angles(self, angle1: 'float', angle2: 'float') -> 'None'` — Set the orientation of the two measurement filters.

### `class FilterCascadeResult(stage_transmission: 'List[float]', cumulative_transmission: 'List[float]', final_angle: 'float')`

The outcome of pushing photons through a sequence of polarizers.


### `class PhotonPolarizationMeasurement(angle: 'float' = 90.0, rng: 'random.Random | None' = None)`

A single photon with a known polarization, measured by filters.

- `measure_polarization(self, angle: 'float') -> 'bool'` — Measure the photon with a polarizer at ``angle``.
- `measure_repeated(self, angle: 'float', n: 'int' = 1000) -> 'Dict[str, float]'` — Measure the *same* photon ``n`` times with the same filter.

## `qc101.bb84`

The BB84 key-distribution protocol and the quantum bit error rate.

### `basis_angle(basis: 'int', bit: 'int') -> 'float'`

The polarization angle that encodes ``bit`` in ``basis``.

### `encode_angle(bit: 'int', basis: 'int') -> 'float'`

Alias of :func:`basis_angle` -- the angle Alice actually sends.

### `run_bb84(rounds: 'int' = 200, eve: 'bool' = False, eve_intercept_probability: 'float' = 1.0, eve_resend_mode: 'str' = 'same_basis', seed: 'Optional[int]' = None, verbose: 'bool' = False) -> 'BB84Result'`

Run the BB84 protocol end to end.

### `class BB84Result(rounds: 'List[Round]' = <factory>, alice_key: 'List[int]' = <factory>, bob_key: 'List[int]' = <factory>, eve_present: 'bool' = False, eve_intercepts: 'int' = 0) -> None`

The outcome of a full BB84 run.

- `summary(self) -> 'str'` — A human-readable report of the run.

### `class Basis()`

The two BB84 bases.


### `class Round(index: 'int', bit: 'int', alice_basis: 'int', angle: 'float', bob_basis: 'int', bob_bit: 'int', eve_present: 'bool' = False, eve_basis: 'Optional[int]' = None, eve_bit: 'Optional[int]' = None, matched_basis: 'bool' = False, sifted: 'bool' = False) -> None`

One round of the protocol, with every random choice recorded.

- `describe(self) -> 'str'`

## `qc101.viz`

Terminal rendering helpers: tables, bar charts, histograms and ASCII Bloch spheres.

### `bar_chart(data: 'Dict[str, float]', width: 'int' = 40, max_value: 'float | None' = None, title: 'str' = '') -> 'str'`

Render a horizontal bar chart with Unicode block characters.

### `bloch_sphere_ascii(x: 'float', y: 'float', z: 'float', size: 'int' = 13) -> 'str'`

Render a Bloch sphere with the state as a marker, using ASCII art.

### `boxed(title: 'str', body: 'str' = '', width: 'int' = 68) -> 'str'`

Draw a titled box around ``body``.

### `histogram(counts: 'Dict[str, int]', width: 'int' = 40, title: 'str' = 'Counts') -> 'str'`

Render a bar chart of measurement counts, normalised to the largest.

### `kv_table(data: 'Dict[str, object]', key_width: 'int' = 28) -> 'str'`

Render a dictionary as an aligned ``key : value`` block.

### `qubit_bloch(alpha: 'float', beta: 'float') -> 'Tuple[float, float, float]'`

Convert the amplitudes ``alpha`` (for |0>) and ``beta`` (for |1>) into Bloch-sphere coordinates ``(x, y, z)``.

### `table(headers: 'Sequence[str]', rows: 'Iterable[Sequence[object]]') -> 'str'`

Render a simple aligned text table.

