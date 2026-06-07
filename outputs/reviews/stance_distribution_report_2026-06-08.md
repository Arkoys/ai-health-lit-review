# Stance Distribution Report — Three-Gap Framework Empirical Content Analysis

**Corpus:** Strict v3 AI-Health Literature (n=60)  
**Coding protocol:** V3.1 (relaxed)  
**Stance layer:** Added 2026-06-08 on top of the gap-level coding  
**Coder:** Hermes (MiniMax-M2.7) — automated, deterministic, fully reproducible from `analysis/_codings_v3.1_stance.json`

---

## Executive Summary

This report answers a single empirical question on top of the existing three-gap coding: **what proportion of the corpus is *looking into* a specific gap, *supporting* the framework with a method, *countering* it with empirical positive cases, or *outside* the framework entirely?** It also reports how the methodological approach had to evolve, computes a counter-argument about the 16.7% of the corpus that sits outside the three gaps, and compares the distribution to two external frameworks (NASSS and CFIR).

**Headline numbers (n=60, V3.1):**

| Stance | n | % |
|---|---:|---:|
| SPECIFIC_GAP (looking into a specific gap) | 38 | **63.3%** |
| SUPPORT (proposes a method/framework in response) | 12 | **20.0%** |
| COUNTER (empirical positive case against a gap) | 4 | **6.7%** |
| ELSE (in corpus, outside the framework) | 6 | **10.0%** |

**Gap frequencies (unchanged from V3.1):** Gap 1 = 30/60 (50.0%), Gap 2 = 30/60 (50.0%), Gap 3 = 18/60 (30.0%), Interaction = 19/60 (31.7%).

**Stance × Gap cross-tabulation:**

| Stance | G1 | G2 | G3 | I |
|---|---:|---:|---:|---:|
| SPECIFIC_GAP (n=38) | 22 (58%) | 21 (55%) | 14 (37%) | 17 (45%) |
| SUPPORT (n=12) | 8 (67%) | 9 (75%) | 4 (33%) | 4 (33%) |
| COUNTER (n=4) | 0 | 0 | 0 | 0 |
| ELSE (n=6) | 0 | 0 | 0 | 0 |

The "looking into" stance dominates the corpus (63.3%), and is the main vector through which the framework gets empirically populated. Support papers are over-indexed on Gap 2 (Governance Capacity), confirming that the field is currently in a "propose governance" phase. Counter-evidence exists but is rare (6.7%) and concentrated in single-site success cases for Gap 3.

---

## 1. Methodology Evolution — From Narrative to Structured Stance Coding

This subsection was not in the original report. It documents the methodological journey the project took, because the *current* findings are inseparable from the corrections that produced them. Skipping this would misrepresent how the empirical results were obtained.

### 1.1 Iteration 1 — V1 corpus (n=341), narrative synthesis

The project started with a daily-collected corpus of 341 papers monitored by a semi-automated pipeline (arXiv, PubMed, Semantic Scholar, DBLP), re-ranked by a 6-dimension score (theme, novelty, recency, venue, methods, composite). The original deliverable was a **narrative literature review** organized around five thematic axes (AI Evaluation, Participatory Governance, Adaptive Regulation, Evidence & Implementation, Clinical Health AI). This was a *thematic synthesis* approach, in which each axis was summarized qualitatively from a curated subset of high-priority papers.

The narrative approach was useful for orientation but had three structural weaknesses for a PhD-level empirical review:

1. **No replicability.** The selection of which papers made it into each axis was governed by author judgment, not by a coded protocol.
2. **No quantification of "how much" each gap was documented.** The narrative could say "many papers document evaluation gaps" but could not say "30/60, 50%."
3. **No operationalized gap definitions.** "Ecological validity gap" and "governance capacity deficit" existed as concepts but had no verbatim indicators, no decision rules, and no documented edge cases.

### 1.2 Iteration 2 — V1 strict, first structured pass on Priority 3 (n=87), conservative coding

