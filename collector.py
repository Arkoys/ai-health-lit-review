"""
AI Health Literature — Unified Multi-Source Collector

Sources:
  1. arXiv        — cs.AI, cs.LG, cs.CY, cs.CV, q-bio, eess.AS
  2. PubMed/NCBI  — clinical AI, governance, evidence, implementation
  3. SemanticScholar — cross-domain, citation awareness
  4. DBLP         — FAccT, AIES, CHI, ICLR, NeurIPS (AI governance/ethics venues)

Usage:
  papers = collect_all()
"""

import json
import re
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import requests
from bs4 import BeautifulSoup

# ─── API Configuration ─────────────────────────────────────────────────────────

ARXIV_API = "http://export.arxiv.org/api/query"
PUBMED_EUTIL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
SEMANTIC_SCHOLAR_API = "https://api.semanticscholar.org/graph/v1"
DBLP_API = "https://api.dblp.org/v1"

HEADERS = {
    "User-Agent": "AI-Health-Lit-Review/2.0 (academic research; hermes-agent)"
}
ARXIV_TIMEOUT = 25
PUB_TIMEOUT = 20
SS_TIMEOUT = 15
DBLP_TIMEOUT = 20

# ─── Search Queries per Source ─────────────────────────────────────────────────

ARXIV_QUERIES = [
    # Query 1: AI Evaluation & Validation in Health
    ("all:AI+evaluation+OR+all:AI+validation+OR+all:algorithmic+audit+OR+all:fairness+healthcare+OR+all:explainable+AI+clinical",
     "AI_EVAL_VALID", 8),
    # Query 2: Governance & Accountability
    ("all:AI+governance+OR+all:algorithmic+accountability+OR+all:AI+regulation+OR+all:AI+oversight",
     "PARTICIPATORY_GOV", 8),
    # Query 3: Adaptive Regulation & Regulatory Sandboxes
    ("all:adaptive+regulation+OR+all:regulatory+sandbox+OR+all:living+lab+AI+OR+all:learning+regulatory+health",
     "ADAPTIVE_REGULATION", 8),
    # Query 4: Evidence, Implementation, NASSS
    ("all:evidence+based+AI+OR+all:implementation+NASSS+OR+all:knowledge+translation+health+OR+all:AI+adoption+barriers",
     "EVIDENCE_IMPLEMENT", 8),
    # Query 5: Clinical AI real-world deployment
    ("all:clinical+AI+OR+all:digital+health+deployment+OR+all:AI+real+world+evidence+OR+all:post+market+surveillance+AI",
     "CLINICAL_HEALTH_AI", 8),
    # Query 6: Participatory AI Design
    ("all:participatory+AI+OR+all:stakeholder+AI+engagement+OR+all:democratic+AI+OR+all:community+AI+health",
     "PARTICIPATORY_GOV", 6),
    # Query 7: Bias, Equity, Fairness in Health AI
    ("all:bias+healthcare+AI+OR+all:health+equity+AI+OR+all:fairness+clinical+AI+OR+all:AI+disparities+health",
     "AI_EVAL_VALID", 6),
    # Query 8: AI Safety & Post-Deployment Monitoring
    ("all:AI+safety+healthcare+OR+all:post+deployment+AI+monitoring+OR+all:AI+incident+reporting+OR+all:AI+adverse+events",
     "AI_EVAL_VALID", 6),
]

