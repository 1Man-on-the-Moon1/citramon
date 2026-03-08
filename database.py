import sqlite3
from datetime import datetime
from typing import Optional, List
import json
from collections import Counter

DATABASE_PATH = "vibestar.db"

# Rating configuration (imported from config if available, fallback defaults)
try:
    from config import RATING_PRIOR_WEIGHT, RATING_PRIOR_VALUE
except ImportError:
    RATING_PRIOR_WEIGHT = 2
    RATING_PRIOR_VALUE = 5.0

def init_db():
    """Initialize the database with all required tables."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            name TEXT NOT NULL,
            gender TEXT NOT NULL,
            age INTEGER NOT NULL,
            city TEXT NOT NULL,
            bio TEXT,
            interests TEXT,
            rating REAL DEFAULT 5.0,
            rating_count INTEGER DEFAULT 0,
            language TEXT DEFAULT 'ru',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_banned BOOLEAN DEFAULT 0,
            is_shadow_banned BOOLEAN DEFAULT 0,
            last_seen TIMESTAMP,
            registration_complete BOOLEAN DEFAULT 0
        )
    ''')
    
    # Add language column if missing (migration for existing DBs)
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN language TEXT DEFAULT 'ru'")
    except sqlite3.OperationalError:
        pass
    
    # Add date_type column to dates if missing
    try:
        cursor.execute("ALTER TABLE dates ADD COLUMN date_type TEXT DEFAULT 'offline'")
    except sqlite3.OperationalError:
        pass

    # Photos table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS photos (
            photo_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            file_id TEXT NOT NULL,
            photo_url TEXT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')
    
    # Matches table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            match_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user1_id INTEGER NOT NULL,
            user2_id INTEGER NOT NULL,
            matched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user1_confirmed BOOLEAN DEFAULT 0,
            user2_confirmed BOOLEAN DEFAULT 0,
            FOREIGN KEY (user1_id) REFERENCES users(user_id),
            FOREIGN KEY (user2_id) REFERENCES users(user_id),
            UNIQUE(user1_id, user2_id)
        )
    ''')
    
    # Likes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS likes (
            like_id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_user_id INTEGER NOT NULL,
            to_user_id INTEGER NOT NULL,
            liked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (from_user_id) REFERENCES users(user_id),
            FOREIGN KEY (to_user_id) REFERENCES users(user_id),
            UNIQUE(from_user_id, to_user_id)
        )
    ''')
    
    # Messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            message_id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id INTEGER NOT NULL,
            from_user_id INTEGER NOT NULL,
            to_user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_read BOOLEAN DEFAULT 0,
            FOREIGN KEY (match_id) REFERENCES matches(match_id),
            FOREIGN KEY (from_user_id) REFERENCES users(user_id),
            FOREIGN KEY (to_user_id) REFERENCES users(user_id)
        )
    ''')
    
    # Dates table (with date_type)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dates (
            date_id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id INTEGER NOT NULL,
            proposer_id INTEGER NOT NULL,
            proposed_date TIMESTAMP,
            date_type TEXT DEFAULT 'offline',
            status TEXT DEFAULT 'pending',
            accepted BOOLEAN DEFAULT 0,
            proposer_arrived BOOLEAN DEFAULT 0,
            other_arrived BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (match_id) REFERENCES matches(match_id),
            FOREIGN KEY (proposer_id) REFERENCES users(user_id)
        )
    ''')
    
    # Ratings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ratings (
            rating_id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_id INTEGER NOT NULL,
            from_user_id INTEGER NOT NULL,
            to_user_id INTEGER NOT NULL,
            stars INTEGER NOT NULL,
            positive_tags TEXT,
            negative_tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_public BOOLEAN DEFAULT 1,
            public_at TIMESTAMP,
            FOREIGN KEY (date_id) REFERENCES dates(date_id),
            FOREIGN KEY (from_user_id) REFERENCES users(user_id),
            FOREIGN KEY (to_user_id) REFERENCES users(user_id),
            UNIQUE(date_id, from_user_id)
        )
    ''')
    
    # Complaints table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS complaints (
            complaint_id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_user_id INTEGER NOT NULL,
            to_user_id INTEGER NOT NULL,
            complaint_type TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pending',
            admin_notes TEXT,
            FOREIGN KEY (from_user_id) REFERENCES users(user_id),
            FOREIGN KEY (to_user_id) REFERENCES users(user_id)
        )
    ''')
    
    # User state tracking for FSM
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_states (
            user_id INTEGER PRIMARY KEY,
            state TEXT,
            data TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')
    
    # Skips table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS skips (
            skip_id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_user_id INTEGER NOT NULL,
            to_user_id INTEGER NOT NULL,
            skipped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (from_user_id) REFERENCES users(user_id),
            FOREIGN KEY (to_user_id) REFERENCES users(user_id),
            UNIQUE(from_user_id, to_user_id)
        )
    ''')
    
    conn.commit()
    conn.close()

class Database:
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    # User operations
    def create_user(self, user_id: int, name: str, gender: str, age: int, city: str, language: str = 'ru') -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO users (user_id, name, gender, age, city, rating, language)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, name, gender, age, city, RATING_PRIOR_VALUE, language))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def get_user(self, user_id: int) -> Optional[dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def update_user(self, user_id: int, **kwargs) -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            fields = ', '.join([f'{k} = ?' for k in kwargs.keys()])
            values = list(kwargs.values()) + [user_id]
            cursor.execute(f'UPDATE users SET {fields}, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?', values)
            conn.commit()
            return True
        finally:
            conn.close()
    
    def delete_user(self, user_id: int) -> bool:
        """Delete user and all related data from all tables."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM photos WHERE user_id = ?', (user_id,))
            cursor.execute('DELETE FROM likes WHERE from_user_id = ? OR to_user_id = ?', (user_id, user_id))
            cursor.execute('DELETE FROM skips WHERE from_user_id = ? OR to_user_id = ?', (user_id, user_id))
            cursor.execute('DELETE FROM messages WHERE from_user_id = ? OR to_user_id = ?', (user_id, user_id))
            cursor.execute('DELETE FROM ratings WHERE from_user_id = ? OR to_user_id = ?', (user_id, user_id))
            cursor.execute('DELETE FROM complaints WHERE from_user_id = ? OR to_user_id = ?', (user_id, user_id))
            cursor.execute('DELETE FROM user_states WHERE user_id = ?', (user_id,))
            cursor.execute('''
                DELETE FROM dates WHERE match_id IN (
                    SELECT match_id FROM matches WHERE user1_id = ? OR user2_id = ?
                )
            ''', (user_id, user_id))
            cursor.execute('DELETE FROM matches WHERE user1_id = ? OR user2_id = ?', (user_id, user_id))
            cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
            conn.commit()
            return True
        except Exception:
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def get_user_by_name(self, name: str) -> Optional[dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE name = ?', (name,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    # Photo operations
    def add_photo(self, user_id: int, file_id: str, photo_url: str = None) -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO photos (user_id, file_id, photo_url)
                VALUES (?, ?, ?)
            ''', (user_id, file_id, photo_url))
            conn.commit()
            return True
        finally:
            conn.close()
    
    def delete_user_photos(self, user_id: int) -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM photos WHERE user_id = ?', (user_id,))
            conn.commit()
            return True
        finally:
            conn.close()
    
    def get_user_photos(self, user_id: int) -> List[dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM photos WHERE user_id = ? ORDER BY uploaded_at', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_photo_count(self, user_id: int) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM photos WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result['count']
    
    # Like operations
    def add_like(self, from_user_id: int, to_user_id: int) -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO likes (from_user_id, to_user_id)
                VALUES (?, ?)
            ''', (from_user_id, to_user_id))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def has_liked(self, from_user_id: int, to_user_id: int) -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 1 FROM likes WHERE from_user_id = ? AND to_user_id = ?
        ''', (from_user_id, to_user_id))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    
    def check_mutual_like(self, user1_id: int, user2_id: int) -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 1 FROM likes WHERE from_user_id = ? AND to_user_id = ?
            UNION ALL
            SELECT 1 FROM likes WHERE from_user_id = ? AND to_user_id = ?
        ''', (user1_id, user2_id, user2_id, user1_id))
        result = cursor.fetchall()
        conn.close()
        return len(result) == 2
    
    # Match operations
    def create_match(self, user1_id: int, user2_id: int) -> Optional[int]:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            if user1_id > user2_id:
                user1_id, user2_id = user2_id, user1_id
            cursor.execute('''
                INSERT INTO matches (user1_id, user2_id)
                VALUES (?, ?)
            ''', (user1_id, user2_id))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            cursor.execute('''
                SELECT match_id FROM matches WHERE user1_id = ? AND user2_id = ?
            ''', (user1_id, user2_id))
            result = cursor.fetchone()
            conn.close()
            return result['match_id'] if result else None
        finally:
            conn.close()
    
    def get_match(self, user1_id: int, user2_id: int) -> Optional[dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        if user1_id > user2_id:
            user1_id, user2_id = user2_id, user1_id
        cursor.execute('''
            SELECT * FROM matches WHERE user1_id = ? AND user2_id = ?
        ''', (user1_id, user2_id))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def get_user_matches(self, user_id: int) -> List[dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM matches WHERE user1_id = ? OR user2_id = ?
            ORDER BY matched_at DESC
        ''', (user_id, user_id))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_match_partner(self, match_id: int, user_id: int) -> Optional[int]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT user1_id, user2_id FROM matches WHERE match_id = ?
        ''', (match_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return row['user2_id'] if row['user1_id'] == user_id else row['user1_id']
        return None
    
    def get_match_by_id(self, match_id: int) -> Optional[dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM matches WHERE match_id = ?', (match_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    # Skip operations
    def add_skip(self, from_user_id: int, to_user_id: int) -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO skips (from_user_id, to_user_id)
                VALUES (?, ?)
            ''', (from_user_id, to_user_id))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def has_skipped(self, from_user_id: int, to_user_id: int) -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 1 FROM skips WHERE from_user_id = ? AND to_user_id = ?
        ''', (from_user_id, to_user_id))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    
    # Message operations
    def send_message(self, match_id: int, from_user_id: int, to_user_id: int, content: str) -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO messages (match_id, from_user_id, to_user_id, content)
                VALUES (?, ?, ?, ?)
            ''', (match_id, from_user_id, to_user_id, content))
            conn.commit()
            return True
        finally:
            conn.close()
    
    def get_match_messages(self, match_id: int, limit: int = 50) -> List[dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM messages WHERE match_id = ?
            ORDER BY sent_at DESC LIMIT ?
        ''', (match_id, limit))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in reversed(rows)]
    
    # Date operations (with date_type)
    def propose_date(self, match_id: int, proposer_id: int, date_type: str = 'offline') -> Optional[int]:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO dates (match_id, proposer_id, date_type, status)
                VALUES (?, ?, ?, 'pending')
            ''', (match_id, proposer_id, date_type))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    def has_pending_date(self, match_id: int) -> bool:
        """Check if there's already a pending or accepted date for this match."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 1 FROM dates WHERE match_id = ? AND status IN ('pending', 'accepted')
        ''', (match_id,))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    
    def accept_date(self, date_id: int) -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE dates SET accepted = 1, status = 'accepted' WHERE date_id = ?
            ''', (date_id,))
            conn.commit()
            return True
        finally:
            conn.close()
    
    def confirm_arrival(self, date_id: int, user_id: int) -> bool:
        """Mark that a user arrived at the date."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            date_record = self.get_date(date_id)
            if not date_record:
                return False
            
            match = self.get_match_by_id(date_record['match_id'])
            if not match:
                return False
            
            if user_id == date_record['proposer_id']:
                cursor.execute('UPDATE dates SET proposer_arrived = 1 WHERE date_id = ?', (date_id,))
            else:
                cursor.execute('UPDATE dates SET other_arrived = 1 WHERE date_id = ?', (date_id,))
            
            conn.commit()
            
            # Check if both arrived
            cursor.execute('SELECT * FROM dates WHERE date_id = ?', (date_id,))
            updated = dict(cursor.fetchone())
            if updated['proposer_arrived'] and updated['other_arrived']:
                cursor.execute("UPDATE dates SET status = 'completed' WHERE date_id = ?", (date_id,))
                conn.commit()
            
            return True
        finally:
            conn.close()
    
    def get_pending_dates(self, user_id: int) -> List[dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT d.*, m.user1_id, m.user2_id FROM dates d
            JOIN matches m ON d.match_id = m.match_id
            WHERE (m.user1_id = ? OR m.user2_id = ?) AND d.status = 'pending'
            ORDER BY d.created_at
        ''', (user_id, user_id))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_date(self, date_id: int) -> Optional[dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM dates WHERE date_id = ?', (date_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def get_completed_date_for_match(self, match_id: int) -> Optional[dict]:
        """Get the most recent completed date for a match."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM dates WHERE match_id = ? AND status = 'completed'
            ORDER BY created_at DESC LIMIT 1
        ''', (match_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def has_completed_date_between(self, user1_id: int, user2_id: int) -> bool:
        """Check if there was a completed date between two users."""
        conn = self.get_connection()
        cursor = conn.cursor()
        if user1_id > user2_id:
            user1_id, user2_id = user2_id, user1_id
        cursor.execute('''
            SELECT 1 FROM dates d
            JOIN matches m ON d.match_id = m.match_id
            WHERE m.user1_id = ? AND m.user2_id = ? AND d.status = 'completed'
            LIMIT 1
        ''', (user1_id, user2_id))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    
    def get_match_id_between(self, user1_id: int, user2_id: int) -> Optional[int]:
        """Get match_id between two users."""
        conn = self.get_connection()
        cursor = conn.cursor()
        if user1_id > user2_id:
            user1_id, user2_id = user2_id, user1_id
        cursor.execute('SELECT match_id FROM matches WHERE user1_id = ? AND user2_id = ?', (user1_id, user2_id))
        row = cursor.fetchone()
        conn.close()
        return row['match_id'] if row else None

    # Rating operations
    def add_rating(self, date_id: int, from_user_id: int, to_user_id: int, 
                   stars: int, positive_tags: List[str] = None, negative_tags: List[str] = None) -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            positive_str = json.dumps(positive_tags) if positive_tags else None
            negative_str = json.dumps(negative_tags) if negative_tags else None
            cursor.execute('''
                INSERT INTO ratings (date_id, from_user_id, to_user_id, stars, positive_tags, negative_tags, is_public, public_at)
                VALUES (?, ?, ?, ?, ?, ?, 1, CURRENT_TIMESTAMP)
            ''', (date_id, from_user_id, to_user_id, stars, positive_str, negative_str))
            conn.commit()
            # Immediately update the user's rating
            self.update_user_rating(to_user_id)
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def get_user_ratings(self, user_id: int) -> List[dict]:
        """Get all public ratings for a user."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT r.*, u.name as reviewer_name FROM ratings r
            LEFT JOIN users u ON r.from_user_id = u.user_id
            WHERE r.to_user_id = ? AND r.is_public = 1
            ORDER BY r.created_at DESC
        ''', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_user_reviews_summary(self, user_id: int) -> dict:
        """Get a summary of all reviews for a user."""
        ratings = self.get_user_ratings(user_id)
        if not ratings:
            return {'count': 0, 'avg': 0.0, 'positive_tags': [], 'negative_tags': [], 'ratings': []}
        
        total_stars = sum(r['stars'] for r in ratings)
        count = len(ratings)
        avg = total_stars / count if count > 0 else 0.0
        
        # Aggregate tags
        pos_counter = Counter()
        neg_counter = Counter()
        for r in ratings:
            if r['positive_tags']:
                try:
                    tags = json.loads(r['positive_tags'])
                    if isinstance(tags, str):
                        tags = json.loads(tags)
                    pos_counter.update(tags)
                except (json.JSONDecodeError, TypeError):
                    pass
            if r['negative_tags']:
                try:
                    tags = json.loads(r['negative_tags'])
                    if isinstance(tags, str):
                        tags = json.loads(tags)
                    neg_counter.update(tags)
                except (json.JSONDecodeError, TypeError):
                    pass
        
        return {
            'count': count,
            'avg': avg,
            'positive_tags': pos_counter.most_common(5),
            'negative_tags': neg_counter.most_common(5),
            'ratings': ratings
        }
    
    def update_user_rating(self, user_id: int):
        """Update user rating using Bayesian average."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT stars FROM ratings WHERE to_user_id = ? AND is_public = 1
            ''', (user_id,))
            rows = cursor.fetchall()
            count = len(rows)
            
            if count == 0:
                # No ratings yet, keep prior
                bayesian_rating = RATING_PRIOR_VALUE
            else:
                total_stars = sum(row['stars'] for row in rows)
                # Bayesian average: (prior_weight * prior_value + sum_stars) / (prior_weight + count)
                bayesian_rating = (RATING_PRIOR_WEIGHT * RATING_PRIOR_VALUE + total_stars) / (RATING_PRIOR_WEIGHT + count)
            
            cursor.execute('''
                UPDATE users SET rating = ?, rating_count = ? WHERE user_id = ?
            ''', (bayesian_rating, count, user_id))
            conn.commit()
        finally:
            conn.close()
    
    def publish_pending_ratings(self):
        """Publish any remaining unpublished ratings (legacy support)."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE ratings SET is_public = 1, public_at = CURRENT_TIMESTAMP
                WHERE is_public = 0
            ''')
            conn.commit()
            # Update ratings for affected users
            cursor.execute('''
                SELECT DISTINCT to_user_id FROM ratings WHERE is_public = 1
            ''')
            users = cursor.fetchall()
            for user in users:
                self.update_user_rating(user['to_user_id'])
        finally:
            conn.close()
    
    # Complaint operations
    def add_complaint(self, from_user_id: int, to_user_id: int, complaint_type: str, description: str = None) -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO complaints (from_user_id, to_user_id, complaint_type, description)
                VALUES (?, ?, ?, ?)
            ''', (from_user_id, to_user_id, complaint_type, description))
            conn.commit()
            return True
        finally:
            conn.close()
    
    def get_pending_complaints(self) -> List[dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM complaints WHERE status = 'pending'
            ORDER BY created_at DESC
        ''')
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_complaint(self, complaint_id: int) -> Optional[dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM complaints WHERE complaint_id = ?', (complaint_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def resolve_complaint(self, complaint_id: int, status: str, admin_notes: str = None) -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE complaints SET status = ?, admin_notes = ? WHERE complaint_id = ?
            ''', (status, admin_notes, complaint_id))
            conn.commit()
            return True
        finally:
            conn.close()
    
    # User state operations
    def set_user_state(self, user_id: int, state: str, data: dict = None) -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            data_str = json.dumps(data) if data else None
            cursor.execute('''
                INSERT INTO user_states (user_id, state, data)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET state = ?, data = ?, updated_at = CURRENT_TIMESTAMP
            ''', (user_id, state, data_str, state, data_str))
            conn.commit()
            return True
        finally:
            conn.close()
    
    def get_user_state(self, user_id: int) -> Optional[dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user_states WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            result = dict(row)
            if result['data']:
                result['data'] = json.loads(result['data'])
            return result
        return None
    
    # Statistics
    def get_stats(self) -> dict:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) as count FROM users WHERE registration_complete = 1')
        total_users = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM matches')
        total_matches = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM dates WHERE status = "completed"')
        confirmed_dates = cursor.fetchone()['count']
        
        cursor.execute('''
            SELECT city, COUNT(*) as count FROM users WHERE registration_complete = 1
            GROUP BY city ORDER BY count DESC
        ''')
        city_stats = {row['city']: row['count'] for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            'total_users': total_users,
            'total_matches': total_matches,
            'confirmed_dates': confirmed_dates,
            'city_stats': city_stats
        }
    
    def ban_user(self, user_id: int, shadow_ban: bool = False) -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            if shadow_ban:
                cursor.execute('''
                    UPDATE users SET is_shadow_banned = 1 WHERE user_id = ?
                ''', (user_id,))
            else:
                cursor.execute('''
                    UPDATE users SET is_banned = 1 WHERE user_id = ?
                ''', (user_id,))
            conn.commit()
            return True
        finally:
            conn.close()
    
    def unban_user(self, user_id: int) -> bool:
        """Unban user (remove both regular and shadow ban)."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE users SET is_banned = 0, is_shadow_banned = 0 WHERE user_id = ?
            ''', (user_id,))
            conn.commit()
            return True
        finally:
            conn.close()
    
    def reset_user_rating(self, user_id: int) -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE users SET rating = ?, rating_count = 0 WHERE user_id = ?
            ''', (RATING_PRIOR_VALUE, user_id))
            conn.commit()
            return True
        finally:
            conn.close()
    
    def full_reset_user_profile(self, user_id: int) -> bool:
        """Full profile reset: delete all ratings/reviews and reset rating to default."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # Delete all ratings FROM this user and TO this user
            cursor.execute('DELETE FROM ratings WHERE from_user_id = ? OR to_user_id = ?', (user_id, user_id))
            # Reset rating to default
            cursor.execute('''
                UPDATE users SET rating = ?, rating_count = 0 WHERE user_id = ?
            ''', (RATING_PRIOR_VALUE, user_id))
            conn.commit()
            # Recalculate ratings for all users who were rated by this user
            cursor.execute('SELECT DISTINCT to_user_id FROM ratings WHERE to_user_id != ?', (user_id,))
            affected = cursor.fetchall()
            for row in affected:
                self.update_user_rating(row['to_user_id'])
            return True
        except Exception:
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def get_all_users(self) -> List[dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT user_id, name, city, rating FROM users WHERE registration_complete = 1')
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    # Dating confirmation operations
    def confirm_dating_occurred(self, match_id: int, user_id: int) -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT user1_id, user2_id FROM matches WHERE match_id = ?', (match_id,))
            match = cursor.fetchone()
            if not match:
                return False
            if user_id == match['user1_id']:
                cursor.execute('UPDATE matches SET user1_confirmed = 1 WHERE match_id = ?', (match_id,))
            elif user_id == match['user2_id']:
                cursor.execute('UPDATE matches SET user2_confirmed = 1 WHERE match_id = ?', (match_id,))
            else:
                return False
            conn.commit()
            return True
        finally:
            conn.close()
    
    def is_dating_confirmed_by_both(self, match_id: int) -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT user1_confirmed, user2_confirmed FROM matches WHERE match_id = ?
        ''', (match_id,))
        match = cursor.fetchone()
        conn.close()
        if not match:
            return False
        return match['user1_confirmed'] and match['user2_confirmed']
    
    def get_match_confirmation_status(self, match_id: int) -> dict:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT user1_id, user2_id, user1_confirmed, user2_confirmed FROM matches WHERE match_id = ?
        ''', (match_id,))
        match = cursor.fetchone()
        conn.close()
        if not match:
            return {}
        return {
            'user1_id': match['user1_id'],
            'user2_id': match['user2_id'],
            'user1_confirmed': match['user1_confirmed'],
            'user2_confirmed': match['user2_confirmed'],
            'both_confirmed': match['user1_confirmed'] and match['user2_confirmed']
        }
