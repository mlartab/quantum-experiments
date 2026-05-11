import cirq
import matplotlib.pyplot as plt
import numpy as np

q0, q1, q2 = cirq.LineQubit.range(3)
TARGET = 6

def make_oracle(target_bits):
    ops = []
    if not target_bits[0]: ops.append(cirq.X(q0))
    if not target_bits[1]: ops.append(cirq.X(q1))
    if not target_bits[2]: ops.append(cirq.X(q2))
    ops.append(cirq.CCZ(q0, q1, q2))
    if not target_bits[0]: ops.append(cirq.X(q0))
    if not target_bits[1]: ops.append(cirq.X(q1))
    if not target_bits[2]: ops.append(cirq.X(q2))
    return ops

def make_diffuser():
    return [
        cirq.H(q0), cirq.H(q1), cirq.H(q2),
        cirq.X(q0), cirq.X(q1), cirq.X(q2),
        cirq.CCZ(q0, q1, q2),
        cirq.X(q0), cirq.X(q1), cirq.X(q2),
        cirq.H(q0), cirq.H(q1), cirq.H(q2),
    ]

target_bits = [(TARGET >> i) & 1 for i in reversed(range(3))]
circuit = cirq.Circuit(
    cirq.H(q0), cirq.H(q1), cirq.H(q2),
    make_oracle(target_bits),
    make_diffuser(),
    cirq.measure(q0, q1, q2, key='result')
)

sim = cirq.Simulator()
result = sim.run(circuit, repetitions=1000)
counts = result.histogram(key='result')
print("Grover search results:", counts)
print(f"Target {TARGET} found: {counts.get(TARGET, 0)} times out of 1000")
