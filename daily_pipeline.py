"""
AI Health Literature — Daily Pipeline (Unified)

Runs the complete daily literature workflow:
  1. Search arXiv + PubMed
  2. Score & rank papers
  3. Update JSON paper database
  4. Write formatted digest
  5. Rebuild aggregate files
  6. Push to GitHub

Usage:
  python3 daily_pipeline.py [--push]
"""

import json
import os
import re
import subprocess
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import requests
import ranker

PROJECT_ROOT = Path(__file__).parent
DB_PATH = PROJECT_ROOT / "data" / "papers.json"
DIGESTS_DIR = PROJECT_ROOT / "outputs" / "digests"
AGGREGATE_FILE = DIGESTS_DIR / "ALL_DIGESTS.md"
AGGREGATE_SHORT = DIGESTS_DIR / "ALL_DIGESTS_SHORT.md"
GITHUB_TOKEN = ""
GITHUB_REPO = ""


# ─── Load Config ──────────────────────────────────────────────────────────────

def load_env():
    global GITHUB_TOKEN, GITHUB_REPO
    with open(PROJECT_ROOT / ".env") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k] = v
    GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
    GITHUB_REPO = os.environ.get("GITHUB_REPO", "")


# ─── Paper Collection ─────────────────────────────────────────────────────────

SEARCH_QUERIES = {
    # arXiv queries: use cat:cs.* + health/AI terms + theme keywords
    # ti: field search is unreliable on arXiv — use cat: + all: combination instead
    "arxiv": [
        # AI_EVAL_VALID: AI evaluation, validation, bias, fairness in health context
        ("(cat:cs.AI+OR+cat:cs.LG+OR+cat:cs.CV)+AND+(all:health+OR+all:clinical+OR+all:medical+OR+all:healthcare)+AND+(all:evaluation+OR+all:validation+OR+all:bias+OR+all:fairness+OR+all:explainability+OR+all:safety+OR+all:robustness)", 8),
        # PARTICIPATORY_GOV: stakeholder, citizen, co-design in health AI
        ("(cat:cs.AI+OR+cat:cs.SC+OR+cat:cs.HC)+AND+(all:health+OR+all:clinical+OR+all:medical)+AND+(all:participatory+OR+all:stakeholder+OR+all:citizen+OR+all:accountability+OR+all:co-design+OR+all:democratic+OR+all:public+engagement)", 8),
        # ADAPTIVE_REGULATION: adaptive/lifecycle regulation, FDA, sandboxes for health AI
        ("(cat:cs.AI+OR+cat:cs.SC+OR+cat:cs.ET)+AND+(all:health+OR+all:clinical+OR+all:medical)+AND+(all:adaptive+OR+all:regulatory+sandbox+OR+all:FDA+OR+all:MDR+OR+all:lifecycle+OR+all:iterative+OR+all:post-market+OR+all:continuous+monitoring)", 8),
        # EVIDENCE_IMPLEMENT: implementation, adoption, NASSS, evidence for health AI
        ("(cat:cs.AI+OR+cat:cs.HC+OR+cat:cs.IR)+AND+(all:health+OR+all:clinical+OR+all:medical)+AND+(all:implementation+OR+all:adoption+OR+all:evidence+OR+all:NASSS+OR+all:uptake+OR+all:scale-up+OR+all:translation)", 8),
        # CLINICAL_HEALTH_AI: clinical AI systems, diagnostics, digital health
        ("(cat:cs.CV+OR+cat:cs.AI+OR+cat:cs.CL)+AND+(all:clinical+OR+all:medical+OR+all:healthcare+OR+all:patient+OR+all:doctor+OR+all:radiology+OR+all:diagnostic)+AND+(all:AI+OR+all:machine+learning+OR+all:deep+learning+OR+all:LLM+OR+all:neural+OR+all:algorithm)", 8),
    ],
    "pubmed": [
        # Each query targets one PhD theme with health AI intersection
        ("(AI[Title/Abstract]+AND+(evaluation[Title/Abstract]+OR+validation[Title/Abstract]+OR+bias[Title/Abstract]+OR+fairness[Title/Abstract]+OR+explainability[Title/Abstract]))+AND+(health[Title/Abstract]+OR+clinical[Title/Abstract]+OR+medical[Title/Abstract]+OR+healthcare[Title/Abstract])+AND+2024:2026[dp]", 8),
        ("(AI[Title/Abstract]+AND+(participatory[Title/Abstract]+OR+stakeholder[Title/Abstract]+OR+citizen[Title/Abstract]+OR+accountability[Title/Abstract]+OR+governance[Title/Abstract]+OR+co-design[Title/Abstract]))+AND+(health[Title/Abstract]+OR+clinical[Title/Abstract]+OR+medical[Title/Abstract])+AND+2024:2026[dp]", 8),
        ("(AI[Title/Abstract]+AND+(adaptive+regulation[Title/Abstract]+OR+regulatory+sandbox[Title/Abstract]+OR+FDA[Title/Abstract]+OR+lifecycle[Title/Abstract]+OR+iterative[Title/Abstract]+OR+post-market[Title/Abstract]))+AND+(health[Title/Abstract]+OR+clinical[Title/Abstract]+OR+medical[Title/Abstract])+AND+2024:2026[dp]", 8),
        ("(AI[Title/Abstract]+AND+(implementation[Title/Abstract]+OR+adoption[Title/Abstract]+OR+evidence[Title/Abstract]+OR+uptake[Title/Abstract]+OR+scale-up[Title/Abstract]+OR+NASSS[Title/Abstract]))+AND+(health[Title/Abstract]+OR+clinical[Title/Abstract]+OR+medical[Title/Abstract]+OR+digital[Title/Abstract])+AND+2024:2026[dp]", 8),
        ("(clinical[Title/Abstract]+OR+medical[Title/Abstract]+OR+healthcare[Title/Abstract])+AND+(AI[Title/Abstract]+OR+machine+learning[Title/Abstract]+OR+deep+learning[Title/Abstract]+OR+digital+health[Title/Abstract]+OR+diagnostic[Title/Abstract])+AND+(safety[Title/Abstract]+OR+performance[Title/Abstract]+OR+validation[Title/Abstract]+OR+reliability[Title/Abstract])+AND+2024:2026[dp]", 8),
    ]
}


