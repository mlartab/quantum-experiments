import cirq
import matplotlib.pyplot as plt
import numpy as np

n_qubits = 4
qubits = cirq.LineQubit.range(n_qubits)

def qft_circuit(qubits):
    n = len(qubits)
    ops = []
    for i in range(n):
        ops.append(cirq.H(qubits[i]))
        for j in range(i + 1, n):
            angle = np.pi / (2 ** (j - i))
            ops.append(cirq.CZ(qubits[j], qubits[i]) ** (angle / np.pi))
    for i in range(n // 2):
        ops.append(cirq.SWAP(qubits[i], qubits[n - 1 - i]))
    return cirq.Circuit(ops)

input_number = 6
input_bits = format(input_number, f'0{n_qubits}b')
state_prep = cirq.Circuit()
for i, bit in enumerate(input_bits):
    if bit == '1':
        state_prep.append(cirq.X(qubits[i]))

qft = qft_circuit(qubits)
full_circuit = state_prep + qft
full_circuit.append(cirq.measure(*qubits, key='result'))

sim = cirq.Simulator()
result = sim.run(full_circuit, repetitions=2000)
counts = result.histogram(key='result')
print("QFT Results (should be flat/uniform):")
for val in sorted(counts.keys()):
    print(f"  State {val}: {counts[val]} times")
