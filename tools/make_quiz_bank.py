#!/usr/bin/env python3
"""Generate the QC101 quiz question bank (one JSON file per section)."""

import json
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "quizzes" / "questions"
OUT.mkdir(parents=True, exist_ok=True)


def q(qid, section, qtype, question, choices=None, answer=None,
      explanation="", difficulty=1, tolerance=None):
    entry = {
        "id": qid,
        "section": section,
        "type": qtype,
        "question": question,
        "choices": choices or [],
        "answer": answer,
        "explanation": explanation,
        "difficulty": difficulty,
    }
    if tolerance is not None:
        entry["tolerance"] = tolerance
    return entry


SECTIONS = {}

# ---------------------------------------------------------------- section 1
SECTIONS[1] = [
    q("s01-q01", 1, "single",
      "What is the central promise of a quantum computer?",
      ["It runs every possible program at once",
       "It computes some problems exponentially faster using superposition and entanglement",
       "It stores more bits than a classical computer",
       "It never makes mistakes"],
      1,
      "The speed-up comes from superposition and entanglement, not from "
      "parallelism or storage."),
    q("s01-q02", 1, "truefalse",
      "A quantum computer replaces the classical computer for everyday tasks.",
      None, "false",
      "Quantum computers are accelerators: they are meant to be used for the "
      "few problems where they win, and to be called from a classical program."),
    q("s01-q03", 1, "single",
      "Which of these is a problem where a quantum computer is NOT expected to help?",
      ["Factoring a large integer", "Simulating a quantum system",
       "Sorting a list of a million names", "Searching an unstructured space"],
      2,
      "Sorting is an excellent classical algorithm; a quantum computer offers "
      "nothing here."),
    q("s01-q04", 1, "multi",
      "Which of the course's 17 sections deals with machine learning?",
      ["Section 16", "Section 17", "Section 4", "Section 12"],
      [0, 1],
      "Sections 16 (classical ML foundation) and 17 (quantum ML with Qiskit)."),
    q("s01-q05", 1, "single",
      "Which programming languages does the course use?",
      ["Python, Q# and Qiskit", "Python and Java", "C++ and Rust", "MATLAB only"],
      0,
      "Microsoft Q# for the Q# section, and Python with Qiskit for the IBM "
      "sections."),
]

# ---------------------------------------------------------------- section 2
SECTIONS[2] = [
    q("s02-q01", 2, "single",
      "According to Malus's law, what is the probability that a photon "
      "polarized at angle theta_p passes a polarizer at angle theta_f?",
      ["cos(theta_p - theta_f)", "cos^2(theta_p - theta_f)", "sin^2(theta_p - theta_f)",
       "1/2 always"],
      1,
      "P(pass) = cos^2(theta_p - theta_f).  At the same angle it is 1, at 90 "
      "degrees it is 0."),
    q("s02-q02", 2, "number",
      "A photon is polarized at 0 degrees and hits a polarizer at 60 "
      "degrees.  What is the probability it passes? (cos^2 of the angle, "
      "to 4 decimals)",
      None, 0.25, "cos^2(60 degrees) = 0.5^2 = 0.25", 2, tolerance=1e-4),
    q("s02-q03", 2, "single",
      "What happens when you measure the polarization of a photon that is in "
      "a superposition of two polarizations?",
      ["You always get the first one", "You always get the second one",
       "You get one of them at random, with probabilities given by the "
       "amplitudes squared", "You get both at once"],
      2,
      "The Born rule: the probability of an outcome is the squared modulus of "
      "its amplitude."),
    q("s02-q04", 2, "truefalse",
      "A classical wave and a quantum photon can both be put into a "
      "superposition, but only the quantum one collapses to a single definite "
      "polarization on measurement.",
      None, "true",
      "This is the 'quantum' part of the photon-polarization story: the "
      "measurement is irreversible."),
    q("s02-q05", 2, "multi",
      "Which angles are orthogonal (mutually exclusive) polarizations?",
      ["0 degrees and 90 degrees", "0 degrees and 180 degrees",
       "45 degrees and 135 degrees", "0 degrees and 45 degrees"],
      [0, 2],
      "Two polarizations are orthogonal when they differ by 90 degrees.  0 and "
      "180 are the same polarization, not orthogonal."),
    q("s02-q06", 2, "single",
      "A photon passes a polarizer at 0 degrees, then a second polarizer at "
      "90 degrees.  What is the probability of passing both?",
      ["1", "1/2", "0", "1/4"],
      2,
      "The first polarizer projects the photon onto the 0-degree direction; "
      "the 90-degree polarizer is orthogonal to that, so the probability is 0."),
]

