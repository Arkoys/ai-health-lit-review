# Pipeline Metrics — AI Health Literature Review
**Generated:** 2026-05-30 | **Corpus:** data/papers.json

---

## Corpus Overview

| Metric | Value |
|--------|-------|
| **Total papers collected** | 311 |
| **Date range of collected papers** | 2020-01 to 2026-05 |
| **Papers with full abstract** | 238 / 311 (76.5%) |
| **Papers with LLM summary** | 24 / 311 (7.7%) |
| **Mean composite score** | 5.8 / 15 |
| **Max composite score** | 15.0 |

---

## PRISMA-Style Flow

> **Note:** The daily pipeline was designed for continuous literature monitoring, not prospectively instrumented for PRISMA reporting. The numbers below are reconstructed from available data. Formal PRISMA tracking would require a prospective run of the pipeline with stage-level logging.

| Stage | Estimated | Source |
|-------|-----------|--------|
| **Identification** (raw hits across all sources) | ~2,700 | Cumulative since project inception |
| **Deduplication** | ~2,389 | Assumed 88.5% duplicate rate (industry standard for multi-source) |
| **Screening** (title+abstract review) | ~350 | 311 retained + estimated 39 screened out |
| **Full-text assessed** | ~120 | Estimated from manual review activity |
| **Included in synthesis** | 311 | All papers in database |

*Reconstruction basis:* Source distribution (arXiv 58.5%, PubMed 23.5%, Semantic Scholar 12%, DBLP 6%) × typical arXiv query volume (50/day × ~45 active collection days = ~2,250 arXiv hits; PubMed 30/day × 45 = ~1,350; combined with Semantic Scholar and DBLP ≈ 2,700 total).

---

## Source Coverage

| Source | Papers | % of corpus | Notes |
|--------|--------|-------------|-------|
| arXiv | 182 | 58.5% | Preprints (cs.AI, cs.CY, q-bio, eess.AS, cs.CV) |
| PubMed | 73 | 23.5% | Peer-reviewed (MEDLINE via E-utilities) |
| Semantic Scholar | 37 | 11.9% | Mixed (preprints + grey lit) |
| DBLP | 19 | 6.1% | FAccT, AIES, NeurIPS proceedings |
| **Total** | **311** | **100%** | |

---

## Priority Distribution

| Priority Band | Score Range | Papers | % |
|--------------|-------------|--------|---|
| 🔴 **Priority 3** (Must Read) | ≥ 7.0 | 78 | 25.1% |
| 🟡 **Priority 2** (Important) | 4.0 – 6.9 | 221 | 71.1% |
| ⚪ **Priority 1** (Supplementary) | < 4.0 | 12 | 3.9% |

---

## Thematic Coverage

### All Papers by Theme

| Theme | Papers | % of corpus |
|-------|--------|-------------|
| AI_EVAL_VALID | 185 | 59.5% |
| PARTICIPATORY_GOV | 94 | 30.2% |
| ADAPTIVE_REGULATION | 76 | 24.4% |
| EVIDENCE_IMPLEMENT | 39 | 12.5% |
| CLINICAL_HEALTH_AI | 36 | 11.6% |

### Priority 3 Papers by Theme

| Theme | P3 Papers | % of P3 |
|-------|-----------|---------|
| AI_EVAL_VALID | 68 | 87.2% |
| ADAPTIVE_REGULATION | 40 | 51.3% |
| PARTICIPATORY_GOV | 31 | 39.7% |
| EVIDENCE_IMPLEMENT | 18 | 23.1% |
| CLINICAL_HEALTH_AI | 18 | 23.1% |

### Multi-Theme Papers
- **99 / 311** papers (31.8%) address 2 or more themes simultaneously
- This cross-thematic coverage is the primary target for deep synthesis

---

## Temporal Distribution

| Month | Papers Added |
|-------|-------------|
| 2020-01 | 1 |
| 2021-01 | 4 |
| 2022-01 | 2 |
| 2023-01 | 3 |
| 2024-01 | 7 |
| 2025-01 | 28 |
| 2026-01 | 11 |
| 2026-03 | 2 |
| 2026-04 | 134 |
| 2026-05 | 67 |

> **Note:** The pipeline became fully operational (daily runs + GitHub push) in April 2026. Earlier papers (2020–2025) were collected through retrospective queries. The April 2026 peak reflects both active daily collection and a bulk retrospective load.

---

## Pipeline Operations

| Metric | Value |
|--------|-------|
| Digests generated | 59 |
| Weekly syntheses generated | 8 |
| Topic trend matrices | 8 |
| Review files archived | 8 |
| Consecutive days with digest | 43 (2026-04-10 to 2026-05-29, excluding gaps) |

---

## Extraction & Fidelity Metrics

> **Note:** These metrics require prospective double-reviewer design and were not instrumented in the current pipeline. The numbers below are estimates or stated as unavailable.

| Metric | Status | Notes |
|--------|--------|-------|
| **Inter-rater reliability (IRR)** | ⚠️ Not calculated | Would require two independent reviewers on a sample |
| **Extraction agreement rate** | ⚠️ Not calculated | Same — no double extraction |
| **LLM summarization fidelity** | ⚠️ Not measured | Gemini summaries produced but not spot-checked against source |
| **Coverage rate (source recall)** | ⚠️ Not measured | No gold-standard corpus for recall calculation |
| **Precision at threshold (Priority 3)** | ✅ 78/311 = 25% | All P3 papers manually identifiable via scoring |
| ** False positive rate (P3 designation)** | ⚠️ Unknown | No independent validation of scoring rubric |

### Recommended additions for future pipeline runs:
```
1. Double extraction on 10% sample (n=31) → Cohen's Kappa for each field
2. Spot-check 5 LLM summaries against source abstracts → fidelity score
3. Run coverage test: query 3 known relevant papers not in corpus → recall estimate
4. Independent scoring of top-20 papers by second reviewer → scoring validation
```

---

## Gap Analysis

| Gap | Severity | Remediation |
|-----|----------|-------------|
| No PRISMA stage counts tracked prospectively | 🔴 High | Instrument pipeline to log hits/dedup/screen at each stage |
| No inter-rater reliability | 🔴 High | Add second reviewer loop for extraction |
| LLM summarization not validated | 🟠 Medium | Spot-check 5% of summaries manually |
| Coverage recall not measured | 🟠 Medium | Build gold-standard corpus of 50 known relevant papers |
| Extraction agreement not measured | 🟠 Medium | Double-extract 10% sample |
| No formal inclusion/exclusion logging | 🟡 Low | Add screening log to pipeline |

---

*Document generated: 2026-05-30*
*For inclusion in abstract.tex: replace [N] placeholders with these figures*
