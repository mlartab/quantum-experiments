import cirq
import cirq_google
import qsimcirq
import matplotlib.pyplot as plt

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

q0 = cirq.GridQubit(4, 4)
q1 = cirq.GridQubit(4, 5)

circuit = cirq.Circuit(
    cirq.H(q0),
    cirq.CNOT(q0, q1),
    cirq.measure([q0, q1], key='result')
)

gateset = cirq_google.GoogleCZTargetGateset()
compiled = cirq.optimize_for_target_gateset(circuit, gateset=gateset)

results = sim_engine.get_sampler(processor_id).run(compiled, repetitions=3000)
histogram = results.histogram(key='result')
print("Bell State Results:", histogram)