def fetch_arxiv(queries: list) -> list:
    papers = []
    seen_ids = set()
    for query, limit in queries:
        url = f"http://export.arxiv.org/api/query?search_query={query}&max_results={limit}&sortBy=submittedDate&sortOrder=descending"
        try:
            r = requests.get(url, timeout=20)
            root = ET.fromstring(r.content)
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            for entry in root.findall("atom:entry", ns):
                paper_id = entry.find("atom:id", ns)
                if paper_id is None:
                    continue
                paper_id = paper_id.text.split("/")[-1]
                if paper_id in seen_ids:
                    continue
                seen_ids.add(paper_id)
                title_el = entry.find("atom:title", ns)
                title = re.sub(r"\s+", " ", title_el.text).strip() if title_el is not None and title_el.text else "N/A"
                abs_el = entry.find("atom:summary", ns)
                abstract = re.sub(r"\s+", " ", abs_el.text).strip() if abs_el is not None and abs_el.text else ""
                authors = [a.find("atom:name", ns) for a in entry.findall("atom:author", ns)[:5]]
                authors = [a.text for a in authors if a is not None and a.text]
                pub_el = entry.find("atom:published", ns)
                published = pub_el.text[:10] if pub_el is not None and pub_el.text else ""
                url_link = f"https://arxiv.org/abs/{paper_id.split('v')[0]}"
                pdf_link = f"https://arxiv.org/pdf/{paper_id.split('v')[0]}"
                papers.append({
                    "paper_id": paper_id,
                    "source": "arxiv",
                    "title": title,
                    "authors": ", ".join(authors) if authors else "N/A",
                    "abstract": abstract,
                    "url": url_link,
                    "pdf_url": pdf_link,
                    "published_date": published,
                    "venue": "arXiv",
                    "doi": "",
                    "themes": [],
                })
        except Exception as e:
            print(f"   arXiv error: {e}")
    return papers


