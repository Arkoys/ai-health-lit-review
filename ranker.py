"""
AI Health Literature — Paper Ranking & Scoring Module

Composite score formula:
  Score = Theme_Score + Novelty_Score + Recency_Boost + Venue_Score + Methods_Bonus

Theme_Score    = count of matched PhD keyword themes × 2
Novelty_Score  = 2 (new argument) | 1 (extension) | 0.5 (redundant/incremental)
Recency_Boost  = 2 (≤30d) | 1 (≤90d) | 0.5 (>90d)
Venue_Score    = 3 (top-tier venue) | 1.5 (recognized venue) | 0 (other)
Methods_Bonus  = 2 (empirical/lab) | 1.5 (systematic review/meta-analysis) | 1 (framework/proposal) | 0.5 (opinion/commentary)

Priority bands:
  3 = Score ≥ 7   → Must read
  2 = Score 4–6.9 → Important
  1 = Score 1.5–3.9 → Supplementary
  0 = Score < 1.5 → Low priority
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


# ─── Configuration ──────────────────────────────────────────────────────────────

PRIORITY_VENUES = {
    3: ["FAccT", "AIES", "NeurIPS", "ICML", "ICLR", "Nature Medicine",
        "JAMA", "The Lancet Digital Health", "Lancet", "Science",
        "Medical Internet Research", "JMIR", "Implementation Science",
        "Lancet Digit Health", "Nat Med",
        "AI and Society", "Ethics", "Fairness", "FAT"],
    1.5: ["Frontiers in Medicine", "Front Med", "Cureus", "Health Affairs",
          "BMJ Global Health", "Nature Biomedical Engineering",
          "JAMA Network Open", "Journal of Medical Ethics",
          "Science Technology & Human Values", "IEEE J Biomed Health Inform",
          "Neurocritical Care", "BMC Medical Imaging", "European Journal of Radiology",
          "Scientific Reports", "Nature Communications", "Cell Reports",
          "PLOS Medicine", "BMJ", "BMJ Open",
          "Pregnancy Hypertension", "Odontology", "Respiratory Medicine",
          "Orvosi Hetilap", "Current Rheumatology Reviews",
          "Biophysical Chemistry", "Psychiatry and Clinical Neurosciences",
          "Australasian Journal of General Practice", "Statistics in Medicine"],
    0.5: ["arXiv", "medRxiv", "bioRxiv", "Preprint"],
}

METHODS_VENUE_DEFAULTS = {
    "arXiv": "preliminary",
    "medRxiv": "preliminary",
    "bioRxiv": "preliminary",
}

METHODS_PATTERNS = {
    2: ["randomized controlled trial", "rct", "multicenter", "prospective cohort",
        "retrospective cohort", "cross-sectional", "case-control", "empirical study",
        "controlled experiment", "validation study", "laboratory"],
    1.5: ["systematic review", "meta-analysis", "meta analysis", "scoping review",
          "literature review", "narrative review"],
    1: ["framework", "conceptual", "proposal", "guideline", "guidance",
        "design pattern", "architecture", "theoretical", "position paper"],
    0.5: ["commentary", "letter", "opinion", "editorial", "perspective",
          "case report", "case series"],
}

THEME_PATTERNS = {
    "AI_EVAL_VALID": {
        "keywords": ["evaluation", "validation", "auditing", "auditing", "model testing",
                     "bias detection", "fairness", "reliability", "robustness",
                     "explainability", "interpretability", "transparency", "safety",
                     "performance assessment", "continuous monitoring", "post-deployment"],
        "weight": 2,
    },
    "PARTICIPATORY_GOV": {
        "keywords": ["participatory", "stakeholder", "citizen", "community",
                     "deliberative", "co-governance", "democratic", "accountability",
                     "public engagement", "co-design", "inclusive AI", "public interest"],
        "weight": 2,
    },
    "ADAPTIVE_REGULATION": {
        "keywords": ["adaptive regulation", "adaptive governance", "agile regulation",
                     "regulatory sandbox", "living lab", "iterative", "dynamic",
                     "experimental regulation", "evidence-based regulation",
                     "outcome-based", "continuous compliance", "lifecycle governance"],
        "weight": 2,
    },
    "EVIDENCE_IMPLEMENT": {
        "keywords": ["evidence-based", "evidence synthesis", "knowledge translation",
                     "implementation science", "policy uptake", "research impact",
                     "knowledge mobilization", "actionable evidence", "evidence gap",
                     "implementation barrier", "NASSS", "adoption", "scale-up"],
        "weight": 2,
    },
    "CLINICAL_HEALTH_AI": {
        "keywords": ["clinical AI", "health AI", "medical AI", "clinical decision support",
                     "diagnostic AI", "digital health", "patient safety", "healthcare AI",
                     "radiology AI", "pathology AI", "oncology AI", "triage AI"],
        "weight": 1,
    },
}

RECENCY_DAYS = {30: 2, 90: 1, 365: 0.5}


# ─── Core Scoring Functions ────────────────────────────────────────────────────

def _parse_date(date_str: str) -> Optional[datetime]:
    """Parse various date formats into datetime."""
    if not date_str:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m", "%Y", "%d %b %Y", "%b %d, %Y"):
        try:
            return datetime.strptime(str(date_str).strip()[:10], fmt)
        except ValueError:
            pass
    return None


def score_recency(published_date: str) -> float:
    """Apply recency boost based on publication date."""
    pub = _parse_date(published_date)
    if not pub:
        return 0.5
    days_old = (datetime.now() - pub).days
    for threshold, boost in sorted(RECENCY_DAYS.items(), reverse=True):
        if days_old <= threshold:
            return boost
    return 0


def score_venue(venue: str) -> float:
    """Score based on publication venue prestige."""
    if not venue:
        return 0
    v = venue.upper()
    for tier, venues in PRIORITY_VENUES.items():
        for pattern in venues:
            if pattern.upper() in v:
                return tier
    return 0


def score_methods(abstract: str, title: str) -> float:
    """Detect methodology type from abstract/title text."""
    text = f"{title} {abstract}".lower()
    for threshold, patterns in sorted(METHODS_PATTERNS.items(), reverse=True):
        for pat in patterns:
            if pat in text:
                return threshold
    return 0.5  # default for unknown


def score_themes(title: str, abstract: str, keywords: list, existing_themes: list) -> tuple[float, list]:
    """Score based on keyword theme matches."""
    text = f"{title} {abstract}".lower()
    matched_themes = list(existing_themes)  # start with pre-tagged themes
    score = len(existing_themes) * 2  # weight pre-tagged themes

    for theme, cfg in THEME_PATTERNS.items():
        if theme in matched_themes:
            continue  # already counted
        if any(kw.lower() in text for kw in cfg["keywords"]):
            matched_themes.append(theme)
            score += cfg["weight"]

    return score, matched_themes


def detect_novelty(title: str, abstract: str) -> float:
    """Infer novelty from linguistic markers."""
    text = f"{title} {abstract}".lower()
    # New contribution indicators
    if any(w in text for w in ["we propose", "we introduce", "novel", "first to", "new framework",
                                "new approach", "new method", "new metric", "we present",
                                "we develop", "we design", "first systematic"]):
        return 2.0
    # Extension indicators
    if any(w in text for w in ["extend", "build on", "adapt", "improve", "enhance",
                                "adaptation of", "extension of", "we apply",
                                "we adapt", "scale to"]):
        return 1.0
    # Redundant/incremental
    if any(w in text for w in ["similar to", "like previous", "consistent with",
                                "as in prior", "baseline", "we replicate"]):
        return 0.5
    return 1.0  # default moderate novelty


# ─── Main Scoring Pipeline ──────────────────────────────────────────────────────

def score_paper(paper: dict) -> dict:
    """Compute full composite score for a single paper."""
    title = paper.get("title", "") or ""
    abstract = paper.get("abstract", "") or ""
    keywords = paper.get("keywords", []) or []
    existing_themes = paper.get("themes", [])
    venue = paper.get("venue", "") or ""
    published_date = paper.get("published_date") or paper.get("date", "") or ""

    # Component scores
    theme_score, themes = score_themes(title, abstract, keywords, existing_themes)
    novelty = detect_novelty(title, abstract)
    recency = score_recency(published_date)
    venue_score = score_venue(venue)
    methods = score_methods(abstract, title)

    # Composite
    composite = theme_score + novelty + recency + venue_score + methods

    # Priority band
    if composite >= 7:
        priority = 3
    elif composite >= 4:
        priority = 2
    elif composite >= 1.5:
        priority = 1
    else:
        priority = 0

    return {
        **paper,
        "score": round(composite, 1),
        "themes": themes,
        "scores": {
            "composite": round(composite, 1),
            "theme_score": round(theme_score, 1),
            "novelty": novelty,
            "recency": recency,
            "venue": venue_score,
            "methods": methods,
        },
        "priority": priority,
        "rank": None,  # set after sorting
    }


def rank_papers(papers: list) -> list:
    """Score and rank all papers. Returns sorted list with rank numbers."""
    scored = [score_paper(p) for p in papers]
    scored.sort(key=lambda x: (x["priority"], x["scores"]["composite"]), reverse=True)
    for i, p in enumerate(scored, 1):
        p["rank"] = i
    return scored


def score_daily_papers(papers: list, date: str) -> dict:
    """Score a batch of new papers and add them to the database."""
    ranked = rank_papers(papers)
    return {
        "date": date,
        "total": len(ranked),
        "priority_3": [p for p in ranked if p["priority"] == 3],
        "priority_2": [p for p in ranked if p["priority"] == 2],
        "priority_1": [p for p in ranked if p["priority"] == 1],
        "all_ranked": ranked,
    }


# ─── Ranking Report Generation ─────────────────────────────────────────────────

def generate_ranking_report(db: dict, days_back: int = 30) -> str:
    """Generate a markdown ranking report from the database."""
    from datetime import timedelta

    cutoff = datetime.now() - timedelta(days=days_back)
    recent_papers = []
    for p in db.get("papers", []):
        pub = _parse_date(p.get("published_date") or "")
        if pub and pub >= cutoff:
            recent_papers.append(p)

    ranked = rank_papers(recent_papers)

    lines = [
        f"# 📊 AI Health Literature — Ranking Report",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')} | **Window:** last {days_back} days | **Papers:** {len(ranked)}",
        "",
        "## 🏆 Top Ranked Papers",
        "",
    ]

    PRIORITY_EMOJI = {3: "🔴", 2: "🟡", 1: "⚪"}
    PRIORITY_LABEL = {3: "Must Read", 2: "Important", 1: "Supplementary"}

    for p in ranked[:15]:
        score = p["scores"]
        lines.extend([
            f"### {PRIORITY_EMOJI.get(p['priority'], '⚫')} [{p['rank']:02d}] {p.get('title', 'N/A')}",
            f"**Priority: {PRIORITY_LABEL.get(p['priority'], 'Unknown')}** | Score: `{score['composite']:.1f}` "
            f"(theme: {score['theme_score']} + novelty: {score['novelty']} + recency: {score['recency']} + venue: {score['venue']} + methods: {score['methods']})",
            f"**Themes:** `{'`, `'.join(p.get('themes', []))}`",
            f"**Venue:** {p.get('venue', 'N/A')} | **Published:** {p.get('published_date', 'N/A')}",
            f"**URL:** {p.get('url', 'N/A')}",
            "",
        ])

    # Theme distribution
    theme_counts = {}
    for p in ranked:
        for t in p.get("themes", []):
            theme_counts[t] = theme_counts.get(t, 0) + 1

    lines.extend([
        "## 📈 Theme Distribution (Last 30 Days)",
        "",
        "| Theme | Papers |",
        "|-------|--------|",
    ])
    for theme, count in sorted(theme_counts.items(), key=lambda x: -x[1]):
        lines.append(f"| {theme} | {count} |")

    # Priority breakdown
    by_priority = {3: [], 2: [], 1: []}
    for p in ranked:
        if p["priority"] in by_priority:
            by_priority[p["priority"]].append(p)

    lines.extend([
        "",
        "## 📋 Priority Breakdown",
        f"- 🔴 **Must Read (Priority 3):** {len(by_priority[3])} papers",
        f"- 🟡 **Important (Priority 2):** {len(by_priority[2])} papers",
        f"- ⚪ **Supplementary (Priority 1):** {len(by_priority[1])} papers",
    ])

    return "\n".join(lines)


# ─── CLI Entry Point ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    db_path = Path("data/papers.json")
    if not db_path.exists():
        print(f"❌ Database not found: {data/papers.json}")
        sys.exit(1)

    with open(db_path, encoding="utf-8") as f:
        db = json.load(f)

    days = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    report = generate_ranking_report(db, days_back=days)
    print(report)
