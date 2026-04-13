# AI Health Literature Review — Midterm Presentation Materials
**Project:** AI Health Literature Review | **Date:** 2026-04-13 | **Author:** Arkoys

---

## 1. Review Question

> **"What methods and frameworks exist for evaluating health AI systems in real-world deployment contexts, and how do governance structures shape their implementation, sustainability, and societal impact?"**

### Why this question is well-scoped:

- **Too broad (avoid):** "AI in healthcare" — unmanageable, zero focus
- **Too narrow (avoid):** "How does the NHS evaluate AI chatbots?" — too specific for a literature review
- **Our question:** Combines two complementary dimensions — evaluation methods AND governance — because technical evaluation without a governance framework tells us nothing about sustainability or real-world impact
- **PhD connection:** Aligns with the 5 thematic keyword groups from the PhD supervisor (AI EVAL/VALID + PARTICIPATORY GOV + ADAPTIVE REG + EVIDENCE & IMPLEMENT + CLINICAL HEALTH AI)

---

## 2. Search Strategy

### Sources consulted

| Source | Type | Coverage | Limit |
|--------|------|---------|-------|
| **arXiv** | Preprint server | cs.AI, cs.LG, cs.CL, cs.CY, q-bio, eess.AS, cs.CV | 50 results/day |
| **PubMed/PMC** | Biomedical database | AI + health/clinical/medical | 30 results/day |
| **NeurIPS (proceedings)** | Conference proceedings | AI/ML 2020-2024 | 20 results/day |

### Keywords — 5 thematic groups

#### Group 1 — AI Evaluation & Validation
`AI evaluation` · `AI validation` · `AI auditing` · `algorithmic auditing` · `model evaluation` · `AI testing` · `deployment evaluation` · `post-deployment monitoring` · `continuous evaluation` · `real-world validation` · `external validation`

#### Group 2 — Participatory Governance & Democracy
`participatory governance` · `participatory AI` · `stakeholder engagement` · `citizen participation` · `algorithmic accountability` · `community-centered AI` · `public interest technology`

#### Group 3 — Adaptive Governance & Regulation
`adaptive regulation` · `regulatory sandboxes` · `living labs` · `experimental regulation` · `evidence-based regulation` · `outcome-based regulation` · `innovation hubs` · `agile regulation`

#### Group 4 — Evidence & Implementation
`evidence-based policy` · `implementation science` · `knowledge translation` · `knowledge mobilization` · `research utilization` · `policy uptake` · `evidence synthesis` · `implementation barriers`

#### Group 5 — Clinical/Health AI Specific
`clinical AI` · `health AI` · `medical AI` · `clinical decision support` · `diagnostic AI` · `AI safety in healthcare` · `clinical validation` · `digital health` · `predictive modeling in healthcare`

### Example Boolean Query Combinations

```
# AI Evaluation + Health
("AI evaluation" OR "AI auditing" OR "deployment evaluation") AND ("healthcare" OR "clinical" OR "medical")

# Governance + Health AI
("participatory governance" OR "algorithmic accountability") AND ("health AI" OR "clinical AI")

# Adaptive Regulation + Health AI
("adaptive regulation" OR "regulatory sandbox") AND ("clinical AI" OR "medical AI")

# Implementation + AI Deployment
("implementation science" OR "knowledge translation") AND ("AI deployment" OR "AI adoption")
```

### Results so far (as of 2026-04-13)
- **Total papers collected:** 33
- **arXiv:** daily (cs.AI, cs.CY, etc.)
- **PubMed:** daily (broad AI + health queries)
- **NeurIPS:** proceedings 2020-2024

---

## 3. Inclusion / Exclusion Criteria

### ✅ Inclusion
- Peer-reviewed papers (journal articles, systematic reviews, peer-reviewed conference proceedings)
- Concerns AI systems applied to healthcare (clinical, medical, healthcare)
- Contains an evaluation method OR a governance framework for health AI
- Date: 2020–2026 (last 5 years + seminal works)
- Language: English (also French if available)
- Access: open access preferred, paywall acceptable if relevant

### ❌ Exclusion
- Opinion pieces, editorials, letters to the editor
- Pure technical ML papers with no health dimension and no evaluation component
- AI papers outside clinical context (e.g., AI for finance, agriculture)
- Publications predating 2020 (except seminal governance works)
- Languages other than English (unless French or German contributions with English abstract available)
- No abstract available (cannot screen)

### Prioritization Criteria
- **Priority 2 (top):** paper intersecting 2+ thematic groups AND includes an empirical method
- **Priority 1 (high):** paper addressing 1 thematic group with an empirical method
- **Priority 0 (normal):** relevant paper but method is unclear or contribution is purely theoretical

---

