import sqlite3
import os
from datetime import datetime
from typing import Optional, List
import json
from collections import Counter

# Rating configuration (imported from config if available, fallback defaults)
try:
    from config import RATING_PRIOR_WEIGHT, RATING_PRIOR_VALUE
except ImportError:
    RATING_PRIOR_WEIGHT = 2
    RATING_PRIOR_VALUE = 5.0

def _ensure_db_path(path: str) -> str:
    normalized = os.path.abspath(os.path.expanduser(path))
    directory = os.path.dirname(normalized)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(normalized, 'a'):
        pass
    return normalized

def _resolve_database_path() -> str:
    # 1. Если путь задан принудительно через переменные окружения
    env_path = os.environ.get("DATABASE_PATH")
    if env_path:
        return _ensure_db_path(env_path)
        
    # 2. RAILWAY: Проверяем наличие папки /data (путь из вашего скриншота)
    # os.name != 'nt' гарантирует, что мы не попытаемся искать диск C:\data на вашем Windows
    if os.name != 'nt' and os.path.isdir("/data"):
        return _ensure_db_path("/data/vibestar.db")
        
    # 3. ЛОКАЛЬНО: Запасной вариант для вашего компьютера
    return _ensure_db_path(os.path.join(os.getcwd(), "vibestar.db"))

DATABASE_PATH = _resolve_database_path()

