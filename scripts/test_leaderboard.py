#!/usr/bin/env python3
"""
Test script to add demo users to the leaderboard for testing
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.database import TriviaDatabase
from src.core.daily_trivia import update_readme, load_trivia_data, load_leaderboard
from datetime import datetime

def add_demo_users():
    """Add demo users to the leaderboard for testing"""
    print("🎯 Adding demo users to leaderboard...")
    
    # Create demo leaderboard data
    demo_leaderboard = {
        "alice_dev": {
            'current_streak': 5,
            'total_correct': 12,
            'total_points': 18,
            'total_answered': 15,
            'last_answered': datetime.now().isoformat(),
            'last_trivia_date': "19.07.2025",
            'answer_history': [
                {'date': '19.07.2025', 'timestamp': datetime.now().isoformat(), 'correct': True},
                {'date': '18.07.2025', 'timestamp': datetime.now().isoformat(), 'correct': True},
                {'date': '17.07.2025', 'timestamp': datetime.now().isoformat(), 'correct': True},
                {'date': '16.07.2025', 'timestamp': datetime.now().isoformat(), 'correct': True},
                {'date': '15.07.2025', 'timestamp': datetime.now().isoformat(), 'correct': True}
            ]
        },
        "bob_coder": {
            'current_streak': 3,
            'total_correct': 8,
            'total_points': 12,
            'total_answered': 10,
            'last_answered': datetime.now().isoformat(),
            'last_trivia_date': "19.07.2025",
            'answer_history': [
                {'date': '19.07.2025', 'timestamp': datetime.now().isoformat(), 'correct': True},
                {'date': '18.07.2025', 'timestamp': datetime.now().isoformat(), 'correct': True},
                {'date': '17.07.2025', 'timestamp': datetime.now().isoformat(), 'correct': True}
            ]
        },
        "charlie_quiz": {
            'current_streak': 7,
            'total_correct': 15,
            'total_points': 25,
            'total_answered': 18,
            'last_answered': datetime.now().isoformat(),
            'last_trivia_date': "19.07.2025",
            'answer_history': [
                {'date': '19.07.2025', 'timestamp': datetime.now().isoformat(), 'correct': True},
                {'date': '18.07.2025', 'timestamp': datetime.now().isoformat(), 'correct': True},
                {'date': '17.07.2025', 'timestamp': datetime.now().isoformat(), 'correct': True},
                {'date': '16.07.2025', 'timestamp': datetime.now().isoformat(), 'correct': True},
                {'date': '15.07.2025', 'timestamp': datetime.now().isoformat(), 'correct': True},
                {'date': '14.07.2025', 'timestamp': datetime.now().isoformat(), 'correct': True},
                {'date': '13.07.2025', 'timestamp': datetime.now().isoformat(), 'correct': True}
            ]
        },
        "diana_smart": {
            'current_streak': 2,
            'total_correct': 6,
            'total_points': 8,
            'total_answered': 8,
            'last_answered': datetime.now().isoformat(),
            'last_trivia_date': "19.07.2025",
            'answer_history': [
                {'date': '19.07.2025', 'timestamp': datetime.now().isoformat(), 'correct': True},
                {'date': '18.07.2025', 'timestamp': datetime.now().isoformat(), 'correct': True}
            ]
        },
        "eddie_brain": {
            'current_streak': 1,
            'total_correct': 4,
            'total_points': 5,
            'total_answered': 6,
            'last_answered': datetime.now().isoformat(),
            'last_trivia_date': "19.07.2025",
            'answer_history': [
                {'date': '19.07.2025', 'timestamp': datetime.now().isoformat(), 'correct': True}
            ]
        }
    }
    
    # Save demo leaderboard to database
    db = TriviaDatabase()
    db.update_leaderboard(demo_leaderboard)
    db.export_compressed_data()
    
    print("✅ Demo users added to leaderboard:")
    for username, stats in demo_leaderboard.items():
        print(f"   - @{username}: {stats['current_streak']} streak, {stats['total_points']} points, {stats['total_correct']} correct")
    
    # Update README with demo leaderboard
    trivia_data = load_trivia_data()
    update_readme(trivia_data, demo_leaderboard)
    
    print("✅ README updated with demo leaderboard!")
    print("📊 Check the README.md file to see the leaderboard in action!")

if __name__ == "__main__":
    add_demo_users() 