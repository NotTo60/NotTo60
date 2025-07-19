import sqlite3
import gzip
import json
import os
from datetime import datetime
from pathlib import Path

class TriviaDatabase:
    def __init__(self, db_path="src/data/trivia.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
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
        """Update daily facts with compressed data"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Clear existing data
            cursor.execute("DELETE FROM daily_facts")
            
            # Insert new data
            for date, fact_data in facts_data.items():
                cursor.execute('''
                    INSERT INTO daily_facts (date, fact, timestamp)
                    VALUES (?, ?, ?)
                ''', (date, fact_data['fact'], fact_data['timestamp']))
            
            conn.commit()
    
    def get_daily_facts(self):
        """Get daily facts data"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM daily_facts ORDER BY date DESC")
            rows = cursor.fetchall()
            
            facts = {}
            for row in rows:
                date, fact, timestamp = row
                facts[date] = {
                    'fact': fact,
                    'timestamp': timestamp
                }
            
            return facts
    
    def update_trivia_questions(self, trivia_data):
        """Update trivia questions with compressed data"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Clear existing data
            cursor.execute("DELETE FROM trivia_questions")
            
            # Insert new data
            for date, question_data in trivia_data.items():
                compressed_options = self.compress_data(question_data.get('options', {}))
                cursor.execute('''
                    INSERT INTO trivia_questions 
                    (date, question, options, correct_answer, explanation, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    date,
                    question_data.get('question', ''),
                    compressed_options,
                    question_data.get('correct_answer', ''),
                    question_data.get('explanation', ''),
                    question_data.get('timestamp', '')
                ))
            
            conn.commit()
    
    def get_trivia_questions(self):
        """Get trivia questions data with decompressed options"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM trivia_questions ORDER BY date DESC")
            rows = cursor.fetchall()
            
            trivia = {}
            for row in rows:
                date, question, compressed_options, correct_answer, explanation, timestamp = row
                trivia[date] = {
                    'question': question,
                    'options': self.decompress_data(compressed_options) or {},
                    'correct_answer': correct_answer,
                    'explanation': explanation,
                    'timestamp': timestamp
                }
            
            return trivia
    
    def export_compressed_data(self, output_dir="src/data"):
        """Export database to compressed files for GitHub Actions"""
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Export leaderboard
        leaderboard = self.get_leaderboard()
        compressed_leaderboard = self.compress_data(leaderboard)
        with open(f"{output_dir}/leaderboard.db.gz", "wb") as f:
            f.write(compressed_leaderboard)
        
        # Export daily facts
        facts = self.get_daily_facts()
        compressed_facts = self.compress_data(facts)
        with open(f"{output_dir}/daily_facts.db.gz", "wb") as f:
            f.write(compressed_facts)
        
        # Export trivia questions
        trivia = self.get_trivia_questions()
        compressed_trivia = self.compress_data(trivia)
        with open(f"{output_dir}/trivia_questions.db.gz", "wb") as f:
            f.write(compressed_trivia)
    
    def import_compressed_data(self, input_dir="src/data"):
        """Import compressed data files into database (for backup restoration)"""
        # Import leaderboard
        leaderboard_path = f"{input_dir}/leaderboard.db.gz"
        if os.path.exists(leaderboard_path):
            with open(leaderboard_path, "rb") as f:
                compressed_data = f.read()
                leaderboard = self.decompress_data(compressed_data)
                self.update_leaderboard(leaderboard)
        
        # Import daily facts
        facts_path = f"{input_dir}/daily_facts.db.gz"
        if os.path.exists(facts_path):
            with open(facts_path, "rb") as f:
                compressed_data = f.read()
                facts = self.decompress_data(compressed_data)
                self.update_daily_facts(facts)
        
        # Import trivia questions
        trivia_path = f"{input_dir}/trivia_questions.db.gz"
        if os.path.exists(trivia_path):
            with open(trivia_path, "rb") as f:
                compressed_data = f.read()
                trivia = self.decompress_data(compressed_data)
                self.update_trivia_questions(trivia) 