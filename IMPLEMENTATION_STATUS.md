# Conference Source Implementation Status

## ✅ Implemented

### NeurIPS Scraper
- **Status**: Fully working
- **Source**: https://proceedings.neurips.cc/
- **Coverage**: Volumes 2020-2024
- **Metadata**: Title, authors, abstract, PDF URL, DOI, publication date
- **Max per day**: Configurable (default 20)
- **Rate limiting**: Respectful delays (0.5s between papers, 1s between volumes)
- **Filtering**: Keyword-based relevance filter applied
- **Scoring**: Full priority scoring (keyword matches, venue priority, terms, recency)

**Implementation details**:
- Navigates from main page to volume pages (`/paper_files/paper/YYYY`)
- Parses `<li class="conference">` blocks for paper listings
- Extracts short title/authors from listing page
- Fetches individual paper pages for full abstract and metadata via `<meta>` tags
- Paper ID format: `neurips:<hash>`
- Venue format: `NeurIPS 2024`

### Integration
- `fetch_conferences()` method added to `LiteratureCollector`
- Dispatches to site-specific scrapers based on URL pattern
- Filters all collected papers through `_is_relevant()`
- Integrated into `collect_all()` workflow
- Configurable via `config.yaml` under `sources.conferences`

## 🚧 Placeholder (Not Yet Implemented)

These scrapers are defined but return empty arrays with log messages:

- `_scrape_nature_medicine()` - RSS feed was 404
- `_scrape_jama()` - RSS feed was 404
- `_scrape_icml()` - Not implemented

To implement:
1. Find current data source (RSS, HTML, API)
2. Adjust parsing logic
3. Test with real data
4. Remove "not yet implemented" log

## 📝 Configuration

In `config.yaml`:

```yaml
conferences:
  enabled: true  # Set false to disable all conference sources
  sites:
    - https://proceedings.neurips.cc/
    # Add more sites as they are implemented
  max_results_per_day: 20
```

## 🧪 Testing

Test conference source only:

```bash
python3 -c "
from collector import LiteratureCollector
import yaml
with open('config.yaml') as f:
    config = yaml.safe_load(f)
config['sources']['conferences']['enabled'] = True
config['sources']['conferences']['sites'] = ['https://proceedings.neurips.cc/']
config['sources']['conferences']['max_results_per_day'] = 5
config['sources']['arxiv']['enabled'] = False
config['sources']['pubmed']['enabled'] = False
collector = LiteratureCollector(config)
papers = collector.fetch_conferences()
print(f'Fetched {len(papers)} papers')
for p in papers[:3]:
    print(p['title'], p['venue'], p['score'])
"
```

Test full workflow:

```bash
python3 run_daily.py
```

## 📊 Example Output

```
2026-04-08 04:41:27,632 - collector - INFO - Found 4034 paper entries in volume 2024
2026-04-08 04:41:31,333 - collector - INFO - Collected 5 papers so far from NeurIPS
2026-04-08 04:41:32,335 - collector - INFO - Fetched 5 relevant papers from https://proceedings.neurips.cc/ (filtered from 5)
```

Typical paper:
```python
{
  'paper_id': 'neurips:000f947dcaff8fbffcc3f53a1314f358',
  'source': 'conference',
  'title': 'MicroAdam: Accurate Adaptive Optimization with Low Space Overhead and Provable Convergence',
  'authors': ['Ionut-Vlad Modoranu', 'Mher Safaryan', ...],
  'abstract': 'We present MicroAdam, a memory-efficient variant of Adam...',
  'url': 'https://proceedings.neurips.cc/paper_files/paper/2024/hash/000f947dcaff8fbffcc3f53a1314f358-Abstract-Conference.html',
  'pdf_url': 'https://proceedings.neurips.cc/paper_files/paper/2024/hash/000f947dcaff8fbffcc3f53a1314f358-Paper-Conference.pdf',
  'published_date': '2024-01-01',
  'venue': 'NeurIPS 2024',
  'doi': '10.5555/1234567',
  'score': 3.0,
  'priority': 0,
  'processing_status': 'pending'
}
```

## 🔜 Next Steps

1. Find working RSS/HTML sources for Nature Medicine and JAMA
2. Implement ICML scraper (similar structure to NeurIPS)
3. Consider adding ACM Digital Library, IEEE Xplore if needed
4. Add venue-based priority boosting for top conferences (NeurIPS, ICML, ICML, JAMA, Nature Med) in config
5. Cache volume listings to avoid re-parsing main page every run
6. Add more robust error handling for site layout changes