PUBMED_QUERIES = [
    # Clinical AI Evaluation
    ("(AI[Title/Abstract] AND (evaluation[Title/Abstract] OR validation[Title/Abstract] OR audit[Title/Abstract])) AND (healthcare[Title/Abstract] OR clinical[Title/Abstract] OR medical[Title/Abstract])",
     "AI_EVAL_VALID", 10),
    # AI Governance
    ("(AI[Title/Abstract] AND (governance[Title/Abstract] OR accountability[Title/Abstract] OR oversight[Title/Abstract] OR regulation[Title/Abstract])) AND (health[Title/Abstract] OR healthcare[Title/Abstract])",
     "PARTICIPATORY_GOV", 10),
    # Adaptive Regulation / FDA
    ("((adaptive regulation[Title/Abstract] OR regulatory sandbox[Title/Abstract] OR FDA[Title/Abstract] OR EU AI Act[Title/Abstract]) AND AI[Title/Abstract])",
     "ADAPTIVE_REGULATION", 8),
    # Evidence & Implementation Science
    ("((evidence-based[Title/Abstract] OR knowledge translation[Title/Abstract] OR implementation science[Title/Abstract] OR NASSS[Title/Abstract]) AND AI[Title/Abstract])",
     "EVIDENCE_IMPLEMENT", 8),
    # Participatory / Stakeholder
    ("((participatory[Title/Abstract] OR stakeholder[Title/Abstract] OR citizen[Title/Abstract] OR community[Title/Abstract]) AND AI[Title/Abstract] AND (health[Title/Abstract] OR medical[Title/Abstract]))",
     "PARTICIPATORY_GOV", 8),
    # Digital Health & Clinical AI
    ("(clinical AI[Title/Abstract] OR digital health[Title/Abstract] OR AI decision support[Title/Abstract]) AND (evaluation[Title/Abstract] OR validation[Title/Abstract])",
     "CLINICAL_HEALTH_AI", 8),
    # AI Bias & Fairness
    ("((bias[Title/Abstract] OR fairness[Title/Abstract] OR equity[Title/Abstract]) AND AI[Title/Abstract] AND (healthcare[Title/Abstract] OR clinical[Title/Abstract]))",
     "AI_EVAL_VALID", 8),
    # AI Sustainability / Pilot Trap
    ("((sustainability[Title/Abstract] OR adoption[Title/Abstract] OR scale-up[Title/Abstract] OR real-world[Title/Abstract]) AND AI[Title/Abstract] AND (health[Title/Abstract] OR clinical[Title/Abstract]))",
     "EVIDENCE_IMPLEMENT", 8),
]

SEMANTIC_SCHOLAR_QUERIES = [
    ("AI evaluation validation healthcare deployment", "AI_EVAL_VALID", 10),
    ("AI governance accountability healthcare", "PARTICIPATORY_GOV", 10),
    ("adaptive regulation AI healthcare FDA", "ADAPTIVE_REGULATION", 8),
    ("AI evidence implementation clinical", "EVIDENCE_IMPLEMENT", 8),
    ("clinical AI decision support real-world", "CLINICAL_HEALTH_AI", 8),
]

DBLP_VENUES = [
    # FAccT: Fairness, Accountability, and Transparency in Socio-Technical Systems
    ("Fairness Accountability Transparency AI", "FAccT", "AI_EVAL_VALID", 10),
    ("algorithmic bias fairness healthcare FAccT", "FAccT", "AI_EVAL_VALID", 8),
    # AIES: AI, Ethics, and Society
    ("AI ethics society governance accountability", "AIES", "PARTICIPATORY_GOV", 10),
    ("ethical AI healthcare algorithmic accountability", "AIES", "AI_EVAL_VALID", 8),
    # CHI: Human-Computer Interaction
    ("human computer interaction AI health fairness", "CHI", "PARTICIPATORY_GOV", 6),
    # ICLR: International Conference on Learning Representations
    ("ICLR AI healthcare evaluation interpretability", "ICLR", "AI_EVAL_VALID", 6),
    # Key health AI governance journals/conferences via DBLP
    ("AI governance healthcare", "AI_Governance", "PARTICIPATORY_GOV", 8),
    ("adaptive regulation AI health", "Adaptive_Reg", "ADAPTIVE_REGULATION", 8),
    ("clinical AI deployment evidence", "Clinical_AI", "CLINICAL_HEALTH_AI", 8),
    ("implementation science AI healthcare", "Impl_Science", "EVIDENCE_IMPLEMENT", 8),
    ("responsible AI healthcare lifecycle", "Responsible_AI", "AI_EVAL_VALID", 8),
]


# ─── Core Fetchers ─────────────────────────────────────────────────────────────

def fetch_arxiv(queries: list, delay: float = 1.0) -> list:
    """Fetch papers from arXiv API."""
    papers = []
    seen_ids = set()

    for query, theme, limit in queries:
        url = f"{ARXIV_API}?search_query={query}&max_results={limit}&sortBy=submittedDate&sortOrder=descending"
        try:
            r = requests.get(url, headers=HEADERS, timeout=ARXIV_TIMEOUT)
            root = ET.fromstring(r.content)
            ns = {"atom": "http://www.w3.org/2005/Atom"}

            for entry in root.findall("atom:entry", ns):
                id_el = entry.find("atom:id", ns)
                if id_el is None:
                    continue
                paper_id = id_el.text.split("/")[-1]
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
                    "themes": [theme],
                })
            time.sleep(delay)
        except Exception as e:
            print(f"   [arXiv] Error on query '{query[:60]}...': {e}")

    return papers


