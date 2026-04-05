"""
Report generation and delivery (Telegram, Email, Google Docs).
"""
import os
import json
import logging
import smtplib
import subprocess
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import List, Dict, Any
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('./logs/reporter.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ReportGenerator:
    """Generate daily digest reports."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.outputs = config.get('outputs', {})
    
    def generate_daily_digest(self, papers: List[Dict[str, Any]], date: str = None) -> str:
        """Generate markdown digest for given papers."""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        md = f"""# AI Health Literature Review - Daily Digest
## {date}

**Total papers reviewed**: {len(papers)}
**Top highlights**: {sum(1 for p in papers if p.get('priority') == 2)} high-priority

---

## 🏆 Top Papers (Priority 2)

"""
        
        # Separate by priority
        top_papers = [p for p in papers if p.get('priority') == 2]
        high_papers = [p for p in papers if p.get('priority') == 1]
        
        for i, paper in enumerate(top_papers, 1):
            md += self._format_paper_markdown(paper, rank=i)
        
        if high_papers:
            md += "\n## 📊 High Priority Papers\n\n"
            for i, paper in enumerate(high_papers, 1):
                md += self._format_paper_markdown(paper, rank=i)
        
        # Trends and gaps summary
        md += self._generate_trends_summary(papers)
        
        # Footer
        md += f"""

---

*Generated automatically by AI Health Lit Review on {datetime.now().strftime('%Y-%m-%d %H:%M')}*
*Database: {self.outputs.get('local', {}).get('database', './data/papers.db')}*
"""
        
        return md
    
    def _format_paper_markdown(self, paper: Dict[str, Any], rank: int = None) -> str:
        """Format a single paper for markdown."""
        title = paper['title']
        if rank:
            title = f"{rank}. {title}"
        
        md = f"""### {title}

**Source**: {paper['source'].upper()} | **Score**: {paper['score']}/10 | **Venue**: {paper.get('venue', 'Unknown')}
**Authors**: {', '.join(paper.get('authors', [])[:3])}{' et al.' if len(paper.get('authors', [])) > 3 else ''}
**Date**: {paper.get('published_date', 'N/A')} | **Link**: {paper.get('url', '#')}
**DOI**: {paper.get('doi', 'N/A') if paper.get('doi') else 'N/A'}

**Summary** ({len(paper.get('summary', '').split())} words):
> {paper.get('summary', 'No summary available.')[:500]}{'...' if len(paper.get('summary', '')) > 500 else ''}

**Methods & Techniques**:
{paper.get('methods', 'Not extracted.')[:200]}{'...' if len(paper.get('methods', '')) > 200 else ''}

**Key Results**:
{paper.get('results', 'Not extracted.')[:200]}{'...' if len(paper.get('results', '')) > 200 else ''}

**Critical Evaluation**:
{paper.get('critique', 'Not extracted.')[:200]}{'...' if len(paper.get('critique', '')) > 200 else ''}

**Research Gaps**:
{paper.get('gaps', 'Not extracted.')[:200]}{'...' if len(paper.get('gaps', '')) > 200 else ''}

**Keywords**: {', '.join(paper.get('keywords', [])[:10])}
**Connections**: {paper.get('connections', 'None identified.')[:150]}{'...' if len(paper.get('connections', '')) > 150 else ''}

---

"""
        return md
    
    def _generate_trends_summary(self, papers: List[Dict[str, Any]]) -> str:
        """Generate aggregate trends and gaps from paper set."""
        all_keywords = []
        all_gaps = []
        
        for p in papers:
            all_keywords.extend(p.get('keywords', []))
            if p.get('gaps'):
                all_gaps.append(p.get('gaps'))
        
        # Count keyword frequency
        keyword_counts = {}
        for kw in all_keywords:
            keyword_counts[kw] = keyword_counts.get(kw, 0) + 1
        
        top_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        md = "## 🔍 Trends & Patterns\n\n"
        md += f"**Most frequent topics**: {', '.join([k for k, _ in top_keywords])}\n\n"
        
        # Simple gap aggregation (could be improved with clustering)
        if all_gaps:
            md += "**Commonly mentioned gaps**:\n"
            # Just list first few unique gaps
            unique_gaps = list(set(all_gaps))[:3]
            for gap in unique_gaps:
                if len(gap) > 100:
                    gap = gap[:100] + "..."
                md += f"- {gap}\n"
        
        return md
    
    def send_telegram(self, message: str, chat_id: str = None) -> bool:
        """Send report to Telegram."""
        telegram_config = self.outputs.get('telegram', {})
        if not telegram_config.get('enabled', False):
            logger.info("Telegram output disabled")
            return False
        
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        target_chat = chat_id or telegram_config.get('channel_id')
        
        if not bot_token or not target_chat:
            logger.error("Telegram bot token or channel ID not configured")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            # Telegram has 4096 char limit, split if needed
            max_len = 4000
            messages = []
            
            if len(message) <= max_len:
                messages.append(message)
            else:
                # Split by sections (at newlines)
                sections = message.split('\n## ')
                current = sections[0]
                for section in sections[1:]:
                    if len(current + '\n## ' + section) <= max_len:
                        current += '\n## ' + section
                    else:
                        messages.append(current)
                        current = '## ' + section
                messages.append(current)
            
            for msg in messages:
                response = requests.post(url, data={
                    'chat_id': target_chat,
                    'text': msg,
                    'parse_mode': 'Markdown',
                    'disable_web_page_preview': True
                }, timeout=10)
                
                if response.status_code != 200:
                    logger.error(f"Telegram send failed: {response.text}")
                    return False
                
                time.sleep(1)  # Rate limiting
            
            logger.info(f"Sent {len(messages)} Telegram messages")
            return True
            
        except Exception as e:
            logger.error(f"Telegram send error: {e}")
            return False
    
    def send_email(self, subject: str, message: str, html_message: str = None) -> bool:
        """Send report via email."""
        email_config = self.outputs.get('email', {})
        if not email_config.get('enabled', False):
            return False
        
        to_email = email_config.get('to')
        if not to_email:
            logger.error("Email recipient not configured")
            return False
        
        # SMTP configuration
        smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', 587))
        smtp_user = os.getenv('SMTP_USER')
        smtp_pass = os.getenv('SMTP_PASS')
        
        if not smtp_user or not smtp_pass:
            logger.error("SMTP credentials not set in environment")
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = smtp_user
            msg['To'] = to_email
            
            # Plain text part
            msg.attach(MIMEText(message, 'plain'))
            
            # HTML part (if provided)
            if html_message:
                msg.attach(MIMEText(html_message, 'html'))
            
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
            
            logger.info(f"Email sent to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Email send failed: {e}")
            return False
    
    def append_to_google_doc(self, content: str, doc_title: str = None) -> bool:
        """Append content to a Google Doc (cumulative knowledge base)."""
        gdocs_config = self.outputs.get('google_docs', {})
        if not gdocs_config.get('enabled', False):
            return False
        
        folder_id = gdocs_config.get('folder_id')
        if not folder_id:
            logger.error("Google Docs folder ID not configured")
            return False
        
        # Requires Google API credentials in environment
        credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
        if not credentials_json:
            logger.error("Google credentials not set")
            return False
        
        try:
            from google.oauth2.service_account import Credentials
            from googleapiclient.discovery import build
            from googleapiclient.errors import HttpError
            
            # Parse credentials
            creds_info = json.loads(credentials_json)
            creds = Credentials.from_service_account_info(
                creds_info,
                scopes=['https://www.googleapis.com/auth/documents', 
                       'https://www.googleapis.com/auth/drive']
            )
            
            drive_service = build('drive', 'v3', credentials=creds)
            docs_service = build('docs', 'v1', credentials=creds)
            
            # Find or create document
            doc_title = doc_title or gdocs_config.get('document_title', 'AI Health Lit Review - Knowledge Base')
            date_str = datetime.now().strftime('%Y-%m-%d')
            
            # Search for existing doc with today's date
            query = f"name contains '{doc_title}' and '{folder_id}' in parents and trashed = false"
            results = drive_service.files().list(q=query, fields="files(id, name)").execute()
            files = results.get('files', [])
            
            if files:
                doc_id = files[0]['id']
                logger.info(f"Found existing doc: {doc_id}")
            else:
                # Create new doc
                file_metadata = {
                    'name': f"{doc_title} - {date_str}",
                    'mimeType': 'application/vnd.google-apps.document',
                    'parents': [folder_id]
                }
                file = drive_service.files().create(body=file_metadata, fields='id').execute()
                doc_id = file.get('id')
                logger.info(f"Created new doc: {doc_id}")
            
            # Append content to doc
            # Get current doc content
            doc = docs_service.documents().get(documentId=doc_id).execute()
            end_index = doc['body']['content'][-1]['endIndex'] - 1
            
            # Insert new content
            requests = [{
                'insertText': {
                    'location': {'index': end_index},
                    'text': f"\n\n# Daily Digest - {date_str}\n\n{content}\n\n---\n"
                }
            }]
            
            docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': requests}
            ).execute()
            
            logger.info(f"Appended to Google Doc {doc_id}")
            return True
            
        except HttpError as e:
            logger.error(f"Google Docs API error: {e}")
            return False
        except Exception as e:
            logger.error(f"Google Docs error: {e}")
            return False
    
    def save_local_markdown(self, content: str, date: str = None) -> str:
        """Save digest to local markdown file, update aggregate file, and optionally sync to GitHub."""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        output_dir = self.outputs.get('local', {}).get('markdown_dir', './outputs/digests')
        os.makedirs(output_dir, exist_ok=True)
        
        filename = f"{output_dir}/digest_{date}.md"
        with open(filename, 'w') as f:
            f.write(content)
        
        self._update_aggregate_markdown(output_dir)
        self._refresh_short_indexes()
        self._sync_digests_to_github(output_dir, date)
        
        logger.info(f"Saved digest to {filename}")
        return filename
    
    def _update_aggregate_markdown(self, output_dir: str) -> str:
        """Rebuild a cumulative markdown file from all digest files."""
        digest_dir = Path(output_dir)
        digest_files = sorted(
            [p for p in digest_dir.glob('digest_*.md') if p.is_file()]
        )
        aggregate_path = digest_dir / 'ALL_DIGESTS.md'
        
        parts = ['# AI Health Literature Review - All Digests\n']
        for path in digest_files:
            parts.append(f"\n\n---\n\n# Source file: {path.name}\n\n")
            parts.append(path.read_text())
        aggregate_path.write_text(''.join(parts))
        logger.info(f"Updated aggregate digest file: {aggregate_path}")
        return str(aggregate_path)
    
    def _refresh_short_indexes(self) -> bool:
        """Refresh short visual index files when the helper script exists."""
        repo_root = Path(__file__).resolve().parent
        script_path = repo_root / 'scripts' / 'update_short_indexes.py'
        if not script_path.exists():
            logger.info('Short index script not found; skipping refresh')
            return False
        try:
            subprocess.run(['python3', str(script_path)], cwd=repo_root, check=True, capture_output=True, text=True)
            logger.info('Refreshed short index files')
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f'Short index refresh failed: {e.stderr or e.stdout or e}')
            return False
    
    def _sync_digests_to_github(self, output_dir: str, date: str) -> bool:
        """Commit and push digest updates to GitHub when a token/repo are configured."""
        github_token = os.getenv('GITHUB_TOKEN')
        github_repo = os.getenv('GITHUB_REPO')
        if not github_token or not github_repo:
            logger.info('GitHub sync not configured; skipping push')
            return False
        
        repo_root = Path(output_dir).resolve().parents[1]
        remote_url = f"https://x-access-token:{github_token}@github.com/{github_repo}.git"
        
        try:
            subprocess.run(['git', 'config', 'user.name', 'Hermes Agent'], cwd=repo_root, check=True, capture_output=True, text=True)
            subprocess.run(['git', 'config', 'user.email', 'hermes-agent@users.noreply.github.com'], cwd=repo_root, check=True, capture_output=True, text=True)
            
            remotes = subprocess.run(['git', 'remote'], cwd=repo_root, check=True, capture_output=True, text=True).stdout.split()
            if 'origin' in remotes:
                subprocess.run(['git', 'remote', 'set-url', 'origin', remote_url], cwd=repo_root, check=True, capture_output=True, text=True)
            else:
                subprocess.run(['git', 'remote', 'add', 'origin', remote_url], cwd=repo_root, check=True, capture_output=True, text=True)
            
            subprocess.run(['git', 'add', '.gitignore', 'outputs/digests'], cwd=repo_root, check=True, capture_output=True, text=True)
            status = subprocess.run(['git', 'status', '--short'], cwd=repo_root, check=True, capture_output=True, text=True).stdout.strip()
            if not status:
                logger.info('No git changes to push')
                return True
            
            # Ensure we are on main for GitHub repos
            branch = subprocess.run(['git', 'branch', '--show-current'], cwd=repo_root, check=True, capture_output=True, text=True).stdout.strip()
            if not branch:
                branch = 'main'
                subprocess.run(['git', 'checkout', '-b', branch], cwd=repo_root, check=True, capture_output=True, text=True)
            elif branch != 'main':
                subprocess.run(['git', 'branch', '-M', 'main'], cwd=repo_root, check=True, capture_output=True, text=True)
            
            subprocess.run(['git', 'commit', '-m', f'Update literature digests for {date}'], cwd=repo_root, check=True, capture_output=True, text=True)
            subprocess.run(['git', 'push', '-u', 'origin', 'main'], cwd=repo_root, check=True, capture_output=True, text=True)
            logger.info('Pushed digest updates to GitHub')
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f'GitHub sync failed: {e.stderr or e.stdout or e}')
            return False

class DailyDigestWorkflow:
    """Orchestrate the daily digest pipeline."""
    
    def __init__(self, config_path: str = 'config.yaml'):
        with open(config_path) as f:
            import yaml
            self.config = yaml.safe_load(f)
        
        from collector import LiteratureCollector
        from summarizer import Summarizer
        from database import PaperDatabase
        
        self.collector = LiteratureCollector(self.config)
        self.summarizer = Summarizer(self.config)
        self.db = PaperDatabase(self.config.get('outputs', {}).get('local', {}).get('database', './data/papers.db'))
        self.reporter = ReportGenerator(self.config)
    
    def run_daily(self):
        """Run the complete daily pipeline."""
        logger.info("=== Starting daily digest workflow ===")
        
        # 1. Collect papers
        logger.info("Step 1: Collecting papers...")
        papers = self.collector.collect_all()
        logger.info(f"Collected {len(papers)} papers")
        
        # 2. Filter to top N by score
        max_papers = self.config.get('summarization', {}).get('max_daily_papers', 10)
        top_papers = sorted(papers, key=lambda x: x['score'], reverse=True)[:max_papers]
        logger.info(f"Selected top {len(top_papers)} papers for summarization")
        
        # 3. Save to DB (pending)
        for paper in top_papers:
            self.db.add_paper(paper)
        
        # 4. Summarize papers
        logger.info("Step 2: Summarizing papers...")
        summarized_papers = self.summarizer.batch_summarize(top_papers)
        logger.info(f"Successfully summarized {len(summarized_papers)} papers")
        
        # 5. Update DB with summaries
        for paper in summarized_papers:
            self.db.update_paper_summary(
                paper_id=paper['paper_id'],
                summary=paper.get('summary', ''),
                critique=paper.get('critique', ''),
                methods=paper.get('methods', ''),
                gaps=paper.get('gaps', '')
            )
        
        # 6. Generate digest
        logger.info("Step 3: Generating digest...")
        digest = self.reporter.generate_daily_digest(summarized_papers)
        
        # 7. Save locally
        date_str = datetime.now().strftime('%Y-%m-%d')
        self.reporter.save_local_markdown(digest, date_str)
        
        # 8. Send outputs
        logger.info("Step 4: Delivering outputs...")
        telegram_ok = self.reporter.send_telegram(digest)
        email_ok = self.reporter.send_email(
            subject=f"AI Health Lit Review - {date_str}",
            message=digest
        )
        gdocs_ok = self.reporter.append_to_google_doc(digest)
        
        # 9. Mark as presented in DB (for weekly selection)
        if len(summarized_papers) >= 10:
            paper_ids = [p['paper_id'] for p in summarized_papers[:10]]
            self.db.mark_papers_presented(paper_ids)
        
        logger.info("=== Daily digest completed ===")
        logger.info(f"Telegram: {'✅' if telegram_ok else '❌'}")
        logger.info(f"Email: {'✅' if email_ok else '❌'}")
        logger.info(f"Google Docs: {'✅' if gdocs_ok else '❌'}")
        
        return {
            'papers_collected': len(papers),
            'papers_summarized': len(summarized_papers),
            'telegram_sent': telegram_ok,
            'email_sent': email_ok,
            'gdocs_updated': gdocs_ok,
            'digest': digest
        }

if __name__ == "__main__":
    workflow = DailyDigestWorkflow()
    result = workflow.run_daily()
    print(json.dumps(result, indent=2))