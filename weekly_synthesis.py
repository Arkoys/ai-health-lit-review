"""
AI Health Literature — Weekly Synthesis Generator

Aggregates daily digests from the past 7 days, re-ranks papers,
detects emerging trends, identifies gaps, and produces a structured weekly report.

Usage:
  python3 weekly_synthesis.py           # generate report
  python3 weekly_synthesis.py --push    # generate + push to GitHub
"""

import json
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# Import ranking module
import ranker


# ─── Configuration ──────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).parent
DIGESTS_DIR = PROJECT_ROOT / "outputs" / "digests"
TOPIC_TRENDS_DIR = PROJECT_ROOT / "outputs" / "topic_trends"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "weekly"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TOPIC_TRENDS_DIR.mkdir(parents=True, exist_ok=True)


# ─── Helpers ────────────────────────────────────────────────────────────────────

def load_db() -> dict:
    """Load the paper database."""
    db_path = PROJECT_ROOT / "data" / "papers.json"
    if db_path.exists():
        with open(db_path, encoding="utf-8") as f:
            return json.load(f)
    return {"papers": []}


def get_week_digests() -> list:
    """Get all digest files from the past 7 days."""
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    digests = []
    for f in sorted(DIGESTS_DIR.glob("digest_*.md"), reverse=True):
        try:
            date_str = re.search(r"(\d{4}-\d{2}-\d{2})", f.name)
            if date_str:
                file_date = datetime.strptime(date_str.group(1), "%Y-%m-%d").date()
                if week_ago <= file_date <= today:
                    digests.append({"date": file_date, "path": f})
        except ValueError:
            continue
    return digests


def extract_papers_from_digest(path: Path) -> list:
    """Parse a digest file and extract paper entries.
    
    Looks for paper entries marked with emoji indicators like ⭐⭐⭐, 🔴, or
    'Featured Papers' / 'Supporting Papers' section markers. Rejects digest headers.
    """
    content = path.read_text(encoding="utf-8")
    papers = []
    
    # Split on section headers (but not the main header)
    # Primary paper blocks start after "Featured Papers" or "Supporting Papers" headers
    # and contain emoji priority markers (⭐⭐⭐, ⭐⭐, 🔴, 🟡)
    
    # Find all paper blocks: lines with priority emoji + title
    # Pattern: starts with emoji, followed by a line that looks like a title
    paper_blocks = re.split(
        r"\n(?:##|###)\s+(?:Featured Papers|Supporting Papers|🏆 Featured Papers|📚 Supporting Papers)",
        content
    )
    
    for block in paper_blocks:
        if not block.strip():
            continue
        # Skip blocks that look like the digest header (no priority markers)
        if "🔬" in block and ("Daily Digest" in block or "Executive Summary" in block):
            # This is the digest header — skip
            continue
        if "🔬" not in block and "⭐" not in block and "🔴" not in block:
            continue
        
        # Extract individual papers within a block (split on ### or numbered headers)
        sub_blocks = re.split(r"\n###+\s*", block)
        for sub in sub_blocks:
            if not sub.strip():
                continue
            
            # Find title: first line that's not an emoji/bullet/pipe
            lines = sub.strip().split("\n")
            title = ""
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                # Skip emoji-only lines, table rows, empty markers
                if re.match(r"^[⭐🔴🟡⚪📈➡️🆕📉]+(\s+\d+)?\s*$", line):
                    continue
                if line.startswith("|") or line.startswith("**") or line.startswith("*"):
                    continue
                if line.startswith("Source") or line.startswith("Authors") or line.startswith("Keywords"):
                    continue
                # Remove priority badge prefix
                title = re.sub(r"^[⭐🔴🟡⚪🔗📄🔬]+\s*", "", line)
                title = re.sub(r"^\d+[\.\)]\s*", "", title)
                title = re.sub(r"^\*\*(HIGH|MEDIUM|LOW)\*\*\s*[-—–]?\s*", "", title)
                break
            
            if not title or len(title) < 10:
                continue
            if any(skip in title.lower() for skip in ["daily digest", "executive summary", 
                    "trends & patterns", "topic tracking", "priority queue",
                    "action items", "generated:", "project:", "sources:"]):
                continue
            
            # Extract links
            links = re.findall(r"\[.*?\]\((https?://[^\)]+)\)", sub)
            arxiv_link = next((l for l in links if "arxiv" in l.lower()), "")
            url = arxiv_link or (links[0] if links else "")
            
            # Extract priority from emoji
            priority = 3 if "⭐⭐⭐" in sub or "🔴" in sub[:3] else 2 if "⭐⭐" in sub or "🟡" in sub[:3] else 1
            
            # Extract themes from backtick tags
            theme_matches = re.findall(r"`([A-Z_]+)`", sub)
            themes = list(set(theme_matches)) if theme_matches else []
            
            # Extract abstract/snippet
            abstract_match = re.search(r"(?:Summary|Abstract)[:>\s]+(.+?)(?:\n\n|\*\*[A-Z]|\n##)", sub, re.DOTALL)
            abstract = abstract_match.group(1).strip().replace("\n", " ")[:400] if abstract_match else ""
            
            papers.append({
                "title": title.strip(),
                "url": url,
                "themes": themes,
                "priority": priority,
                "abstract": abstract,
                "source_digest": path.name,
            })
    
    return papers