def fetch_pubmed(queries: list, delay: float = 0.4) -> list:
    """Fetch papers from PubMed E-utilities."""
    papers = []
    seen_ids = set()

    for query, theme, limit in queries:
        try:
            # Search
            r = requests.get(
                f"{PUBMED_EUTIL}/esearch.fcgi",
                params={"db": "pubmed", "term": query, "retmax": limit,
                        "retmode": "json", "sort": "date"},
                headers=HEADERS, timeout=PUB_TIMEOUT
            )
            data = r.json()
            ids = data.get("esearchresult", {}).get("idlist", [])
            if not ids:
                continue

            # Fetch details
            r2 = requests.get(
                f"{PUBMED_EUTIL}/efetch.fcgi",
                params={"db": "pubmed", "id": ",".join(ids), "retmode": "xml", "rettype": "abstract"},
                headers=HEADERS, timeout=PUB_TIMEOUT
            )
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

                doi_el = art.find("ArticleIdList/ArticleId[@idType='doi']")
                doi = doi_el.text if doi_el is not None and doi_el.text else ""

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
                    "doi": doi,
                    "themes": [theme],
                })
            time.sleep(delay)
        except Exception as e:
            print(f"   [PubMed] Error on query '{query[:60]}...': {e}")

    return papers


def fetch_semantic_scholar(queries: list, delay: float = 1.0) -> list:
    """Fetch papers from Semantic Scholar Graph API (free tier)."""
    papers = []
    seen_ids = set()
    fields = "paperId,title,authors,abstract,year,venue,externalIds,url,openAccessPdf"

    for query_str, theme, limit in queries:
        try:
            url = f"{SEMANTIC_SCHOLAR_API}/paper/search"
            r = requests.get(url, params={
                "query": query_str,
                "limit": min(limit, 20),  # API max 20 per page
                "fields": fields,
                "year": "2020-2026",
                "sort": "recency"
            }, headers=HEADERS, timeout=SS_TIMEOUT)
            data = r.json()
            items = data.get("data", [])

            for item in items:
                pid = item.get("paperId", "")
                if not pid or pid in seen_ids:
                    continue
                seen_ids.add(pid)

                # Reject non-health papers via title/abstract filtering
                title = item.get("title", "N/A")
                abstract = item.get("abstract", "") or ""
                text_check = f"{title} {abstract}".lower()
                health_indicators = ["health", "medical", "clinical", "patient", "hospital",
                                     "diagnosis", "treatment", "physician", "doctor", "care",
                                     "disease", "drug", "therapy", "surgery", "radiology",
                                     "imaging", "biomarker", "cancer", "diabetes", "mental"]
                if not any(w in text_check for w in health_indicators):
                    continue

                authors = ", ".join(
                    a.get("name", "N/A") for a in item.get("authors", [])[:5]
                )

                ext_ids = item.get("externalIds", {}) or {}
                doi = ext_ids.get("DOI", "") or ""
                ss_url = item.get("url", "") or item.get("openAccessPdf", {}).get("url", "")

                year = str(item.get("year", ""))
                published = f"{year}-01-01" if year else ""

                papers.append({
                    "paper_id": f"ss:{pid}",
                    "source": "semanticscholar",
                    "title": title,
                    "authors": authors,
                    "abstract": abstract[:2000],
                    "url": ss_url or f"https://www.semanticscholar.org/paper/{pid}",
                    "pdf_url": item.get("openAccessPdf", {}).get("url", ""),
                    "published_date": published,
                    "venue": item.get("venue", "") or "N/A",
                    "doi": doi,
                    "themes": [theme],
                })
            time.sleep(delay)
        except Exception as e:
            print(f"   [SemanticScholar] Error on query '{query_str[:60]}...': {e}")

    return papers