def fetch_pubmed(queries: list) -> list:
    papers = []
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    seen_ids = set()

    for query, limit in queries:
        try:
            r = requests.get(f"{base}/esearch.fcgi?db=pubmed&term={query}&retmax={limit}&retmode=json&sort=date", timeout=15)
            data = r.json()
            ids = data.get("esearchresult", {}).get("idlist", [])
            if not ids:
                continue

            ids_str = ",".join(ids)
            r2 = requests.get(f"{base}/efetch.fcgi?db=pubmed&id={ids_str}&retmode=xml&rettype=abstract", timeout=15)
            root = ET.fromstring(r2.content)

            for art in root.findall(".//PubmedArticle"):
                pmid_el = art.find("MedlineCitation/PMID")
                if pmid_el is None or pmid_el.text is None:
                    continue
                pmid = pmid_el.text
                if pmid in seen_ids:
                    continue
                seen_ids.add(pmid)

                title_el = art.find("ArticleTitle")
                title = (title_el.text or "N/A").strip() if title_el is not None else "N/A"
                abs_els = art.findall("AbstractText")
                abstract = " ".join(ae.text.strip() for ae in abs_els if ae.text) if abs_els else ""
                pubdate_el = art.find("Journal/JournalIssue/PubDate")
                year = ""
                if pubdate_el is not None:
                    y_el = pubdate_el.find("Year")
                    m_el = pubdate_el.find("Month")
                    d_el = pubdate_el.find("Day")
                    year = y_el.text if y_el is not None and y_el.text else ""
                    month = m_el.text if m_el is not None and m_el.text else "01"
                    day = d_el.text if d_el is not None and d_el.text else "01"
                    if month.isdigit():
                        month = f"{int(month):02d}"
                    else:
                        MONTH_MAP = {"Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
                                     "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
                                     "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"}
                        month = MONTH_MAP.get(month, "01")
                    year = f"{year}-{month}-{day}" if year else ""
                else:
                    year = ""

                journal_el = art.find("Journal/Title")
                journal = journal_el.text if journal_el is not None and journal_el.text else "N/A"
                authors_els = art.findall("Author")
                author_parts = []
                for a in authors_els[:5]:
                    ln = a.find("LastName")
                    if ln is None or ln.text is None:
                        continue
                    fn = a.find("ForeName")
                    initial = fn.text[0] if fn is not None and fn.text else "."
                    author_parts.append(f"{ln.text} {initial}")
                authors = ", ".join(author_parts) if author_parts else "N/A"

                papers.append({
                    "paper_id": f"pmid:{pmid}",
                    "source": "pubmed",
                    "title": title,
                    "authors": authors,
                    "abstract": abstract,
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                    "pdf_url": "",
                    "published_date": year,
                    "venue": journal,
                    "doi": "",
                    "themes": [],
                })
        except Exception as e:
            print(f"   PubMed error: {e}")
    return papers


def collect_papers() -> list:
    print("  Collecting papers...")
    arxiv_papers = fetch_arxiv(SEARCH_QUERIES["arxiv"])
    pubmed_papers = fetch_pubmed(SEARCH_QUERIES["pubmed"])
    all_papers = arxiv_papers + pubmed_papers
    print(f"  Collected {len(all_papers)} papers ({len(arxiv_papers)} arXiv, {len(pubmed_papers)} PubMed)")
    return all_papers


# ─── Database Update ────────────────────────────────────────────────────────────