# ---------------------------------------------------------------- section 3
SECTIONS[3] = [
    q("s03-q01", 3, "single", "What is i^2?", ["-1", "1", "i", "-i"], 0,
      "i is the square root of -1, so i^2 = -1."),
    q("s03-q02", 3, "number",
      "What is the modulus squared of the complex number 3 + 4i?",
      None, 25, "|3 + 4i|^2 = 3^2 + 4^2 = 25", 1, tolerance=1e-9),
    q("s03-q03", 3, "single",
      "What is (3 + 4i) * (3 - 4i)?",
      ["25", "9 - 16i", "-7 + 24i", "-25"], 0,
      "A complex number times its conjugate is its modulus squared: 25."),
    q("s03-q04", 3, "truefalse",
      "For two independent events A and B, P(A and B) = P(A) * P(B).",
      None, "true",
      "Independence is exactly the statement that the joint probability "
      "factorizes."),
    q("s03-q05", 3, "multi",
      "Which of these are axioms of Boolean algebra?",
      ["Commutativity of AND", "Associativity of AND", "Excluded middle",
       "Non-contradiction"],
      [0, 1, 2, 3],
      "Boolean algebra satisfies the classical logic laws including excluded "
      "middle and non-contradiction."),
    q("s03-q06", 3, "single",
      "A matrix A is unitary when...",
      ["A^T = A", "A^dagger A = I", "det(A) = 1", "A has real entries"],
      1,
      "Unitary means the conjugate transpose is the inverse: A^dagger A = I."),
    q("s03-q07", 3, "single",
      "What is the probability of a quantum measurement outcome given the "
      "amplitude of that outcome?",
      ["the amplitude itself", "the amplitude squared", "the absolute value",
       "the amplitude cubed"],
      1,
      "The Born rule: P = |amplitude|^2."),
]

# ---------------------------------------------------------------- section 4
SECTIONS[4] = [
    q("s04-q01", 4, "single",
      "In BB84, how many bases are there and what are they called?",
      ["Two: rectilinear and diagonal", "Three: H, V and D",
       "One: only vertical", "Four: 0, 45, 90 and 135 degrees"],
      0,
      "BB84 uses two bases: rectilinear (0/90) and diagonal (45/135)."),
    q("s04-q02", 4, "single",
      "What is the step called where Alice and Bob publicly compare their "
      "bases and keep only the rounds where they matched?",
      ["Sifting", "Distillation", "Amplification", "Authentication"],
      0,
      "Sifting.  The bases must be revealed publicly, but the bit values "
      "must not be."),
    q("s04-q03", 4, "truefalse",
      "In an ideal BB84 run with no eavesdropper, the quantum bit error rate "
      "is zero.",
      None, "true",
      "With matching bases the outcome is always correct, so the ideal QBER "
      "is 0%."),
    q("s04-q04", 4, "single",
      "About what quantum bit error rate indicates an eavesdropper in a "
      "one-way BB84 system?",
      ["11%", "50%", "0%", "90%"],
      0,
      "Around 11% is the standard threshold: roughly 25% of the sifted bits "
      "are exposed and half of those are corrupted."),
    q("s04-q05", 4, "multi",
      "Which are genuine requirements for a one-time pad?",
      ["The key must be used only once", "The key must be as long as the message",
       "The key must be perfectly random", "The key must be shared publicly"],
      [0, 1, 2],
      "A one-time pad needs a one-time, uniformly random, equal-length key -- "
      "and it must be shared secretly, not publicly."),
    q("s04-q06", 4, "single",
      "If Eve intercepts every photon, measures it in a basis of her own "
      "choosing and resends it in that same basis, about what fraction of "
      "the sifted key bits does she get wrong?",
      ["25%", "0%", "50%", "75%"],
      0,
      "Half the time she picks Alice's basis and causes no error; half the "
      "time she picks the other one and Bob's reading is random.  "
      "Q = 1/2 * 0 + 1/2 * 1/2 = 25%."),
    q("s04-q07", 4, "single",
      "Eve intercepts, measures, and resends in a *random* basis instead of "
      "the one she measured in.  What is the resulting QBER?",
      ["25%", "37.5%", "50%", "12.5%"],
      1,
      "1/4 of the rounds are perfect, and the other 3/4 have a 50% error "
      "rate: 3/8 = 37.5%."),
]