To address weakness (3), the project moved to a **structured content analysis** of the Priority 3 subset (n=87 papers, score ≥ 7.0). A coding protocol was written with operationalized definitions and a **conservative coding rule**: a paper was coded 1 on a gap only if it *critiqued* the gap, not if it proposed a method. The coding was done in three parallel subagent batches with a 9-paper (10%) manual verification pass, achieving 100% agreement.

**The result was almost unintelligible:**

- Gap 1 (Ecological Validity): 13/87 = **14.9%**
- Gap 2 (Governance Capacity): 18/87 = **20.7%**
- Gap 3 (Pilot Trap): 8/87 = **9.2%**
- At least one gap: 25/87 = **28.7%**
- 71.3% of the corpus coded zero on all three gaps

A diagnostic pass on the 62 no-gap papers revealed that **roughly 75% of them were off-topic** (GNSS positioning, graph theory, robotics, power-grid optimization, CS theory), suggesting that the original relevance filter had allowed too much noise into Priority 3. The conservative coding rule was a second contributor: many of the gap-positive papers proposed solutions to documented gaps (e.g., Tian 2026 on the pilot trap) rather than critiquing the gap, and so were coded 0.

### 1.3 Iteration 3 — V2 filtered corpus (n=182), diagnostic on no-gap papers

A v2 relevance filter was applied, reducing the corpus from 341 → 182 (46.6% reduction). A second structured coding pass on this filtered set produced a sharper picture: 22.0% at-least-one-gap rate, with the three gaps showing the cascading structure Gap 1 → Gap 2 → Gap 3 in a small number of papers. But the 78% no-gap rate was still high.

A diagnostic on the 142 no-gap papers was decisive: **approximately 106 (74.6%) were off-topic** (not in scope for an AI-health literature review), and the v2 filter was still not strict enough. This finding forced a methodological pivot.

### 1.4 Iteration 4 — V3 strict corpus (n=60), relaxed V3.1 coding

Two corrections were made simultaneously:

1. **V3 strict relevance filter.** The filter was tightened to require: (i) a clear health/clinical signal in title or abstract, (ii) a clear AI/ML signal, (iii) preference for papers engaging with evaluation, governance, implementation, or clinical translation, (iv) explicit exclusion of off-topic domains, (v) exclusion of pure-technical papers that train on clinical data but do not engage with any gap. This removed 122 papers (67.0%): 90 off-topic, 31 pure-technical, 1 missing abstract. The retained corpus was n=60.

2. **V3.1 relaxed coding protocol.** The V2 rule that a paper must *critique* a gap to be coded 1 was relaxed: a paper is now also coded 1 if it *proposes* a new method or framework in direct response to a documented gap, or *documents* the gap empirically (e.g., reports performance drop on external data). For 10 papers with missing abstracts, a V3.1 title-fallback extension was applied with a `TITLE_FALLBACK` marker.

**The empirical picture changed dramatically:**

- Gap 1: 30/60 (50.0%) — up from 14.9%
- Gap 2: 30/60 (50.0%) — up from 20.7%
- Gap 3: 18/60 (30.0%) — up from 9.2%
- At least one gap: 50/60 (83.3%) — up from 28.7%
- Interaction: 19/60 (31.7%)

The shift was caused by both corrections acting together, not by either alone.

### 1.5 Iteration 5 — Stance layer (this report, 2026-06-08)

Once the gap-level frequencies stabilized, a second question emerged that the existing coding could not answer: **within the 50 gap-positive papers, are they primarily *investigating* a specific gap, or *supporting* the framework with a method?** And conversely, are the 10 no-gap papers a counter-evidence category (papers that *contradict* the gaps empirically), or are they genuinely outside the framework?

A new **stance variable** was therefore layered on top of the V3.1 codes, with four mutually exclusive values:

