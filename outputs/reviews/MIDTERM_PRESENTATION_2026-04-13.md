# AI Health Literature Review — Midterm Presentation Materials
**Project:** AI Health Literature Review | **Date:** 2026-04-13 | **Author:** Arkoys

---

## 1. Review Question

> **"What methods and frameworks exist for evaluating health AI systems in real-world deployment contexts, and how do governance structures shape their implementation, sustainability, and societal impact?"**

### Pourquoi cette question est bien scoped :

- **Trop large (à éviter) :** "AI in healthcare" — impossible à couvrir, zéro focus
- **Trop étroite (à éviter) :** "How does the NHS evaluate AI chatbots?" — trop spécifique pour une revue de littérature
- **Notre question :** Combine deux dimensions complémentaires — méthodes d'évaluation ET gouvernance — parce que l'évaluation technique sans cadre de gouvernance ne dit rien de la durabilité ni de l'impact réel
- **Connexion au projet PhD :** S'inscrit dans les 5 axes keyword du directeur de thèse (AI EVAL/VALID + PARTICIPATORY GOV + ADAPTIVE REG + EVIDENCE & IMPLEMENT + CLINICAL HEALTH AI)

---

## 2. Search Strategy

### Sources consultées

| Source | Type | Couverture | Limite |
|--------|------|-----------|--------|
| **arXiv** | Preprint server | cs.AI, cs.LG, cs.CL, cs.CY, q-bio, eess.AS, cs.CV | 50 résultats/jour |
| **PubMed/PMC** | Base biomédicale | AI + health/clinical/medical | 30 résultats/jour |
| **NeurIPS (proceedings)** | Conference proceedings | AI/ML 2020-2024 | 20 résultats/jour |

### Keywords — 5 groupes thématiques

#### Groupe 1 — AI Evaluation & Validation
`AI evaluation` · `AI validation` · `AI auditing` · `algorithmic auditing` · `model evaluation` · `AI testing` · `deployment evaluation` · `post-deployment monitoring` · `continuous evaluation` · `real-world validation` · `external validation`

#### Groupe 2 — Participatory Governance & Democracy
`participatory governance` · `participatory AI` · `stakeholder engagement` · `citizen participation` · `algorithmic accountability` · `community-centered AI` · `public interest technology`

#### Groupe 3 — Adaptive Governance & Regulation
`adaptive regulation` · `regulatory sandboxes` · `living labs` · `experimental regulation` · `evidence-based regulation` · `outcome-based regulation` · `innovation hubs` · `agile regulation`

#### Groupe 4 — Evidence & Implementation
`evidence-based policy` · `implementation science` · `knowledge translation` · `knowledge mobilization` · `research utilization` · `policy uptake` · `evidence synthesis` · `implementation barriers`

#### Groupe 5 — Clinical/Health AI Specific
`clinical AI` · `health AI` · `medical AI` · `clinical decision support` · `diagnostic AI` · `AI safety in healthcare` · `clinical validation` · `digital health` · `predictive modeling in healthcare`

### Requêtes booléennes combinées (exemples)

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

### Resultats bruts (à date)
- **Total papers collectés :** 33
- **arXiv :** quotidien (catégories cs.AI, cs.CY, etc.)
- **PubMed :** quotidien (requêtes large AI + health)
- **NeurIPS :** proceedings 2020-2024

---

## 3. Inclusion / Exclusion Criteria

### ✅ Inclusion
- Peer-reviewed papers (articles, revues systématiques, conférences avec comité de lecture)
- Concerne les systèmes AI appliqués au secteur de la santé (clinical, medical, healthcare)
- Contient une méthode d'évaluation OU un cadre de gouvernance pour l'AI en santé
- Date : 2020–2026 (5 dernières années + séminales)
- Langue : anglais (ET français si disponible)
- Accès : open access préférences, paywall acceptable si pertinent

### ❌ Exclusion
- Opinion pieces, editorials, letters to the editor
- Pure technical ML papers sans dimension santé ni évaluation
- Papers sur l'AI hors contexte clinique (ex: AI pour finances, agriculture)
- Publications antérieures à 2020 (sauf travaux sém类inaux sur governance)
- Langues autres qu'anglais (sauf contributions françaises、德国学者如果有英文 abstract)
- Pas d'abstract disponible (impossible à screen)

### Critères de priorisation
- **Priority 2 (top) :** papier qui intersecte 2+ groupes thématiques ET inclut une méthode empirique
- **Priority 1 (high) :** papier qui adresse 1 groupe thématique avec méthode empirique
- **Priority 0 (normal) :** papier pertinent mais méthode floue ou contribution théorique seule

---

