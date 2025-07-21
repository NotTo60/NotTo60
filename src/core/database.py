import sqlite3
import gzip
import json
import os
from datetime import datetime
from pathlib import Path
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import base64
import secrets

class TriviaDatabase:
    def __init__(self, db_path="src/data/trivia.db"):
        self.db_path = db_path
        # Ensure the directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.init_database()

    def _get_password(self):
        password = os.getenv("TRIVIA_DB_PASSWORD")
        if not password:
            raise RuntimeError("TRIVIA_DB_PASSWORD environment variable is required for database encryption.")
        return password.encode()

    def _get_fernet(self, salt=None):
        password = self._get_password()
        if salt is None:
            # Use a fixed salt for export (for reproducibility in git), or store salt in file header
            salt = b"trivia_db_salt_2024"  # 16 bytes, can be changed for more security
        print(f"[DEBUG] Using salt: {salt}")
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=390000,
            backend=default_backend(),
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        print(f"[DEBUG] Derived key (first 16): {key[:16]}")
        return Fernet(key)

    def init_database(self):
        """Initialize the database with required tables"""
        try:
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
                        date TEXT PRIMARY KEY,
                        fact TEXT NOT NULL,
                        timestamp TEXT NOT NULL
                    )
                ''')
                
                # Create trivia_questions table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS trivia_questions (
                        date TEXT PRIMARY KEY,
                        question TEXT NOT NULL,
                        options TEXT NOT NULL,
                        correct_answer TEXT NOT NULL,
                        explanation TEXT,
                        timestamp TEXT NOT NULL
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
                        date TEXT PRIMARY KEY,
                        fact TEXT NOT NULL,
                        timestamp TEXT NOT NULL
                    )
                ''')
                
                # Create trivia_questions table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS trivia_questions (
                        date TEXT PRIMARY KEY,
                        question TEXT NOT NULL,
                        options TEXT NOT NULL,
                        correct_answer TEXT NOT NULL,
                        explanation TEXT,
                        timestamp TEXT NOT NULL
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
        json_str = json.dumps(data, ensure_ascii=False)
        return gzip.compress(json_str.encode('utf-8'))
    
    def decompress_data(self, compressed_data):
        """Decompress gzipped data"""
        if compressed_data is None:
            return None
        decompressed = gzip.decompress(compressed_data)
        return json.loads(decompressed.decode('utf-8'))

    def encrypt_data(self, data_bytes):
        f = self._get_fernet()
        print("[DEBUG] Encrypting data...")
        print(f"[DEBUG] Data bytes (first 16): {data_bytes[:16]}")
        encrypted = f.encrypt(data_bytes)
        print(f"[DEBUG] Encrypted bytes (first 16): {encrypted[:16]}")
        return encrypted

    def decrypt_data(self, encrypted_bytes):
        f = self._get_fernet()
        print("[DEBUG] Decrypting data...")
        print(f"[DEBUG] Encrypted bytes (first 16): {encrypted_bytes[:16]}")
        try:
            decrypted = f.decrypt(encrypted_bytes)
            print(f"[DEBUG] Decrypted bytes (first 16): {decrypted[:16]}")
            return decrypted
        except Exception as e:
            print(f"[DEBUG] Decryption failed: {e}")
            raise
    
    def update_leaderboard(self, leaderboard_data):
        """Update leaderboard with compressed data"""
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
    
    def get_leaderboard(self):
        """Get leaderboard data with decompressed history"""
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
    
    def update_daily_facts(self, facts_data):
        """Update daily facts with compressed data (timestamp as PK)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for timestamp, fact_data in facts_data.items():
                cursor.execute('''
                    INSERT OR IGNORE INTO daily_facts (timestamp, fact)
                    VALUES (?, ?)
                ''', (timestamp, fact_data['fact']))
            conn.commit()
    
    def get_daily_facts(self):
        """Get daily facts data"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM daily_facts ORDER BY timestamp DESC")
            rows = cursor.fetchall()
            facts = {}
            for row in rows:
                timestamp, fact = row
                facts[timestamp] = {
                    'fact': fact,
                    'timestamp': timestamp
                }
            return facts

    def get_trivia_questions(self):
        """Get trivia questions data with decompressed options"""
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
    
    def update_trivia_questions(self, trivia_data):
        """Update trivia questions with compressed data (timestamp as PK)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for timestamp, question_data in trivia_data.items():
                compressed_options = self.compress_data(question_data.get('options', {}))
                cursor.execute('''
                    INSERT OR IGNORE INTO trivia_questions 
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
    
    def export_compressed_data(self, output_dir="src/data"):
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
        with open(f"{output_dir}/trivia_database.db.gz", "wb") as f:
            f.write(encrypted)
        
        print("✅ Database exported to single encrypted compressed file")
    
    def import_compressed_data(self, input_dir="src/data"):
        """Import single compressed data file into database (for backup restoration)"""
        database_path = f"{input_dir}/trivia_database.db.gz"
        if os.path.exists(database_path):
            with open(database_path, "rb") as f:
                encrypted = f.read()
                try:
                    # Try decrypting (new format)
                    compressed = self.decrypt_data(encrypted)
                    all_data = self.decompress_data(compressed)
                    print("✅ Database imported from single encrypted compressed file")
                except Exception:
                    try:
                        # Try decompressing as plaintext (legacy format)
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