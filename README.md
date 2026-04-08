# AI Health Literature Review System

Automated daily monitoring and summarization of cutting-edge AI research applied to healthcare.

## Features

- **Automated Collection**: Fetches new papers from arXiv, PubMed, and conference sites daily
  - **arXiv**: 7 categories (cs.AI, cs.LG, cs.CL, cs.CY, q-bio, eess.AS, cs.CV) – up to 50/day
  - **PubMed**: Broad AI/health query across pubmed/pmc – up to 30/day
  - **Conferences**: NeurIPS proceedings (2020-2024) with full metadata extraction – up to 20/day
- **Intelligent Filtering**: Uses keyword matching and priority scoring to surface relevant papers
- **Multi-Provider Summarization**: Uses Gemini (2M free tokens) with fallbacks to HuggingFace and OpenRouter
- **Smart Fallback**: Automatically switches providers if one fails
- **Multiple Outputs**: Telegram, Email, Google Docs (cumulative knowledge base), local Markdown
- **Prioritization**: Scores papers by relevance, venue quality, and recency
- **Trend Analysis**: Identifies common keywords and research gaps across daily papers

## Quick Start

### 1. Install

```bash
# Clone / navigate to the project
cd ~/ai-health-lit-review

# Run installer
chmod +x install.sh
./install.sh

# Or manual setup:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
mkdir -p data logs outputs/digests
cp .env.example .env  # then edit .env
```

**Note**: The installer sets up a daily cron job at 09:00. If you need a different time, edit your crontab (`crontab -e`).

### 2. Configure API Keys

Edit `.env` and add your API keys. At minimum:

```bash
# REQUIRED for summarization (2M tokens/month free)
GEMINI_API_KEY=AIzaSy...

# OPTIONAL but recommended for fallback
HUGGINGFACE_API_KEY=hf_...
OPENROUTER_API_KEY=sk-or-...

# OPTIONAL for outputs
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
SMTP_USER=...
SMTP_PASS=...
GOOGLE_CREDENTIALS_JSON={...}
```

**Get free API keys:**

- **Gemini**: Go to https://aistudio.google.com/ → "Get API Key" (2M tokens/month free)
- **HuggingFace**: https://huggingface.co/settings/tokens (30K tokens/month free)
- **OpenRouter**: https://openrouter.ai/ (account needed, various models)

### 3. Test

```bash
source venv/bin/activate

# Test summarizer with sample paper
python run_daily.py --test-summarize

# Test email
python run_daily.py --test-email

# Test Telegram
python run_daily.py --test-telegram

# Check database
python run_daily.py --stats

# Run full daily pipeline
python run_daily.py
```

### 4. Set up Cron (optional)

The installer already added a cron job (runs daily at 08:00). To modify:

```bash
crontab -e
```

Manual cron entry:
```
0 8 * * * cd /home/agent/ai-health-lit-review && source venv/bin/activate && python run_daily.py >> logs/cron_$(date +\%Y\%m\%d).log 2>&1
```

## Configuration

Edit `config.yaml` to customize:

- **Keywords**: Add/remove search terms
- **Sources**: Enable/disable arXiv, PubMed, conference sites
- **Max daily papers**: How many to summarize (default: 10)
- **Outputs**: Enable/disable Telegram, email, Google Docs
- **Priority venues**: Add your lab's target conferences/journals
- **Scoring weights**: Adjust what makes a paper "high priority"

## Outputs

### 1. Daily Markdown Digest
Saved to `outputs/digests/digest_YYYY-MM-DD.md`

### 2. Telegram Message
Formatted with Markdown, sent to configured channel. Includes:
- Top papers (priority 2)
- High priority papers (priority 1)
- Trends summary
- Links to full papers

### 3. Email Digest
Same content as Telegram, delivered to configured email.

### 4. Google Docs Knowledge Base
Appends daily digest to a cumulative document. Creates document if doesn't exist.
Useful for building a searchable knowledge base over time.

### 5. Local Database
SQLite database at `data/papers.db` tracks all collected papers, summaries, and status.
Tables:
- `papers`: All papers with metadata, scores, summaries
- `presentations`: Record of group presentations
- `daily_digests`: Log of sent digests