def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY, username TEXT, name TEXT NOT NULL,
        gender TEXT NOT NULL, age INTEGER NOT NULL, city TEXT NOT NULL,
        bio TEXT, interests TEXT, rating REAL DEFAULT 5.0,
        rating_count INTEGER DEFAULT 0, language TEXT DEFAULT 'ru',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_banned BOOLEAN DEFAULT 0, is_shadow_banned BOOLEAN DEFAULT 0,
        last_seen TIMESTAMP, registration_complete BOOLEAN DEFAULT 0)''')
    try: cursor.execute("ALTER TABLE users ADD COLUMN language TEXT DEFAULT 'ru'")
    except sqlite3.OperationalError: pass
    try: cursor.execute("ALTER TABLE users ADD COLUMN zodiac TEXT DEFAULT NULL")
    except sqlite3.OperationalError: pass
    try: cursor.execute("ALTER TABLE dates ADD COLUMN date_type TEXT DEFAULT 'offline'")
    except sqlite3.OperationalError: pass
    try: cursor.execute("ALTER TABLE ratings ADD COLUMN is_anonymous BOOLEAN DEFAULT 0")
    except sqlite3.OperationalError: pass
    cursor.execute('''CREATE TABLE IF NOT EXISTS photos (
        photo_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
        file_id TEXT NOT NULL, photo_url TEXT,
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS matches (
        match_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user1_id INTEGER NOT NULL, user2_id INTEGER NOT NULL,
        matched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        user1_confirmed BOOLEAN DEFAULT 0, user2_confirmed BOOLEAN DEFAULT 0,
        FOREIGN KEY (user1_id) REFERENCES users(user_id),
        FOREIGN KEY (user2_id) REFERENCES users(user_id),
        UNIQUE(user1_id, user2_id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS likes (
        like_id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_user_id INTEGER NOT NULL, to_user_id INTEGER NOT NULL,
        liked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (from_user_id) REFERENCES users(user_id),
        FOREIGN KEY (to_user_id) REFERENCES users(user_id),
        UNIQUE(from_user_id, to_user_id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
        message_id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER NOT NULL, from_user_id INTEGER NOT NULL,
        to_user_id INTEGER NOT NULL, content TEXT NOT NULL,
        sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, is_read BOOLEAN DEFAULT 0,
        FOREIGN KEY (match_id) REFERENCES matches(match_id),
        FOREIGN KEY (from_user_id) REFERENCES users(user_id),
        FOREIGN KEY (to_user_id) REFERENCES users(user_id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS dates (
        date_id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER NOT NULL, proposer_id INTEGER NOT NULL,
        proposed_date TIMESTAMP, date_type TEXT DEFAULT 'offline',
        status TEXT DEFAULT 'pending', accepted BOOLEAN DEFAULT 0,
        proposer_arrived BOOLEAN DEFAULT 0, other_arrived BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (match_id) REFERENCES matches(match_id),
        FOREIGN KEY (proposer_id) REFERENCES users(user_id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS ratings (
        rating_id INTEGER PRIMARY KEY AUTOINCREMENT,
        date_id INTEGER NOT NULL, from_user_id INTEGER NOT NULL,
        to_user_id INTEGER NOT NULL, stars INTEGER NOT NULL,
        positive_tags TEXT, negative_tags TEXT,
        is_anonymous BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_public BOOLEAN DEFAULT 1, public_at TIMESTAMP,
        FOREIGN KEY (date_id) REFERENCES dates(date_id),
        FOREIGN KEY (from_user_id) REFERENCES users(user_id),
        FOREIGN KEY (to_user_id) REFERENCES users(user_id),
        UNIQUE(date_id, from_user_id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS complaints (
        complaint_id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_user_id INTEGER NOT NULL, to_user_id INTEGER NOT NULL,
        complaint_type TEXT NOT NULL, description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'pending', admin_notes TEXT,
        FOREIGN KEY (from_user_id) REFERENCES users(user_id),
        FOREIGN KEY (to_user_id) REFERENCES users(user_id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS user_states (
        user_id INTEGER PRIMARY KEY, state TEXT, data TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS skips (
        skip_id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_user_id INTEGER NOT NULL, to_user_id INTEGER NOT NULL,
        skipped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (from_user_id) REFERENCES users(user_id),
        FOREIGN KEY (to_user_id) REFERENCES users(user_id),
        UNIQUE(from_user_id, to_user_id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS bot_settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    # Insert default welcome messages if not exist
    for lang in['ru', 'en', 'ka', 'es', 'de']:
        default_msg = {
            'ru': 'Наши правила просты',
            'en': 'Our rules are simple',
            'ka': 'ჩვენი წესები მარტივია',
            'es': 'Nuestras reglas son simples',
            'de': 'Unsere Regeln sind einfach'
        }[lang]
        try:
            cursor.execute('INSERT INTO bot_settings (key, value) VALUES (?, ?)',
                         (f'welcome_msg_{lang}', default_msg))
        except sqlite3.IntegrityError:
            pass
    conn.commit()
    conn.close()

class Database:
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = _ensure_db_path(db_path)
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    def create_user(self, user_id, name, gender, age, city, language='ru'):
        conn = self.get_connection(); cursor = conn.cursor()
        try:
            cursor.execute('SELECT AVG(stars) as avg_rating, COUNT(*) as cnt FROM ratings WHERE to_user_id = ?', (user_id,))
            row = cursor.fetchone()
            rating = row['avg_rating'] if row and row['cnt'] > 0 else RATING_PRIOR_VALUE
            rating_count = row['cnt'] if row and row['cnt'] > 0 else 0
            cursor.execute('INSERT INTO users (user_id, name, gender, age, city, rating, rating_count, language) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                         (user_id, name, gender, age, city, rating, rating_count, language))
            conn.commit(); return True
        except sqlite3.IntegrityError: return False
        finally: conn.close()
    def get_user(self, user_id):
        conn = self.get_connection(); cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        row = cursor.fetchone(); conn.close()
        return dict(row) if row else None
    def update_user(self, user_id, **kwargs):
        conn = self.get_connection(); cursor = conn.cursor()
        try:
            fields = ', '.join([f'{k} = ?' for k in kwargs.keys()])
            values = list(kwargs.values()) +[user_id]
            cursor.execute(f'UPDATE users SET {fields}, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?', values)
            conn.commit(); return True
        finally: conn.close()
    def delete_user(self, user_id):
        conn = self.get_connection(); cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM photos WHERE user_id = ?', (user_id,))
            cursor.execute('DELETE FROM likes WHERE from_user_id = ? OR to_user_id = ?', (user_id, user_id))
            cursor.execute('DELETE FROM skips WHERE from_user_id = ? OR to_user_id = ?', (user_id, user_id))
            cursor.execute('DELETE FROM messages WHERE from_user_id = ? OR to_user_id = ?', (user_id, user_id))
            cursor.execute('DELETE FROM complaints WHERE from_user_id = ? OR to_user_id = ?', (user_id, user_id))
            cursor.execute('DELETE FROM user_states WHERE user_id = ?', (user_id,))
            cursor.execute('DELETE FROM dates WHERE match_id IN (SELECT match_id FROM matches WHERE user1_id = ? OR user2_id = ?)', (user_id, user_id))
            cursor.execute('DELETE FROM matches WHERE user1_id = ? OR user2_id = ?', (user_id, user_id))
            cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
            conn.commit(); return True
        except: conn.rollback(); return False
        finally: conn.close()
    def get_user_by_name(self, name):
        conn = self.get_connection(); cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE name = ?', (name,))
        row = cursor.fetchone(); conn.close()
        return dict(row) if row else None
    def add_photo(self, user_id, file_id, photo_url=None):
        conn = self.get_connection(); cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO photos (user_id, file_id, photo_url) VALUES (?, ?, ?)', (user_id, file_id, photo_url))
            conn.commit(); return True
        finally: conn.close()
    def delete_user_photos(self, user_id):
        conn = self.get_connection(); cursor = conn.cursor()
        try: cursor.execute('DELETE FROM photos WHERE user_id = ?', (user_id,)); conn.commit(); return True
        finally: conn.close()
    def get_user_photos(self, user_id):
        conn = self.get_connection(); cursor = conn.cursor()
        cursor.execute('SELECT * FROM photos WHERE user_id = ? ORDER BY uploaded_at', (user_id,))
        rows = cursor.fetchall(); conn.close()
        return [dict(row) for row in rows]
    def get_photo_count(self, user_id):
        conn = self.get_connection(); cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM photos WHERE user_id = ?', (user_id,))
        result = cursor.fetchone(); conn.close()
        return result['count']
    def add_like(self, from_user_id, to_user_id):
        conn = self.get_connection(); cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO likes (from_user_id, to_user_id) VALUES (?, ?)', (from_user_id, to_user_id))
            conn.commit(); return True
        except sqlite3.IntegrityError: return False
        finally: conn.close()
    def has_liked(self, from_user_id, to_user_id):
        conn = self.get_connection(); cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM likes WHERE from_user_id = ? AND to_user_id = ?', (from_user_id, to_user_id))
        result = cursor.fetchone(); conn.close()
        return result is not None
    def check_mutual_like(self, user1_id, user2_id):
        conn = self.get_connection(); cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM likes WHERE from_user_id = ? AND to_user_id = ? UNION ALL SELECT 1 FROM likes WHERE from_user_id = ? AND to_user_id = ?',
                       (user1_id, user2_id, user2_id, user1_id))
        result = cursor.fetchall(); conn.close()
        return len(result) == 2
    def create_match(self, user1_id, user2_id):
        conn = self.get_connection(); cursor = conn.cursor()
        try:
            if user1_id > user2_id: user1_id, user2_id = user2_id, user1_id
            cursor.execute('INSERT INTO matches (user1_id, user2_id) VALUES (?, ?)', (user1_id, user2_id))
            conn.commit(); return cursor.lastrowid
        except sqlite3.IntegrityError:
            cursor.execute('SELECT match_id FROM matches WHERE user1_id = ? AND user2_id = ?', (user1_id, user2_id))
            result = cursor.fetchone(); conn.close()
            return result['match_id'] if result else None
        finally: conn.close()
    def get_match(self, user1_id, user2_id):
        conn = self.get_connection(); cursor = conn.cursor()
        if user1_id > user2_id: user1_id, user2_id = user2_id, user1_id
        cursor.execute('SELECT * FROM matches WHERE user1_id = ? AND user2_id = ?', (user1_id, user2_id))
        row = cursor.fetchone(); conn.close()
        return dict(row) if row else None
    def get_user_matches(self, user_id):
        conn = self.get_connection(); cursor = conn.cursor()
        cursor.execute('SELECT * FROM matches WHERE user1_id = ? OR user2_id = ? ORDER BY matched_at DESC', (user_id, user_id))
        rows = cursor.fetchall(); conn.close()
        return [dict(row) for row in rows]
    def get_match_partner(self, match_id, user_id):
        conn = self.get_connection(); cursor = conn.cursor()
        cursor.execute('SELECT user1_id, user2_id FROM matches WHERE match_id = ?', (match_id,))
        row = cursor.fetchone(); conn.close()
        if row: return row['user2_id'] if row['user1_id'] == user_id else row['user1_id']
        return None
    def get_match_by_id(self, match_id):
        conn = self.get_connection(); cursor = conn.cursor()
        cursor.execute('SELECT * FROM matches WHERE match_id = ?', (match_id,))
        row = cursor.fetchone(); conn.close()
        return dict(row) if row else None
    def add_skip(self, from_user_id, to_user_id):
        conn = self.get_connection(); cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO skips (from_user_id, to_user_id) VALUES (?, ?)', (from_user_id, to_user_id))
            conn.commit(); return True
        except sqlite3.IntegrityError: return False
        finally: conn.close()
    def has_skipped(self, from_user_id, to_user_id):
        conn = self.get_connection(); cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM skips WHERE from_user_id = ? AND to_user_id = ?', (from_user_id, to_user_id))
        result = cursor.fetchone(); conn.close()
        return result is not None
    def send_message(self, match_id, from_user_id, to_user_id, content):
        conn = self.get_connection(); cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO messages (match_id, from_user_id, to_user_id, content) VALUES (?, ?, ?, ?)',
                         (match_id, from_user_id, to_user_id, content))
            conn.commit(); return True
        finally: conn.close()
    def get_match_messages(self, match_id, limit=50):
        conn = self.get_connection(); cursor = conn.cursor()
        cursor.execute('SELECT * FROM messages WHERE match_id = ? ORDER BY sent_at DESC LIMIT ?', (match_id, limit))
        rows = cursor.fetchall(); conn.close()
        return [dict(row) for row in reversed(rows)]
    def propose_date(self, match_id, proposer_id, date_type='offline'):
        conn = self.get_connection(); cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO dates (match_id, proposer_id, date_type, status) VALUES (?, ?, ?, 'pending')",
                         (match_id, proposer_id, date_type))
            conn.commit(); return cursor.lastrowid
        finally: conn.close()
    def has_pending_date(self, match_id):
        conn = self.get_connection(); cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM dates WHERE match_id = ? AND status IN ('pending', 'accepted')", (match_id,))
        result = cursor.fetchone(); conn.close()
        return result is not None
    def accept_date(self, date_id):
        conn = self.get_connection(); cursor = conn.cursor()
        try:
            cursor.execute("UPDATE dates SET accepted = 1, status = 'accepted' WHERE date_id = ?", (date_id,))
            conn.commit(); return True
        finally: conn.close()
    def confirm_arrival(self, date_id, user_id):
        conn = self.get_connection(); cursor = conn.cursor()
        try:
            date_record = self.get_date(date_id)
            if not date_record: return False
            match = self.get_match_by_id(date_record['match_id'])
            if not match: return False
            if user_id == date_record['proposer_id']:
                cursor.execute('UPDATE dates SET proposer_arrived = 1 WHERE date_id = ?', (date_id,))
            else:
                cursor.execute('UPDATE dates SET other_arrived = 1 WHERE date_id = ?', (date_id,))
            conn.commit()
            cursor.execute('SELECT * FROM dates WHERE date_id = ?', (date_id,))
            updated = dict(cursor.fetchone())
            if updated['proposer_arrived'] and updated['other_arrived']:
                cursor.execute("UPDATE dates SET status = 'completed' WHERE date_id = ?", (date_id,))
                conn.commit()
            return True
        finally: conn.close()
    def get_pending_dates(self, user_id):
        conn = self.get_connection(); cursor = conn.cursor()
        cursor.execute('''SELECT d.*, m.user1_id, m.user2_id FROM dates d
            JOIN matches m ON d.match_id = m.match_id
            WHERE (m.user1_id = ? OR m.user2_id = ?) AND d.status = 'pending'
            ORDER BY d.created_at''', (user_id, user_id))
        rows = cursor.fetchall(); conn.close()
        return [dict(row) for row in rows]
    def get_date(self, date_id):
        conn = self.get_connection(); cursor = conn.cursor()
        cursor.execute('SELECT * FROM dates WHERE date_id = ?', (date_id,))
        row = cursor.fetchone(); conn.close()
        return dict(row) if row else None
    def get_completed_date_for_match(self, match_id):
        conn = self.get_connection(); cursor = conn.cursor()
        cursor.execute('SELECT * FROM dates WHERE match_id = ? AND status = \'completed\' ORDER BY created_at DESC LIMIT 1', (match_id,))
        row = cursor.fetchone(); conn.close()
        return dict(row) if row else None
    def has_completed_date_between(self, user1_id, user2_id):
        conn = self.get_connection(); cursor = conn.cursor()
        if user1_id > user2_id: user1_id, user2_id = user2_id, user1_id
        cursor.execute('''SELECT 1 FROM dates d JOIN matches m ON d.match_id = m.match_id
            WHERE m.user1_id = ? AND m.user2_id = ? AND d.status = 'completed' LIMIT 1''', (user1_id, user2_id))
        result = cursor.fetchone(); conn.close()
        return result is not None
    def get_match_id_between(self, user1_id, user2_id):
        conn = self.get_connection(); cursor = conn.cursor()
        if user1_id > user2_id: user1_id, user2_id = user2_id, user1_id
        cursor.execute('SELECT match_id FROM matches WHERE user1_id = ? AND user2_id = ?', (user1_id, user2_id))
        row = cursor.fetchone(); conn.close()
        return row['match_id'] if row else None
    def add_rating(self, date_id, from_user_id, to_user_id, stars, positive_tags=None, negative_tags=None, is_anonymous=False):
        conn = self.get_connection(); cursor = conn.cursor()
        try:
            positive_str = json.dumps(positive_tags) if positive_tags else None
            negative_str = json.dumps(negative_tags) if negative_tags else None
            cursor.execute('''INSERT INTO ratings (date_id, from_user_id, to_user_id, stars, positive_tags, negative_tags, is_anonymous, is_public, public_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1, CURRENT_TIMESTAMP)''',
                (date_id, from_user_id, to_user_id, stars, positive_str, negative_str, 1 if is_anonymous else 0))
            conn.commit(); self.update_user_rating(to_user_id); return True
        except sqlite3.IntegrityError: return False
        finally: conn.close()
    def get_user_ratings(self, user_id):
        conn = self.get_connection(); cursor = conn.cursor()
        cursor.execute('''SELECT r.*, u.name as reviewer_name FROM ratings r
            LEFT JOIN users u ON r.from_user_id = u.user_id
            WHERE r.to_user_id = ? AND r.is_public = 1
            ORDER BY r.created_at DESC''', (user_id,))
        rows = cursor.fetchall(); conn.close()
        return [dict(row) for row in rows]
    def get_user_reviews_summary(self, user_id):
        ratings = self.get_user_ratings(user_id)
        if not ratings: return {'count': 0, 'avg': 0.0, 'positive_tags': [], 'negative_tags': [], 'ratings':[]}
        total_stars = sum(r['stars'] for r in ratings)
        count = len(ratings)
        avg = total_stars / count if count > 0 else 0.0
        pos_counter = Counter(); neg_counter = Counter()
        for r in ratings:
            if r['positive_tags']:
                try:
                    tags = json.loads(r['positive_tags'])
                    if isinstance(tags, str): tags = json.loads(tags)
                    pos_counter.update(tags)
                except: pass
            if r['negative_tags']:
                try:
                    tags = json.loads(r['negative_tags'])
                    if isinstance(tags, str): tags = json.loads(tags)
                    neg_counter.update(tags)
                except: pass
        return {'count': count, 'avg': avg, 'positive_tags': pos_counter.most_common(5),
                'negative_tags': neg_counter.most_common(5), 'ratings': ratings}
    def update_user_rating(self, user_id):
        conn = self.get_connection(); cursor = conn.cursor()
        try:
            cursor.execute('SELECT stars FROM ratings WHERE to_user_id = ? AND is_public = 1', (user_id,))
            rows = cursor.fetchall(); count = len(rows)
            if count == 0: bayesian_rating = RATING_PRIOR_VALUE
            else:
                total_stars = sum(row['stars'] for row in rows)
                bayesian_rating = (RATING_PRIOR_WEIGHT * RATING_PRIOR_VALUE + total_stars) / (RATING_PRIOR_WEIGHT + count)
            cursor.execute('UPDATE users SET rating = ?, rating_count = ? WHERE user_id = ?', (bayesian_rating, count, user_id))
            conn.commit()
        finally: conn.close()
    def publish_pending_ratings(self):
        conn = self.get_connection(); cursor = conn.cursor()
        try:
            cursor.execute('UPDATE ratings SET is_public = 1, public_at = CURRENT_TIMESTAMP WHERE is_public = 0')
            conn.commit()
            cursor.execute('SELECT DISTINCT to_user_id FROM ratings WHERE is_public = 1')
            users = cursor.fetchall()
            for user in users: self.update_user_rating(user['to_user_id'])
        finally: conn.close()
    def add_complaint(self, from_user_id, to_user_id, complaint_type, description=None):
        conn = self.get_connection(); cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO complaints (from_user_id, to_user_id, complaint_type, description) VALUES (?, ?, ?, ?)',
                         (from_user_id, to_user_id, complaint_type, description))
            conn.commit(); return True
        finally: conn.close()
    def get_pending_complaints(self):
        conn = self.get_connection(); cursor = conn.cursor()
        cursor.execute("SELECT * FROM complaints WHERE status = 'pending' ORDER BY created_at DESC")
        rows = cursor.fetchall(); conn.close()
        return [dict(row) for row in rows]
    def get_complaint(self, complaint_id):
        conn = self.get_connection(); cursor = conn.cursor()
        cursor.execute('SELECT * FROM complaints WHERE complaint_id = ?', (complaint_id,))
        row = cursor.fetchone(); conn.close()
        return dict(row) if row else None
    def resolve_complaint(self, complaint_id, status, admin_notes=None):
        conn = self.get_connection(); cursor = conn.cursor()
        try:
            cursor.execute('UPDATE complaints SET status = ?, admin_notes = ? WHERE complaint_id = ?', (status, admin_notes, complaint_id))
            conn.commit(); return True
        finally: conn.close()
    def set_user_state(self, user_id, state, data=None):
        conn = self.get_connection(); cursor = conn.cursor()
        try:
            data_str = json.dumps(data) if data else None
            cursor.execute('''INSERT INTO user_states (user_id, state, data) VALUES (?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET state = ?, data = ?, updated_at = CURRENT_TIMESTAMP''',
                (user_id, state, data_str, state, data_str))
            conn.commit(); return True
        finally: conn.close()
    def get_user_state(self, user_id):
        conn = self.get_connection(); cursor = conn.cursor()
        cursor.execute('SELECT * FROM user_states WHERE user_id = ?', (user_id,))
        row = cursor.fetchone(); conn.close()
        if row:
            result = dict(row)
            if result['data']: result['data'] = json.loads(result['data'])
            return result
        return None
    def get_stats(self):
        conn = self.get_connection(); cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM users WHERE registration_complete = 1')
        total_users = cursor.fetchone()['count']
        cursor.execute('SELECT COUNT(*) as count FROM matches')
        total_matches = cursor.fetchone()['count']
        cursor.execute('SELECT COUNT(*) as count FROM dates WHERE status = "completed"')
        confirmed_dates = cursor.fetchone()['count']
        cursor.execute('SELECT city, COUNT(*) as count FROM users WHERE registration_complete = 1 GROUP BY city ORDER BY count DESC')
        city_stats = {row['city']: row['count'] for row in cursor.fetchall()}
        conn.close()
        return {'total_users': total_users, 'total_matches': total_matches,
                'confirmed_dates': confirmed_dates, 'city_stats': city_stats}
    def ban_user(self, user_id):
        conn = self.get_connection(); cursor = conn.cursor()
        try:
            cursor.execute('UPDATE users SET is_banned = 1 WHERE user_id = ?', (user_id,))
            conn.commit(); return True
        finally: conn.close()
    def unban_user(self, user_id):
        conn = self.get_connection(); cursor = conn.cursor()
        try:
            cursor.execute('UPDATE users SET is_banned = 0 WHERE user_id = ?', (user_id,))
            conn.commit(); return True
        finally: conn.close()
    def reset_user_rating(self, user_id):
        conn = self.get_connection(); cursor = conn.cursor()
        try:
            cursor.execute('UPDATE users SET rating = ?, rating_count = 0 WHERE user_id = ?', (RATING_PRIOR_VALUE, user_id))
            conn.commit(); return True
        finally: conn.close()
    def full_reset_user_profile(self, user_id):
        conn = self.get_connection(); cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM ratings WHERE from_user_id = ? OR to_user_id = ?', (user_id, user_id))
            cursor.execute('UPDATE users SET rating = ?, rating_count = 0 WHERE user_id = ?', (RATING_PRIOR_VALUE, user_id))
            conn.commit()
            cursor.execute('SELECT DISTINCT to_user_id FROM ratings WHERE to_user_id != ?', (user_id,))
            for row in cursor.fetchall(): self.update_user_rating(row['to_user_id'])
            return True
        except: conn.rollback(); return False
        finally: conn.close()
    def get_incoming_likes(self, user_id):
        conn = self.get_connection(); cursor = conn.cursor()
        cursor.execute('''SELECT l.from_user_id FROM likes l
            LEFT JOIN matches m ON (
                (m.user1_id = CASE WHEN l.from_user_id < l.to_user_id THEN l.from_user_id ELSE l.to_user_id END
                 AND m.user2_id = CASE WHEN l.from_user_id < l.to_user_id THEN l.to_user_id ELSE l.from_user_id END)
            )
            WHERE l.to_user_id = ? AND m.match_id IS NULL
            ORDER BY l.liked_at DESC''', (user_id,))
        rows = cursor.fetchall(); conn.close()
        return[row['from_user_id'] for row in rows]
    def get_all_users(self):
        conn = self.get_connection(); cursor = conn.cursor()
        cursor.execute('SELECT user_id, name, city, rating FROM users WHERE registration_complete = 1')
        rows = cursor.fetchall(); conn.close()
        return [dict(row) for row in rows]
    def confirm_dating_occurred(self, match_id, user_id):
        conn = self.get_connection(); cursor = conn.cursor()
        try:
            cursor.execute('SELECT user1_id, user2_id FROM matches WHERE match_id = ?', (match_id,))
            match = cursor.fetchone()
            if not match: return False
            if user_id == match['user1_id']: cursor.execute('UPDATE matches SET user1_confirmed = 1 WHERE match_id = ?', (match_id,))
            elif user_id == match['user2_id']: cursor.execute('UPDATE matches SET user2_confirmed = 1 WHERE match_id = ?', (match_id,))
            else: return False
            conn.commit(); return True
        finally: conn.close()
    def is_dating_confirmed_by_both(self, match_id):
        conn = self.get_connection(); cursor = conn.cursor()
        cursor.execute('SELECT user1_confirmed, user2_confirmed FROM matches WHERE match_id = ?', (match_id,))
        row = cursor.fetchone(); conn.close()
        if row: return bool(row['user1_confirmed']) and bool(row['user2_confirmed'])
        return False
    def get_match_confirmation_status(self, match_id):
        conn = self.get_connection(); cursor = conn.cursor()
        cursor.execute('SELECT user1_id, user2_id, user1_confirmed, user2_confirmed FROM matches WHERE match_id = ?', (match_id,))
        row = cursor.fetchone(); conn.close()
        if row: return {'user1_id': row['user1_id'], 'user2_id': row['user2_id'],
                        'user1_confirmed': bool(row['user1_confirmed']), 'user2_confirmed': bool(row['user2_confirmed'])}
        return {}
    def get_setting(self, key, default=''):
        conn = self.get_connection(); cursor = conn.cursor()
        try:
            cursor.execute('SELECT value FROM bot_settings WHERE key = ?', (key,))
            row = cursor.fetchone(); conn.close()
            return row['value'] if row else default
        except Exception:
            conn.close()
            return default
    def set_setting(self, key, value):
        conn = self.get_connection(); cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO bot_settings (key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP) ON CONFLICT(key) DO UPDATE SET value = ?, updated_at = CURRENT_TIMESTAMP', (key, value, value))
            conn.commit()
        except Exception:
            # Table might not exist, create it
            cursor.execute('''CREATE TABLE IF NOT EXISTS bot_settings (
                key TEXT PRIMARY KEY, value TEXT NOT NULL, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
            cursor.execute('INSERT INTO bot_settings (key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP) ON CONFLICT(key) DO UPDATE SET value = ?, updated_at = CURRENT_TIMESTAMP', (key, value, value))
            conn.commit()
        conn.close()