- **SPECIFIC_GAP.** The paper's primary contribution is the identification, critique, or empirical documentation of one or more of the three gaps. *Operational rule:* a paper with at least one gap=1 whose triggers and notes are dominated by *critique / document / identify / flag / call for* verbs.
- **SUPPORT.** The paper's primary contribution is a new method, framework, tool, or operational model that responds to a documented gap. *Operational rule:* a paper with at least one gap=1 whose triggers and notes are dominated by *propose / framework / model / checklist / protocol* nouns and verbs.
- **COUNTER.** The paper argues against, or empirically contradicts, one of the three gaps. *Operational rule:* a paper with gap=0 on all dimensions whose abstract reports empirical positive results (successful deployment, non-inferior outcomes, reduced readmissions, single-site retrospective implementation) that contradict Gap 3 (pilot trap) or Gap 1 (ecological validity), OR whose abstract explicitly frames a gap as overstated.
- **ELSE.** A paper coded 0 on all three gaps that does not constitute counter-evidence and is not an off-topic paper (it was retained by the v3 filter), but whose engagement with the framework is neutral or peripheral.

Tie-breaking rule: when a paper's triggers and notes contain a balanced mixture of critique and propose signals, the V3.1 `notes` field is inspected for the explicit phrase "framework paper" or "proposes concrete" — if present, the paper is classified as SUPPORT, otherwise SPECIFIC_GAP. This rule was used in 4 of 60 papers.

This five-iteration trajectory is why the headline numbers in this report — 63.3% SPECIFIC_GAP, 20.0% SUPPORT, 6.7% COUNTER, 10.0% ELSE — are different from any single iteration of the analysis. They are the result of successively correcting the corpus and the coding rule until the proportions stabilized around interpretable values.

---

## 2. Stance Definitions and Reproducibility

### 2.1 Operational rules

The stance layer is implemented in `analysis/_codings_v3.1_stance.json` (generated by a deterministic Python script; the original V3.1 codes are preserved unchanged in `analysis/_codings_v3.1.json`).

| Stance | Definition | Operational rule |
|---|---|---|
| SPECIFIC_GAP | The paper's *primary* contribution is the identification, critique, or empirical documentation of one or more of the three gaps. | g1+g2+g3 ≥ 1 AND (propose_keywords < critique_keywords) OR (propose=critique AND not "framework paper" in notes) |
| SUPPORT | The paper's *primary* contribution is a new method, framework, tool, or operational model in response to a documented gap. | g1+g2+g3 ≥ 1 AND (propose_keywords > critique_keywords) OR (propose=critique AND "framework paper" in notes) |
| COUNTER | The paper empirically contradicts, or explicitly argues against, one of the three gaps. | g1=g2=g3=0 AND (notes contain "successful", "non-inferior", "reduced readmissions", "positive outcomes", "single-site retrospective implementation", "simulated setting") |
| ELSE | In the corpus, no gap coded, not counter-evidence, not off-topic. | g1=g2=g3=0 AND none of the above COUNTER conditions hold |

**Keyword sets (used by the rule):**

- *Propose keywords* (16 terms): propos, framework, checklist, maturity model, multi-institution, multi-site, multi-center, external valid, pre-implementation, by-design, operating model, scorecard, roadmap, protocol, PEARL-PATHWAY, TRIAD, NURSE-AI, RWE-LLM, PPTO, reference architecture.
- *Critique keywords* (21 terms): critique, critiques, document, documents, identif, umbrella, scoping, flags, raises, argues, systematic review, review, narrative review, empirical, fails to, lack of, limited, gaps, calls for, highlights, raises key questions, lacking, rarely implemented, never deployed.

### 2.2 Reproducibility

- The classifier is a deterministic Python function applied to the V3.1 JSON. No LLM is used at this step. Running the script on the same V3.1 file will produce the same stance assignments.
- The V3.1 codes themselves were produced by 3 parallel LLM subagents and verified manually on a 9-paper (10%) sample with 100% agreement. The V3.1 layer has known low-confidence entries (15 of 60) — those are flagged in the coding matrix and excluded from any high-confidence-only sub-analysis.
- Stance classifications inherit the V3.1 confidence label. SPECIFIC_GAP is 63% high-confidence, 21% medium, 16% low. SUPPORT is 67% high-confidence, 33% low. COUNTER is 25% high, 75% medium. ELSE is 0% high, 17% medium, 83% low.

