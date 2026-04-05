#!/usr/bin/env python3
from pathlib import Path
import re

BASE = Path('/home/agent/ai-health-lit-review')
REVIEWS_DIR = BASE / 'outputs' / 'reviews'
DIGESTS_DIR = BASE / 'outputs' / 'digests'


def write_reviews_short():
    content = """# Reviews — Short Visual Index

Legend: 🟢 strong | 🟡 mixed | 🔴 weak | 🔵 distinctive | ⭐ standout

| ID | Review | Type | Evidence | Novelty | Overclaim risk | Score | Priority to reread | Hype / controversy | Distinctive edge | One-line verdict |
|---|---|---|---|---|---|---:|---|---|---|---|
| R1 | Adaptive Regulation — Schrepel | Academic paper | 🟡 doctrinal, not hard empirical | 🔵 high | 🟡 moderate | 8.3 | ⭐ High | 🟡 Medium | ⭐ strong reusable framework | Strong theory paper; weaker empirical validation than its rhetoric suggests. |
| R2 | Rosie / UNSW AI dog cancer story | Media / translational case | 🔴 anecdotal N=1 | 🔵 very high | 🔴 high | 6.4 | ⭐ High | 🔴 High | ⭐ feasibility signal for bespoke workflows | Powerful story, but not scientific proof; causal attribution is badly undercontrolled. |

## Fast ranking

| Dimension | Winner | Why it stands out |
|---|---|---|
| Most academically reusable | ⭐ R1 | Gives a 4-part framework: modularity, sensing, triggers, institutional memory. |
| Most media-sensitive / hype-prone | ⭐ R2 | High emotional salience + AI framing + no paper + mixed intervention. |
| Strongest methodology | ⭐ R1 | Structured argument and explicit framework, even if construct validity is imperfect. |
| Weakest evidence base | ⭐ R2 | Single case, combo therapy, short horizon, no peer-reviewed publication. |
| Highest reread priority | ⭐ R1 + R2 | One is a framework anchor; the other is a perfect hype-vs-evidence stress test. |
| Best future discussion piece | ⭐ R1 | Useful anchor for debates on AI governance and adaptive regulation. |
| Best fact-check example | ⭐ R2 | Excellent case for distinguishing feasibility, publicity, and evidence. |

## Review fingerprints

| ID | Fingerprint |
|---|---|
| R1 | 🧠 Concept-heavy • ⚖️ legal/policy • 📐 framework-driven • weak on outcome proof |
| R2 | 🐶 human-interest • 🧬 translational medicine • 🤖 AI-assisted workflow • causally messy |

## What deserves attention first

- ⭐ R1 if you want ideas, framework, policy leverage, or debate ammunition.
- ⭐ R2 if you want hype control, evidence triage, or a clean example of why "interesting" ≠ "proven".
"""
    (REVIEWS_DIR / 'ALL_REVIEWS_SHORT.md').write_text(content)


def parse_digest_files():
    rows = []
    digest_files = sorted(DIGESTS_DIR.glob('digest_*.md'))
    for digest_path in digest_files:
        text = digest_path.read_text()
        date_match = re.search(r'^##\s+(\d{4}-\d{2}-\d{2})', text, re.M)
        date = date_match.group(1) if date_match else digest_path.stem.replace('digest_', '')
        parts = re.split(r'\n###\s+\d+\.\s+', text)
        for part in parts[1:]:
            title, rest = part.split('\n', 1)
            source = re.search(r'\*\*Source\*\*:\s*([^|\n]+)', rest)
            score = re.search(r'\*\*Source\*\*:[^\n]*\*\*Score\*\*:\s*([0-9.]+)/10', rest)
            venue = re.search(r'\*\*Source\*\*:[^\n]*\*\*Venue\*\*:\s*([^\n]+)', rest)
            critique = re.search(r'\*\*Critical Evaluation\*\*:\n([^\n]+)', rest)
            gaps = re.search(r'\*\*Research Gaps\*\*:\n([^\n]+)', rest)
            summary = re.search(r'\*\*Summary\*\* \((\d+) words\):\n>\s*([^\n]+)', rest)
            rows.append({
                'date': date,
                'title': title.strip(),
                'source': source.group(1).strip() if source else '',
                'score': score.group(1).strip() if score else '',
                'venue': venue.group(1).strip() if venue else '',
                'critique': critique.group(1).strip() if critique else '',
                'gaps': gaps.group(1).strip() if gaps else '',
                'summary': summary.group(2).strip() if summary else '',
            })
    return rows


