import sqlite3
from typing import List, Set
from datetime import datetime
from config import DB_PATH
from scrapers.base_scraper import JobItem

class JobDatabase:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS seen_jobs (
                    id TEXT PRIMARY KEY,
                    platform TEXT NOT NULL,
                    title TEXT NOT NULL,
                    company TEXT NOT NULL,
                    url TEXT NOT NULL,
                    score INTEGER DEFAULT 0,
                    first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    emailed_at TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_seen_url ON seen_jobs(url);
            """)
            conn.commit()

    def filter_new_jobs(self, jobs: List[JobItem]) -> List[JobItem]:
        """Returns only jobs that have not been emailed or seen before."""
        if not jobs:
            return []

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM seen_jobs")
            seen_ids: Set[str] = {row["id"] for row in cursor.fetchall()}

        new_jobs = [j for j in jobs if j.id not in seen_ids]
        return new_jobs

    def record_and_mark_emailed(self, jobs: List[JobItem]):
        """Records jobs into DB and marks them as sent."""
        if not jobs:
            return

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            for j in jobs:
                cursor.execute("""
                    INSERT OR REPLACE INTO seen_jobs (
                        id, platform, title, company, url, score, first_seen_at, emailed_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    j.id,
                    j.platform,
                    j.title,
                    j.company,
                    j.url,
                    j.score,
                    now,
                    now,
                ))
            conn.commit()

    def get_stats(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as total FROM seen_jobs")
            total = cursor.fetchone()["total"]
            cursor.execute("""
                SELECT platform, COUNT(*) as count 
                FROM seen_jobs 
                GROUP BY platform
            """)
            by_platform = {row["platform"]: row["count"] for row in cursor.fetchall()}
            return {"total": total, "by_platform": by_platform}