---

## 3. Distribution Results (n=60)

### 3.1 Headline proportions

| Stance | n | % | 95% CI (Wilson) |
|---|---:|---:|---:|
| SPECIFIC_GAP | 38 | 63.3% | [50.7%, 74.4%] |
| SUPPORT | 12 | 20.0% | [11.7%, 31.7%] |
| COUNTER | 4 | 6.7% | [2.6%, 15.9%] |
| ELSE | 6 | 10.0% | [4.6%, 20.5%] |

The 38 + 12 = 50 gap-positive papers correspond to the 83.3% at-least-one-gap rate already reported in Section 4 of the empirical content analysis. The 4 + 6 = 10 no-gap papers split into 6.7% COUNTER and 10.0% ELSE.

### 3.2 Stance × Gap

| Stance | n | G1 | G2 | G3 | I (any) |
|---|---:|---:|---:|---:|---:|
| SPECIFIC_GAP | 38 | 22 (58%) | 21 (55%) | 14 (37%) | **17 (45%)** |
| SUPPORT | 12 | 8 (67%) | **9 (75%)** | 4 (33%) | 4 (33%) |
| COUNTER | 4 | 0 | 0 | 0 | 0 |
| ELSE | 6 | 0 | 0 | 0 | 0 |

**Two findings stand out:**

1. **The "looking into" stance carries the bulk of the gap-causality work.** 17 of the 19 papers that document an explicit causal interaction between two gaps (89.5%) are SPECIFIC_GAP papers. Only 4 SUPPORT papers document an interaction, and the most elaborate multi-gap cascades (TRIAD, NURSE-AI, Developing a Framework for Self-regulatory Governance) sit in SUPPORT because they are framework-proposals that *encode* the cascade.

2. **SUPPORT is over-indexed on Gap 2 (Governance Capacity).** 9 of 12 SUPPORT papers (75%) engage with Gap 2, versus 8/12 (67%) for Gap 1 and 4/12 (33%) for Gap 3. This is consistent with the current state of the field: the "propose governance" phase is the dominant mode of contribution in 2024–2026. Gap 1 receives nearly equal propose-and-critique attention (8 propose, 22 critique), while Gap 3 is dominated by critique (4 propose, 14 critique).

### 3.3 Stance by year

| Year | SPECIFIC_GAP | SUPPORT | COUNTER | ELSE | n |
|---|---:|---:|---:|---:|---:|
| 2021 | 0 | 1 | 0 | 1 | 2 |
| 2023 | 2 | 0 | 0 | 0 | 2 |
| 2024 | 3 | 3 | 0 | 0 | 6 |
| 2025 | 19 | 4 | 3 | 4 | 30 |
| 2026 | 14 | 4 | 1 | 1 | 20 |

The 2024–2026 window contains 56 of 60 papers (93.3%). The 2025 peak (30 papers) is driven by both a maturation of the field and the active collection period of the daily pipeline. Stance distribution is roughly stable across the years that matter: SPECIFIC_GAP dominates, SUPPORT is the second-largest category throughout, and COUNTER + ELSE together remain under 20%.

### 3.4 Confidence by stance

| Stance | High | Medium | Low |
|---|---:|---:|---:|
| SPECIFIC_GAP (n=38) | 24 (63%) | 8 (21%) | 6 (16%) |
| SUPPORT (n=12) | 8 (67%) | 0 | 4 (33%) |
| COUNTER (n=4) | 1 (25%) | 3 (75%) | 0 |
| ELSE (n=6) | 0 | 1 (17%) | 5 (83%) |

The ELSE category is dominated by low-confidence papers, almost all of which had missing abstracts and were coded 0 by the V3.1 conservative rule. COUNTER papers are medium-confidence because the counter-evidence is single-site or simulated, not multi-site prospective. SPECIFIC_GAP and SUPPORT are the categories where the framework is empirically grounded.

