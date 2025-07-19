#!/usr/bin/env python3
"""
Migration script to convert JSON data to SQLite database with gzip compression
"""

import sys
import os
import json
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from core.database import TriviaDatabase

def load_json_data(file_path):
    """Load JSON data from file"""
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def migrate_data():
    """Migrate existing JSON data to database"""
    print("🔄 Starting migration to SQLite database with gzip compression...")
    
    # Initialize database
    db = TriviaDatabase()
    
    # Migrate leaderboard data
    print("📊 Migrating leaderboard data...")
    leaderboard_path = "src/data/leaderboard.json"
    leaderboard_data = load_json_data(leaderboard_path)
    if leaderboard_data:
        db.update_leaderboard(leaderboard_data)
        print(f"✅ Migrated {len(leaderboard_data)} leaderboard entries")
    else:
        print("⚠️  No leaderboard data found")
    
    # Migrate daily facts data
    print("📚 Migrating daily facts data...")
    facts_path = "src/data/daily_facts.json"
    facts_data = load_json_data(facts_path)
    if facts_data:
        # Convert to expected format
        converted_facts = {}
        
        # Handle current fact
        if "current" in facts_data and facts_data["current"]:
            current_fact = facts_data["current"]
            date = current_fact.get("date", "current")
            converted_facts[date] = {
                "fact": current_fact["fact"],
                "timestamp": datetime.now().isoformat()
            }
        
        # Handle history facts
        for fact in facts_data.get("history", []):
            date = fact.get("date", "unknown")
            converted_facts[date] = {
                "fact": fact["fact"],
                "timestamp": datetime.now().isoformat()
            }
        
        db.update_daily_facts(converted_facts)
        print(f"✅ Migrated {len(converted_facts)} daily facts")
    else:
        print("⚠️  No daily facts data found")
    
    # Migrate trivia questions data
    print("🎯 Migrating trivia questions data...")
    trivia_path = "src/data/trivia.json"
    trivia_data = load_json_data(trivia_path)
    if trivia_data:
        # Convert to expected format
        converted_trivia = {}
        
        # Handle current trivia
        if "current" in trivia_data and trivia_data["current"]:
            current_trivia = trivia_data["current"]
            today = datetime.now().strftime("%d.%m.%Y")
            converted_trivia[today] = {
                "question": current_trivia.get("question", ""),
                "options": current_trivia.get("options", {}),
                "correct_answer": current_trivia.get("correct_answer", ""),
                "explanation": current_trivia.get("explanation", ""),
                "timestamp": datetime.now().isoformat()
            }
        
        # Handle history trivia
        for i, trivia in enumerate(trivia_data.get("history", [])):
            date = f"history_{i}"
            converted_trivia[date] = {
                "question": trivia.get("question", ""),
                "options": trivia.get("options", {}),
                "correct_answer": trivia.get("correct_answer", ""),
                "explanation": trivia.get("explanation", ""),
                "timestamp": datetime.now().isoformat()
            }
        
        db.update_trivia_questions(converted_trivia)
        print(f"✅ Migrated {len(converted_trivia)} trivia questions")
    else:
        print("⚠️  No trivia questions data found")
    
    # Export compressed data files
    print("🗜️  Exporting compressed data files...")
    db.export_compressed_data()
    print("✅ Compressed data files exported")
    
    # Show compression statistics
    print("\n📈 Compression Statistics:")
    
    # Original JSON sizes
    original_sizes = {}
    for file_name in ["leaderboard.json", "daily_facts.json", "trivia_questions.json"]:
        file_path = f"src/data/{file_name}"
        if os.path.exists(file_path):
            original_size = os.path.getsize(file_path)
            original_sizes[file_name] = original_size
            print(f"📄 {file_name}: {original_size:,} bytes")
    
    # Compressed sizes
    compressed_sizes = {}
    for file_name in ["leaderboard.db.gz", "daily_facts.db.gz", "trivia_questions.db.gz"]:
        file_path = f"src/data/{file_name}"
        if os.path.exists(file_path):
            compressed_size = os.path.getsize(file_path)
            compressed_sizes[file_name] = compressed_size
            print(f"🗜️  {file_name}: {compressed_size:,} bytes")
    
    # Calculate savings
    total_original = sum(original_sizes.values())
    total_compressed = sum(compressed_sizes.values())
    if total_original > 0:
        savings = ((total_original - total_compressed) / total_original) * 100
        print(f"\n💾 Total space saved: {savings:.1f}% ({total_original:,} → {total_compressed:,} bytes)")
    
    print("\n🎉 Migration completed successfully!")
    print("📁 Database file: src/data/trivia.db")
    print("🗜️  Compressed files: src/data/*.db.gz")

if __name__ == "__main__":
    migrate_data() 