# Systematic Literature Review: Health AI Evaluation, Governance, and Implementation

**A PRISM-Enhanced Evidence Synthesis**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Overview

This repository contains a **systematic literature review** investigating methods and frameworks for evaluating health AI systems in real-world deployment contexts, and how governance structures shape their implementation, sustainability, and societal impact.

The review addresses a critical gap in the health AI literature: while thousands of AI-enabled medical devices have been authorized and deployed, there is limited synthesis of how these systems are evaluated post-deployment, what governance mechanisms exist, and why many promising pilot projects fail to transition to routine clinical care.

**Research Question:**

> *What methods and frameworks exist for evaluating health AI systems in real-world deployment contexts, and how do governance structures shape their implementation, sustainability, and societal impact?*

### Methodological Contribution

This review employs **PRISM** (Paper Retrieval and Intelligence System for Medicine), an automated literature review framework developed to enhance the efficiency and comprehensiveness of evidence synthesis. PRISM integrates multi-source paper collection, intelligent ranking, LLM-powered summarization, and configurable thematic analysis — enabling systematic coverage of rapidly evolving scientific fields.

The PRISM framework is documented in this repository as a **reusable methodological tool** that can be adapted for other systematic literature reviews.

---

## Research Framework

The review analyzes literature across **five interconnected thematic dimensions**:

| Theme | Focus | Example Keywords |
|-------|-------|------------------|
| **AI Evaluation & Validation** | Performance assessment, bias detection, post-deployment monitoring | algorithmic auditing, model robustness, continuous evaluation |
| **Participatory Governance** | Stakeholder engagement, democratic oversight, accountability | citizen participation, co-governance, algorithmic accountability |
| **Adaptive Regulation** | Flexible regulatory approaches, regulatory sandboxes, living labs | iterative regulation, evidence-based policy, FDA frameworks |
| **Evidence & Implementation** | Knowledge translation, adoption barriers, implementation science | policy uptake, knowledge mobilization, implementation barriers |
| **Clinical Health AI** | Domain-specific applications, clinical validation, patient safety | diagnostic AI, clinical decision support, FDA approval |

These themes reflect the three-dimensional gap framework central to this review:
1. **Evaluation gap** — insufficient post-deployment performance monitoring
2. **Governance gap** — fragmented accountability and regulatory misalignment
3. **Implementation gap** — failure to transition from pilot to routine care

---

## PRISM Framework

PRISM (Paper Retrieval and Intelligence System for Medicine) is an automated pipeline for systematic literature review. It was developed to address the challenge of keeping pace with the exponential growth of health AI publications while maintaining methodological rigor.

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      THEMATIC QUERIES                           │
│  (Evaluation │ Governance │ Implementation │ Clinical AI)       │
└─────────────────────────┬───────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │  arXiv   │    │  PubMed  │    │Semantic  │
    │   API    │    │   API    │    │ Scholar  │
    └────┬─────┘    └────┬─────┘    └────┬─────┘
         └──────────────┼──────────────┘
                        ▼
              ┌─────────────────┐
              │    COLLECTOR     │
              │  Deduplication  │
              └────────┬────────┘
                       ▼
              ┌─────────────────┐
              │     RANKER      │
              │  Venue + Terms  │
              │   + Recency     │
              └────────┬────────┘
                       ▼
              ┌─────────────────┐
              │   SUMMARIZER    │
              │  LLM Extraction │
              │  (Methods/Gaps) │
              └────────┬────────┘
                       ▼
              ┌─────────────────┐
              │    REPORTER     │
              │  Digest + Trend │
              │     Analysis    │
              └────────┬────────┘
                       ▼
         ┌────────────┼────────────┐
         ▼            ▼            ▼
   ┌──────────┐ ┌──────────┐ ┌──────────┐
   │  Daily   │ │  Weekly  │ │  SQLite  │
   │  Digest  │ │ Synthesis│ │ Database │
   └──────────┘ └──────────┘ └──────────┘