def extract_topic_trends(digests: list) -> dict:
    """Extract topic frequency from multiple digests for trend analysis."""
    # Known topic keywords → theme mapping
    topic_keywords = {
        "Adaptive AI Evaluation": ["adaptive", "learning", "iterative", "continuously learning", "L/P/R"],
        "Regulatory Divergence (US/EU)": ["regulatory", "FDA", "MDR", "US", "EU", "Europe", "divergence"],
        "Governance Frameworks": ["governance", "framework", "institutional", "pilot trap", "scaling"],
        "Bias & Fairness": ["bias", "fairness", "discrimination", "equity"],
        "Explainability": ["explainability", "interpretability", "SHAP", "LIME", "uncertainty"],
        "Evidence Synthesis": ["evidence", "synthesis", "meta-analysis", "systematic review"],
        "Implementation Barriers": ["implementation", "adoption", "NASSS", "barriers", "uptake"],
        "Clinical Validation": ["validation", "clinical trial", "real-world", "multicenter"],
        "Human-AI Collaboration": ["uncertainty", "human-in-the-loop", "expert-guided", "collaboration"],
        "Regulatory Sandboxes": ["sandbox", "living lab", "experimental", "innovation hub"],
        "Participatory Governance": ["participatory", "stakeholder", "citizen", "community", "co-design"],
        "Post-Deployment Monitoring": ["post-deployment", "continuous monitoring", "surveillance"],
        "Low-Resource Settings": ["low-resource", "LMIC", "global health", "equity"],
        "Privacy & Federated Learning": ["privacy", "federated", "GDPR", "data protection"],
    }

    topic_counts = defaultdict(lambda: {"count": 0, "trend": "stable", "papers": []})
    high_priority = []

    for dig in digests:
        content = dig["path"].read_text(encoding="utf-8").lower()
        dig_date = dig["date"].isoformat()

        for topic, keywords in topic_keywords.items():
            if any(kw.lower() in content for kw in keywords):
                topic_counts[topic]["count"] += 1
                # Track if it appeared in priority sections
                priority_section = re.search(
                    rf"{re.escape(topic)}(?:.*?\n{{0,5}}.*?(?:⭐|🔴|Priority[:\s]*[123]|HIGH|CRITICAL))",
                    content, re.DOTALL | re.IGNORECASE
                )
                if priority_section or any(kw.lower() in content[:content.find(topic) + 200] if topic.lower() in content else False for kw in keywords[:2]):
                    topic_counts[topic]["papers"].append(dig_date)

    # Determine trend per topic
    for topic, data in topic_counts.items():
        recent_count = data["count"]
        # Simple trend: ≥3 mentions in last 7d = "rising", 2 = "stable", 1 = "emerging"
        if recent_count >= 3:
            data["trend"] = "rising"
        elif recent_count == 2:
            data["trend"] = "stable"
        else:
            data["trend"] = "emerging"

    return dict(topic_counts)


# ─── Weekly Report Generation ───────────────────────────────────────────────────

