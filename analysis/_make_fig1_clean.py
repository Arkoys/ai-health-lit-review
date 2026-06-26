"""
Regenerate Figure 1 — Gap frequencies in the v3 corpus (n=60).

Source: _codings_v3.1.json (60 papers, ground truth).
Output: analysis/figures/fig1_gap_frequencies.png

Numbers shown are verified against the report text (04b):
  G1 = 30/60 = 50.0%
  G2 = 30/60 = 50.0%
  G3 = 18/60 = 30.0%
  Interaction (any causal pathway) = 19/60 = 31.7%
  At least one gap = 50/60 = 83.3%
  No gap = 10/60 = 16.7%
"""

import json
import os
from collections import Counter

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

CODINGS = '/home/agent/ai-health-lit-review/analysis/_codings_v3.1.json'
OUT = '/home/agent/ai-health-lit-review/analysis/figures'
os.makedirs(OUT, exist_ok=True)

with open(CODINGS) as f:
    papers = json.load(f)

# Normalize arrows to count interaction papers consistently
def normalize(d):
    return d.replace('->', '→').replace('-->', '→').replace('=>', '→')

n = len(papers)
g1 = sum(p['gap1'] for p in papers)
g2 = sum(p['gap2'] for p in papers)
g3 = sum(p['gap3'] for p in papers)
inter = sum(p['interaction_present'] for p in papers)
at_least_one = sum(1 for p in papers if p['gap1']==1 or p['gap2']==1 or p['gap3']==1)
no_gap = n - at_least_one

# Direction counts (normalized arrows)
direction_counter = Counter()
for p in papers:
    if p['interaction_present'] == 1:
        for d in p['interaction_directions']:
            direction_counter[normalize(d)] += 1

# Colors (matching fig3 palette)
COL_G1 = '#4c72b0'
COL_G2 = '#dd8452'
COL_G3 = '#55a467'
COL_INT = '#c44e52'
COL_NEU = '#9aa0a6'

# ---- Two-panel figure ----
fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

# ---- LEFT: Frequency of each gap (bars) ----
ax = axes[0]
labels = [
    'Gap 1\nEcological Validity',
    'Gap 2\nGovernance Capacity',
    'Gap 3\nPilot Trap',
    'Causal Interaction\n(any direction)',
]
vals = [g1, g2, g3, inter]
colors = [COL_G1, COL_G2, COL_G3, COL_INT]
bars = ax.bar(labels, vals, color=colors, edgecolor='black', linewidth=0.7)
for bar, v in zip(bars, vals):
    pct = v / n * 100
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.6,
            f'{v}\n({pct:.1f}%)',
            ha='center', va='bottom', fontsize=11, fontweight='bold')
ax.set_ylabel('Number of papers (n=60)', fontsize=11)
ax.set_title('Frequency of each gap and causal interactions', fontsize=11.5)
ax.set_ylim(0, max(vals) * 1.25)
ax.grid(axis='y', alpha=0.3)
ax.set_axisbelow(True)
plt.setp(ax.get_xticklabels(), fontsize=9.5)

# Add a horizontal reference line at 50% (n=30) for visual context
ax.axhline(30, color='black', linestyle=':', linewidth=0.8, alpha=0.5)
ax.text(3.45, 30.5, '50% (n=30)', fontsize=8.5, alpha=0.7, ha='right')

# ---- RIGHT: Composition of the corpus (donut) ----
ax = axes[1]
sizes = [at_least_one, no_gap]
labels_pie = [f'At least one gap\n({at_least_one} papers, {at_least_one/n*100:.1f}%)',
              f'No gap documented\n({no_gap} papers, {no_gap/n*100:.1f}%)']
pie_colors = [COL_INT, COL_NEU]
wedges, texts, autotexts = ax.pie(
    sizes, labels=labels_pie, colors=pie_colors,
    autopct='', startangle=90,
    wedgeprops=dict(width=0.42, edgecolor='white', linewidth=2),
    textprops=dict(fontsize=10.5)
)
# Centre annotation
ax.text(0, 0.08, f'{at_least_one}/{n}', ha='center', va='center',
        fontsize=22, fontweight='bold')
ax.text(0, -0.18, 'papers engage\nwith ≥1 gap', ha='center', va='center',
        fontsize=10, color='#444')
ax.set_title('Corpus coverage of the three-gap framework', fontsize=11.5)

# ---- Figure-level title removed: caption goes in LaTeX ----
# (Title will appear in the report via \caption{} — kept here only
# to avoid ambiguity during local inspection.)

plt.tight_layout()
out_path = f'{OUT}/fig1_gap_frequencies.png'
plt.savefig(out_path, dpi=160, bbox_inches='tight')
plt.close()

print(f'Wrote {out_path}')
print()
print('Verification against report (must match 04b text):')
print(f'  G1 = {g1}/{n} = {g1/n*100:.1f}%   (rapport dit 50.0%)')
print(f'  G2 = {g2}/{n} = {g2/n*100:.1f}%   (rapport dit 50.0%)')
print(f'  G3 = {g3}/{n} = {g3/n*100:.1f}%   (rapport dit 30.0%)')
print(f'  Interaction = {inter}/{n} = {inter/n*100:.1f}%   (rapport dit 31.7%)')
print(f'  At least one gap = {at_least_one}/{n} = {at_least_one/n*100:.1f}%   (rapport dit 83.3%)')
print(f'  No gap = {no_gap}/{n} = {no_gap/n*100:.1f}%   (rapport dit 16.7%)')
print()
print('Direction counts (normalized arrows):')
for d, c in sorted(direction_counter.items(), key=lambda x: -x[1]):
    print(f'  {d}: {c}')
print(f'  Sum of direction entries: {sum(direction_counter.values())} (vs 19 distinct interaction papers)')
