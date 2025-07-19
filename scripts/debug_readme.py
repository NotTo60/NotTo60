#!/usr/bin/env python3
"""
Debug script to test the update_readme function
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.daily_trivia import load_trivia_data, load_leaderboard, get_top_leaderboard, update_readme

def debug_readme_update():
    """Debug the README update process"""
    print("🔍 Debugging README update...")
    
    # Load data
    trivia_data = load_trivia_data()
    leaderboard = load_leaderboard()
    
    print(f"📊 Leaderboard loaded: {len(leaderboard)} users")
    print(f"   Users: {list(leaderboard.keys())}")
    
    # Test get_top_leaderboard
    top_users = get_top_leaderboard(leaderboard)
    print(f"🏆 Top users: {len(top_users)} users")
    for i, (username, stats) in enumerate(top_users, 1):
        print(f"   {i}. @{username}: {stats['total_points']} points, {stats['current_streak']} streak")
    
    # Test update_readme
    print("📝 Updating README...")
    update_readme(trivia_data, leaderboard)
    print("✅ README update completed!")
    
    # Check if README was actually updated
    with open("README.md", "r") as f:
        content = f.read()
        if "No participants yet" in content:
            print("❌ README still shows 'No participants yet'")
        else:
            print("✅ README updated successfully!")

if __name__ == "__main__":
    debug_readme_update() 