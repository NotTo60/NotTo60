#!/usr/bin/env python3
"""
Script to update README with existing trivia data and demo leaderboard
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.daily_trivia import load_trivia_data, load_leaderboard, update_readme
from datetime import datetime

def update_readme_only():
    """Update README with existing data and demo leaderboard"""
    print("📝 Updating README with existing data...")
    
    # Load existing data
    trivia_data = load_trivia_data()
    leaderboard = load_leaderboard()
    
    print(f"📊 Leaderboard loaded: {len(leaderboard)} users")
    print(f"   Users: {list(leaderboard.keys())}")
    
    # Check if we have current trivia
    current_trivia = trivia_data.get("current")
    if not current_trivia:
        print("⚠️  No current trivia found, creating a simple one for testing")
        # Create a simple trivia for testing
        trivia_data["current"] = {
            "question": "Which animal has the longest lifespan?",
            "options": {
                "A": "Greenland Shark",
                "B": "Giant Tortoise", 
                "C": "Bowhead Whale"
            },
            "correct_answer": "A",
            "explanation": "Greenland sharks can live for over 400 years, making them the longest-living vertebrates known to science.",
            "date": datetime.now().strftime("%d.%m.%Y"),
            "category": "animals"
        }
    
    # Update README
    update_readme(trivia_data, leaderboard)
    print("✅ README updated successfully!")

if __name__ == "__main__":
    update_readme_only() 