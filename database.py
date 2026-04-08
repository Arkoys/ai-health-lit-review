"""
Database management for AI Health Literature Review.
"""
import os
import sqlite3
from datetime import datetime
from typing import Optional, Dict, Any, List
import json

class PaperDatabase:
    def __init__(self, db_path: str = "./data/papers.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """Create tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS papers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    paper_id TEXT UNIQUE NOT NULL,
                    source TEXT NOT NULL,
                    title TEXT NOT NULL,
                    authors TEXT,
                    abstract TEXT,
                    url TEXT,
                    pdf_url TEXT,
                    published_date DATE,
                    venue TEXT,
                    doi TEXT,
                    keywords TEXT,
                    score REAL DEFAULT 0.0,
                    priority INTEGER DEFAULT 0,
                    summary TEXT,
                    critique TEXT,
                    methods TEXT,
                    gaps TEXT,
                    related_papers TEXT,
                    processing_status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS presentations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    paper_id TEXT NOT NULL,
                    presentation_date DATE NOT NULL,
                    presenter TEXT,
                    notes TEXT,
                    FOREIGN KEY (paper_id) REFERENCES papers(paper_id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS daily_digests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    digest_date DATE NOT NULL UNIQUE,
                    papers_included TEXT,  -- JSON array of paper_ids
                    total_papers_count INTEGER,
                    highlight_papers TEXT,  -- JSON array of top papers
                    trends_observed TEXT,
                    gaps_identified TEXT,
                    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    sent_to_telegram BOOLEAN DEFAULT 0,
                    sent_to_email BOOLEAN DEFAULT 0,
                    sent_to_gdocs BOOLEAN DEFAULT 0
                )
            """)
            
            conn.execute("CREATE INDEX IF NOT EXISTS idx_papers_score ON papers(score DESC)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_papers_date ON papers(published_date DESC)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_papers_status ON papers(processing_status)")
            conn.commit()
    
    def add_paper(self, paper_data: Dict[str, Any]) -> bool:
        """Add a new paper to the database. Returns True if inserted, False if duplicate."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Check if paper already exists
                cursor = conn.execute(
                    "SELECT id FROM papers WHERE paper_id = ?",
                    (paper_data['paper_id'],)
                )
                if cursor.fetchone():
                    return False  # Duplicate
                
                # Prepare data
                data = {
                    'paper_id': paper_data['paper_id'],
                    'source': paper_data['source'],
                    'title': paper_data['title'],
                    'authors': json.dumps(paper_data.get('authors', [])) if isinstance(paper_data.get('authors'), list) else paper_data.get('authors', ''),
                    'abstract': paper_data.get('abstract', ''),
                    'url': paper_data.get('url', ''),
                    'pdf_url': paper_data.get('pdf_url', ''),
                    'published_date': paper_data.get('published_date'),
                    'venue': paper_data.get('venue', ''),
                    'doi': paper_data.get('doi', ''),
                    'keywords': json.dumps(paper_data.get('keywords', [])) if isinstance(paper_data.get('keywords'), list) else paper_data.get('keywords', ''),
                    'score': paper_data.get('score', 0.0),
                    'priority': paper_data.get('priority', 0),
                    'summary': paper_data.get('summary', ''),
                    'critique': paper_data.get('critique', ''),
                    'methods': paper_data.get('methods', ''),
                    'gaps': paper_data.get('gaps', ''),
                    'related_papers': json.dumps(paper_data.get('related_papers', [])) if isinstance(paper_data.get('related_papers'), list) else paper_data.get('related_papers', ''),
                    'processing_status': paper_data.get('processing_status', 'pending'),
                    'last_updated': datetime.now().isoformat()
                }
                
                placeholders = ', '.join(['?' for _ in data])
                columns = ', '.join(data.keys())
                values = tuple(data.values())
                
                conn.execute(
                    f"INSERT INTO papers ({columns}) VALUES ({placeholders})",
                    values
                )
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error adding paper {paper_data.get('paper_id')}: {e}")
            return False
    
    def get_papers_needing_summarization(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get papers that are pending summarization."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM papers 
                WHERE processing_status = 'pending' 
                OR (processing_status = 'summarized' AND summary = '')
                ORDER BY score DESC, published_date DESC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def update_paper_summary(self, paper_id: str, summary: str, critique: str = '', 
                           methods: str = '', gaps: str = '') -> bool:
        """Update paper with summary and analysis."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE papers 
                    SET summary = ?, critique = ?, methods = ?, gaps = ?,
                        processing_status = 'summarized', last_updated = ?
                    WHERE paper_id = ?
                """, (summary, critique, methods, gaps, datetime.now().isoformat(), paper_id))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error updating paper {paper_id}: {e}")
            return False
    
    def get_top_papers_daily(self, date: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top papers for a given date (or latest)."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            if date:
                # Get papers published on that date
                query = """
                    SELECT * FROM papers 
                    WHERE date(published_date) = ?
                    AND processing_status IN ('summarized', 'presented')
                    ORDER BY score DESC
                    LIMIT ?
                """
                cursor = conn.execute(query, (date, limit))
            else:
                # Get recent papers (last 3 days)
                query = """
                    SELECT * FROM papers 
                    WHERE published_date >= date('now', '-3 days')
                    AND processing_status IN ('summarized', 'presented')
                    ORDER BY score DESC
                    LIMIT ?
                """
                cursor = conn.execute(query, (limit,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def mark_papers_presented(self, paper_ids: List[str]) -> bool:
        """Mark papers as presented in group meeting."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                for pid in paper_ids:
                    conn.execute(
                        "UPDATE papers SET processing_status = 'presented' WHERE paper_id = ?",
                        (pid,)
                    )
                conn.commit()
                return True
        except Exception as e:
            print(f"Error marking papers presented: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total_papers,
                    COUNT(CASE WHEN processing_status = 'pending' THEN 1 END) as pending,
                    COUNT(CASE WHEN processing_status = 'summarized' THEN 1 END) as summarized,
                    COUNT(CASE WHEN processing_status = 'presented' THEN 1 END) as presented,
                    AVG(score) as avg_score,
                    MAX(published_date) as latest_paper_date
                FROM papers
            """)
            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
            return {}
    
    def close(self):
        """Close database connection (not needed with context managers)."""
        pass

if __name__ == "__main__":
    # Quick test
    db = PaperDatabase()
    print("Database initialized. Stats:", db.get_statistics())