def generate_weekly_report(week_start: str, week_end: str, digests: list, ranked_papers: list) -> str:
    """Generate the full weekly synthesis markdown report."""

    TREND_EMOJI = {"rising": "📈", "stable": "➡️", "emerging": "🆕", "declining": "📉"}
    PRIORITY_EMOJI = {3: "🔴", 2: "🟡", 1: "⚪"}
    PRIORITY_LABEL = {3: "Must Read", 2: "Important", 1: "Supplementary"}

    lines = [
        "# 📅 AI Health Literature — Weekly Synthesis",
        f"**Week:** {week_start} → {week_end} | **Digests processed:** {len(digests)} | **Papers ranked:** {len(ranked_papers)}",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "---",
        "",
    ]

    # ── Top Papers Re-Ranked ──────────────────────────────────────────────
    lines.extend([
        "## 🏆 Top Papers This Week (Re-Ranked)",
        "",
        f"Applied ranking algorithm across {len(ranked_papers)} papers from {len(digests)} daily digests.",
        "",
    ])

    for p in ranked_papers[:10]:
        score = p.get("scores", {})
        url = p.get("url", p.get("pdf_url", ""))
        link_md = f"[🔗 Full Text]({url})" if url else ""
        themes_md = "`" + "`, `".join(p.get("themes", [])) + "`" if p.get("themes") else ""
        lines.extend([
            f"### {PRIORITY_EMOJI.get(p['priority'], '⚫')} [{p['rank']:02d}] {p.get('title', 'N/A')} {link_md}",
            f"| Priority | Score | Theme | Novelty | Recency | Venue | Methods |",
            f"|----------|-------|-------|---------|---------|-------|--------|",
            f"| {PRIORITY_LABEL.get(p['priority'], '?')} | **{score.get('composite', '?')}** | {score.get('theme_score', '?')} | {score.get('novelty', '?')} | {score.get('recency', '?')} | {score.get('venue', '?')} | {score.get('methods', '?')} |",
            f"| **Themes:** {themes_md} |",
            "",
        ])

    # ── Topic Trends ─────────────────────────────────────────────────────
    topic_data = extract_topic_trends(digests)

    lines.extend([
        "---",
        "",
        "## 📊 Topic Trends This Week",
        "",
        f"| Topic | Mentions | Trend |",
        f"|-------|----------|-------|",
    ])
    for topic, data in sorted(topic_data.items(), key=lambda x: -x[1]["count"]):
        emoji = TREND_EMOJI.get(data["trend"], "•")
        lines.append(f"| {emoji} {topic} | {data['count']} | {data['trend'].title()} |")

    # Rising topics detail
    rising = [(t, d) for t, d in topic_data.items() if d["trend"] == "rising"]
    if rising:
        lines.extend(["", "### 📈 Rising Topics — In Depth", ""])
        for topic, data in rising:
            lines.append(f"**{topic}** appeared {data['count']}× this week.")
        lines.append("")

    # ── Emerging Gaps ─────────────────────────────────────────────────────
    all_covered_themes = set()
    for p in ranked_papers:
        all_covered_themes.update(p.get("themes", []))

    THEME_LABELS = {
        "AI_EVAL_VALID": "AI Evaluation & Validation",
        "PARTICIPATORY_GOV": "Participatory Governance",
        "ADAPTIVE_REGULATION": "Adaptive Regulation",
        "EVIDENCE_IMPLEMENT": "Evidence & Implementation",
        "CLINICAL_HEALTH_AI": "Clinical Health AI",
    }

    gaps = [t for t in THEME_LABELS if t not in all_covered_themes]

    lines.extend([
        "---",
        "",
        "## 🔍 Research Gaps Identified",
        "",
    ])
    if gaps:
        lines.append("**Themes with NO recent coverage — consider expanding search:**")
        for g in gaps:
            lines.append(f"- ⚠️ `{g}` — {THEME_LABELS.get(g, g)}")
    else:
        lines.append("All 5 PhD themes have recent coverage this week. ✅")

    # Cross-theme analysis
    cross_theme = [p for p in ranked_papers if len(p.get("themes", [])) >= 2]
    lines.extend([
        "",
        f"**Cross-theme papers:** {len(cross_theme)}/{len(ranked_papers)} papers address multiple themes simultaneously.",
        "",
    ])

    # ── Priority Breakdown ───────────────────────────────────────────────
    by_priority = defaultdict(list)
    for p in ranked_papers:
        by_priority[p["priority"]].append(p)

    lines.extend([
        "---",
        "",
        "## 📋 Priority Breakdown",
        f"- 🔴 **Must Read (Priority 3):** {len(by_priority[3])} papers",
        f"- 🟡 **Important (Priority 2):** {len(by_priority[2])} papers",
        f"- ⚪ **Supplementary (Priority 1):** {len(by_priority[1])} papers",
        "",
    ])

    # ── Action Items ──────────────────────────────────────────────────────
    lines.extend([
        "---",
        "",
        "## 🎯 Action Items for Next Week",
        "",
        f"- [ ] Read top {min(5, len([p for p in ranked_papers if p['priority']==3]))} Priority 3 papers in full",
        f"- [ ] Expand search for gaps: {', '.join(gaps) if gaps else 'All themes covered'}",
        f"- [ ] Chase cross-theme papers for PhD chapter connections",
        f"- [ ] Review ranking scores — calibrate thresholds if needed",
        f"- [ ] Check for new venues / preprints missed by current search",
        "",
    ])

    # ── Footer ───────────────────────────────────────────────────────────
    lines.extend([
        "---",
        "",
        f"*Generated: {datetime.now().isoformat()}*",
        f"*Project: [Arkoys/ai-health-lit-review](https://github.com/Arkoys/ai-health-lit-review)*",
    ])

    return "\n".join(lines)


