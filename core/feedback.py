import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
import config


class FeedbackManager:
    """
    Manages user feedback data for search results.
    Stores likes, favorites, and irrelevant markings.
    """

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or config.FEEDBACK_DB_PATH
        self._init_database()

    def _init_database(self):
        """Initialize database schema if not exists."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Feedback records table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                image_id INTEGER NOT NULL,
                feedback_type TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                session_id TEXT
            )
        ''')

        # Query statistics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS query_stats (
                query TEXT PRIMARY KEY,
                search_count INTEGER DEFAULT 1,
                avg_top_score REAL,
                last_search DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create indexes for faster queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_feedback_image_id
            ON feedback(image_id)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_feedback_query
            ON feedback(query)
        ''')

        conn.commit()
        conn.close()
        print(f"Feedback database initialized at {self.db_path}")

    def record_feedback(
        self,
        query: str,
        image_id: int,
        feedback_type: str,
        session_id: Optional[str] = None
    ) -> bool:
        """
        Record user feedback.

        Args:
            query: Search query that led to this result
            image_id: ID of the image
            feedback_type: One of 'like', 'favorite', 'irrelevant'
            session_id: Optional session identifier

        Returns:
            True if successful
        """
        if feedback_type not in ['like', 'favorite', 'irrelevant']:
            raise ValueError(f"Invalid feedback type: {feedback_type}")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO feedback (query, image_id, feedback_type, session_id)
            VALUES (?, ?, ?, ?)
        ''', (query, image_id, feedback_type, session_id))

        conn.commit()
        conn.close()

        return True

    def update_query_stats(self, query: str, top_score: float):
        """
        Update query statistics.

        Args:
            query: Search query
            top_score: Similarity score of top result
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check if query exists
        cursor.execute('SELECT search_count, avg_top_score FROM query_stats WHERE query = ?', (query,))
        result = cursor.fetchone()

        if result:
            count, avg_score = result
            new_count = count + 1
            new_avg = (avg_score * count + top_score) / new_count

            cursor.execute('''
                UPDATE query_stats
                SET search_count = ?, avg_top_score = ?, last_search = ?
                WHERE query = ?
            ''', (new_count, new_avg, datetime.now(), query))
        else:
            cursor.execute('''
                INSERT INTO query_stats (query, search_count, avg_top_score, last_search)
                VALUES (?, 1, ?, ?)
            ''', (query, top_score, datetime.now()))

        conn.commit()
        conn.close()

    def get_feedback_stats(self, image_id: int) -> Dict:
        """
        Get feedback statistics for an image.

        Args:
            image_id: Image ID

        Returns:
            Dict with counts for each feedback type
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT feedback_type, COUNT(*)
            FROM feedback
            WHERE image_id = ?
            GROUP BY feedback_type
        ''', (image_id,))

        results = cursor.fetchall()
        conn.close()

        stats = {'like': 0, 'favorite': 0, 'irrelevant': 0}
        for feedback_type, count in results:
            stats[feedback_type] = count

        return stats

    def get_popular_queries(self, limit: int = 10) -> List[Dict]:
        """
        Get most popular queries.

        Args:
            limit: Number of queries to return

        Returns:
            List of dicts with query stats
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT query, search_count, avg_top_score, last_search
            FROM query_stats
            ORDER BY search_count DESC
            LIMIT ?
        ''', (limit,))

        results = cursor.fetchall()
        conn.close()

        return [
            {
                'query': row[0],
                'search_count': row[1],
                'avg_top_score': row[2],
                'last_search': row[3]
            }
            for row in results
        ]

    def get_top_rated_images(self, limit: int = 20) -> List[Dict]:
        """
        Get images with most positive feedback.

        Args:
            limit: Number of images to return

        Returns:
            List of dicts with image stats
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                image_id,
                SUM(CASE WHEN feedback_type = 'like' THEN 1 ELSE 0 END) as likes,
                SUM(CASE WHEN feedback_type = 'favorite' THEN 1 ELSE 0 END) as favorites,
                SUM(CASE WHEN feedback_type = 'irrelevant' THEN 1 ELSE 0 END) as irrelevant,
                COUNT(*) as total_feedback
            FROM feedback
            GROUP BY image_id
            HAVING likes + favorites > irrelevant
            ORDER BY (likes + favorites * 2) DESC
            LIMIT ?
        ''', (limit,))

        results = cursor.fetchall()
        conn.close()

        return [
            {
                'image_id': row[0],
                'likes': row[1],
                'favorites': row[2],
                'irrelevant': row[3],
                'total_feedback': row[4]
            }
            for row in results
        ]

    def get_feedback_for_query(self, query: str) -> List[Dict]:
        """
        Get all feedback for a specific query.

        Args:
            query: Search query

        Returns:
            List of feedback records
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT image_id, feedback_type, timestamp, session_id
            FROM feedback
            WHERE query = ?
            ORDER BY timestamp DESC
        ''', (query,))

        results = cursor.fetchall()
        conn.close()

        return [
            {
                'image_id': row[0],
                'feedback_type': row[1],
                'timestamp': row[2],
                'session_id': row[3]
            }
            for row in results
        ]
