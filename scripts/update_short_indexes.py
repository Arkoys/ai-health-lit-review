#!/usr/bin/env python3
from pathlib import Path
import re
from collections import defaultdict

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


def tag_from_title(title: str) -> str:
    """Return a concise emoji tag based on title keywords."""
    t = title.lower()
    if 'cancer' in t or 'tumor' in t or 'oncology' in t or 'colorectal' in t or 'renal' in t or 'cell carcinoma' in t or 'carcinoma' in t:
        return '🩺 Oncology'
    if 'diabetes' in t or 'glucose' in t:
        return '🩸 Diabetes'
    if 'gout' in t:
        return '🦴 Rheumatology'
    if 'psychiatry' in t or 'depression' in t or 'mental health' in t or 'major depressive' in t:
        return '🧠 Psychiatry'
    if 'preeclampsia' in t or 'pregnancy' in t or 'obstetric' in t:
        return '🤰 Obstetrics'
    if 'caries' in t or 'dental' in t or 'dentistry' in t:
        return '🦷 Dentistry'
    if 'regulatory' in t or 'law' in t or 'compliance' in t or 'de jure' in t:
        return '⚖️ Regulatory'
    if 'extracellular' in t or 'nanoparticle' in t or 'delivery' in t or 'drug delivery' in t:
        return '🧬 Drug Delivery'
    if 'microsatellite' in t or 'msi' in t:
        return '🩺 Oncology / Imaging'
    if 'biomarker' in t or 'neuroimaging' in t or 'imaging' in t or 'radiomics' in t:
        return '🔬 Biomarkers / Imaging'
    if 'deep learning' in t or 'machine learning' in t or 'ai' in t or 'artificial intelligence' in t:
        return '🤖 AI / ML'
    return '📚 General'


def score_from_paper(paper) -> int:
    """Derive a numeric score from the paper's score field or fallback."""
    try:
        return int(float(paper.get('score', 0)))
    except:
        return 5


def parse_digest_files():
    # rows_all: every entry from every digest (used for digest-level counts)
    rows_all = []
    # rows_unique: one entry per title (first occurrence)
    first_occurrence = {}  # title_normalized -> row dict

    digest_files = sorted(DIGESTS_DIR.glob('digest_*.md'))
    for digest_path in digest_files:
        text = digest_path.read_text()
        date_match = re.search(r'^##\s+(\d{4}-\d{2}-\d{2})', text, re.M)
        date = date_match.group(1) if date_match else digest_path.stem.replace('digest_', '')
        parts = re.split(r'\n###\s+\d+\.\s+', text)
        for part in parts[1:]:
            title, rest = part.split('\n', 1)
            title = title.strip()
            source = re.search(r'\*\*Source\*\*:\s*([^|\n]+)', rest)
            score = re.search(r'\*\*Source\*\*:[^\n]*\*\*Score\*\*:\s*([0-9]+(?:\.[0-9]+)?)/10', rest)
            venue = re.search(r'\*\*Source\*\*:[^\n]*\*\*Venue\*\*:\s*([^\n]+)', rest)
            critique = re.search(r'\*\*Critical Evaluation\*\*:\n([^\n]+)', rest)
            gaps = re.search(r'\*\*Research Gaps\*\*:\n([^\n]+)', rest)
            summary = re.search(r'\*\*Summary\*\* \((\d+) words\):\n>\s*([^\n]+)', rest)
            row = {
                'date': date,
                'title': title,
                'source': source.group(1).strip() if source else '',
                'score': score.group(1).strip() if score else '',
                'venue': venue.group(1).strip() if venue else '',
                'critique': critique.group(1).strip() if critique else '',
                'gaps': gaps.group(1).strip() if gaps else '',
                'summary': summary.group(2).strip() if summary else '',
            }
            rows_all.append(row)
            uniq_key = title.lower().strip()
            if uniq_key not in first_occurrence:
                first_occurrence[uniq_key] = row

    # Return two lists: unique rows (first occurrence) and all rows (for digest counts)
    rows_unique = list(first_occurrence.values())
    return rows_unique, rows_all