# ─── Topic Matrix Generation ───────────────────────────────────────────────────

def generate_topic_matrix(weeks_back: int = 4) -> str:
    """Generate a multi-week topic tracking matrix."""

    today = datetime.now().date()
    start = today - timedelta(weeks=weeks_back)

    # Collect digests per week
    week_data = defaultdict(lambda: {"digests": [], "topics": defaultdict(int)})

    for f in DIGESTS_DIR.glob("digest_*.md"):
        date_str = re.search(r"(\d{4}-\d{2}-\d{2})", f.name)
        if not date_str:
            continue
        try:
            file_date = datetime.strptime(date_str.group(1), "%Y-%m-%d").date()
            if file_date < start:
                continue
        except ValueError:
            continue

        # ISO week number
        week_key = file_date.strftime("%Y-W%W")

        topic_keywords = {
            "AI Eval/Valid": ["evaluation", "validation", "auditing", "bias", "reliability", "explainability"],
            "Participatory Gov": ["participatory", "stakeholder", "citizen", "democratic", "accountability"],
            "Adaptive Regulation": ["adaptive", "regulatory sandbox", "iterative", "lifecycle", "FDA", "MDR"],
            "Evidence/Implement": ["evidence", "implementation", "adoption", "NASSS", "uptake"],
            "Clinical AI": ["clinical AI", "health AI", "diagnostic", "radiology", "digital health"],
            "Governance Frameworks": ["governance framework", "institutional", "scaling", "pilot trap"],
            "US/EU Divergence": ["US", "EU", "Europe", "divergence", "regulatory DNA"],
        }

        content = f.read_text(encoding="utf-8").lower()
        week_data[week_key]["digests"].append(f.name)

        for topic, keywords in topic_keywords.items():
            if any(kw.lower() in content for kw in keywords):
                week_data[week_key]["topics"][topic] += 1

    lines = [
        f"# 📊 Topic Tracking Matrix",
        f"**Period:** last {weeks_back} weeks | **Generated:** {datetime.now().strftime('%Y-%m-%d')}",
        "",
        "| Week | # Digests | AI Eval/Valid | Participatory Gov | Adaptive Reg | Evidence/Impl | Clinical AI | Gov Frameworks | US/EU Div. |",
        "|-----|-----------|--------------|-------------------|--------------|---------------|-------------|----------------|------------|",
    ]

    sorted_weeks = sorted(week_data.keys(), reverse=True)
    for wk in sorted_weeks:
        data = week_data[wk]
        week_label = datetime.strptime(wk + "-1", "%Y-W%W-%w").strftime("Week %W (%b %d)")
        counts = data["topics"]
        lines.append(
            f"| {week_label} | {len(data['digests'])} | "
            f"{_matrix_cell(counts.get('AI Eval/Valid', 0))} | "
            f"{_matrix_cell(counts.get('Participatory Gov', 0))} | "
            f"{_matrix_cell(counts.get('Adaptive Regulation', 0))} | "
            f"{_matrix_cell(counts.get('Evidence/Implement', 0))} | "
            f"{_matrix_cell(counts.get('Clinical AI', 0))} | "
            f"{_matrix_cell(counts.get('Governance Frameworks', 0))} | "
            f"{_matrix_cell(counts.get('US/EU Divergence', 0))} |"
        )

    lines.extend(["", "**Legend:** 🟢 Strong (3+) | 🟡 Moderate (1-2) | ⚪ Low (0) |"])
    return "\n".join(lines)


def _matrix_cell(count: int) -> str:
    if count >= 3:
        return f"🟢 {count}"
    elif count >= 1:
        return f"🟡 {count}"
    else:
        return f"⚪ 0"