# ---------------------------------------------------------------- section 5
SECTIONS[5] = [
    q("s05-q01", 5, "single",
      "What is the state of a photon polarized at 45 degrees, written in the "
      "horizontal/vertical basis?",
      ["|0>", "|1>", "(|0> + |1>)/sqrt(2)", "(|0> - |1>)/sqrt(2)"],
      2,
      "45 degrees is the 'plus' superposition of the two polarizations."),
    q("s05-q02", 5, "single",
      "Why does a state vector have to be normalized?",
      ["So the computer can store it faster",
       "So that the squared amplitudes sum to 1, which is the total probability",
       "Because the Born rule needs a complex number",
       "So that measurements are equally likely"],
      1,
      "Normalization is what makes the probabilities add up to one."),
    q("s05-q03", 5, "truefalse",
      "The evolution of a quantum state between measurements is deterministic "
      "and reversible.",
      None, "true",
      "Unitary evolution is deterministic and reversible; only measurement is "
      "irreversible."),
    q("s05-q04", 5, "single",
      "Which of these is a valid probability distribution over two outcomes?",
      ["0.3, 0.3", "0.6, 0.6", "0.7, 0.3", "1.2, -0.2"],
      2,
      "The two numbers must be between 0 and 1 and must sum to 1."),
    q("s05-q05", 5, "multi",
      "Which statements about measurement are true?",
      ["Measurement is irreversible", "Measurement is probabilistic",
       "Measurement can be undone by applying the same gate again",
       "The state after measurement is an eigenvector of the measurement operator"],
      [0, 1, 3],
      "Once a measurement has collapsed the state you cannot get the original "
      "superposition back by applying a gate."),
    q("s05-q06", 5, "single",
      "Von Neumann's model of a measurement has two stages.  What are they?",
      ["Preparation and detection", "Evolution and collapse",
       "Encoding and decoding", "Rotation and reflection"],
      1,
      "Unitary (Schrodinger) evolution, then a non-unitary projection -- the "
      "collapse."),
]

# ---------------------------------------------------------------- section 6
SECTIONS[6] = [
    q("s06-q01", 6, "single",
      "What physical system is the qubit of this course built from?",
      ["A photon's polarization", "An electron's spin", "A charged particle in a box",
       "A superconducting flux"],
      1,
      "The course models spin-1/2 particles: two states, up and down, with "
      "the same mathematical structure as photon polarization."),
    q("s06-q02", 6, "single",
      "How many states does a qubit have?",
      ["One", "Two", "Infinitely many", "Three"],
      1,
      "Two basis states, |0> and |1>, but a continuum of superpositions of them."),
    q("s06-q03", 6, "truefalse",
      "A qubit in the state |0> can also be in the state (|0> + |1>)/sqrt(2) "
      "if you rotate it first.",
      None, "true",
      "Rotations move a qubit around the Bloch sphere; every pure state is "
      "reachable from |0>."),
    q("s06-q04", 6, "single",
      "What does 'spin up' correspond to in the two-state system?",
      ["|0>", "|1>", "|+>", "the Bloch sphere"],
      0,
      "By convention spin up is |0> and spin down is |1>."),
    q("s06-q05", 6, "multi",
      "Which experiments are done with spin states in the course?",
      ["Stern-Gerlach", "Double-slit", "Mach-Zehnder", "Bell tests"],
      [0, 1, 2, 3],
      "The course walks through the Stern-Gerlach experiment, the double-slit "
      "and the Mach-Zehnder interferometer, and then the Bell experiments."),
    q("s06-q06", 6, "single",
      "Why is the spin-1/2 system a good model for a qubit?",
      ["Because it has exactly two measurable components",
       "Because spin is a classical quantity",
         "Because spin can be measured without disturbing it",
       "Because spin states are continuous"],
      0,
      "Two measurable components with the right algebraic structure is all a "
      "qubit needs."),
]

