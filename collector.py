"""
Literature collector from multiple sources (arXiv, PubMed, etc.)
Using only standard library + requests (no external dependencies).
"""
import os
import json
import logging
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import requests
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('./logs/collector.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LiteratureCollector:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.sources = config.get('sources', {})
        self.keywords = [k.lower() for k in config.get('keywords', [])]
        self.priority_venues = [v.lower() for v in config.get('priority_indicators', {}).get('venues', [])]
        self.priority_terms = [t.lower() for t in config.get('priority_indicators', {}).get('terms', [])]
        self.scoring = config.get('scoring', {})
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.config.get('processing', {}).get('user_agent', 'AI-Health-Lit-Review/1.0')
        })
    
    def fetch_arxiv(self) -> List[Dict[str, Any]]:
        """Fetch recent papers from arXiv using direct API.

        arXiv's date filtering is brittle and broad category queries can be slow.
        We therefore request recent results by category and apply the date filter locally.
        """
        if not self.sources.get('arxiv', {}).get('enabled', True):
            return []
        
        papers = []
        categories = self.sources['arxiv'].get('categories', ['cs.AI', 'cs.LG', 'cs.CL', 'q-bio', 'eess.AS', 'cs.CV', 'cs.NE', 'stat.ML'])
        max_results = min(self.sources['arxiv'].get('max_results_per_day', 50), 25)
        query = f"({' OR '.join(f'cat:{c}' for c in categories)})"
        cutoff_date = (datetime.now() - timedelta(days=7)).date()
        
        url = "https://export.arxiv.org/api/query"
        params = {
            'search_query': query,
            'start': 0,
            'max_results': max_results,
            'sortBy': 'submittedDate',
            'sortOrder': 'descending'
        }
        
        for attempt in range(3):
            try:
                logger.info(f"Fetching arXiv papers with query: {query} (attempt {attempt + 1}/3)")
                response = self.session.get(url, params=params, timeout=20)
                if response.status_code == 429:
                    wait_time = 5 * (attempt + 1)
                    logger.warning(f"arXiv rate limited (429), waiting {wait_time}s before retry")
                    time.sleep(wait_time)
                    continue
                response.raise_for_status()
                
                root = ET.fromstring(response.content)
                ns = {
                    'atom': 'http://www.w3.org/2005/Atom',
                    'arxiv': 'http://arxiv.org/schemas/atom'
                }
                
                for entry in root.findall('atom:entry', ns):
                    try:
                        paper = self._process_arxiv_entry(entry, ns)
                        if not paper:
                            continue
                        if paper.get('published_date'):
                            pub_date = datetime.strptime(paper['published_date'][:10], '%Y-%m-%d').date()
                            if pub_date < cutoff_date:
                                continue
                        if self._is_relevant(paper):
                            papers.append(paper)
                    except Exception as e:
                        logger.warning(f"Error processing arXiv entry: {e}")
                        continue
                break
            except Exception as e:
                logger.error(f"Error fetching arXiv on attempt {attempt + 1}: {e}")
                if attempt < 2:
                    time.sleep(3 * (attempt + 1))
        
        logger.info(f"Fetched {len(papers)} relevant papers from arXiv")
        return papers
    
    def _process_arxiv_entry(self, entry: ET.Element, ns: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Process a single arXiv entry."""
        try:
            # Title
            title_elem = entry.find('atom:title', ns)
            title = title_elem.text.strip() if title_elem is not None else ''
            
            # Abstract
            summary_elem = entry.find('atom:summary', ns)
            abstract = summary_elem.text.strip() if summary_elem is not None else ''
            abstract_lower = abstract.lower()
            
            # Quick keyword filter
            if not self._contains_keywords(abstract_lower):
                return None
            
            # ID
            id_elem = entry.find('atom:id', ns)
            entry_id = id_elem.text if id_elem is not None else ''
            arxiv_id = entry_id.split('/')[-1]
            paper_id = f"arxiv:{arxiv_id}"
            
            # Authors
            authors = []
            for author_elem in entry.findall('atom:author', ns):
                name_elem = author_elem.find('atom:name', ns)
                if name_elem is not None and name_elem.text:
                    authors.append(name_elem.text.strip())
            
            # Published date
            published_elem = entry.find('atom:published', ns)
            published_str = published_elem.text if published_elem is not None else ''
            published_date = published_str[:10] if published_str else ''
            
            # PDF URL
            pdf_url = ''
            for link in entry.findall('atom:link', ns):
                if link.get('title') == 'pdf' or link.get('rel') == 'related':
                    pdf_url = link.get('href', '')
                    break
            
            # DOI
            doi = ''
            for link in entry.findall('atom:link', ns):
                if link.get('title') == 'doi':
                    doi = link.get('href', '')
                    break
            
            # Calculate score
            score = self._calculate_score(
                title=title,
                abstract=abstract_lower,
                venue='arXiv',
                authors=authors,
                published_date=published_date
            )
            
            return {
                'paper_id': paper_id,
                'source': 'arxiv',
                'title': title,
                'authors': authors,
                'abstract': abstract,
                'url': entry_id,
                'pdf_url': pdf_url,
                'published_date': published_date,
                'venue': 'arXiv',
                'doi': doi,
                'keywords': self._extract_keywords_from_text(title + " " + abstract),
                'score': score,
                'priority': 2 if score >= 8 else 1 if score >= 5 else 0,
                'processing_status': 'pending'
            }
            
        except Exception as e:
            logger.error(f"Error processing arXiv entry: {e}")
            return None
    
    def fetch_pubmed(self) -> List[Dict[str, Any]]:
        """Fetch recent papers from PubMed using E-utilities.

        We search with broad AI/medical terms, then fetch XML metadata/abstracts and
        apply recency + relevance filters locally for robustness.
        """
        if not self.sources.get('pubmed', {}).get('enabled', True):
            return []
        
        papers = []
        max_results = self.sources['pubmed'].get('max_results_per_day', 30)
        cutoff_date = (datetime.now() - timedelta(days=7)).date()
        
        keyword_subset = self.keywords[:6]
        ai_terms = [k for k in keyword_subset if k not in ('healthcare', 'medical', 'clinical')]
        keyword_str = " OR ".join([f'\"{k}\"[Title/Abstract]' for k in ai_terms])
        clinical_str = 'healthcare[Title/Abstract] OR medical[Title/Abstract] OR clinical[Title/Abstract] OR patient[Title/Abstract]'
        query = f"({keyword_str}) AND ({clinical_str})"
        
        try:
            logger.info(f"Searching PubMed with query: {query[:150]}...")
            base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
            
            search_params = {
                'db': 'pubmed',
                'term': query,
                'retmax': max_results,
                'sort': 'date',
                'retmode': 'json'
            }
            
            response = self.session.get(base_url + 'esearch.fcgi', params=search_params, timeout=30)
            response.raise_for_status()
            search_data = response.json()
            id_list = search_data.get('esearchresult', {}).get('idlist', [])
            logger.info(f"Found {len(id_list)} PubMed IDs")
            
            if not id_list:
                return []
            
            fetch_params = {
                'db': 'pubmed',
                'id': ','.join(id_list[:max_results]),
                'retmode': 'xml',
                'rettype': 'abstract'
            }
            response = self.session.get(base_url + 'efetch.fcgi', params=fetch_params, timeout=30)
            response.raise_for_status()
            root = ET.fromstring(response.content)
            articles = self._parse_pubmed_xml(root)
            
            for pmid, article in articles.items():
                paper = self._process_pubmed_article(article, pmid)
                if not paper:
                    continue
                if paper.get('published_date'):
                    try:
                        pub_date = datetime.strptime(paper['published_date'][:10], '%Y-%m-%d').date()
                        if pub_date < cutoff_date:
                            continue
                    except Exception:
                        pass
                if self._is_relevant(paper):
                    papers.append(paper)
            
        except Exception as e:
            logger.error(f"Error fetching PubMed: {e}")
        
        logger.info(f"Fetched {len(papers)} relevant papers from PubMed")
        return papers
    
    def _parse_pubmed_xml(self, root: ET.Element) -> Dict[str, Any]:
        """Parse PubMed EFetch XML response into a simple article dictionary."""
        result = {}
        
        for article_node in root.findall('.//PubmedArticle'):
            pmid = article_node.findtext('.//MedlineCitation/PMID', default='').strip()
            if not pmid:
                continue
            
            article = {
                'uid': pmid,
                'title': article_node.findtext('.//Article/ArticleTitle', default='').strip(),
                'abstract': ' '.join(
                    ''.join(elem.itertext()).strip()
                    for elem in article_node.findall('.//Abstract/AbstractText')
                    if ''.join(elem.itertext()).strip()
                ).strip(),
                'source': article_node.findtext('.//Article/Journal/Title', default='').strip(),
                'pubdate': self._extract_pubmed_date(article_node),
                'author': [],
                'doi': ''
            }
            
            for author in article_node.findall('.//AuthorList/Author'):
                lastname = author.findtext('LastName', default='').strip()
                forename = author.findtext('ForeName', default='').strip()
                collective = author.findtext('CollectiveName', default='').strip()
                name = collective or ' '.join(part for part in [forename, lastname] if part).strip()
                if name:
                    article['author'].append({'name': name})
            
            for eloc in article_node.findall('.//Article/ELocationID'):
                if eloc.get('EIdType') == 'doi' and eloc.text:
                    article['doi'] = eloc.text.strip()
                    break
            if not article['doi']:
                for article_id in article_node.findall('.//PubmedData/ArticleIdList/ArticleId'):
                    if article_id.get('IdType') == 'doi' and article_id.text:
                        article['doi'] = article_id.text.strip()
                        break
            
            result[pmid] = article
        
        return result
    
    def _extract_pubmed_date(self, article_node: ET.Element) -> str:
        """Extract a best-effort YYYY-MM-DD publication date from PubMed XML."""
        month_map = {
            'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04', 'may': '05', 'jun': '06',
            'jul': '07', 'aug': '08', 'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'
        }
        pubdate = article_node.find('.//Article/Journal/JournalIssue/PubDate')
        if pubdate is None:
            pubdate = article_node.find('.//PubDate')
        if pubdate is None:
            return ''
        
        year = (pubdate.findtext('Year', default='') or '').strip()
        month = (pubdate.findtext('Month', default='') or '').strip()
        day = (pubdate.findtext('Day', default='') or '').strip()
        medline_date = (pubdate.findtext('MedlineDate', default='') or '').strip()
        
        if not year and medline_date:
            m = re.search(r'(\d{4})', medline_date)
            if m:
                year = m.group(1)
        if not month:
            month = '01'
        elif month.isdigit():
            month = month.zfill(2)
        else:
            month = month_map.get(month[:3].lower(), '01')
        if not day or not day.isdigit():
            day = '01'
        else:
            day = day.zfill(2)
        
        return f"{year}-{month}-{day}" if year else ''
    
    def _process_pubmed_article(self, article: Dict[str, Any], pmid: str) -> Optional[Dict[str, Any]]:
        """Process a PubMed article."""
        try:
            title = article.get('title', '').strip()
            if not title:
                title = article.get('articleTitle', '').strip()
            
            abstract = article.get('abstract', '')
            if not abstract:
                # Try other fields
                abstract = article.get('abstractText', '')
            
            if not abstract:
                return None
            
            abstract_lower = abstract.lower()
            if not self._contains_keywords(abstract_lower):
                return None
            
            # Authors
            authors = []
            author_list = article.get('author', [])
            if isinstance(author_list, list):
                for a in author_list:
                    if isinstance(a, dict):
                        name = a.get('name', '')
                        if name:
                            authors.append(name)
            elif isinstance(author_list, str):
                # Comma-separated string
                authors = [a.strip() for a in author_list.split(',') if a.strip()]
            
            # Publication date
            pubdate = article.get('pubdate', '')
            if not pubdate:
                pubdate = article.get('publicationDate', '')
            published_date = pubdate[:10] if isinstance(pubdate, str) and len(pubdate) >= 10 else pubdate
            
            # Venue / Source
            venue = article.get('source', '')
            if not venue:
                venue = article.get('journal', '')
                if isinstance(venue, dict):
                    venue = venue.get('title', '')
            
            # DOI
            doi = article.get('doi', '')
            if not doi:
                article_ids = article.get('articleids', [])
                if isinstance(article_ids, list):
                    for aid in article_ids:
                        if isinstance(aid, dict) and aid.get('idtype') == 'doi':
                            doi = aid.get('value', '')
            
            # URL
            url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            
            # Calculate score
            score = self._calculate_score(
                title=title,
                abstract=abstract_lower,
                venue=venue,
                authors=authors,
                published_date=published_date
            )
            
            return {
                'paper_id': f"pmid:{pmid}",
                'source': 'pubmed',
                'title': title,
                'authors': authors,
                'abstract': abstract,
                'url': url,
                'pdf_url': '',
                'published_date': published_date,
                'venue': venue,
                'doi': doi,
                'keywords': self._extract_keywords_from_text(title + " " + abstract),
                'score': score,
                'priority': 2 if score >= 8 else 1 if score >= 5 else 0,
                'processing_status': 'pending'
            }
            
        except Exception as e:
            logger.error(f"Error processing PubMed article {pmid}: {e}")
            return None
    
    def _contains_keywords(self, text: str) -> bool:
        """Check if text contains any of our target keywords."""
        return any(keyword in text for keyword in self.keywords)
    
    def _calculate_score(self, title: str, abstract: str, venue: str, 
                        authors: List[str], published_date: str) -> float:
        """Calculate relevance score for a paper."""
        score = 0.0
        
        # Combine text for keyword search
        text = (title + " " + abstract).lower()
        
        # Keyword matches
        keyword_matches = sum(1 for kw in self.keywords if kw in text)
        score += min(keyword_matches * self.scoring.get('keyword_match', 1.0), 5.0)
        
        # Priority venue bonus
        venue_lower = venue.lower()
        if any(pv in venue_lower for pv in self.priority_venues):
            score += self.scoring.get('priority_venue', 3.0)
        
        # Priority terms bonus
        if any(term in text for term in self.priority_terms):
            score += self.scoring.get('priority_term', 2.0)
        
        # Recency (published in last 7 days gets +1)
        try:
            if isinstance(published_date, str) and len(published_date) >= 10:
                pub_date = datetime.strptime(published_date[:10], '%Y-%m-%d')
                if (datetime.now() - pub_date).days <= 7:
                    score += self.scoring.get('recency', 1.0)
        except:
            pass
        
        # Clinical terms bonus
        clinical_terms = ['clinical', 'trial', 'patient', 'cohort', 'prospective', 'retrospective']
        if any(term in text for term in clinical_terms):
            score += 1.0
        
        return round(score, 2)
    
    def _extract_keywords_from_text(self, text: str, max_keywords: int = 10) -> List[str]:
        """Simple keyword extraction from text."""
        # Domain keywords to look for
        domain_keywords = [
            'LLM', 'GPT', 'transformer', 'neural network', 'CNN', 'RNN',
            'multimodal', 'vision-language', 'text-to-image',
            'DPO', 'RLHF', 'reinforcement learning', 'supervised fine-tuning',
            'continual learning', 'federated learning', 'privacy',
            'explainable AI', 'XAI', 'interpretability',
            'clinical trial', 'diagnosis', 'prognosis', 'screening',
            'oncology', 'radiology', 'pathology', 'cardiology',
            'mental health', 'epidemiology', 'public health',
            'deployment', 'implementation', 'evaluation', 'safety',
            'bias', 'fairness', 'ethics'
        ]
        
        text_lower = text.lower()
        found = []
        for kw in domain_keywords:
            if kw.lower() in text_lower and kw not in found:
                found.append(kw)
            if len(found) >= max_keywords:
                break
        
        return found
    
    def _is_relevant(self, paper: Dict[str, Any]) -> bool:
        """Check if paper meets minimum score threshold."""
        min_score = self.scoring.get('min_score_threshold', 3.0)
        return paper['score'] >= min_score
    
    def collect_all(self) -> List[Dict[str, Any]]:
        """Run all collectors and return combined list of papers."""
        all_papers = []
        
        logger.info("Starting literature collection...")
        
        # Fetch from each source
        arxiv_papers = self.fetch_arxiv()
        all_papers.extend(arxiv_papers)
        
        pubmed_papers = self.fetch_pubmed()
        all_papers.extend(pubmed_papers)
        
        # Deduplicate by similar title
        unique_papers = self._deduplicate_by_title(all_papers)
        
        logger.info(f"Total unique papers collected: {len(unique_papers)}")
        return unique_papers
    
    def _deduplicate_by_title(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove papers with very similar titles."""
        seen_titles = {}
        unique = []
        
        for paper in papers:
            # Normalize title
            norm_title = ''.join(c for c in paper['title'].lower() if c.isalnum() or c.isspace())[:50].strip()
            
            if norm_title not in seen_titles:
                seen_titles[norm_title] = paper
                unique.append(paper)
            else:
                # Keep the one with higher score
                if paper['score'] > seen_titles[norm_title]['score']:
                    seen_titles[norm_title] = paper
                    # Replace in unique list
                    for i, u in enumerate(unique):
                        if u['paper_id'] == seen_titles[norm_title]['paper_id']:
                            unique[i] = paper
                            break
        
        return unique

if __name__ == "__main__":
    # Quick test
    with open('config.yaml') as f:
        import yaml
        config = yaml.safe_load(f)
    
    collector = LiteratureCollector(config)
    papers = collector.collect_all()
    print(f"Collected {len(papers)} papers")
    for p in papers[:3]:
        print(f"- {p['title'][:80]}... (score: {p['score']})")