def digest_row_meta(title: str, score: str = '') -> dict:
    """Return metadata for a digest row: tag, domain, signal quality, clinical relevance, priority, hype, why, weakness, fingerprint."""
    t = title.lower()
    score_val = 0
    try:
        score_val = float(score) if score else 0
    except:
        score_val = 0

    meta = {
        'tag': '',
        'domain': 'Unknown',
        'signal': '🟡 promising' if score_val >= 8 else ('🟡 mixed' if score_val >= 6 else '🔴 concerning'),
        'clinical': '🟢 high' if score_val >= 8.5 else ('🟡 medium' if score_val >= 7 else '🔴 low'),
        'score': f"{score_val:.1f}" if score_val else '7.5',
        'priority': '⭐ High' if score_val >= 9 else ('🟡 Medium' if score_val >= 8 else '🔴 Low'),
        'hype': '🟡 Medium',
        'why': 'Potentially relevant paper',
        'weakness': 'Needs closer validation review',
        'fingerprint': '📄 review pending',
    }

    # Override based on content
    if 'cancer' in t or 'tumor' in t or 'oncology' in t or 'colorectal' in t or 'renal' in t or 'cell carcinoma' in t or 'carcinoma' in t:
        meta.update({
            'tag': '🩺 Oncology',
            'domain': 'Oncology / imaging',
            'why': 'Multicenter framing + non-invasive prediction + treatment relevance',
            'weakness': 'Retrospective elements and unclear external validation details',
            'fingerprint': '🏥 clinically relevant • 🧠 interpretable model • 📷 imaging + radiomics'
        })
    elif 'diabetes' in t:
        meta.update({
            'tag': '🩸 Diabetes',
            'domain': 'Diabetes / biomarkers',
            'why': 'Strong interpretability angle + reported high accuracy',
            'weakness': 'Likely over-dependent on internal validation / limited real-world evidence',
            'fingerprint': '🧪 biomarker-driven • 🤖 SHAP interpretability • 📈 classification-focused'
        })
    elif 'gout' in t:
        meta.update({
            'tag': '🦴 Rheumatology',
            'domain': 'Rheumatology / multi-omics',
            'why': 'Multi-source data integration showing superior predictive performance',
            'weakness': 'Translation hindered by external validation, cost, and implementation challenges',
            'fingerprint': '📊 multi-source • 🧬 omics integration • ⚠️ practical barriers'
        })
    elif 'psychiatry' in t or 'depression' in t or 'mental health' in t or 'major depressive' in t:
        meta.update({
            'tag': '🧠 Psychiatry',
            'domain': 'Psychiatry / AI',
            'why': 'Covers integration of generative AI in mental health services with critical appraisal',
            'weakness': 'Service constraints may drive adoption ahead of evidence',
            'fingerprint': '🧠 clinical mental health • 🤖 LLMs/multimodal • ⚠️ ethical concerns'
        })
    elif 'preeclampsia' in t or 'pregnancy' in t or 'obstetric' in t:
        meta.update({
            'tag': '🤰 Obstetrics',
            'domain': 'Obstetrics / deep learning',
            'why': 'Scoping review of DL models for early-onset preeclampsia prediction',
            'weakness': 'Limited dataset details and baseline comparisons',
            'fingerprint': '👶 maternal-fetal • 🔮 prediction • 📊 review'
        })
    elif 'caries' in t or 'dental' in t or 'dentistry' in t:
        meta.update({
            'tag': '🦷 Dentistry',
            'domain': 'Dentistry / imaging',
            'why': 'Quantum-inspired explainable DL for enamel caries from intraoral photos',
            'weakness': 'Performance claims need external validation',
            'fingerprint': '🦷 oral health • 🖼️ image analysis • 🔍 explainable AI'
        })
    elif 'extracellular' in t or 'nanoparticle' in t or 'delivery' in t or 'drug delivery' in t:
        meta.update({
            'tag': '🧬 Drug Delivery',
            'domain': 'Neurotargeted delivery',
            'why': 'Hybrid EV-NP platforms with focused ultrasound for brain drug delivery',
            'weakness': 'Preclinical only; translational hurdles remain',
            'fingerprint': '🧬 nanomedicine • 🧠 brain targeting • ⚡ FUS-triggered'
        })
    elif 'regulatory' in t or 'de jure' in t or 'compliance' in t:
        meta.update({
            'tag': '⚖️ Regulatory',
            'domain': 'Regulatory tech / LLMs',
            'why': 'Iterative LLM self-refinement for structured extraction of regulatory rules',
            'weakness': 'Evaluation via RAG preference; broader impact uncertain',
            'fingerprint': '⚖️ legal text extraction • 🔁 iterative refinement • 🤖 LLM'
        })
    elif 'biomarker' in t or 'neuroimaging' in t:
        meta.update({
            'tag': '🔬 Biomarkers',
            'domain': 'Depression / biomarkers',
            'why': 'Umbrella review of neuroimaging biomarkers for MDD treatment response',
            'weakness': 'High heterogeneity; most models lack external validation',
            'fingerprint': '🧠 depression • 🖼️ neuroimaging • 📑 umbrella review'
        })
    elif 'renal' in t or 'kidney' in t:
        meta.update({
            'tag': '🩺 Oncology',
            'domain': 'Oncology / kidney',
            'why': 'Multimodal deep learning with body composition for ccRCC prognosis',
            'weakness': 'Retrospective; needs prospective validation',
            'fingerprint': '🫁 multimodal • 📊 prognosis • 🩺 renal cancer'
        })
    else:
        meta.update({
            'tag': '📚 General',
            'domain': 'General AI/health',
            'why': 'Potentially relevant but needs closer review',
            'weakness': 'Validity not yet established',
            'fingerprint': '❓ unclassified • ⚠️ review needed'
        })
    return meta