# ---------------------------------------------------------------- section 7
SECTIONS[7] = [
    q("s07-q01", 7, "single",
      "What is the column-matrix representation of a pure qubit state?",
      ["A 1x2 column vector of complex amplitudes", "A 2x2 matrix",
       "A 4-vector", "A scalar"],
      0,
      "alpha|0> + beta|1> becomes the column vector (alpha, beta)^T."),
    q("s07-q02", 7, "number",
      "The state (|0> + i|1>)/sqrt(2).  What is the probability of "
      "measuring |0>?",
      None, 0.5, "The amplitude of |0> is 1/sqrt(2), and |1/sqrt(2)|^2 = 1/2.",
      1, tolerance=1e-9),
    q("s07-q03", 7, "single",
      "What is the inner product of two identical normalized states?",
      ["0", "1", "-1", "their modulus squared"],
      1,
      "<psi|psi> = 1 for a normalized state."),
    q("s07-q04", 7, "truefalse",
      "A qubit state vector is a column vector and a gate acts on the left.",
      None, "true",
      "psi' = U psi, with U a 2x2 unitary matrix on the left of the column "
      "vector."),
    q("s07-q05", 7, "multi",
      "Which of these matrices are the Pauli gates?",
      ["X = [[0,1],[1,0]]", "Y = [[0,-i],[i,0]]", "Z = [[1,0],[0,-1]]",
       "H = [[1,0],[0,1]]"],
      [0, 1, 2],
      "H is the Hadamard gate, not a Pauli gate."),
    q("s07-q06", 7, "single",
      "The Bloch sphere: what do the poles represent?",
      ["|0> and |1>", "|+> and |->", "the equator", "the measurement basis"],
      0,
      "The poles are the computational basis states; the equator is the "
      "set of equal-probability superpositions."),
]

# ---------------------------------------------------------------- section 8
SECTIONS[8] = [
    q("s08-q01", 8, "single",
      "Why is a quantum gate reversible?",
      ["Because gates are made of mirrors", "Because the gate matrix is unitary",
       "Because every gate has an inverse button", "Because measurement is reversible"],
      1,
      "A unitary matrix is invertible, with inverse equal to its adjoint."),
    q("s08-q02", 8, "multi",
      "Which operations are irreversible?",
      ["Measurement", "Resetting a qubit to |0>", "Applying an X gate",
       "Applying a CNOT"],
      [0, 1],
      "Reset and measurement destroy information; X and CNOT are unitary and "
      "therefore reversible."),
    q("s08-q03", 8, "truefalse",
      "Two different quantum states can have the same measurement statistics "
      "in one basis.",
      None, "true",
      "|+> and |-> both give 50/50 in the Z basis but are perfectly "
      "distinguishable in the X basis."),
    q("s08-q04", 8, "single",
      "What is the no-cloning theorem?",
      ["You cannot copy an unknown quantum state exactly",
       "You cannot delete a quantum state",
       "You cannot send a qubit faster than light",
       "You cannot measure a qubit"],
      0,
      "No-cloning: an arbitrary unknown quantum state cannot be copied "
      "perfectly.  Classical bits have no such restriction."),
    q("s08-q05", 8, "single",
      "The adjoint of a matrix A is written A^dagger.  How is it defined?",
      ["The transpose", "The conjugate transpose", "The inverse",
       "The element-wise square"],
      1,
      "A^dagger = (A*)^T, the conjugate transpose."),
    q("s08-q06", 8, "single",
      "If a gate's matrix is Hermitian, then...",
      ["it is its own inverse", "it is the identity", "it is not reversible",
       "it measures the qubit"],
      0,
      "For a Hermitian unitary, A^dagger = A and A^dagger A = I, so A^2 = I."),
]