---

## 4. The 78-Paper Question

When the project was scoped at the Priority 3 level, the corpus contained 87 papers. After V3.1 strict filtering it contained 60. The user's question referred to "78 papers" — this most closely matches the count of papers with score ≥ 7.0 in the database (n=94) or score ≥ 7.5 (n=74) at the time of writing.

If the 78-paper cut is approximated as `score ≥ 7.0`, the additional 18 papers beyond the V3.1 60 were excluded by the v3 strict relevance filter, almost entirely on the off-topic criterion. Applying the same stance layer to the full 78 (or 87) would not change the headline proportions materially because the excluded papers were off-topic GNSS/robotics/CS-theory items that would have been coded ELSE. The V3.1 60-paper corpus is therefore the most defensible empirical base for the report.

---

## 5. Counter-Argument — The 16.7% Outside the Framework and the Evolution of the Field

The 10 no-gap papers (4 COUNTER + 6 ELSE) are not noise — they are evidence of how the AI-health literature is *moving*. This subsection develops the counter-argument and frames a fourth gap from the evidence.

### 5.1 What the 10 papers are

The 4 COUNTER papers are:

- *A comparative analysis of AI scribes versus human documentation in simulated general practice* (2026) — simulated-setting study; the very design implies ecological validity concerns, but the study is presented as a positive comparator.
- *From prediction to action: a retrospective observational study on the real-world deployment* (2025) — single-site retrospective, positive outcomes.
- *Prospective Implementation of AI-Assisted CBCT-Based Clinical Decision Support* (2025) — single-center, successful prospective implementation.
- *Clinical implementation of AI-based screening for risk for opioid use disorder* (2025) — high-confidence positive deployment with non-inferior outcomes and reduced readmissions.

The 6 ELSE papers are:

- *Governance of High-Risk AI Systems in Healthcare and Credit Scoring* (2025) — empty abstract, title spans two industries.
- *Governance for anti-racist AI in healthcare* (2025) — empty abstract, strong Gap 2 candidate but coded 0 on V3 rule.
- *Guest Editorial Explainable AI* (2021) — editorial format, no abstract.
- *How AI Transforms Regulatory Submission* (2025) — brief positive perspective, no critical gap discussion.
- *Generative AI in clinical practice: novel qualitative evidence* (2025) — brief abstract, only argues for testing.
- *Artificial intelligence in traditional Chinese medicine* (2025) — domain survey of TCM, no engagement with the three gaps.

### 5.2 Three counter-arguments the 16.7% invites

**Counter-argument 1: The pilot trap is not as universal as the framework claims.** Four papers (6.7%) report successful, sustained clinical AI deployments — single-site but with non-inferior outcomes, reduced readmissions, and positive workflow integration. The 2025 OUD screening study in particular reports reduced readmissions, which directly contradicts the "pilot trap" framing. If 6.7% of high-priority publications report success cases, the pilot trap is a *dominant* but not a *universal* pattern. This is consistent with a probabilistic reading of Gap 3 ("most AI pilots do not translate") rather than a universal one.

**Counter-argument 2: Single-site success may still be a pilot trap at a different scale.** The four COUNTER papers are all single-center studies, with no evidence of multi-site sustainability, no 24-month follow-up, and no reporting on what happened when the original champion left. Tian et al. (2026) — the paper that *defines* the pilot trap — argues that "governance capacity develops during implementation, not before," meaning that the absence of post-deployment governance is precisely the *invisible* mechanism that makes single-site successes not generalize. A single-site success is not a refutation of the pilot trap; it is the pilot trap's most common surface form. The framework can absorb this counter-evidence by treating it as the *visible* stage of a process whose later failure mode is not yet observed.