## 4. PRISMA-Style Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    IDENTIFICATION                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  arXiv: 50/day × ~30 days = ~1,500 search results   │  │
│  │  PubMed: 30/day × ~30 days = ~900 search results     │  │
│  │  NeurIPS: 20/day × unique session = ~200 results      │  │
│  │  MANUAL / OTHER: ~100 results (conferences, blogs)   │  │
│  │  TOTAL IDENTIFIED ≈ 2,700 papers                     │  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                               │
│                            ▼                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                    SCREENING                         │  │
│  │  Title + abstract → 300-400 candidates              │  │
│  │  De-duplication → ~280 papers                        │  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                               │
│                            ▼                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                  FULL TEXT READ                      │  │
│  │  Full read → 80-100 papers                          │  │
│  │  Apply inclusion/exclusion → ~50 retained            │  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                               │
│                            ▼                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                   INCLUDED                           │  │
│  │  ~40-50 papers in final synthesis                   │  │
│  │  (target: 30-50 for scoping review)                  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Current status (2026-04-13)
- **Identified:** ~2,700 (cumulative raw since project start)
- **After screening:** 33 papers in DB (score ≥ 3.0, prioritized)
- **Fully read:** ~10 papers with complete summaries
- **Included in synthesis:** 3 papers archived with full reviews

---

## 5. Data Extraction Table (Draft)

| ID | Title | Authors | Year | Source | Country | AI System / Method | Evaluation Method | Governance Dimension | Main Finding | Theme(s) |
|----|-------|---------|------|--------|---------|---------------------|-------------------|---------------------|--------------|----------|
| 001 | From Pilot Trap to Institutional Capacity: A Governance Framework for Sustainable Clinical AI Implementation | Jin Tian et al. | 2026 | PubMed | China | Provincial clinical AI platform (18-month implementation) | Qualitative case study, 18-month longitudinal | 6-module governance framework (institutional carrier, infra governance, regulatory/ethics, coordination, scaling, lifecycle oversight) | Governance capacity develops DURING implementation, not before. "Pilot trap" is governance failure, not technical failure | ADAPTIVE_REG, EVIDENCE_IMPL |
| 002 | Adaptive Regulation | Thibault Schrepel | 2026 | SSRN/EJRR | EU | 8 EU Digital Acts (AI Act, DSA, DMA, etc.) | 14-criterion doctrinal coding across 4 dimensions (monitoring, triggering, adaptation, learning) | Blueprint for adaptive regulation: modular architecture, distributed sensing, pluralistic triggers, networked institutional memory | ADAPTIVE_REG, AI_EVAL |
| 003 | AI Policymaking: Mapping Integration Gaps Across the Public Policy Cycle | Lnenicka et al. | 2026 | Government Information Quarterly | 8 European countries | AI-enabled policy actions across 6 policy stages | Multi-country comparative exploratory case study, document analysis | Uneven AI integration: agenda setting high, implementation/evaluation low. No country has full lifecycle integration | PARTICIPATORY_GOV, ADAPTIVE_REG |
| 004 | [Add more rows — 5-10 papers recommended for presentation] | | | | | | | | | |

### How to read this table:
- **Fixed columns:** title, authors, year, source, country, AI system/method, evaluation method, governance dimension, main finding, themes
- **Theme codes:** `AI_EVAL_VALID` · `PARTICIPATORY_GOV` · `ADAPTIVE_REG` · `EVIDENCE_IMPL` · `CLINICAL_HEALTH_AI`
- **AI System/Method:** which AI system is studied, or what method the authors use
- **Evaluation Method:** how the AI or governance is evaluated (empirical, coding, qualitative, etc.)
- **Governance Dimension:** which aspect of governance is covered

---

## 6. Presentation Notes

### Recommended slides:

1. **Slide 1 — Intro:** Project title + PhD connection (5 keyword themes)
2. **Slide 2 — Review Question:** The question as formulated + why it is well-scoped
3. **Slide 3 — Search Strategy:** Sources table + keywords by group (5 colors for 5 groups)
4. **Slide 4 — Inclusion/Exclusion:** Simple 2-column list ✅ / ❌
5. **Slide 5 — PRISMA Flow:** Funnel diagram with estimated numbers at each stage
6. **Slide 6 — Data Extraction Table:** 3-4 populated rows + explain the columns
7. **Slide 7 — Next Steps:** What remains before final submission

### Key talking points:
- "This review is not just a list of papers — it is a constructed argument"
- "The question links technical evaluation AND governance because the two are inseparable in the real world"
- "The prioritization criteria are transparent: we prioritize papers that intersect multiple themes AND have an empirical method"
- "The 3 papers already archived as full reviews show that governance develops during implementation, not before — a first recurrent pattern"

---

*Document generated: 2026-04-13*
*Project: Arkoys/ai-health-lit-review*