# ---------------------------------------------------------------- section 9
SECTIONS[9] = [
    q("s09-q01", 9, "single",
      "How many basis states does a system of 3 qubits have?",
      ["3", "6", "8", "9"],
      2,
      "2^3 = 8 basis states."),
    q("s09-q02", 9, "single",
      "What is the Kronecker product of two qubits used for?",
      ["Adding their amplitudes", "Building the joint state of the two-qubit system",
       "Measuring them", "Resetting them"],
      1,
      "|psi> tensor |phi> is the state of the combined system."),
    q("s09-q03", 9, "truefalse",
      "The order of the qubits matters: |0> tensor |1> is not the same state "
      "as |1> tensor |0>.",
      None, "true",
      "The two live in different basis states of the 2-qubit space."),
    q("s09-q04", 9, "single",
      "A CNOT with the first qubit as control and the second as target does "
      "what?",
      ["Flips the target if the control is |1>",
       "Flips the control if the target is |1>",
       "Swaps the two qubits", "Measures both qubits"],
      0,
      "The control is untouched; the target is flipped only when the control "
      "is |1>."),
    q("s09-q05", 9, "multi",
      "Which two-qubit gates are entangling?",
      ["CNOT", "CZ", "Hadamard on one qubit", "SWAP"],
      [0, 1, 3],
      "A SWAP can be built from three CNOTs, so it entangles too.  A single "
      "Hadamard on one qubit does not."),
    q("s09-q06", 9, "single",
      "How many classical bits does a 3-qubit register have in the usual "
      "measurement setup?",
      ["3", "8", "1", "6"],
      0,
      "One classical bit per qubit: 3 qubits need 3 classical bits."),
]

# ---------------------------------------------------------------- section 10
SECTIONS[10] = [
    q("s10-q01", 10, "single",
      "What is the Bell state (|00> + |11>)/sqrt(2) called?",
      ["Phi+", "Psi+", "Phi-", "Psi-"],
      0,
      "|Phi+> = (|00> + |11>)/sqrt(2) is the 'plus' phase state."),
    q("s10-q02", 10, "truefalse",
      "Measuring one qubit of a Bell pair instantly determines the state of "
      "the other -- but that does not allow faster-than-light messaging.",
      None, "true",
      "The correlation is real, but the outcome on the receiving side is "
      "completely random."),
    q("s10-q03", 10, "single",
      "How much entanglement entropy does a Bell pair have?",
      ["0 bits", "1 bit", "2 bits", "1/2 bit"],
      1,
      "The reduced state of one qubit is maximally mixed, so the entropy is "
      "one bit."),
    q("s10-q04", 10, "multi",
      "Which statements about entanglement are true?",
      ["A product state is not entangled",
       "Entanglement cannot be created by a local unitary alone",
       "Entanglement can be destroyed by tracing out one qubit",
       "A Bell pair can be cloned"],
      [0, 1, 2],
      "No-cloning means you cannot duplicate the pair and keep both copies "
      "entangled."),
    q("s10-q05", 10, "single",
      "The CHSH parameter S for a Bell pair is...",
      ["1", "2", "2*sqrt(2)", "4"],
      2,
      "Classical correlations reach S = 2; quantum correlations reach "
      "2*sqrt(2) ~ 2.83."),
    q("s10-q06", 10, "single",
      "What is the maximum entanglement entropy of a 4-qubit maximally "
      "entangled state?",
      ["1 bit", "2 bits", "4 bits", "8 bits"],
      1,
      "n/2 bits: a maximally entangled n-qubit state carries n/2 bits."),
]

# ---------------------------------------------------------------- section 11
SECTIONS[11] = [
    q("s11-q01", 11, "single",
      "What does the entangled-photon simulator keep track of?",
      ["A single photon's angle", "The four joint probabilities (00, 01, 10, 11)",
       "The polarization of one photon only", "A classical wave"],
      1,
      "The simulator evolves the state (p00, p01, p10, p11) of the pair."),
    q("s11-q02", 11, "truefalse",
      "In the entangled simulator, measuring the two photons in the same "
      "basis always gives matching or anti-matching outcomes, never "
      "mismatched ones.",
      None, "true",
      "That perfect correlation is the signature of the entangled state."),
    q("s11-q03", 11, "single",
      "If the two photons of an entangled pair are measured in *different* "
      "bases, the outcomes are...",
      ["perfectly correlated", "uncorrelated -- each is random",
       "always both zero", "always both one"],
      1,
      "Different bases break the correlation -- which is exactly what makes "
      "the pair useless for communication."),
    q("s11-q04", 11, "multi",
      "Which of these does the course's simulator demonstrate?",
      ["Malus's law for a single photon", "Collapse after measurement",
       "The no-cloning theorem", "The CHSH inequality"],
      [0, 1, 3],
      "No-cloning is discussed but the simulators demonstrate the rest."),
    q("s11-q05", 11, "single",
      "How does the course's cross-check confirm that the photon simulator "
      "and the qubit model agree?",
      ["They produce the same probability tables",
       "They run the same code", "They use the same random numbers",
       "They do not cross-check"],
      0,
      "The two independent models are compared numerically and must match."),
]

