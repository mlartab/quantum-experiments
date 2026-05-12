# ================================================================
# QUANTUM BELIEF NETWORK
# Modeling misinformation spread using quantum circuits
#
# Core idea:
#   Classical models treat belief as binary — you believe or not.
#   Quantum model treats belief as a probability amplitude —
#   you exist in superposition of both until social pressure
#   forces a collapse into a definite position.
#
# This maps perfectly to how misinformation actually spreads:
#   - People are uncertain before they decide (superposition)
#   - Social connections bias the collapse (entanglement)
#   - Propaganda rotates the probability (gate operations)
#   - Journalism tries to correct it (error correction)
#   - Echo chambers lock beliefs in place (decoherence trap)
# ================================================================

import cirq
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from collections import Counter

sim = cirq.Simulator()

# ----------------------------------------------------------------
# HELPER: measure belief state of a circuit
# Returns probability of believing truth (measuring |0>)
# ----------------------------------------------------------------
def belief_probability(circuit, qubit, repetitions=2000):
    c = circuit.copy()
    c.append(cirq.measure(qubit, key='belief'))
    result = sim.run(c, repetitions=repetitions)
    counts = result.histogram(key='belief')
    truth_count = counts.get(0, 0)
    return truth_count / repetitions

# ================================================================
# EXPERIMENT 1: HOW PROPAGANDA WORKS
# A single person starts believing truth.
# Propaganda is applied in increasing doses.
# We measure how belief shifts.
# ================================================================
print("=" * 60)
print("EXPERIMENT 1: PROPAGANDA DOSE vs BELIEF SHIFT")
print("One person. Increasing propaganda exposure.")
print("=" * 60)

person = cirq.LineQubit(0)
angles = np.linspace(0, np.pi, 20)
truth_probabilities = []

for angle in angles:
    circuit = cirq.Circuit(
        # Start: person believes truth |0>
        # Apply propaganda: Rx rotates toward |1> (false belief)
        cirq.rx(angle)(person)
    )
    prob_truth = belief_probability(circuit, person)
    truth_probabilities.append(prob_truth)

print("\nPropaganda dose → Probability of believing truth:")
for i, (angle, prob) in enumerate(zip(angles, truth_probabilities)):
    bar = '#' * int(prob * 30)
    space = '.' * (30 - int(prob * 30))
    print(f"  Dose {angle/np.pi:.1f}π  [{bar}{space}]  {prob:.2f}")

# ================================================================
# EXPERIMENT 2: ECHO CHAMBER FORMATION
# 5 people connected in a network.
# One person exposed to propaganda.
# Watch it spread through social connections (CNOT gates).
# ================================================================
print()
print("=" * 60)
print("EXPERIMENT 2: ECHO CHAMBER FORMATION")
print("5 people. Propaganda enters through person 0.")
print("Social connections spread it.")
print("=" * 60)

people = cirq.LineQubit.range(5)

# Start: all people uncertain (superposition)
# This represents people who have not formed an opinion yet
initial_state = cirq.Circuit([cirq.H(p) for p in people])

scenarios = {
    'No propaganda': cirq.Circuit(
        [cirq.H(p) for p in people],
        cirq.measure(*people, key='beliefs')
    ),
    'Propaganda hits person 0 only': cirq.Circuit(
        [cirq.H(p) for p in people],
        cirq.rx(np.pi * 0.8)(people[0]),
        cirq.measure(*people, key='beliefs')
    ),
    'Echo chamber (all connected)': cirq.Circuit(
        [cirq.H(p) for p in people],
        cirq.rx(np.pi * 0.8)(people[0]),
        cirq.CNOT(people[0], people[1]),
        cirq.CNOT(people[1], people[2]),
        cirq.CNOT(people[2], people[3]),
        cirq.CNOT(people[3], people[4]),
        cirq.measure(*people, key='beliefs')
    ),
    'Journalism corrects after echo chamber': cirq.Circuit(
        [cirq.H(p) for p in people],
        cirq.rx(np.pi * 0.8)(people[0]),
        cirq.CNOT(people[0], people[1]),
        cirq.CNOT(people[1], people[2]),
        cirq.CNOT(people[2], people[3]),
        cirq.CNOT(people[3], people[4]),
        # Journalism: apply correction to all people
        *[cirq.rx(-np.pi * 0.5)(p) for p in people],
        cirq.measure(*people, key='beliefs')
    ),
}

echo_results = {}
for scenario_name, circuit in scenarios.items():
    result = sim.run(circuit, repetitions=1000)
    measurements = result.measurements['beliefs']
    # Average belief: 0 = truth, 1 = misinformation
    # Lower average = more people believe truth
    avg_false_belief = np.mean(measurements)
    truth_believers = np.mean(measurements == 0)
    echo_results[scenario_name] = {
        'avg_false': avg_false_belief,
        'truth_pct': truth_believers * 100
    }
    print(f"\n  {scenario_name}")
    print(f"    Believe truth:         {truth_believers*100:.1f}%")
    print(f"    Believe misinformation: {(1-truth_believers)*100:.1f}%")

