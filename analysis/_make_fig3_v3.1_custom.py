"""
_regen_fig3_custom_palette.py

Regenerated version of fig3_gap_count_distribution.png with the user-requested palette:
- Gap 1 = blue (#3c64a7)
- Gap 2 = amber (#f0a73a)
- Gap 3 = red (#d93838)
- Causal interaction = purple (#8e44ad)

The previous fig3 (in _make_figures_v3.1.py) used a palette where:
- "2 gaps" was GREEN and "3 gaps" was red (counting by # gaps per paper).
- There was no causal interaction visualization.

This version instead shows the four CORE categories directly (Gap 1, Gap 2,
Gap 3, Causal Interaction) as the user requested, with the right panel breaking
down each category into "alone" vs "with causal interaction".

Run:  python3 _regen_fig3_custom_palette.py
Input: analysis/_codings_v3.1_stance.json
Output: analysis/figures/fig3_gap_count_distribution.png
"""
import json
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# === User-requested palette ===
COL_GAP1_BLUE  = '#3c64a7'  # blue   - Gap 1 (Ecological Validity)
COL_GAP2_AMBER = '#f0a73a'  # amber  - Gap 2 (Governance Capacity)
COL_GAP3_RED   = '#d93838'  # red    - Gap 3 (Pilot Trap)
COL_INT_PURPLE = '#8e44ad'  # purple - Causal Interaction

# === Load V3.1 corpus ===
with open('/home/agent/ai-health-lit-review/analysis/_codings_v3.1_stance.json') as f:
    papers = json.load(f)
n = len(papers)

gap1_papers = [p for p in papers if p['gap1']==1]
gap2_papers = [p for p in papers if p['gap2']==1]
gap3_papers = [p for p in papers if p['gap3']==1]
int_papers  = [p for p in papers if p.get('interaction_present')==1]

# Pairwise overlap with interaction
g1_and_int = sum(1 for p in papers if p['gap1']==1 and p.get('interaction_present')==1)
g2_and_int = sum(1 for p in papers if p['gap2']==1 and p.get('interaction_present')==1)
g3_and_int = sum(1 for p in papers if p['gap3']==1 and p.get('interaction_present')==1)
int_no_gap = sum(1 for p in int_papers
                 if p['gap1']==0 and p['gap2']==0 and p['gap3']==0)

# === Two-panel figure ===
fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

# Left: paper counts by category with the requested palette
ax = axes[0]
categories = ['Gap 1\nEcological Validity',
              'Gap 2\nGovernance Capacity',
              'Gap 3\nPilot Trap',
              'Causal\nInteraction']
counts = [len(gap1_papers), len(gap2_papers), len(gap3_papers), len(int_papers)]
colors  = [COL_GAP1_BLUE, COL_GAP2_AMBER, COL_GAP3_RED, COL_INT_PURPLE]

bars = ax.bar(categories, counts, color=colors, edgecolor='black', linewidth=0.7)
for bar, v in zip(bars, counts):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.6,
            f'{v}\n({100*v/n:.1f}%)', ha='center', va='bottom',
            fontsize=11, fontweight='bold')
ax.set_ylabel('Number of papers (n=60)', fontsize=11)
ax.set_title('Paper counts by category\n(categories overlap — papers may be in multiple)',
             fontsize=11)
ax.set_ylim(0, max(counts) * 1.30)
ax.grid(axis='y', alpha=0.3)
ax.set_axisbelow(True)

# Right: each category split into "alone" vs "with causal interaction"
ax = axes[1]
g1_only = len(gap1_papers) - g1_and_int
g2_only = len(gap2_papers) - g2_and_int
g3_only = len(gap3_papers) - g3_and_int

cats        = ['Gap 1', 'Gap 2', 'Gap 3', 'Interaction\n(no other gap)']
only_vals   = [g1_only, g2_only, g3_only, int_no_gap]
and_int_vals= [g1_and_int, g2_and_int, g3_and_int, 0]
x_pos       = np.arange(len(cats))

ax.bar(x_pos, only_vals,
       color=[COL_GAP1_BLUE, COL_GAP2_AMBER, COL_GAP3_RED, COL_INT_PURPLE],
       edgecolor='black', linewidth=0.7,
       label='alone (no causal interaction)')
ax.bar(x_pos, and_int_vals, bottom=only_vals,
       color=COL_INT_PURPLE, edgecolor='black', linewidth=0.7,
       hatch='//', alpha=0.85,
       label='+ causal interaction (purple)')

for i, (o, a) in enumerate(zip(only_vals, and_int_vals)):
    total = o + a
    if o > 0:
        ax.text(i, o/2, f'{o}', ha='center', va='center',
                fontsize=11, fontweight='bold', color='white')
    if a > 0:
        ax.text(i, o + a/2, f'+{a}', ha='center', va='center',
                fontsize=10, fontweight='bold', color='white')
    ax.text(i, total + 0.5, f'n={total}', ha='center', va='bottom',
            fontsize=10, fontweight='bold')

ax.set_xticks(x_pos)
ax.set_xticklabels(cats, fontsize=10)
ax.set_ylabel('Number of papers', fontsize=11)
ax.set_title('Each category split: alone vs with causal interaction',
             fontsize=11)
ax.set_ylim(0, max(o + a for o, a in zip(only_vals, and_int_vals)) * 1.20)
ax.grid(axis='y', alpha=0.3)
ax.set_axisbelow(True)
ax.legend(loc='upper right', fontsize=9.5, framealpha=0.9)

fig.suptitle(
    'Figure (regenerated). Gap categories and causal interaction in the v3.1 corpus (n=60)\n'
    'Palette: blue=Gap 1, amber=Gap 2, red=Gap 3, purple=causal interaction',
    fontsize=12, fontweight='bold'
)

plt.tight_layout()
out_path = '/home/agent/ai-health-lit-review/analysis/figures/fig3_gap_count_distribution.png'
plt.savefig(out_path, dpi=160, bbox_inches='tight')
plt.close()
print(f'Saved: {out_path}')
print(f'File size: {os.path.getsize(out_path)} bytes')