def load_db() -> dict:
    if DB_PATH.exists():
        with open(DB_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {
        "metadata": {"created": datetime.now().isoformat(), "total_papers": 0, "version": "1.0"},
        "keyword_themes": {}, "priority_venues": [], "papers": []
    }


def save_db(db: dict):
    db["metadata"]["last_updated"] = datetime.now().isoformat()
    db["metadata"]["total_papers"] = len(db["papers"])
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False, default=str)
    print(f"  Saved {len(db['papers'])} papers to database")


def update_database(new_papers: list) -> list:
    """Add new papers to DB, avoid duplicates, return scored+ranked papers."""
    db = load_db()

    # Build dedup key
    existing_keys = {p.get("paper_id", "") for p in db["papers"]}
    existing_titles = {re.sub(r"[^\w]", "", p.get("title", "").lower())[:80] for p in db["papers"]}

    added = []
    for paper in new_papers:
        key = paper.get("paper_id", "")
        title_key = re.sub(r"[^\w]", "", paper.get("title", "").lower())[:80]

        if key in existing_keys or title_key in existing_titles:
            continue  # already in DB

        # Score it
        scored = ranker.score_paper(paper)
        scored["added_date"] = datetime.now().strftime("%Y-%m-%d")
        scored["added_via"] = "daily_pipeline"
        db["papers"].append(scored)
        added.append(scored)

    save_db(db)
    print(f"  Added {len(added)} new papers to DB")
    return added


# ─── Digest Generation ──────────────────────────────────────────────────────────

def check_digest_version() -> tuple[str, int]:
    """Find the next available digest filename for today."""
    today = datetime.now().strftime("%Y-%m-%d")
    base = DIGESTS_DIR / f"digest_{today}.md"
    if not base.exists():
        return str(base), 1
    v2 = DIGESTS_DIR / f"digest_{today}_v2.md"
    if not v2.exists():
        return str(v2), 2
    for i in range(3, 100):
        f = DIGESTS_DIR / f"digest_{today}_v{i}.md"
        if not f.exists():
            return str(f), i
    return str(base), 1