## 4. PRISMA-Style Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    IDENTIFICATION                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  arXiv: 50/jour × ~30 jours = ~1,500 search results  │  │
│  │  PubMed: 30/jour × ~30 jours = ~900 search results    │  │
│  │  NeurIPS: 20/jour × session unique = ~200 results     │  │
│  │  MANUAL / OTHER: ~100 results (conférences, blogs)   │  │
│  │  TOTAL IDENTIFIED ≈ 2,700 papers                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                                │
│                            ▼                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                    SCREENING                         │  │
│  │  Titre + abstract → 300-400 candidates              │  │
│  │  De-duplication → ~280 papers                        │  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                                │
│                            ▼                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                  FULL TEXT READ                      │  │
│  │  Lecture complète → 80-100 papers                   │  │
│  │  Apply inclusion/exclusion → ~50 retained            │  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                                │
│                            ▼                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                   INCLUDED                            │  │
│  │  ~40-50 papers in final synthesis                    │  │
│  │  (target : 30-50 for scoping review)                 │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Statut actuel (2026-04-13)
- **Identifiés :** ~2,700 (cumul brut depuis le démarrage du projet)
- **Après screening :** 33 papers dans la DB (score ≥ 3.0, priorisés)
- **Entièrement lus :** ~10 papers avec summaries complètes
- **Inclus dans la synthèse :** 3 papers archivés avec reviews complètes

---

## 5. Data Extraction Table (Draft)

| ID | Title | Authors | Year | Source | Country | AI System / Method | Evaluation Method | Governance Dimension | Main Finding | Theme(s) |
|----|-------|---------|------|--------|---------|---------------------|-------------------|---------------------|--------------|----------|
| 001 | From Pilot Trap to Institutional Capacity: A Governance Framework for Sustainable Clinical AI Implementation | Jin Tian et al. | 2026 | PubMed | China | Provincial clinical AI platform (18-month implementation) | Qualitative case study, 18-month longitudinal | 6-module governance framework (institutional carrier, infra governance, regulatory/ethics, coordination, scaling, lifecycle oversight) | Governance capacity develops DURING implementation, not before. "Pilot trap" is governance failure, not technical failure | ADAPTIVE_REG, EVIDENCE_IMPL |
| 002 | Adaptive Regulation (Schrepel) | Thibault Schrepel | 2026 | SSRN/EJRR | EU | 8 EU Digital Acts (AI Act, DSA, DMA, etc.) | 14-criterion doctrinal coding across 4 dimensions (monitoring, triggering, adaptation, learning) | Blueprint for adaptive regulation: modular architecture, distributed sensing, pluralistic triggers, networked institutional memory | ADAPTIVE_REG, AI_EVAL |
| 003 | AI Policymaking: Mapping Integration Gaps Across the Public Policy Cycle | Lnenicka et al. | 2026 | Government Information Quarterly | 8 European countries | AI-enabled policy actions across 6 policy stages | Multi-country comparative exploratory case study, document analysis | Uneven AI integration: agenda setting high, implementation/evaluation low. No country has full lifecycle integration | PARTICIPATORY_GOV, ADAPTIVE_REG |
| 004 | [À compléter avec plus de lignes — 5-10 papers recommandés pour la présentation] | | | | | | | | | |

### Comment lire ce tableau :
- **Colonnes fixes :** titre, auteurs, année, source, pays, AI system/method, evaluation method, governance dimension, main finding, themes
- **Theme codes :** `AI_EVAL_VALID` · `PARTICIPATORY_GOV` · `ADAPTIVE_REG` · `EVIDENCE_IMPL` · `CLINICAL_HEALTH_AI`
- **AI System/Method :** quel système AI est étudié, ou quelle méthode les auteurs utilisent
- **Evaluation Method :** comment l'AI ou la governance est évaluée (empirique, coding, qualitative, etc.)
- **Governance Dimension :** quel aspect de la gouvernance est couvert

---

## 6. Notes de présentation orale

### Slides recommandés :

1. **Slide 1 — Intro** : Titre du projet + connexion à la thèse PhD (5 thèses keywords)
2. **Slide 2 — Review Question** : La question telle qu'elle est formulée + pourquoi elle est bien scopée
3. **Slide 3 — Search Strategy** : Tableau sources + keywords par groupe (5 couleurs pour les 5 groupes)
4. **Slide 4 — Inclusion/Exclusion** : Liste simple en 2 colonnes ✅ / ❌
5. **Slide 5 — PRISMA Flow** : Diagramme en entonnoir avec nombres estimés
6. **Slide 6 — Data Extraction Table** : 3-4 lignes populated + expliquer les colonnes
7. **Slide 7 — Prochaines étapes** : Ce qui reste à faire avant la soutenance finale

### Points clés à verbaliser :
- "La revue n'est pas juste une liste de papers — c'est un argument construit"
- "La question lie évaluation technique ET gouvernance parce que les deux sont inséparables dans le monde réel"
- "Le criteria de prioritization est transparent : on prioritize les papers qui intersectent plusieurs thèmes ET qui ont une méthode empirique"
- "Les 3 papers que j'ai déjà archivés en revue montrent que la gouvernance se développe pendant l'implémentation, pas avant — c'est un premier pattern récurrent"

---

*Document généré : 2026-04-13*
*Projet : Arkoys/ai-health-lit-review*