def fetch_dblp_venues(delay: float = 1.5) -> list:
    """Fetch papers from DBLP for top AI ethics/governance venues."""
    papers = []
    seen_ids = set()

    for venue_path, venue_name, theme, limit in DBLP_VENUES:
        try:
            url = f"https://dblp.org/search/publ/api?q={venue_path}&format=xml&h={limit}&year=2020%3A2026&c=0"
            r = requests.get(url, headers=HEADERS, timeout=DBLP_TIMEOUT)
            if r.status_code != 200:
                continue
            root = ET.fromstring(r.content)

            for hit in root.findall(".//hit"):
                info = hit.find("info")
                if info is None:
                    continue

                pid = info.find("key")
                if pid is None:
                    continue
                pid_text = pid.text or ""
                if pid_text in seen_ids:
                    continue
                seen_ids.add(pid_text)

                title_el = info.find("title")
                title = title_el.text.strip() if title_el is not None and title_el.text else "N/A"

                # Skip non-English / non-health titles roughly
                title_lower = title.lower()
                health_kw = ["health", "medical", "clinical", "patient", "ai", "algorithm",
                              "fairness", "bias", "governance", "ethics", "regulation",
                              "explainability", "interpretability", "decision", "diagnos"]
                if not any(k in title_lower for k in health_kw):
                    continue

                abstract_el = info.find("abstract")
                abstract = abstract_el.text[:1000] if abstract_el is not None and abstract_el.text else ""

                authors_els = info.findall("authors/author")
                authors = ", ".join(
                    a.text for a in authors_els[:5] if a is not None and a.text
                ) or "N/A"

                year_el = info.find("year")
                year = year_el.text if year_el is not None and year_el.text else ""
                published = f"{year}-01-01" if year else ""

                venue_el = info.find("venue")
                venue = venue_el.text if venue_el is not None and venue_el.text else venue_name
                if not venue:
                    venue = venue_name

                url_el = info.find("url")
                url = url_el.text if url_el is not None and url_el.text else f"https://dblp.org/rec/{pid_text}"

                doi_el = info.find("doi")
                doi = doi_el.text if doi_el is not None and doi_el.text else ""

                papers.append({
                    "paper_id": f"dblp:{pid_text}",
                    "source": "dblp",
                    "title": title,
                    "authors": authors,
                    "abstract": abstract,
                    "url": url,
                    "pdf_url": "",
                    "published_date": published,
                    "venue": venue,
                    "doi": doi,
                    "themes": [theme],
                })
            time.sleep(delay)
        except Exception as e:
            print(f"   [DBLP] Error on venue {venue_name}: {e}")

    return papers


# ─── Main Collector ────────────────────────────────────────────────────────────

def collect_all(dry_run: bool = False) -> list:
    """
    Collect papers from all sources.
    Returns list of paper dicts (no dedup — caller should dedup).
    """
    all_papers = []

    if dry_run:
        print("  [DRY RUN] Skipping all API calls")
        return all_papers

    print("  [arXiv] Fetching...")
    arxiv_papers = fetch_arxiv(ARXIV_QUERIES)
    print(f"  [arXiv] Got {len(arxiv_papers)} papers")
    all_papers.extend(arxiv_papers)

    print("  [PubMed] Fetching...")
    pubmed_papers = fetch_pubmed(PUBMED_QUERIES)
    print(f"  [PubMed] Got {len(pubmed_papers)} papers")
    all_papers.extend(pubmed_papers)

    print("  [SemanticScholar] Fetching...")
    ss_papers = fetch_semantic_scholar(SEMANTIC_SCHOLAR_QUERIES)
    print(f"  [SemanticScholar] Got {len(ss_papers)} papers")
    all_papers.extend(ss_papers)

    print("  [DBLP] Fetching governance/ethics venues...")
    dblp_papers = fetch_dblp_venues()
    print(f"  [DBLP] Got {len(dblp_papers)} papers")
    all_papers.extend(dblp_papers)

    return all_papers


def dedup_papers(papers: list, existing_ids: set, existing_titles: set) -> list:
    """Remove duplicates based on ID and title."""
    cleaned = []
    for p in papers:
        pid = p.get("paper_id", "")
        title_key = re.sub(r"[^\w]", "", p.get("title", "")[:80]).lower()
        if pid in existing_ids or title_key in existing_titles:
            continue
        cleaned.append(p)
    return cleaned


if __name__ == "__main__":
    print("Testing collector (dry run)...")
    papers = collect_all(dry_run=True)
    print(f"\nWould collect from: arXiv, PubMed, SemanticScholar, DBLP")