def generate_digest_markdown(papers: list, added_count: int) -> str:
    """Generate the full formatted digest markdown."""
    today_str = datetime.now().strftime("%Y-%m-%d")
    day_name = datetime.now().strftime("%A")

    # Score and rank all papers
    scored = [ranker.score_paper(p) for p in papers]
    ranked = ranker.rank_papers(scored)

    priority_3 = [p for p in ranked if p["priority"] == 3]
    priority_2 = [p for p in ranked if p["priority"] == 2]
    priority_1 = [p for p in ranked if p["priority"] == 1]

    PRIORITY_EMOJI = {3: "🔴", 2: "🟡", 1: "⚪"}
    PRIORITY_LABEL = {3: "Must Read", 2: "Important", 1: "Supplementary"}

    lines = [
        f"# 🔬 AI Health Literature Review — Daily Digest",
        f"**Date:** {today_str} ({day_name}) | **Papers analyzed:** {len(ranked)} | "
        f"**New in DB:** +{added_count}",
        "",
        "---",
        "",
    ]

    # Executive Summary — aggregate themes
    theme_counts = defaultdict(int)
    for p in ranked:
        for t in p.get("themes", []):
            theme_counts[t] += 1

    top_themes = sorted(theme_counts.items(), key=lambda x: -x[1])[:5]
    theme_bullets = ", ".join(f"`{t}` ({n} papers)" for t, n in top_themes)

    lines.extend([
        "## 📊 Executive Summary",
        f"**Top themes today:** {theme_bullets}",
        f"**Priority breakdown:** 🔴 {len(priority_3)} · 🟡 {len(priority_2)} · ⚪ {len(priority_1)}",
        "",
    ])

    # Trending topics (detect from content)
    all_text = " ".join(p.get("title", "") + " " + p.get("abstract", "") for p in ranked).lower()
    topic_signals = {
        "🔴 Adaptive AI Evaluation": sum(1 for kw in ["adaptive", "learning", "iterative", "continuously", "dynamic"] if kw in all_text),
        "🔴 Regulatory Divergence (US/EU)": sum(1 for kw in ["FDA", "MDR", "EU", "regulatory DNA", "US agility"] if kw in all_text),
        "🟡 Governance Frameworks": sum(1 for kw in ["governance", "framework", "institutional", "pilot trap"] if kw in all_text),
        "🟡 Evidence Synthesis": sum(1 for kw in ["evidence", "synthesis", "meta-analysis", "meta-analysis"] if kw in all_text),
        "🟡 Implementation Barriers": sum(1 for kw in ["implementation", "adoption", "NASSS", "uptake", "barriers"] if kw in all_text),
    }
    trending = [t for t, c in topic_signals.items() if c >= 1]
    if trending:
        lines.append(f"**Trending:** {' · '.join(trending[:3])}")
    lines.append("")

    # Featured Papers
    lines.extend(["## 🏆 Featured Papers", ""])

    for p in priority_3:
        lines.extend(generate_paper_block(p, PRIORITY_EMOJI[3], PRIORITY_LABEL[3]))
        lines.append("")

    if priority_2:
        lines.extend(["## 📚 Supporting Papers", ""])
        for p in priority_2[:7]:
            lines.extend(generate_paper_block(p, PRIORITY_EMOJI[2], PRIORITY_LABEL[2]))
            lines.append("")

    # Cross-Analysis
    cross = [p for p in ranked if len(p.get("themes", [])) >= 2]
    gaps = [t for t in ["AI_EVAL_VALID", "PARTICIPATORY_GOV", "ADAPTATIVE_REGULATION", "EVIDENCE_IMPLEMENT", "CLINICAL_HEALTH_AI"]
            if t not in theme_counts]

    lines.extend([
        "---",
        "",
        "## 🔍 Cross-Analysis",
        "",
        f"**Cross-theme papers:** {len(cross)}/{len(ranked)} address multiple themes simultaneously.",
    ])
    if gaps:
        lines.append(f"**Gaps today:** No papers found for: `{', '.join(gaps)}`")
    lines.append("")

    # Topic Distribution
    lines.extend([
        "## 📈 Topic Distribution",
        "",
        "| Theme | Papers |",
        "|-------|--------|",
    ])
    for theme, count in sorted(theme_counts.items(), key=lambda x: -x[1]):
        bar = "█" * min(count, 10)
        lines.append(f"| {theme} | {bar} {count} |")
    lines.append("")

    # Priority Queue
    lines.extend(["## 🎯 Priority Queue", ""])
    for i, p in enumerate(priority_3[:5], 1):
        url = p.get("url", "")
        link = f"[🔗 arXiv]({url})" if "arxiv" in url else f"[🔗 Link]({url})" if url else ""
        lines.append(f"{i}. **{p['title'][:80]}** {link}")
    lines.append("")

    # Footer
    lines.extend([
        "---",
        "",
        f"*Generated: {datetime.now().isoformat()}*",
        f"*Project: [Arkoys/ai-health-lit-review](https://github.com/Arkoys/ai-health-lit-review)*",
        f"*Sources: arXiv · PubMed · JMIR · Cureus · Front Med · Nature Medicine · Lancet*",
    ])

    return "\n".join(lines)


