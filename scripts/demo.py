#!/usr/bin/env python3
"""
Demo script for testing the trivia system with WOW facts and daily facts
"""

import os
import json
import random
from datetime import datetime
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.daily_trivia import *
from src.core.wow_facts import get_wow_fact, create_trivia_from_wow_fact
from src.core.daily_facts import get_daily_fact, get_todays_fact

def demo_trivia_generation():
    """Demo the trivia generation process with WOW facts and daily facts"""
    print("🎯 Interactive AI-Powered Trivia Demo with WOW Facts & Daily Facts")
    print("=" * 70)
    
    # Set up environment for demo
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  No OpenAI API key found. Using WOW facts from APIs and fallback trivia.")
        print("   Set OPENAI_API_KEY environment variable for AI-generated questions.")
    
    # Test single daily fact (what's actually needed per day)
    print("\n💡 Testing Daily Fact (1 per day)...")
    daily_fact = get_todays_fact()
    print(f"✅ {daily_fact['fact']}")
    print(f"   Timestamp: {daily_fact.get('timestamp', 'N/A')}")
    
    # Generate trivia with WOW facts
    print("\n🔄 Generating trivia question with WOW facts...")
    trivia_data = load_trivia_data()
    
    # Create demo trivia (standalone, not based on facts)
    demo_trivia = {
        "question": "What is the largest planet in our solar system?",
        "options": {
            "A": "Jupiter",
            "B": "Saturn", 
            "C": "Neptune"
        },
        "correct_answer": "A",
        "category": "space",
        "explanation": "Jupiter is the largest planet in our solar system, with a mass more than twice that of Saturn.",
        "date": datetime.now().strftime(DATE_FORMAT)
    }
    
    trivia_data["current"] = demo_trivia
    save_trivia_data(trivia_data)
    
    print(f"✅ Generated trivia: {demo_trivia['question']}")
    
    # Get today's daily fact
    daily_fact = get_todays_fact()
    print(f"💡 Daily Fact: {daily_fact['fact']}")
    
    # Create empty leaderboard (no demo users)
    empty_leaderboard = {}
    
    save_leaderboard(empty_leaderboard)
    
    # Update README
    update_readme(trivia_data, empty_leaderboard)
    
    print("\n📊 Demo Data Created:")
    print(f"   - Trivia question: {demo_trivia['question']}")
    print(f"   - Correct answer: {demo_trivia['correct_answer']}) {demo_trivia['options'][demo_trivia['correct_answer']]}")
    print(f"   - Daily Fact: {daily_fact['fact']}")
    print(f"   - Leaderboard: Empty (no demo users)")
    print(f"   - README updated with trivia, daily fact, and empty leaderboard")
    
    print("\n🎮 How to Test:")
    print("   1. Check the README.md file for the trivia question")
    print("   2. Look for the 'Did You Know?' section with daily fact")
    print("   3. The answer links will point to GitHub issues")
    print("   4. In a real setup, users would click these links to answer")
    print("   5. Daily facts are fetched from real APIs when available")
    
    print("\n📁 Generated Files:")
    print("   - trivia.db (SQLite database)")
    print("   - *.db.gz (compressed data exports)")
    print("   - README.md (updated with trivia, daily fact, and leaderboard)")

def show_answer_links():
    """Show what the answer links would look like"""
    print("\n🔗 Answer Links (for demo):")
    print("   These would be the actual GitHub issue links:")
    
    base_url = f"https://github.com/{GITHUB_USERNAME}/{GITHUB_REPO}"
    links = {
        "A": f"{base_url}/issues/new?title=Trivia+Answer+A&body={ISSUE_TEMPLATE.format(answer_text='A')}",
        "B": f"{base_url}/issues/new?title=Trivia+Answer+B&body={ISSUE_TEMPLATE.format(answer_text='B')}", 
        "C": f"{base_url}/issues/new?title=Trivia+Answer+C&body={ISSUE_TEMPLATE.format(answer_text='C')}"
    }
    
    for option, link in links.items():
        print(f"   {option}) {link}")

def test_single_fact():
    """Test single fact generation (what's actually needed)"""
    print("\n🧪 Testing Single Fact Generation")
    print("=" * 40)
    
    # Test today's fact (the only one needed per day)
    print(f"\n📅 Today's fact:")
    today_fact = get_todays_fact()
    print(f"✅ {today_fact['fact']}")
    print(f"   Timestamp: {today_fact.get('timestamp', 'N/A')}")

def show_configuration():
    """Show the current configuration"""
    print("\n⚙️  Current Configuration:")
    print("=" * 30)
    print(f"   - GitHub Username: {GITHUB_USERNAME}")
    print(f"   - GitHub Repo: {GITHUB_REPO}")
    print(f"   - Trivia Categories: {len(TRIVIA_CATEGORIES)} categories")
    print(f"   - Daily Fact Categories: {len(DAILY_FACT_CATEGORIES)} categories")
    print(f"   - WOW Keywords: {len(WOW_KEYWORDS)} keywords")
    print(f"   - WOW Fact APIs: {len(WOW_FACT_APIS)} endpoints")
    print(f"   - Daily Fact APIs: {len(DAILY_FACT_SOURCES)} endpoints")
    print(f"   - Daily Fact Templates: {len(DAILY_FACT_TEMPLATES)} templates")
    print(f"   - Max Leaderboard Entries: {MAX_LEADERBOARD_ENTRIES}")
    print(f"   - OpenAI Model: {MODEL}")
    print(f"   - Max Tokens: {MAX_TOKENS}")
    print(f"   - Temperature: {TEMPERATURE}")

if __name__ == "__main__":
    demo_trivia_generation()
    show_answer_links()
    test_single_fact()
    show_configuration()
    
    print("\n🎉 Demo complete! Check the generated files to see the trivia system in action.")
    print("🌟 The system fetches 1 daily fact and generates 1 trivia question per day!")
    print("💡 Simple, efficient, and focused on what's actually needed!") 