## Database Schema

### papers table
- `paper_id`: Unique ID (e.g., arxiv:2405.12345, pmid:123456)
- `source`: 'arxiv', 'pubmed', 'conference'
- `title`, `authors`, `abstract`, `url`, `pdf_url`
- `published_date`, `venue`, `doi`
- `keywords`: JSON array
- `score`: Relevance score (0-10)
- `priority`: 0=normal, 1=high, 2=top
- `summary`, `critique`, `methods`, `gaps`: Generated content
- `related_papers`: JSON array of connected paper IDs
- `processing_status`: 'pending', 'summarized', 'presented', 'archived'

## Scoring Algorithm

Papers are scored based on:

1. **Keyword matches** (+1 per keyword, max 5)
2. **Priority venue** (+3 if matches top conference/journal list)
3. **Priority terms** (+2 if contains "clinical trial", "real-world", "FDA", etc.)
4. **Recency** (+1 if published in last 7 days)
5. **Clinical relevance** (+1 if contains clinical terms)

Min score threshold (default 3.0) to be included in daily digest.

## Provider Fallback Chain

Summarization tries providers in order:

1. **Gemini** (primary) - 2M tokens/month free, high quality
2. **HuggingFace** (fallback) - Llama 3.3 70B, 30K tokens/month free
3. **OpenRouter** (tertiary) - Various models, may have costs

If a provider fails (API error, rate limit, etc.), automatically tries next.
Results are cached in database so failed papers can be retried later.

## Extending the System

### Adding New Sources

Create a new method in `collector.py`:
```python
def fetch_custom_source(self):
    # Your logic here
    papers = []
    # Process into standard format:
    # {
    #   'paper_id': 'custom:unique_id',
    #   'source': 'custom',
    #   'title': str,
    #   'authors': list,
    #   'abstract': str,
    #   'url': str,
    #   'published_date': 'YYYY-MM-DD',
    #   'venue': str,
    #   'score': float,
    #   ...
    # }
    return papers
```

Then add to `collect_all()` method.

### Customizing Summarization Prompt

Edit `_build_prompt()` in `summarizer.py` for each provider. The prompt structure is critical for consistent extraction.

### Adding New Outputs

Create a new method in `ReportGenerator`:
```python
def send_slack(self, message): ...
def post_to_notion(self, content): ...
def send_to_discord(self, webhook_url): ...
```

Then add to `generate_daily_digest()` workflow.

## Requirements

- Python 3.10+
- Internet connection (for API calls)
- API keys (at least one summarization provider)
- Optional: Telegram bot, SMTP, Google service account

## Troubleshooting

### "No providers available" error
- Check that `GEMINI_API_KEY` (or other keys) are set in `.env`
- Verify API key is valid (test with `--test-summarize`)
- Check logs in `logs/summarizer.log`

### Telegram not sending
- Verify `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are set
- Bot must be admin in channel/group if posting to channel
- Check `logs/reporter.log`

### Email not sending
- Verify SMTP credentials (SMTP_USER, SMTP_PASS)
- For Gmail, use App Password (2FA enabled)
- Check spam folder
- See `logs/reporter.log`

### PubMed collection empty
- NCBI E-utilities may rate limit; consider adding email parameter
- Try reducing `max_results_per_day` in config
- Check `logs/collector.log`

### Gemini API errors
- Check your quota at AI Studio
- 2M tokens/month free, resets monthly
- If hitting rate limits, reduce `max_daily_papers`

## Project Structure

```
ai-health-lit-review/
├── collector.py          # arXiv, PubMed, conference fetchers
├── summarizer.py         # LLM providers (Gemini, HF, OpenRouter)
├── reporter.py           # Telegram, Email, Google Docs outputs
├── database.py           # SQLite management
├── daily.py              # Workflow orchestrator
├── run_daily.py          # CLI entry point
├── config.yaml           # Configuration
├── .env.example          # Environment template
├── requirements.txt      # Python dependencies
├── install.sh            # Setup script
└── README.md             # This file
```

## License

This project is provided as-is for research purposes.

## Support

Issues and feature requests: [create an issue](#) (or contact your lab's tech lead)

---

**Built with ❤️ for the LiGHT lab and AI in health research**