# ---------------------------------------------------------------- section 12
SECTIONS[12] = [
    q("s12-q01", 12, "single",
      "What are the three stages of a quantum program?",
      ["Init, compute, read out", "Load, save, print", "Compile, link, run",
       "Setup, loop, exit"],
      0,
      "Irreversible initialization, reversible gates, irreversible "
      "measurement."),
    q("s12-q02", 12, "single",
      "Why does a state-vector simulator need memory proportional to 2^n?",
      ["It stores one number per basis state", "It stores a full matrix",
       "It stores the gates", "It stores the shots"],
      0,
      "There are 2^n basis states and each needs a complex amplitude."),
    q("s12-q03", 12, "truefalse",
      "A state-vector simulator and a real quantum computer return the same "
      "kind of answer.",
      None, "false",
      "The simulator returns exact amplitudes; the hardware returns counts "
      "from sampled measurements."),
    q("s12-q04", 12, "single",
      "What does 'compiling' a circuit into a single unitary matrix give you?",
      ["The exact output state for any input", "A faster circuit",
       "A measurement", "A classical program"],
      0,
      "The product of the gate matrices is the circuit's unitary, so you can "
      "apply it to any input state exactly."),
    q("s12-q05", 12, "multi",
      "Which are quantum gates that are their own inverses?",
      ["H", "X", "Z", "S"],
      [0, 1, 2],
      "S is not: S^dagger = S^3, so S applied four times is the identity, not "
      "twice."),
    q("s12-q06", 12, "single",
      "How many gate applications does a Toffoli (CCNOT) gate need in a "
      "two-level quantum computer?",
      ["1", "2", "6", "It cannot be implemented"],
      2,
      "A Toffoli needs at least 6 two-qubit gates in the standard "
      "construction."),
]

# ---------------------------------------------------------------- section 13
SECTIONS[13] = [
    q("s13-q01", 13, "single",
      "In Microsoft Q#, how are the qubits of a register ordered when you "
      "print a result?",
      ["Left to right", "Right to left", "In random order", "By index"],
      1,
      "Q# prints (q2, q1, q0) while the state vector is written "
      "(q0, q1, q2) -- the classic ordering trap."),
    q("s13-q02", 13, "truefalse",
      "A Q# operation's result array is in the same order as the qubits in "
      "the register.",
      None, "false",
      "The result array is reversed relative to the qubit order -- the "
      "course's 'Verifying Results' article is about exactly this."),
    q("s13-q02b", 13, "single",
      "What is the Q# equivalent of a measurement followed by a conditional "
      "X gate?",
      ["M followed by an if with X inside",
       "Reset followed by H", "H followed by M", "A message pass"],
      0,
      "That is exactly the 'Set' operation from the course's QB4 program."),
    q("s13-q03", 13, "multi",
      "Which of these are genuine Q# language features?",
      ["let bindings", "mutable variables", "message passing between qubits",
       "the Q# keyword 'mutable'"],
      [0, 2, 3],
      "Q# variables are immutable by default; 'mutable' is introduced "
      "explicitly."),
    q("s13-q04", 13, "single",
      "Why does the course say the Q# simulator is worth learning before "
      "Qiskit?",
      ["Because Q# is faster", "Because it isolates the quantum ideas from the "
       "programming-language noise", "Because Qiskit is deprecated",
       "Because Q# runs on IBM hardware"],
      1,
      "Q# has no classical control flow to hide behind, so the quantum "
      "structure is visible."),
    q("s13-q05", 13, "single",
      "In the course's QB4 program, how many qubits are used?",
      ["2", "3", "4", "8"],
      2,
      "Four qubits, with histograms over all 16 bit strings."),
]