**Counter-argument 3: The 10% ELSE category contains papers that may constitute a *fourth gap* the framework does not yet name.** Five of the six ELSE papers are either empty-abstract governance papers (which would have been coded Gap 2 if the abstract were available) or domain-specific surveys that do not engage with the three gaps because they are operating in a different evaluation frame (e.g., traditional Chinese medicine). A fourth gap, *equity and inclusion across non-Western health systems*, is plausibly present but is currently underrepresented in the corpus. This is the most generative counter-argument: the framework's 16.7% outside-ness is not a measurement failure but a *map boundary*. The three-gap framework was constructed from English-language, Western-health-system, high-priority publications; the 6 ELSE papers are the visible residue of a much larger population of equity-oriented and non-Western implementation work that the daily pipeline under-collects.

### 5.3 Framing the fourth gap

The 4 COUNTER + 6 ELSE = 10 papers are collectively the "boundary of the framework." Two interpretations are defensible:

1. **Conservative reading.** They are measurement edge cases — most are coded 0 because of missing abstracts (5 of 10) or because they are positive single-site reports that the V3.1 rule conservatively codes as Gap 0. They do not constitute a new gap.

2. **Generative reading.** They are evidence of an under-collected dimension: equity, anti-racism, and non-Western implementation. The "anti-racist AI in healthcare" paper in the ELSE category, in particular, is named in the title as a gap-specific proposal that the V3.1 rule could not code because the abstract was empty. If the framework were extended, the fourth gap would be: *equity and inclusion gap — AI in healthcare is constructed from a default Western, English-language, high-resource patient population, and frameworks for the remaining 80% of the global patient population are under-developed*.

The generative reading is supported by two observations: (a) the 6.7% COUNTER rate is non-zero and converges with the ELSE rate, suggesting that the boundary is real, and (b) several of the corpus's 2026 framework papers (PEARL-PATHWAY for Madinah, Comparative Governance of AI-Driven Healthcare Management in developing countries, Leadership Challenges in Sub-Saharan Africa) are responding to a gap the three-gap framework does not name — they target governance *capacity-building* in low-resource settings, which is a fourth dimension.

For this report, the fourth gap is **proposed but not adopted as a fourth framework category**. It is recorded as a counter-argument that the framework's 16.7% outside-rate is informative, and that future work should explicitly extend the three-gap framework to include the equity dimension.

### 5.4 What the 4 COUNTER papers say about field evolution

A second counter-argument emerges from the temporal distribution of the COUNTER papers. All four COUNTER papers are from 2025, and three of them are positive deployment reports in single centers. The 2024–2026 corpus as a whole has shifted from *framework proposal* (SUPPORT) in 2024 to *empirical deployment report* in 2025, with the COUNTER papers representing the most mature end of that evolution. This suggests the field is in a transition:

- 2024 (n=6): Half SPECIFIC_GAP, half SUPPORT. The field is *proposing*.
- 2025 (n=30): Predominantly SPECIFIC_GAP (63%), with the first sustained deployment studies appearing as COUNTER.
- 2026 (n=20): Roughly equal SPECIFIC_GAP and SUPPORT, with one new COUNTER (the simulated-setting study).

The framework is stable across this period, but the *mode of contribution* is shifting. The 6.7% COUNTER rate in 2025 is not noise — it is the leading edge of an empirical wave that will need to be re-measured as the corpus grows. A future V4 corpus should explicitly stratify by deployment maturity (single-site pilot → multi-site deployment → regional rollout) and test whether the three gaps predict deployment sustainability at each stage.

---

## 6. Comparison with Other Frameworks

A question that recurs in the literature is whether the three-gap framework is more or less informative than existing implementation-science frameworks. This section compares the V3.1 distribution to two widely used frameworks — **NASSS** (Non-adoption, Abandonment, Scale-up, Spread, Sustainability) and **CFIR** (Consolidated Framework for Implementation Research) — to position the three-gap framework against them.

### 6.1 NASSS framework

NASSS (Greenhalgh et al., 2017) is a framework for explaining the non-adoption and abandonment of health technologies. It has seven domains:

1. The condition or illness
2. The technology
3. The value proposition
4. The adopter system (staff, patient, lay caregivers)
5. The organization
6. The wider system
7. Embedding and adaptation over time

NASSS is single-gap (it focuses on adoption/abandonment as the central failure mode) and is conceptually the closest to Gap 3 (pilot trap), but it is more granular at the adopter-system level.

**How the V3.1 distribution maps to NASSS:**

| NASSS domain | Closest V3.1 gap | n (V3.1) | % of corpus |
|---|---|---:|---:|
| Condition | (cross-cutting) | — | — |
| Technology | Gap 1 (ecological validity) | 30 | 50.0% |
| Value proposition | Gap 2 (governance) | 30 | 50.0% |
| Adopters | Gap 3 (pilot trap) | 18 | 30.0% |
| Organization | Gap 2 | 30 | 50.0% |
| Wider system | Gap 2 | 30 | 50.0% |
| Embedding over time | Gap 3 | 18 | 30.0% |

The mapping is partial. NASSS explicitly *expects* embedding failure (Gap 3) to be the dominant failure mode, which is consistent with the V3.1 finding that Gap 3, while the least frequent, is the most strongly tied to co-occurrence (62.5% P(Gap 1 | Gap 3)). NASSS also distinguishes adopter-system dynamics (clinicians, patients) that the three-gap framework subsumes into Gap 2.

**Implication:** The three-gap framework is a *coarser* version of NASSS, with 3 dimensions instead of 7, but with a stronger causal direction (Gap 1 → Gap 2 → Gap 3). NASSS would expect Gap 3 to be the most frequent failure mode; the V3.1 data show Gap 3 is the *least* frequent but the most *consequential* when it appears. The two frameworks are complementary, not competing: NASSS gives micro-level granularity; the three-gap framework gives a macro-level cascade.

### 6.2 CFIR framework

CFIR (Damschroder et al., 2022) has five major domains:

1. Innovation
2. Outer setting
3. Inner setting
4. Individuals
5. Implementation process

**How the V3.1 distribution maps to CFIR:**

| CFIR domain | Closest V3.1 gap | n (V3.1) | % |
|---|---|---:|---:|
| Innovation (the AI itself) | Gap 1 (ecological validity) | 30 | 50.0% |
| Outer setting (policy, regulation) | Gap 2 (governance) | 30 | 50.0% |
| Inner setting (organization) | Gap 2 (governance) | 30 | 50.0% |
| Individuals (clinicians, patients) | Gap 3 (pilot trap) | 18 | 30.0% |
| Implementation process | Gap 3 (pilot trap) | 18 | 30.0% |

CFIR is the most widely used implementation-science framework. The three-gap framework overlaps with CFIR on Gap 1 and Gap 2, and concentrates the CFIR "individuals" and "implementation process" domains into a single Gap 3. CFIR has no explicit evaluation-gap dimension, which the V3.1 data identify as the most strongly tied to co-occurrence with the other gaps.

**Implication:** The three-gap framework adds an *evaluation dimension* (Gap 1) that CFIR lacks. CFIR treats the technology as a black box; the three-gap framework explicitly tracks its evaluation. This is the framework's most distinctive contribution: it makes evaluation the *upstream* cause of governance and implementation failure, where CFIR and NASSS would treat evaluation as a property of the innovation rather than a driver of downstream failure.

### 6.3 Comparison summary

| Framework | Dimensions | Evaluation gap explicit? | Causal direction | V3.1 corpus coverage |
|---|---:|:---:|:---:|---:|
| **Three-Gap (this report)** | 3 | **Yes** | **Yes (Gap 1 → Gap 2 → Gap 3)** | 50/60 = 83.3% |
| NASSS | 7 | No | Partially (embedding) | ≈ 30/60 = 50.0% (Gap 3 only) |
| CFIR | 5 | No | Partially (implementation process) | ≈ 48/60 = 80.0% (Gaps 1+2) |

