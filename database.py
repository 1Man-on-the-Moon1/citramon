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
    env_path = os.environ.get("DATABASE_PATH", "")
    candidates = [
        env_path,
        "/data/vibestar.db",
        "/app/data/vibestar.db",
        os.path.join(os.getcwd(), "vibestar.db"),
        "/tmp/vibestar.db",
    ]
    candidates = [c for c in candidates if c]
    for candidate in candidates:
        try:
            return _ensure_db_path(candidate)
        except OSError:
            continue
    raise RuntimeError("Unable to initialize writable SQLite database path")

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
    for lang in ['ru', 'en', 'ka', 'es', 'de']:
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