# ---------------------------------------------------------------- section 14
SECTIONS[14] = [
    q("s14-q01", 14, "single",
      "Where do you run a quantum circuit on real IBM hardware?",
      ["IBM Quantum Experience, at quantum-computing.ibm.com",
       "At quantum-computing.ibm.com only", "On a local desktop",
       "Inside the Qiskit Python package"],
      0,
      "The course's 'IBM Quantum Note' points at the current URL."),
    q("s14-q02", 14, "truefalse",
      "To run a circuit on real hardware you need a quantum experience "
      "account.",
      None, "true",
      "The service is account-based and free tier is available for learning."),
    q("s14-q03", 14, "single",
      "What is the main practical difference between a simulator and a real "
      "device when you submit a job?",
      ["The simulator is instant, the device is queued",
       "The simulator is free, the device is not", "There is no difference",
       "The device gives exact amplitudes"],
      0,
      "Real devices run in queues with a calibration that changes over time."),
    q("s14-q04", 14, "multi",
      "Which of these are things you can do on the IBM Quantum platform?",
      ["Run a circuit on a simulator", "Run a circuit on a real QPU",
       "Inspect the calibration data", "Run a classical neural network"],
      [0, 1, 2],
      "The platform is for quantum circuits; classical neural networks are "
      "not its job."),
]

# ---------------------------------------------------------------- section 15
SECTIONS[15] = [
    q("s15-q01", 15, "single",
      "In Qiskit 2.x, which object runs a circuit on a simulator?",
      ["BasicAer.get_backend", "AerSimulator", "QuantumInstance",
       "qiskit.algorithms.Shor"],
      1,
      "BasicAer, QuantumInstance and qiskit.algorithms.Shor were all removed "
      "in Qiskit 1.0."),
    q("s15-q02", 15, "single",
      "What is the modern way to bind parameters to a circuit?",
      ["bind_parameters", "assign_parameters", "set_parameters_only",
       "fix_parameters"],
      1,
      "bind_parameters was removed; assign_parameters returns a new circuit."),
    q("s15-q03", 15, "truefalse",
      "Shor's algorithm is really a period-finding algorithm, and the "
      "factoring step is classical.",
      None, "true",
      "The quantum part finds the period r of a^x mod N; gcd(a^(r/2) +/- 1, N) "
      "then factors N classically."),
    q("s15-q04", 15, "single",
      "In a period-finding circuit with m counting qubits, the measurement "
      "peaks sit at multiples of...",
      ["2^m / r", "2^m * r", "r / 2^m", "m / r"],
      0,
      "That is why the continued-fraction step recovers r from the measured "
      "value."),
    q("s15-q05", 15, "multi",
      "Which of these are legitimate modern Qiskit 2.x APIs?",
      ["Statevector(circuit)", "Operator(circuit)",
       "qiskit.algorithms.phase_estimation", "qiskit_aer.AerSimulator"],
      [0, 1, 3],
      "qiskit.algorithms was removed entirely in Qiskit 1.0."),
    q("s15-q06", 15, "single",
      "In Qiskit, which qubit does the leftmost character of a counts "
      "bitstring refer to?",
      ["Qubit 0", "The highest-numbered qubit", "It depends", "The control qubit"],
      1,
      "Qiskit's bitstrings are printed most-significant-qubit first, i.e. "
      "q_{n-1} ... q_0."),
    q("s15-q07", 15, "single",
      "Why is the course's Shor code 'temporary fix' needed?",
      ["Because Qiskit removed the Shor class, so the circuit has to be "
       "rebuilt by hand", "Because of a hardware bug", "Because numpy changed",
       "Because the licence expired"],
      0,
      "The 'Shor's Algorithm - Temporary Fix' course article explains "
      "exactly this."),
]