```

### Key Features

- **Multi-source collection** from academic APIs (arXiv, PubMed, Semantic Scholar, DBLP)
- **Intelligent ranking** using venue prestige, keyword relevance, recency, and novelty detection
- **LLM-powered summarization** with structured extraction of methods, findings, and limitations
- **Configurable thematics** for domain-specific filtering
- **Automated digests** with trend analysis and gap identification
- **Full reproducibility** through deterministic configuration

---

## Repository Structure

```
ai-health-lit-review/
├── collector.py          # Multi-source paper collection
├── ranker.py             # Paper scoring and ranking
├── summarizer.py         # LLM-powered summarization
├── reporter.py           # Digest generation and delivery
├── database.py           # SQLite storage backend
├── daily_pipeline.py     # Daily collection workflow
├── weekly_synthesis.py   # Weekly trend analysis
├── config.yaml           # Framework configuration
├── requirements.txt      # Python dependencies
│
├── bib/                  # Bibliography
│   └── references.bib
│
├── sections/             # LaTeX manuscript
│   ├── 00_abstract.tex
│   ├── 01_introduction.tex
│   ├── 03_methods.tex
│   ├── 04_results.tex
│   └── ...
│
├── analysis/             # Quantitative analysis
│   ├── figures/          # Generated visualizations
│   ├── SUMMARY.md        # Gap analysis summary
│   └── coding_*.json     # Thematic coding data
│
└── outputs/              # Generated digests
    ├── digests/          # Daily summaries
    └── weekly/           # Weekly syntheses
```

---

## Outputs

| Output | Description |
|--------|-------------|
| `main.pdf` | Complete literature review manuscript |
| `analysis/SUMMARY.md` | Quantitative gap analysis |
| `bib/references.bib` | BibTeX bibliography |
| `outputs/digests/` | Daily paper digests |
| `outputs/weekly/` | Weekly trend syntheses |

---

## Quick Start

### Prerequisites

- Python 3.10+
- API keys for LLM providers (see [API Keys](#api-keys))

### Installation

```bash
git clone https://github.com/Arkoys/ai-health-lit-review.git
cd ai-health-lit-review
./install.sh
cp .env.example .env
# Edit .env with your API keys
```

### Reusing PRISM for Your Own Review

PRISM can be adapted for any systematic literature review by modifying `config.yaml`. For optimal results, we **highly recommend using an AI agent** such as [Hermes Agent](https://hermes-agent.nousresearch.com/) to orchestrate the workflow — agents can handle the iterative configuration, analyze outputs, and refine the pipeline more efficiently than manual operation.
======= REPLACE


1. **Define your search keywords** by theme:
   ```yaml
   keywords:
     # Theme 1
     - keyword 1
     - keyword 2
     # Theme 2
     - keyword 3
   ```

2. **Configure priority venues**:
   ```yaml
   priority_indicators:
     venues:
       - Nature Medicine
       - Lancet Digital Health
   ```

3. **Adjust scoring weights**:
   ```yaml
   scoring:
     keyword_match: 1.0
     priority_venue: 3.0
     recency: 1.0
     min_score_threshold: 3.0
   ```

4. **Run the pipeline**:
   ```bash
   source venv/bin/activate
   python run_daily.py --test-summarize
   python run_daily.py
   ```

---

## API Keys

### Required

| Provider | Purpose | Free Tier |
|----------|---------|-----------|
| [Google AI Studio](https://aistudio.google.com/apikey) | LLM summarization | 2M tokens/month |

### Optional Fallbacks

| Provider | Purpose |
|----------|---------|
| [HuggingFace](https://huggingface.co/settings/tokens) | Alternative LLM |
| [OpenRouter](https://openrouter.ai/) | Multi-model access |
| [Ollama](https://ollama.ai/) | Local models |

### Optional Outputs

- `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID`: Telegram notifications
- `SMTP_USER` / `SMTP_PASS`: Email digests
- `GOOGLE_CREDENTIALS_JSON`: Google Docs integration

---

## Citation

```bibtex
@misc{cartiernegadi2026healthai,
  author = {Victor Cartier-Negadi},
  title = {{Systematic Literature Review: Health AI Evaluation, Governance, and Implementation}},
  year = {2026},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/Arkoys/ai-health-lit-review}},
  doi = {10.5281/zenodo.XXXXXXX}
}
```

---

## Acknowledgments

This research was conducted as part of a Master's thesis at [LiGHT Lab](https://light.epfl.ch/), École Polytechnique Fédérale de Lausanne (EPFL).

---

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.