# ================================================================
# EXPERIMENT 3: QUANTUM ERROR CORRECTION AS JOURNALISM
# Shows mathematically that error correction techniques
# from quantum computing map to journalistic fact-checking
# ================================================================
print()
print("=" * 60)
print("EXPERIMENT 3: ERROR CORRECTION = JOURNALISM")
print("Can we recover truth after heavy propaganda exposure?")
print("=" * 60)

person = cirq.LineQubit(0)
propaganda_levels = [0.2, 0.4, 0.6, 0.8, 1.0]
recovery_results = []

for level in propaganda_levels:
    # After propaganda
    corrupted = cirq.Circuit(cirq.rx(np.pi * level)(person))
    prob_before = belief_probability(corrupted, person)

    # After journalism (correction gate)
    corrected = cirq.Circuit(
        cirq.rx(np.pi * level)(person),
        cirq.rx(-np.pi * level)(person)
    )
    prob_after = belief_probability(corrected, person)
    recovery_results.append((level, prob_before, prob_after))
    print(f"\n  Propaganda level {level:.1f}:")
    print(f"    Truth belief BEFORE journalism: {prob_before:.2f}")
    print(f"    Truth belief AFTER  journalism: {prob_after:.2f}")
    print(f"    Recovery: {'+' if prob_after > prob_before else ''}{(prob_after - prob_before)*100:.1f}%")

# ================================================================
# EXPERIMENT 4: NETWORK TOPOLOGY vs RESILIENCE
# Open diverse network vs closed echo chamber
# Which resists misinformation better?
# ================================================================
print()
print("=" * 60)
print("EXPERIMENT 4: OPEN NETWORK vs ECHO CHAMBER")
print("Which social network topology resists misinformation?")
print("=" * 60)

people = cirq.LineQubit.range(6)
propaganda_person = people[0]
propaganda_gate = cirq.rx(np.pi * 0.9)

# Closed echo chamber: everyone connected to everyone
echo_chamber = cirq.Circuit(
    [cirq.H(p) for p in people],
    propaganda_gate(propaganda_person),
    cirq.CNOT(people[0], people[1]),
    cirq.CNOT(people[1], people[2]),
    cirq.CNOT(people[2], people[3]),
    cirq.CNOT(people[3], people[4]),
    cirq.CNOT(people[4], people[5]),
    cirq.measure(*people, key='beliefs')
)

# Open diverse network: people connected to DIFFERENT sources
# Some connections go back to truth (represented by no CNOT from 0)
open_network = cirq.Circuit(
    [cirq.H(p) for p in people],
    propaganda_gate(propaganda_person),
    cirq.CNOT(people[0], people[1]),
    # People 2,3,4,5 have diverse connections — not only from person 0
    # Represented by H gates reintroducing uncertainty
    cirq.H(people[2]),
    cirq.H(people[3]),
    cirq.CNOT(people[1], people[4]),
    cirq.H(people[5]),
    cirq.measure(*people, key='beliefs')
)

echo_result = sim.run(echo_chamber, repetitions=1000)
open_result = sim.run(open_network, repetitions=1000)

echo_truth = np.mean(echo_result.measurements['beliefs'] == 0) * 100
open_truth = np.mean(open_result.measurements['beliefs'] == 0) * 100

print(f"\n  Echo chamber  — truth believers: {echo_truth:.1f}%")
print(f"  Open network  — truth believers: {open_truth:.1f}%")
print(f"\n  Open network is {open_truth - echo_truth:.1f}% more resistant to misinformation")

# ================================================================
# VISUALIZATION
# ================================================================

fig = plt.figure(figsize=(18, 10))
fig.patch.set_facecolor('#0a0a2e')
gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.35)

# Chart 1: Propaganda dose curve
ax1 = fig.add_subplot(gs[0, 0])
ax1.set_facecolor('#0a0a2e')
ax1.plot(angles / np.pi, truth_probabilities,
         'o-', color='#00d4ff', linewidth=2, markersize=5)
ax1.axhline(y=0.5, color='#ff6b6b', linewidth=1,
            linestyle='--', alpha=0.7, label='50/50 uncertain')
ax1.fill_between(angles / np.pi, truth_probabilities, 0.5,
                 where=[p < 0.5 for p in truth_probabilities],
                 alpha=0.2, color='#ff2244', label='Misinformation wins')
ax1.fill_between(angles / np.pi, truth_probabilities, 0.5,
                 where=[p >= 0.5 for p in truth_probabilities],
                 alpha=0.2, color='#00d4ff', label='Truth wins')
ax1.set_title('Propaganda Dose Effect\non Single Person', color='white', fontsize=11)
ax1.set_xlabel('Propaganda dose (x π)', color='#00d4ff')
ax1.set_ylabel('Probability of believing truth', color='#00d4ff')
ax1.tick_params(colors='white')
ax1.legend(facecolor='#0a0a2e', labelcolor='white', fontsize=8)
for spine in ax1.spines.values(): spine.set_edgecolor('#00d4ff')