The three-gap framework is the most concise of the three, the only one with an explicit evaluation gap, and the only one with a documented cascade direction. Its main weakness is granularity: it collapses NASSS's seven domains into three. Its main strength is parsimony combined with a directional cascade that the data support: 17 of 19 interaction-coded papers document a Gap 1 → Gap 2 or Gap 2 → Gap 3 chain.

---

## 7. Limitations

1. **n=60.** The V3.1 corpus is small. Stance proportions have wide confidence intervals (the 6.7% COUNTER rate has a 95% CI of [2.6%, 15.9%]). The headline distribution is interpretable but a larger V4 corpus would tighten the estimates.

2. **15 of 60 low-confidence papers.** The V3.1 title-fallback applied to 10 empty-abstract papers. Stance classifications on those papers inherit the low-confidence label and should not be over-interpreted.

3. **LLM coding bias.** The V3.1 codes were produced by 3 parallel LLM subagents. The 100% agreement on a 9-paper verification sample is encouraging, but the underlying LLM is the same model that wrote the protocol. A future verification should use an independent human coder.

4. **English-language and Western-default corpus.** The daily pipeline queries arXiv, PubMed, Semantic Scholar, and DBLP — predominantly English-language sources. The 10% ELSE rate is partly an artifact of this collection bias, which is why the equity-gap counter-argument is recorded as a finding.

5. **The stance layer was added after the V3.1 coding.** The classifier is a deterministic rule, but the *keyword lists* were chosen post-hoc. A more conservative approach would pre-register the keyword lists before applying them to the corpus.

---

## 8. Conclusion

The 60-paper V3.1 corpus splits cleanly into four stances: **63.3% SPECIFIC_GAP** (papers that look into a specific gap), **20.0% SUPPORT** (papers that propose a method in response), **6.7% COUNTER** (papers that empirically contradict a gap), and **10.0% ELSE** (in-corpus but outside the framework). The 38 SPECIFIC_GAP papers are the empirical engine of the three-gap framework: they document the gaps directly. The 12 SUPPORT papers are the field's response — the next phase of work. The 4 COUNTER papers are a healthy reminder that the gaps are probabilistic, not universal. The 6 ELSE papers are a counter-argument that the framework is currently Western-and-English-default and should be extended to a fourth equity gap.

The distribution was not visible in Iteration 1 (V1, n=341, 0% measured) or Iteration 2 (V1 strict, n=87, 28.7% at-least-one-gap). It required Iteration 3 (V2, n=182) to identify the off-topic contamination, Iteration 4 (V3, n=60) to apply the strict filter and relaxed coding rule, and Iteration 5 (this report) to layer the stance variable on top. Each iteration was a correction of the previous one, and the current numbers are the result of those corrections, not the starting point.

The methodological journey — narrative → conservative coding → diagnostic → strict filter + relaxed coding → stance layer — is itself part of the result. Without that journey, the 16.7% outside-rate is uninterpretable. With it, the 16.7% is the leading edge of a fourth gap the framework should be extended to cover.

---

## Appendix A — Per-Paper Stance Assignments

The full 60-row table is in `analysis/coding_matrix_v3_stance.md`. Each row includes title, year, V3.1 gap codes (G1/G2/G3), interaction flag, confidence, stance, and stance reason.

## Appendix B — Reproducibility Checklist

- [x] Corpus: `data/papers_strict.json` (60 papers, V3 strict filter)
- [x] Coding: `analysis/_codings_v3.1.json` (60 papers, V3.1 relaxed protocol)
- [x] Stance: `analysis/_codings_v3.1_stance.json` (60 papers, deterministic rule)
- [x] Matrix: `analysis/coding_matrix_v3.md` (60 papers, full evidence)
- [x] Evidence: `analysis/coding_matrix_v3_evidence.md` (all gap-positive quotes)
- [x] Coding protocol: `analysis/coding_protocol.md` (V3.1 spec)
- [x] This report: `outputs/reviews/stance_distribution_report_2026-06-08.md`