# ─── GitHub Push ───────────────────────────────────────────────────────────────

def push_to_github(files: list, commit_msg: str):
    """Commit and push files to GitHub."""
    # Load env
    with open(PROJECT_ROOT / ".env") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                import os
                os.environ[k] = v

    token = os.environ.get("GITHUB_TOKEN", "")
    repo = os.environ.get("GITHUB_REPO", "")

    if not token or not repo:
        print("❌ Missing GITHUB_TOKEN or GITHUB_REPO")
        return False

    remote_url = f"https://x-access-token:{token}@github.com/{repo}.git"
    subprocess.run(["git", "remote", "set-url", "origin", remote_url], cwd=PROJECT_ROOT, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Hermes Agent"], cwd=PROJECT_ROOT, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "hermes-agent@users.noreply.github.com"], cwd=PROJECT_ROOT, check=True, capture_output=True)

    for f in files:
        subprocess.run(["git", "add", str(f)], cwd=PROJECT_ROOT, check=True, capture_output=True)

    result = subprocess.run(["git", "status", "--short"], cwd=PROJECT_ROOT, capture_output=True, text=True)
    if not result.stdout.strip():
        print("✅ Nothing to push — no changes detected")
        return True

    subprocess.run(["git", "commit", "-m", commit_msg], cwd=PROJECT_ROOT, check=True, capture_output=True)
    result = subprocess.run(["git", "push", "origin", "main"], cwd=PROJECT_ROOT, capture_output=True, text=True)
    pushed = result.returncode == 0
    print("✅ Pushed" if pushed else f"❌ Push failed: {result.stderr}")
    return pushed


# ─── Main ──────────────────────────────────────────────────────────────────────

def main(push: bool = False):
    print("📅 Weekly Synthesis Generator — Starting...")

    # 1. Get last 7 days of digests
    digests = get_week_digests()
    print(f"   Found {len(digests)} digests from the past 7 days")
    if not digests:
        print("❌ No recent digests found")
        return

    week_start = digests[-1]["date"].strftime("%Y-%m-%d")
    week_end = digests[0]["date"].strftime("%Y-%m-%d")

    # 2. Extract papers from each digest
    all_papers = []
    for dig in digests:
        papers = extract_papers_from_digest(dig["path"])
        all_papers.extend(papers)
    print(f"   Extracted {len(all_papers)} papers from digests")

    # 3. Load full DB and merge with extracted papers
    db = load_db()
    
    # Build a map keyed on title (normalized)
    def norm_key(t):
        return re.sub(r'[^\w\s]', '', t.lower())[:100]

    paper_map = {norm_key(p.get("title", "")): p for p in db.get("papers", [])}

    scored_papers = []
    seen_keys = set()
    for digest_paper in all_papers:
        key = norm_key(digest_paper["title"])
        if key in paper_map and key not in seen_keys:
            db_paper = paper_map[key]
            scored = ranker.score_paper(db_paper)
            scored["source_digest"] = digest_paper["source_digest"]
            scored_papers.append(scored)
            seen_keys.add(key)
        elif key not in seen_keys:
            # Unknown paper — score with limited data but flag as new
            scored = ranker.score_paper(digest_paper)
            scored["source_digest"] = digest_paper["source_digest"]
            scored["is_new"] = True
            scored_papers.append(scored)
            seen_keys.add(key)

    # 4. Rank all papers
    ranked = ranker.rank_papers(scored_papers)
    print(f"   Ranked {len(ranked)} papers")

    # 5. Generate weekly report
    report = generate_weekly_report(week_start, week_end, digests, ranked)
    today_str = datetime.now().strftime("%Y-%m-%d")
    week_file = OUTPUT_DIR / f"weekly_{today_str}.md"
    week_file.write_text(report, encoding="utf-8")
    print(f"   Weekly report: {week_file}")

    # 6. Generate topic matrix
    matrix = generate_topic_matrix(weeks_back=4)
    matrix_file = TOPIC_TRENDS_DIR / f"matrix_{today_str}.md"
    matrix_file.write_text(matrix, encoding="utf-8")
    print(f"   Topic matrix: {matrix_file}")

    # 7. Push if requested
    if push:
        import os
        push_to_github(
            [week_file, matrix_file],
            f"Weekly synthesis {today_str} + topic matrix"
        )
    else:
        print("\n" + "="*60)
        print(report)
        print("="*60)
        print("\n" + matrix)


if __name__ == "__main__":
    main(push="--push" in sys.argv)