# Chart 2: Echo chamber results
ax2 = fig.add_subplot(gs[0, 1:])
ax2.set_facecolor('#0a0a2e')
scenario_names = [s.replace(' (all connected)', '\n(all connected)').replace(' after echo chamber', '\nafter echo chamber')
                  for s in echo_results.keys()]
truth_pcts = [v['truth_pct'] for v in echo_results.values()]
colors = ['#00d4ff', '#ff6b35', '#ff2244', '#00ff88']
bars = ax2.bar(range(len(scenario_names)), truth_pcts,
               color=colors, edgecolor='white', linewidth=0.5, width=0.6)
ax2.axhline(y=50, color='white', linewidth=1,
            linestyle='--', alpha=0.5, label='50% baseline')
ax2.set_title('Echo Chamber Formation\n% of population believing truth',
              color='white', fontsize=11)
ax2.set_xticks(range(len(scenario_names)))
ax2.set_xticklabels(scenario_names, color='white', fontsize=8)
ax2.set_ylabel('% believing truth', color='#00d4ff')
ax2.tick_params(colors='white')
ax2.set_ylim(0, 100)
for spine in ax2.spines.values(): spine.set_edgecolor('#00d4ff')
for bar, val in zip(bars, truth_pcts):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
             f'{val:.0f}%', ha='center', color='white', fontsize=10, fontweight='bold')

# Chart 3: Journalism recovery
ax3 = fig.add_subplot(gs[1, 0])
ax3.set_facecolor('#0a0a2e')
levels = [r[0] for r in recovery_results]
before = [r[1] for r in recovery_results]
after  = [r[2] for r in recovery_results]
ax3.plot(levels, before, 'o-', color='#ff2244',
         linewidth=2, markersize=6, label='Before journalism')
ax3.plot(levels, after,  's-', color='#00ff88',
         linewidth=2, markersize=6, label='After journalism')
ax3.fill_between(levels, before, after, alpha=0.15, color='#00ff88')
ax3.set_title('Journalism as Error Correction\nRecovery of truth belief',
              color='white', fontsize=11)
ax3.set_xlabel('Propaganda level', color='#00d4ff')
ax3.set_ylabel('Probability of believing truth', color='#00d4ff')
ax3.tick_params(colors='white')
ax3.legend(facecolor='#0a0a2e', labelcolor='white', fontsize=9)
for spine in ax3.spines.values(): spine.set_edgecolor('#00d4ff')

# Chart 4: Network topology comparison
ax4 = fig.add_subplot(gs[1, 1])
ax4.set_facecolor('#0a0a2e')
network_data = [echo_truth, open_truth]
network_labels = ['Echo Chamber\n(closed network)', 'Open Network\n(diverse sources)']
net_colors = ['#ff2244', '#00d4ff']
bars4 = ax4.bar(network_labels, network_data,
                color=net_colors, edgecolor='white', linewidth=0.5, width=0.5)
ax4.set_title('Network Topology\nvs Misinformation Resistance',
              color='white', fontsize=11)
ax4.set_ylabel('% believing truth', color='#00d4ff')
ax4.tick_params(colors='white')
ax4.set_ylim(0, 100)
for spine in ax4.spines.values(): spine.set_edgecolor('#00d4ff')
for bar, val in zip(bars4, network_data):
    ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
             f'{val:.0f}%', ha='center', color='white', fontsize=12, fontweight='bold')

# Chart 5: The model summary
ax5 = fig.add_subplot(gs[1, 2])
ax5.set_facecolor('#0a0a2e')
ax5.axis('off')
model_text = [
    ("THE QUANTUM BELIEF MODEL", '#ffffff', 12),
    ("", '#ffffff', 10),
    ("Person  =  qubit", '#00d4ff', 10),
    ("|0>  =  believes truth", '#00ff88', 10),
    ("|1>  =  believes false", '#ff2244', 10),
    ("superposition  =  uncertain", '#ffd700', 10),
    ("", '#ffffff', 10),
    ("H gate  =  introduce doubt", '#00d4ff', 10),
    ("Rx(θ)  =  propaganda dose", '#ff6b35', 10),
    ("Rx(-θ)  =  journalism", '#00ff88', 10),
    ("CNOT  =  social influence", '#a855f7', 10),
    ("", '#ffffff', 10),
    ("Error correction  =", '#ffffff', 10),
    ("Fact checking", '#00ff88', 10),
    ("", '#ffffff', 10),
    ("Decoherence  =", '#ffffff', 10),
    ("Rumor degradation", '#ff6b35', 10),
]
y_pos = 0.98
for text, color, size in model_text:
    ax5.text(0.05, y_pos, text, transform=ax5.transAxes,
             color=color, fontsize=size, verticalalignment='top',
             fontfamily='monospace')
    y_pos -= 0.065

plt.suptitle('Quantum Belief Network — Modeling Misinformation as Quantum Decoherence\n'
             'Each person = a qubit | Social connection = entanglement | Opinion = measurement collapse',
             color='white', fontsize=11, y=1.01)

plt.savefig('quantum_belief_network.png', dpi=200,
            bbox_inches='tight', facecolor='#0a0a2e')
plt.show()
print("\nSaved as quantum_belief_network.png")
print("\nAll 4 experiments complete.")