def generate_paper_block(p: dict, emoji: str, label: str) -> list:
    """Generate a formatted block for a single paper."""
    url = p.get("url", "") or p.get("pdf_url", "")
    arxiv_link = f"https://arxiv.org/abs/{p.get('paper_id', '').split('v')[0]}" if "arxiv" in url or "arxiv" in p.get("source", "") else ""
    pdf_link = f"https://arxiv.org/pdf/{p.get('paper_id', '').split('v')[0]}" if arxiv_link else ""
    pubmed_link = f"https://pubmed.ncbi.nlm.nih.gov/{p.get('paper_id', '').replace('pmid:', '')}/" if "pmid" in p.get("paper_id", "") else ""

    lines = [
        f"### {emoji} {p.get('title', 'N/A')}",
        "",
        f"**Authors:** {p.get('authors', 'N/A')} | **Source:** {p.get('source', 'N/A')} | **Published:** {p.get('published_date', 'N/A')}",
        f"**Venue:** {p.get('venue', 'N/A')} | **Priority:** {label} | **Score:** `{p['scores']['composite']}`",
    ]

    # Score breakdown
    sc = p["scores"]
    lines.append(f"**Score breakdown:** theme `{sc['theme_score']}` + novelty `{sc['novelty']}` + recency `{sc['recency']}` + venue `{sc['venue']}` + methods `{sc['methods']}`")

    # Links
    link_parts = []
    if arxiv_link:
        link_parts.append(f"[arXiv]({arxiv_link})")
    if pdf_link:
        link_parts.append(f"[PDF]({pdf_link})")
    if pubmed_link:
        link_parts.append(f"[PubMed]({pubmed_link})")
    if url and not arxiv_link and not pubmed_link:
        link_parts.append(f"[Link]({url})")
    if link_parts:
        lines.append(f"**Links:** {' · '.join(link_parts)}")

    # Themes
    themes = p.get("themes", [])
    if themes:
        lines.append(f"**Themes:** `{'`, `'.join(themes)}`")

    # Abstract
    abstract = p.get("abstract", "")
    if abstract:
        snippet = abstract[:350].strip()
        if len(abstract) > 350:
            snippet += "…"
        lines.extend(["", f"> {snippet}", ""])

    return lines


# ─── Aggregate Files ───────────────────────────────────────────────────────────