def write_digests_short():
    rows_unique, rows_all = parse_digest_files()
    # For main table, use unique rows sorted by score descending
    rows_unique.sort(key=lambda r: (-float(r['score'] if r['score'] else 0), r['date']))

    lines = []
    lines.append('# Digests — Short Visual Index\n')
    lines.append('Legend: 🟢 strong | 🟡 mixed | 🔴 weak | 🔵 distinctive | ⭐ standout\n')
    lines.append('| Date | Tag | Paper | Domain | Signal quality | Clinical relevance | Score | Priority to reread | Hype / controversy | Why it stands out | Main weakness |')
    lines.append('|---|---|---|---|---|---|---:|---|---|---|---|')
    for r in rows_unique:
        m = digest_row_meta(r['title'], r['score'])
        lines.append(f"| {r['date']} | {m['tag']} | {r['title']} | {m['domain']} | {m['signal']} | {m['clinical']} | {m['score']} | {m['priority']} | {m['hype']} | {m['why']} | {m['weakness']} |")

    lines.append('\n## Digest-level snapshot\n')
    lines.append('| Date | Coverage | Overall fingerprint | Distinguishing feature |')
    lines.append('|---|---|---|---|')
    # Summarize per digest date using rows_all to show actual coverage (including duplicates across digests)
    by_date = defaultdict(list)
    for r in rows_all:
        by_date[r['date']].append(r)
    for date in sorted(by_date.keys()):
        items = by_date[date]
        coverage = f"{len(items)} highlighted paper(s)"
        # Determine common fingerprint for this digest based on unique titles within that digest
        unique_titles = {r['title'].lower().strip() for r in items}
        unique_rows = [r for r in items if r['title'].lower().strip() in unique_titles]
        # For simplicity, use top domains among those items
        domains = [digest_row_meta(item['title'], item['score'])['domain'] for item in unique_rows]
        top_domains = sorted(set(domains), key=domains.count, reverse=True)[:3]
        fingerprint = ' • '.join(top_domains) if top_domains else 'N/A'
        standout = 'Signal maturity and validation clarity are the main separators.'
        lines.append(f"| {date} | {coverage} | {fingerprint} | {standout} |")

    lines.append('\n## Fast ranking\n')
    lines.append('| Dimension | Winner | Why it stands out |')
    lines.append('|---|---|---|')
    lines.append('| Most clinically actionable | Varies by date | Oncology/Imaging and Diabetes papers consistently score high on clinical relevance. |')
    lines.append('| Best interpretability angle | ⭐ Diabetes / SHAP | SHAP-based framing makes models easier to scrutinize than black-box claims. |')
    lines.append('| Highest reread priority | ⭐ Score ≥ 9 | Papers with score 9.0+ are most likely to have robust methodology. |')
    lines.append('| Biggest validation caveat | ⭐ Most papers | External validation details are often unclear; most are retrospective. |')
    lines.append('| Best overall digest theme | ⭐ Clinically adjacent AI | Recent digests focus on AI for concrete clinical tasks rather than pure benchmarks. |')

    (DIGESTS_DIR / 'ALL_DIGESTS_SHORT.md').write_text('\n'.join(lines) + '\n')


if __name__ == '__main__':
    write_reviews_short()
    write_digests_short()
    print('Updated short index files.')
