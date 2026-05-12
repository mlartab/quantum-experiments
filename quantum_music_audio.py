#!/usr/bin/env python3
"""Quantum Music Composer + Audio Export (pure sine waves)"""

import cirq
import cirq_google
import qsimcirq
import matplotlib.pyplot as plt
import numpy as np
from scipy.io.wavfile import write as wav_write

# --- QVM setup (identical) ---
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
print("Virtual Willow ready.\n")

# --- Quantum notes generation ---
qubits = [cirq.GridQubit(4, i) for i in range(4, 12)]
circuit = cirq.Circuit(
    [cirq.H(q) for q in qubits],
    cirq.measure(*qubits, key='music')
)
gateset = cirq_google.GoogleCZTargetGateset()
compiled = cirq.optimize_for_target_gateset(circuit, gateset=gateset)
results = sim_engine.get_sampler(processor_id).run(compiled, repetitions=64)
bits = results.measurements['music']
notes_raw = [int(''.join(str(b) for b in row), 2) for row in bits]

note_names = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
notes = []
for val in notes_raw:
    semitone = (val & 0b111111) % 24
    octave = 4 + semitone // 12
    note = note_names[semitone % 12] + str(octave)
    duration = 0.25 + 0.25 * ((val >> 6) & 0b11) / 3
    notes.append((note, semitone, duration))

# --- Note frequency dictionary ---
FREQ = {
    'C4': 261.63, 'C#4': 277.18, 'D4': 293.66, 'D#4': 311.13, 'E4': 329.63,
    'F4': 349.23, 'F#4': 369.99, 'G4': 392.00, 'G#4': 415.30, 'A4': 440.00,
    'A#4': 466.16, 'B4': 493.88,
    'C5': 523.25, 'C#5': 554.37, 'D5': 587.33, 'D#5': 622.25, 'E5': 659.25,
    'F5': 698.46, 'F#5': 739.99, 'G5': 783.99, 'G#5': 830.61, 'A5': 880.00,
    'A#5': 932.33, 'B5': 987.77,
    'C6': 1046.50, 'C#6': 1108.73, 'D6': 1174.66, 'D#6': 1244.51, 'E6': 1318.5,
    'F6': 1396.9, 'F#6': 1479.9, 'G6': 1568.0, 'G#6': 1661.2, 'A6': 1760.0,
    'A#6': 1864.7, 'B6': 1975.5
}

# --- Audio synthesis ---
SAMPLE_RATE = 44100
audio = np.array([], dtype=np.float32)

for note_name, semitone, duration in notes:
    freq = FREQ.get(note_name, 440.0)
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    # simple envelope to avoid clicks
    envelope = np.ones_like(t)
    attack = int(0.01 * SAMPLE_RATE)
    release = int(0.05 * SAMPLE_RATE)
    if len(t) > attack + release:
        envelope[:attack] = np.linspace(0, 1, attack)
        envelope[-release:] = np.linspace(1, 0, release)
    else:
        envelope *= 0.8  # just soften short notes
    wave = 0.3 * np.sin(2 * np.pi * freq * t) * envelope
    audio = np.concatenate([audio, wave])

# Normalize and convert to 16-bit PCM
audio = np.int16(audio / np.max(np.abs(audio)) * 32767)

wav_write('quantum_melody.wav', SAMPLE_RATE, audio)
print("Audio saved as quantum_melody.wav — your quantum-generated composition!")