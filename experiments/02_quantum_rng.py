import cirq
import cirq_google
import qsimcirq
import matplotlib.pyplot as plt
import numpy as np

processor_id = "willow_pink"
noise_props = cirq_google.engine.load_device_noise_properties(processor_id)
noise_model = cirq_google.NoiseModelFromGoogleNoiseProperties(noise_props)
sim = qsimcirq.QSimSimulator(noise=noise_model)
device = cirq_google.engine.create_device_from_processor_id(processor_id)
cal = cirq_google.engine.load_median_device_calibration(processor_id)
sim_processor = cirq_google.engine.SimulatedLocalProcessor(
    processor_id=processor_id, sampler=sim, device=device,
    calibrations={cal.timestamp // 1000: cal}
)
sim_engine = cirq_google.engine.SimulatedLocalEngine([sim_processor])

qubits = [cirq.GridQubit(4, i) for i in range(4, 9)]
circuit = cirq.Circuit(
    [cirq.H(q) for q in qubits],
    cirq.measure(*qubits, key='random')
)
gateset = cirq_google.GoogleCZTargetGateset()
compiled = cirq.optimize_for_target_gateset(circuit, gateset=gateset)
results = sim_engine.get_sampler(processor_id).run(compiled, repetitions=500)
bits = results.measurements['random']
numbers = [int(''.join(str(b) for b in row), 2) for row in bits]
print("First 10 quantum random numbers:", numbers[:10])
print("Average:", round(np.mean(numbers), 2))
