#!/usr/bin/env python3
"""
Main entry point for daily literature digest.
This script can be run manually or via cron.
"""
import os
import sys
import argparse
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def load_dotenv(env_path='.env'):
    """Load environment variables from .env file."""
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip().strip('"\'')

def main():
    parser = argparse.ArgumentParser(description='AI Health Literature Daily Digest')
    parser.add_argument('--config', default='config.yaml', help='Path to config file')
    parser.add_argument('--date', help='Specific date (YYYY-MM-DD), defaults to today')
    parser.add_argument('--test-email', action='store_true', help='Test email delivery only')
    parser.add_argument('--test-telegram', action='store_true', help='Test Telegram delivery only')
    parser.add_argument('--test-summarize', action='store_true', help='Test summarizer with sample paper')
    parser.add_argument('--list-db', action='store_true', help='List papers in database')
    parser.add_argument('--stats', action='store_true', help='Show database statistics')
    
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Check required environment variables
    if not os.getenv('GEMINI_API_KEY'):
        print("⚠️  Warning: GEMINI_API_KEY not set. Summarization will fail.")
        print("   Set it in .env file or export GEMINI_API_KEY=...")
    
    if args.test_summarize:
        # Quick summarizer test
        from summarizer import Summarizer
        import yaml
        
        with open(args.config) as f:
            config = yaml.safe_load(f)
        
        try:
            summarizer = Summarizer(config)
            test_paper = {
                'paper_id': 'test',
                'title': 'Large Language Models Enable得过 predicting clinical outcomes from EHR data',
                'authors': ['A. Researcher', 'B. Scientist'],
                'abstract': 'We demonstrate that LLMs can achieve SOTA performance on clinical prediction tasks...',
                'venue': 'Nature Medicine',
                'published_date': '2025-04-01'
            }
            result = summarizer.summarize_paper(test_paper)
            if result:
                print("✅ Summarizer test successful!")
                print(f"Summary: {result.get('summary', [])[:200]}...")
            else:
                print("❌ Summarizer test failed")
        except Exception as e:
            print(f"❌ Summarizer test error: {e}")
        return
    
    if args.test_email:
        # Test email only
        from reporter import ReportGenerator
        import yaml
        
        with open(args.config) as f:
            config = yaml.safe_load(f)
        
        reporter = ReportGenerator(config)
        test_msg = "This is a test email from AI Health Lit Review system."
        success = reporter.send_email(
            subject="[TEST] AI Health Lit Review",
            message=test_msg
        )
        print(f"Email test: {'✅' if success else '❌'}")
        return
    
    if args.test_telegram:
        # Test Telegram only
        from reporter import ReportGenerator
        import yaml
        
        with open(args.config) as f:
            config = yaml.safe_load(f)
        
        reporter = ReportGenerator(config)
        test_msg = "This is a test message from AI Health Lit Review system."
        success = reporter.send_telegram(test_msg)
        print(f"Telegram test: {'✅' if success else '❌'}")
        return
    
    if args.list_db:
        # List papers in database
        from database import PaperDatabase
        db = PaperDatabase()
        import sqlite3
        conn = sqlite3.connect(db.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("""
            SELECT paper_id, title, score, processing_status, published_date 
            FROM papers 
            ORDER BY published_date DESC 
            LIMIT 20
        """)
        rows = cursor.fetchall()
        print(f"Latest 20 papers in database ({db.get_statistics().get('total_papers', 0)} total):")
        for row in rows:
            print(f"- [{row['processing_status']}] {row['paper_id']}: {row['title'][:60]}... (score: {row['score']})")
        return
    
    if args.stats:
        # Show database stats
        from database import PaperDatabase
        db = PaperDatabase()
        stats = db.get_statistics()
        print("Database Statistics:")
        for k, v in stats.items():
            print(f"  {k}: {v}")
        return
    
    # Run full daily workflow
    try:
        from daily import DailyDigestWorkflow
        
        workflow = DailyDigestWorkflow(args.config)
        result = workflow.run_daily()
        
        print("\n" + "="*50)
        print("DAILY DIGEST COMPLETED")
        print("="*50)
        print(f"Papers collected: {result['papers_collected']}")
        print(f"Papers summarized: {result['papers_summarized']}")
        print(f"Telegram: {'✅' if result['telegram_sent'] else '❌'}")
        print(f"Email: {'✅' if result['email_sent'] else '❌'}")
        print(f"Google Docs: {'✅' if result['gdocs_updated'] else '❌'}")
        print(f"\nDigest preview (first 500 chars):")
        print(result['digest'][:500] + "...")
        
    except ImportError as e:
        print(f"❌ Error: Required module not found: {e}")
        print("   Make sure you've installed requirements: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error running daily workflow: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()