def rebuild_aggregate():
    """Rebuild ALL_DIGESTS.md and ALL_DIGESTS_SHORT.md."""
    digests = sorted(DIGESTS_DIR.glob("digest_*.md"), reverse=True)

    # Full aggregate
    all_lines = ["# AI Health Literature Review — All Digests\n\n---\n"]
    for f in digests:
        content = f.read_text(encoding="utf-8")
        # Extract date from filename
        date_match = re.search(r"(\d{4}-\d{2}-\d{2}(?:_v\d+)?)", f.name)
        date_label = date_match.group(1) if date_match else f.name
        all_lines.append(f"## Source file: [{date_label}](outputs/digests/{f.name})\n\n")
        all_lines.append(content)
        all_lines.append("\n\n---\n\n")

    AGGREGATE_FILE.write_text("".join(all_lines), encoding="utf-8")

    # Short index
    short_lines = ["# AI Health Literature — Short Index\n\n## Latest Digests\n\n"]
    for f in digests[:14]:
        date_match = re.search(r"(\d{4}-\d{2}-\d{2}(?:_v\d+)?)", f.name)
        date_label = date_match.group(1) if date_match else f.name
        # Extract paper titles
        titles = re.findall(r"^### [\w🔴🟡⚪]+ (.+)$", content, re.M)
        short_lines.append(f"### [{date_label}](outputs/digests/{f.name})\n")
        for t in titles[:5]:
            short_lines.append(f"- {t[:100]}\n")
        short_lines.append("\n")

    AGGREGATE_SHORT.write_text("".join(short_lines), encoding="utf-8")
    print(f"  Rebuilt aggregate files ({len(digests)} digests)")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main(push: bool = False):
    print(f"\n📅 Daily Pipeline — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    load_env()

    # 1. Collect
    new_papers = collect_papers()

    # 2. Update DB and get new scored papers
    added = update_database(new_papers)

    # 3. Score all papers for today's digest
    all_db_papers = load_db()["papers"]
    # Combine: papers from today collection + recent DB entries
    today_str = datetime.now().strftime("%Y-%m-%d")
    recent = [p for p in all_db_papers
              if p.get("added_date", "") == today_str
              or p.get("published_date", "") == today_str]

    # If we got new papers, use those. Otherwise use all collected today.
    papers_for_digest = added if added else new_papers

    # 4. Generate digest
    digest_path, version = check_digest_version()
    digest_content = generate_digest_markdown(papers_for_digest, len(added))
    Path(digest_path).parent.mkdir(parents=True, exist_ok=True)
    Path(digest_path).write_text(digest_content, encoding="utf-8")
    print(f"  Digest written: {digest_path} (v{version})")

    # 5. Rebuild aggregates
    rebuild_aggregate()

    # 6. Push
    if push:
        push_to_github(
            [digest_path, AGGREGATE_FILE, AGGREGATE_SHORT],
            f"Daily digest {today_str} (v{version}): {len(added)} new papers"
        )

    print(f"\n✅ Pipeline complete — {len(added)} new papers added, digest v{version} ready")
    return digest_content, len(added), version


def push_to_github(files: list, commit_msg: str) -> bool:
    """Push files to GitHub. Gracefully skips gitignored files."""
    if not GITHUB_TOKEN or not GITHUB_REPO:
        print("  ⚠️ No GitHub config — skipping push")
        return False

    remote_url = f"https://x-access-token:{GITHUB_TOKEN}@github.com/{GITHUB_REPO}.git"
    subprocess.run(["git", "remote", "set-url", "origin", remote_url], cwd=PROJECT_ROOT, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Hermes Agent"], cwd=PROJECT_ROOT, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "hermes-agent@users.noreply.github.com"], cwd=PROJECT_ROOT, check=True, capture_output=True)

    for f in files:
        f_path = Path(f) if isinstance(f, str) else f
        # Skip gitignored files
        result = subprocess.run(
            ["git", "check-ignore", str(f_path)],
            cwd=PROJECT_ROOT, capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f"  ↩️  Skipping gitignored: {f_path.name}")
            continue
        subprocess.run(["git", "add", str(f_path)], cwd=PROJECT_ROOT, check=True, capture_output=True)

    result = subprocess.run(["git", "status", "--short"], cwd=PROJECT_ROOT, capture_output=True, text=True)
    if not result.stdout.strip():
        print("  Nothing to push — no changes")
        return True

    subprocess.run(["git", "commit", "-m", commit_msg], cwd=PROJECT_ROOT, check=True, capture_output=True)
    result = subprocess.run(["git", "push", "origin", "main"], cwd=PROJECT_ROOT, capture_output=True, text=True)
    ok = result.returncode == 0
    print("  ✅ GitHub push OK" if ok else f"  ❌ Push failed: {result.stderr.decode()}")
    return ok


def send_telegram_digest(content: str, chat_id: str = None) -> bool:
    """Send digest to Telegram. Reads token from .env TELEGRAM_BOT_TOKEN."""
    import os as _os
    with open(PROJECT_ROOT / ".env") as _f:
        for line in _f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                _os.environ[k] = v

    bot_token = _os.environ.get("TELEGRAM_BOT_TOKEN", "")
    target = chat_id or _os.environ.get("TELEGRAM_CHANNEL_ID", "") or _os.environ.get("TELEGRAM_CHAT_ID", "")

    if not bot_token or not target:
        print("  ⚠️ Telegram: no bot token or chat ID configured — skipping")
        return False

    import requests as _req
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    max_len = 4000
    sent = 0
    try:
        # Send in chunks if needed
        for i in range(0, len(content), max_len):
            chunk = content[i:i+max_len]
            r = _req.post(url, json={"chat_id": target, "text": chunk, "parse_mode": "Markdown"}, timeout=30)
            if r.ok:
                sent += 1
        print(f"  ✅ Telegram: sent {sent} message(s)")
        return True
    except Exception as e:
        print(f"  ❌ Telegram error: {e}")
        return False


if __name__ == "__main__":
    import sys
    push = "--push" in sys.argv
    telegram = "--telegram" in sys.argv
    content, added_count, version = main(push=push)

    if telegram:
        send_telegram_digest(content)
    elif push:
        # Also send to Telegram when --push is used
        send_telegram_digest(content)