# ---------------------------------------------------------------- section 16
SECTIONS[16] = [
    q("s16-q01", 16, "single",
      "What are the three ingredients of every machine-learning system?",
      ["Data, model, loss", "Data, code, hardware", "Model, loss, GPU",
       "Features, labels, GPU"],
      0,
      "Data, a model with tunable parameters, and a loss that says how wrong "
      "the model is."),
    q("s16-q02", 16, "single",
      "What does gradient descent update?",
      ["The data", "The parameters of the model", "The loss function",
       "The learning rate"],
      1,
      "The parameters are moved downhill along the gradient of the loss."),
    q("s16-q03", 16, "truefalse",
      "If the training error is very low but the test error is high, the "
      "model is overfitting.",
      None, "true",
      "Low training error plus high test error is the signature of "
      "overfitting (high variance)."),
    q("s16-q04", 16, "single",
      "What does the sigmoid function output?",
      ["A real number of any size", "A number between 0 and 1",
       "A probability distribution over many classes", "A vector"],
      1,
      "sigmoid(z) = 1/(1+e^-z) always lies strictly between 0 and 1."),
    q("s16-q05", 16, "multi",
      "What does L2 (ridge) regularization do?",
      ["Shrinks all the weights smoothly towards zero",
       "Can drive some weights exactly to zero",
       "Adds a penalty proportional to the sum of the squares of the weights",
       "Always increases the training accuracy"],
      [0, 2],
      "Driving weights exactly to zero is the hallmark of L1, not L2."),
    q("s16-q06", 16, "single",
      "In the classical KNN of the course, what is the weight formula?",
      ["w = 1 / d^2", "w = 1 - 0.25 * d^2", "w = exp(-d)", "w = d"],
      1,
      "w_i = 1 - 0.25 * d_i^2, with d the squared Euclidean distance."),
    q("s16-q07", 16, "single",
      "What is the decision boundary of a logistic regression model?",
      ["Where the probability is 0.5, i.e. a straight line in feature space",
       "The curve where the probability is 0.5",
       "Always a circle", "The set of support vectors"],
      0,
      "The sigmoid is monotone, so p = 0.5 exactly when w.x + b = 0 -- a "
      "straight line."),
    q("s16-q08", 16, "single",
      "Why is a hidden layer needed in a neural network?",
      ["To make training faster", "To introduce non-linearity, so the model "
       "can bend its decision boundary", "To reduce the number of parameters",
       "To store more data"],
      1,
      "Without a non-linearity, stacking linear layers is still a linear "
      "model."),
]

# ---------------------------------------------------------------- section 17
SECTIONS[17] = [
    q("s17-q01", 17, "single",
      "In the course's quantum KNN, what replaces the classical distance?",
      ["A quantum random number", "Interference between amplitude-encoded states",
       "A faster CPU", "A different loss function"],
      1,
      "The overlap of the encoded states is computed by interference, and it "
      "equals the classical similarity."),
    q("s17-q02", 17, "truefalse",
      "The quantum KNN and the classical KNN of the course produce the same "
      "class probabilities.",
      None, "true",
      "The algebra shows sum_i (v_i + q_i)^2 = 4 w_i, so the measurement "
      "statistics reproduce the classical weights exactly."),
    q("s17-q03", 17, "single",
      "What is a quantum kernel?",
      ["K(x, z) = |<phi(x)|phi(z)>|^2, with phi a quantum feature map",
       "A quantum computer that sorts data", "A rule for choosing a learning rate",
       "A quantum Fourier transform"],
      0,
      "The quantum kernel replaces the classical inner product with a "
      "quantum overlap."),
    q("s17-q04", 17, "single",
      "Which feature map does the course's qsvm.py use?",
      ["ZZFeatureMap with 4 features and 2 repetitions",
       "AngleEmbedding with 1 feature", "HellingerEmbedding",
       "A Fourier transform of the raw data"],
      0,
      "ZZFeatureMap(feature_dimension=4, reps=2, entanglement='linear')."),
    q("s17-q05", 17, "multi",
      "Which parts of a machine-learning pipeline stay classical in quantum "
      "ML?",
      ["The loss function", "The optimizer", "The data preprocessing",
       "The quantum feature map"],
      [0, 1, 2],
      "Only the feature map (and the kernel it induces) is quantum."),
    q("s17-q06", 17, "single",
      "What does the 'significance of quantum machine learning' really "
      "amount to?",
      ["Quantum computers will learn every model better",
       "It is mainly a new way to compute a similarity or kernel",
       "It removes the need for a train/test split",
       "It makes the loss function unnecessary"],
      1,
      "The honest summary: quantum ML is a new way to compute a kernel, "
      "useful where that kernel is hard to compute classically."),
    q("s17-q07", 17, "single",
      "In the quantum KNN circuit, what does the Hadamard gate on the "
      "'training vs query' qubit do?",
      ["It measures the qubits", "It creates the interference between the "
       "training half and the query half", "It resets the qubits",
       "It entangles the two classes"],
      1,
      "The Hadamard turns the sum and the difference of the amplitudes into "
      "the measurement statistics."),
]

for section, questions in SECTIONS.items():
    path = OUT / f"section_{section:02d}.json"
    with path.open("w", encoding="utf-8") as handle:
        json.dump(questions, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    print(f"wrote {path.name}: {len(questions)} questions")
