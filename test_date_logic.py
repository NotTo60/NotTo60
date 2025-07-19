#!/usr/bin/env python3
"""
Test script to demonstrate the enhanced date checking logic
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from datetime import datetime, timedelta
from core.process_answers import can_user_answer_today
from core.config import *

def test_date_logic():
    """Test the enhanced date checking logic"""
    print("🧪 Testing Enhanced Date Logic")
    print("=" * 40)
    
    # Create a test leaderboard
    test_leaderboard = {
        "user1": {
            "current_streak": 5,
            "total_correct": 12,
            "total_answered": 15,
            "last_answered": datetime.now().isoformat(),
            "last_trivia_date": "20.07.2025",
            "answer_history": [
                {
                    "date": "20.07.2025",
                    "timestamp": datetime.now().isoformat(),
                    "correct": True
                }
            ]
        },
        "user2": {
            "current_streak": 3,
            "total_correct": 8,
            "total_answered": 10,
            "last_answered": (datetime.now() - timedelta(hours=1)).isoformat(),
            "last_trivia_date": "19.07.2025",
            "answer_history": [
                {
                    "date": "19.07.2025",
                    "timestamp": (datetime.now() - timedelta(hours=1)).isoformat(),
                    "correct": True
                }
            ]
        },
        "user3": {
            "current_streak": 1,
            "total_correct": 3,
            "total_answered": 5,
            "last_answered": (datetime.now() - timedelta(hours=3)).isoformat(),
            "last_trivia_date": "19.07.2025",
            "answer_history": [
                {
                    "date": "19.07.2025",
                    "timestamp": (datetime.now() - timedelta(hours=3)).isoformat(),
                    "correct": False
                }
            ]
        },
        "new_user": {
            "current_streak": 0,
            "total_correct": 0,
            "total_answered": 0,
            "last_answered": None,
            "last_trivia_date": None,
            "answer_history": []
        }
    }
    
    current_trivia_date = "20.07.2025"
    
    print(f"📅 Current Trivia Date: {current_trivia_date}")
    print(f"⏰ Grace Period: {GRACE_PERIOD_HOURS} hours")
    print(f"🌍 Timezone: {TIMEZONE}")
    print()
    
    # Test each user
    for username, user_data in test_leaderboard.items():
        print(f"👤 Testing {username}:")
        print(f"   Last trivia date: {user_data.get('last_trivia_date', 'Never')}")
        print(f"   Last answered: {user_data.get('last_answered', 'Never')}")
        
        can_answer, reason = can_user_answer_today(test_leaderboard, username, current_trivia_date)
        
        if can_answer:
            print(f"   ✅ Can answer: Yes")
        else:
            print(f"   ❌ Can answer: No - {reason}")
        print()
    
    print("📊 Test Scenarios:")
    print("1. user1: Already answered today's trivia (20.07.2025) - Should be blocked")
    print("2. user2: Answered yesterday, within grace period - Should be blocked")
    print("3. user3: Answered yesterday, outside grace period - Should be allowed")
    print("4. new_user: Never answered - Should be allowed")

if __name__ == "__main__":
    test_date_logic() 