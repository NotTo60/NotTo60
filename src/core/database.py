import sqlite3
import gzip
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import base64
import secrets
from core.config import DB_PATH, DB_COMPRESSED_PATH, DB_DIR
import logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

CURRENT_SCHEMA_VERSION = 1

class TriviaDatabase:
    def __init__(self, db_path=DB_PATH):
        try:
            self.db_path = db_path
            # Ensure the directory exists
            Path(DB_DIR).mkdir(parents=True, exist_ok=True)
            self.init_database()
        except Exception as e:
            logging.error("[database.py] [__init__] Error initializing database: %s", e)
            raise

    def _get_password(self):
        password = os.getenv("TRIVIA_DB_PASSWORD")
        if not password:
            logging.error("[database.py] [_get_password] TRIVIA_DB_PASSWORD environment variable is required for database encryption.")
            raise RuntimeError("TRIVIA_DB_PASSWORD environment variable is required for database encryption.")
        return password.encode()

    def _get_fernet(self, salt=None):
        password = self._get_password()
        if salt is None:
            import base64
            env_salt = os.getenv("TRIVIA_DB_SALT")
            if not env_salt:
                logging.error("[database.py] [_get_fernet] TRIVIA_DB_SALT environment variable is required for database encryption.")
                raise RuntimeError("TRIVIA_DB_SALT environment variable is required for database encryption. Please set it as a base64-encoded 16-byte value.")
            salt = base64.b64decode(env_salt)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=390000,
            backend=default_backend(),
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return Fernet(key)

    def ensure_meta_table(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS meta (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    schema_version INTEGER NOT NULL
                )
            ''')
            conn.commit()

    def get_schema_version(self):
        try:
            self.ensure_meta_table()
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='meta'")
                if cursor.fetchone() is None:
                    return 0
                cursor.execute("SELECT schema_version FROM meta LIMIT 1")
                row = cursor.fetchone()
                if row:
                    return int(row[0])
                return 0
        except Exception:
            return 0

    def set_schema_version(self, version):
        self.ensure_meta_table()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO meta (id, schema_version) VALUES (1, ?)", (version,))
            conn.commit()

    def migrate_schema(self, old_version):
        self.ensure_meta_table()
        # Example: future migrations
        if old_version == CURRENT_SCHEMA_VERSION:
            return  # No migration needed, don't log
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Add migration steps here for future versions
            # if old_version < 2:
            #     cursor.execute("ALTER TABLE ...")
            #     ...
            conn.commit()
        logging.info(f"[database.py] [migrate_schema] Migrated schema from version {old_version} to {CURRENT_SCHEMA_VERSION}")

    def init_database(self):
        """Initialize the database with required tables and handle schema versioning"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Meta table for schema version
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS meta (
                        id INTEGER PRIMARY KEY CHECK (id = 1),
                        schema_version INTEGER NOT NULL
                    )
                ''')
                # Create leaderboard table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS leaderboard (
                        username TEXT PRIMARY KEY,
                        current_streak INTEGER DEFAULT 0,
                        total_correct INTEGER DEFAULT 0,
                        total_points INTEGER DEFAULT 0,
                        total_answered INTEGER DEFAULT 0,
                        last_answered TEXT,
                        last_trivia_date TEXT,
                        answer_history TEXT
                    )
                ''')
                # Create daily_facts table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS daily_facts (
                        timestamp TEXT PRIMARY KEY,
                        fact TEXT NOT NULL
                    )
                ''')
                # Create trivia_questions table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS trivia_questions (
                        timestamp TEXT PRIMARY KEY,
                        question TEXT NOT NULL,
                        options TEXT NOT NULL,
                        correct_answer TEXT NOT NULL,
                        explanation TEXT
                    )
                ''')
                conn.commit()
                # Check schema version and migrate if needed
                version = self.get_schema_version()
                if version < CURRENT_SCHEMA_VERSION:
                    self.migrate_schema(version)
                    self.set_schema_version(CURRENT_SCHEMA_VERSION)
        except Exception as e:
            logging.error("[database.py] [init_database] Error initializing database: %s", e)
            raise
        except Exception as e:
            print(f"Error initializing database: {e}")
            # Try to create directory and retry
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create leaderboard table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS leaderboard (
                        username TEXT PRIMARY KEY,
                        current_streak INTEGER DEFAULT 0,
                        total_correct INTEGER DEFAULT 0,
                        total_points INTEGER DEFAULT 0,
                        total_answered INTEGER DEFAULT 0,
                        last_answered TEXT,
                        last_trivia_date TEXT,
                        answer_history TEXT
                    )
                ''')
                
                # Create daily_facts table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS daily_facts (
                        timestamp TEXT PRIMARY KEY,
                        fact TEXT NOT NULL
                    )
                ''')
                
                # Create trivia_questions table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS trivia_questions (
                        timestamp TEXT PRIMARY KEY,
                        question TEXT NOT NULL,
                        options TEXT NOT NULL,
                        correct_answer TEXT NOT NULL,
                        explanation TEXT
                    )
                ''')
                
                conn.commit()
                
                # Import compressed data if database is empty and compressed file exists
                cursor.execute("SELECT COUNT(*) FROM leaderboard")
                leaderboard_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM daily_facts")
                facts_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM trivia_questions")
                trivia_count = cursor.fetchone()[0]
                
                if leaderboard_count == 0 and facts_count == 0 and trivia_count == 0:
                    print("📥 Importing compressed data from git...")
                    self.import_compressed_data()
    
    def compress_data(self, data):
        """Compress data using gzip"""
        try:
            json_str = json.dumps(data, ensure_ascii=False)
            return gzip.compress(json_str.encode('utf-8'))
        except Exception as e:
            logging.error("[database.py] [compress_data] Error compressing data: %s", e)
            raise
    
    def decompress_data(self, compressed_data):
        """Decompress gzipped data"""
        try:
            if compressed_data is None:
                return None
            decompressed = gzip.decompress(compressed_data)
            return json.loads(decompressed.decode('utf-8'))
        except Exception as e:
            logging.error("[database.py] [decompress_data] Error decompressing data: %s", e)
            raise

    def encrypt_data(self, data_bytes):
        try:
            f = self._get_fernet()
            encrypted = f.encrypt(data_bytes)
            return encrypted
        except Exception as e:
            logging.error("[database.py] [encrypt_data] Error encrypting data: %s", e)
            raise

    def decrypt_data(self, encrypted_bytes):
        try:
            f = self._get_fernet()
            decrypted = f.decrypt(encrypted_bytes)
            return decrypted
        except Exception as e:
            logging.error("[database.py] [decrypt_data] Error decrypting data: %s", e)
            raise
    
    def update_leaderboard(self, leaderboard_data):
        """Update leaderboard with compressed data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Clear existing data
                cursor.execute("DELETE FROM leaderboard")
                
                # Insert new data
                for username, data in leaderboard_data.items():
                    compressed_history = self.compress_data(data.get('answer_history', []))
                    cursor.execute('''
                        INSERT INTO leaderboard 
                        (username, current_streak, total_correct, total_points, total_answered, 
                         last_answered, last_trivia_date, answer_history)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        username,
                        data.get('current_streak', 0),
                        data.get('total_correct', 0),
                        data.get('total_points', 0),
                        data.get('total_answered', 0),
                        data.get('last_answered'),
                        data.get('last_trivia_date'),
                        compressed_history
                    ))
                
                conn.commit()
        except Exception as e:
            logging.error("[database.py] [update_leaderboard] Error updating leaderboard: %s", e)
            raise
    
    def get_leaderboard(self):
        """Get leaderboard data with decompressed history"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM leaderboard")
                rows = cursor.fetchall()
                
                leaderboard = {}
                for row in rows:
                    username, streak, correct, points, answered, last_answered, last_date, compressed_history = row
                    leaderboard[username] = {
                        'current_streak': streak,
                        'total_correct': correct,
                        'total_points': points,
                        'total_answered': answered,
                        'last_answered': last_answered,
                        'last_trivia_date': last_date,
                        'answer_history': self.decompress_data(compressed_history) or []
                    }
                
                return leaderboard
        except Exception as e:
            logging.error("[database.py] [get_leaderboard] Error getting leaderboard: %s", e)
            return {}
    
    def update_daily_facts(self, facts_data):
        """Update daily facts with compressed data (timestamp as PK)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                for timestamp, fact_data in facts_data.items():
                    cursor.execute('''
                        INSERT OR IGNORE INTO daily_facts (timestamp, fact)
                        VALUES (?, ?)
                    ''', (timestamp, fact_data['fact']))
                conn.commit()
        except Exception as e:
            logging.error("[database.py] [update_daily_facts] Error updating daily facts: %s", e)
            raise
    
    def get_daily_facts(self):
        """Get daily facts data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT timestamp, fact FROM daily_facts ORDER BY timestamp DESC")
                rows = cursor.fetchall()
                facts = {}
                for row in rows:
                    timestamp, fact = row
                    facts[timestamp] = {
                        'fact': fact,
                        'timestamp': timestamp
                    }
                return facts
        except Exception as e:
            logging.error("[database.py] [get_daily_facts] Error getting daily facts: %s", e)
            return {}

    def get_trivia_questions(self):
        """Get trivia questions data with decompressed options"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM trivia_questions ORDER BY timestamp DESC")
                rows = cursor.fetchall()
                trivia = {}
                for row in rows:
                    timestamp, question, compressed_options, correct_answer, explanation = row
                    trivia[timestamp] = {
                        'question': question,
                        'options': self.decompress_data(compressed_options) if hasattr(self, 'decompress_data') else {},
                        'correct_answer': correct_answer,
                        'explanation': explanation,
                        'timestamp': timestamp
                    }
                return trivia
        except Exception as e:
            logging.error("[database.py] [get_trivia_questions] Error getting trivia questions: %s", e)
            return {}
    
    def update_trivia_questions(self, trivia_data):
        """Update trivia questions with compressed data (timestamp as PK)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                for timestamp, question_data in trivia_data.items():
                    compressed_options = self.compress_data(question_data.get('options', {}))
                    cursor.execute('''
                        INSERT OR REPLACE INTO trivia_questions 
                        (timestamp, question, options, correct_answer, explanation)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        timestamp,
                        question_data.get('question', ''),
                        compressed_options,
                        question_data.get('correct_answer', ''),
                        question_data.get('explanation', '')
                    ))
                conn.commit()
        except Exception as e:
            logging.error("[database.py] [update_trivia_questions] Error updating trivia questions: %s", e)
            raise
    
    def export_compressed_data(self, output_dir=DB_DIR):
        """Export all database tables to a single compressed file for GitHub Actions"""
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Collect all data from all tables
        all_data = {
            "leaderboard": self.get_leaderboard(),
            "daily_facts": self.get_daily_facts(),
            "trivia_questions": self.get_trivia_questions(),
            "export_timestamp": datetime.now().isoformat()
        }
        
        # Export to single compressed file
        compressed_data = self.compress_data(all_data)
        encrypted = self.encrypt_data(compressed_data)
        with open(DB_COMPRESSED_PATH, "wb") as f:
            f.write(encrypted)
        
        logging.info("[database.py] [export_compressed_data] Database exported to single encrypted compressed file")
    
    def import_compressed_data(self, input_dir=DB_DIR):
        """Import single compressed data file into database (for backup restoration)"""
        database_path = DB_COMPRESSED_PATH
        if os.path.exists(database_path):
            with open(database_path, "rb") as f:
                encrypted = f.read()
                try:
                    # Try decrypting (new format)
                    compressed = self.decrypt_data(encrypted)
                    print("[IMPORT-DB] Decompressing database...")
                    all_data = self.decompress_data(compressed)
                    print("✅ Database imported from single encrypted compressed file")
                except Exception:
                    try:
                        # Try decompressing as plaintext (legacy format)
                        print("[IMPORT-DB] Decompressing database (legacy format)...")
                        all_data = self.decompress_data(encrypted)
                        print("⚠️ Imported legacy unencrypted database, re-encrypting...")
                        self.export_compressed_data(os.path.dirname(database_path))
                    except Exception as e:
                        print(f"❌ Failed to import database: {e}")
                        return
                # Import each table
                if "leaderboard" in all_data:
                    self.update_leaderboard(all_data["leaderboard"])
                if "daily_facts" in all_data:
                    self.update_daily_facts(all_data["daily_facts"])
                if "trivia_questions" in all_data:
                    self.update_trivia_questions(all_data["trivia_questions"])
        else:
            print("❌ No compressed database file found") 

    def prune_trivia_questions(self, days=90):
        """Delete trivia questions older than the specified number of days."""
        try:
            cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM trivia_questions WHERE substr(timestamp, 1, 10) < ?", (cutoff,))
                deleted = cursor.rowcount
                conn.commit()
            logging.info(f"[database.py] [prune_trivia_questions] Pruned {deleted} trivia questions older than {cutoff}.")
        except Exception as e:
            logging.error("[database.py] [prune_trivia_questions] Error pruning trivia questions: %s", e)

    def prune_daily_facts(self, days=90):
        """Delete daily facts older than the specified number of days."""
        try:
            cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM daily_facts WHERE substr(timestamp, 1, 10) < ?", (cutoff,))
                deleted = cursor.rowcount
                conn.commit()
            logging.info(f"[database.py] [prune_daily_facts] Pruned {deleted} daily facts older than {cutoff}.")
        except Exception as e:
            logging.error("[database.py] [prune_daily_facts] Error pruning daily facts: %s", e)

    def prune_leaderboard(self, min_last_answered_days=180):
        """Delete leaderboard entries for users who haven't answered in more than min_last_answered_days days."""
        try:
            cutoff = (datetime.now() - timedelta(days=min_last_answered_days)).strftime('%Y-%m-%d')
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM leaderboard WHERE last_answered IS NOT NULL AND substr(last_answered, 1, 10) < ?", (cutoff,))
                deleted = cursor.rowcount
                conn.commit()
            logging.info(f"[database.py] [prune_leaderboard] Pruned {deleted} leaderboard entries with last_answered before {cutoff}.")
        except Exception as e:
            logging.error("[database.py] [prune_leaderboard] Error pruning leaderboard: %s", e) 