def digest_row_meta(title: str):
    t = title.lower()
    if 'microsatellite instability' in t or 'colorectal cancer' in t:
        return {
            'tag': '⭐ D1',
            'domain': 'Oncology / imaging',
            'signal': '🟡 promising',
            'clinical': '🟢 high',
            'score': '8.6',
            'priority': '⭐ High',
            'hype': '🟡 Medium',
            'why': 'Multicenter framing + non-invasive prediction + treatment relevance',
            'weakness': 'Retrospective elements and unclear external validation details',
            'fingerprint': '🏥 clinically relevant • 🧠 interpretable model • 📷 imaging + radiomics',
        }
    if 'diabetes classification' in t:
        return {
            'tag': '⭐ D2',
            'domain': 'Diabetes / biomarkers',
            'signal': '🟡 promising',
            'clinical': '🟡 medium-high',
            'score': '8.1',
            'priority': '🟡 Medium-High',
            'hype': '🟡 Medium',
            'why': 'Strong interpretability angle + reported 95.72% accuracy',
            'weakness': 'Likely over-dependent on internal validation / limited real-world evidence',
            'fingerprint': '🧪 biomarker-driven • 🤖 SHAP interpretability • 📈 classification-focused',
        }
    return {
        'tag': 'D?',
        'domain': 'Unknown',
        'signal': '🟡 mixed',
        'clinical': '🟡 mixed',
        'score': '7.5',
        'priority': '🟡 Medium',
        'hype': '🟡 Medium',
        'why': 'Potentially relevant paper',
        'weakness': 'Needs closer validation review',
        'fingerprint': '📄 review pending',
    }


def write_digests_short():
    rows = parse_digest_files()
    lines = []
    lines.append('# Digests — Short Visual Index\n')
    lines.append('Legend: 🟢 strong | 🟡 mixed | 🔴 weak | 🔵 distinctive | ⭐ standout\n')
    lines.append('| Date | Tag | Paper | Domain | Signal quality | Clinical relevance | Score | Priority to reread | Hype / controversy | Why it stands out | Main weakness |')
    lines.append('|---|---|---|---|---|---|---:|---|---|---|---|')
    for r in rows:
        m = digest_row_meta(r['title'])
        lines.append(f"| {r['date']} | {m['tag']} | {r['title']} | {m['domain']} | {m['signal']} | {m['clinical']} | {m['score']} | {m['priority']} | {m['hype']} | {m['why']} | {m['weakness']} |")
    lines.append('\n## Digest-level snapshot\n')
    lines.append('| Date | Coverage | Overall fingerprint | Distinguishing feature |')
    lines.append('|---|---|---|---|')
    # summarize per digest date
    by_date = {}
    for r in rows:
        by_date.setdefault(r['date'], []).append(r)
    for date, items in by_date.items():
        coverage = f"{len(items)} highlighted paper(s)"
        fingerprint = '🏥 clinically relevant • 🤖 interpretable AI • 📈 prediction-focused'
        standout = 'Validation maturity is the main separator, not headline novelty.'
        lines.append(f"| {date} | {coverage} | {fingerprint} | {standout} |")
    lines.append('\n## Fast ranking\n')
    lines.append('| Dimension | Winner | Why it stands out |')
    lines.append('|---|---|---|')
    lines.append('| Most clinically actionable | ⭐ D1 | Direct oncology/imaging relevance and potential treatment pathway implications. |')
    lines.append('| Best interpretability angle | ⭐ D2 | SHAP-based framing makes the model easier to scrutinize than black-box claims. |')
    lines.append('| Highest reread priority | ⭐ D1 | More likely to matter in translational / near-clinic discussions. |')
    lines.append('| Biggest validation caveat | ⭐ D2 | High reported performance but likely still heavily internal-validation dependent. |')
    lines.append('| Best overall digest theme | ⭐ 2026-04-05 | Interpretable, clinically adjacent AI rather than benchmark hype. |')
    (DIGESTS_DIR / 'ALL_DIGESTS_SHORT.md').write_text('\n'.join(lines) + '\n')


if __name__ == '__main__':
    write_reviews_short()
    write_digests_short()
    print('Updated short index files.')
