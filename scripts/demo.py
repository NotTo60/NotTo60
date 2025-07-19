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
    
    # Test WOW facts from APIs
    print("\n🌟 Testing WOW Facts from APIs...")
    test_categories = ["science", "space", "animals", "human_body", "general"]
    
    for category in test_categories:
        print(f"\n📡 Fetching {category} WOW fact...")
        wow_result = get_wow_fact(category)
        print(f"✅ {wow_result['fact']}")
        print(f"   Source: {wow_result['source']}")
        print(f"   Category: {wow_result['category']}")
    
    # Test daily facts from APIs
    print("\n💡 Testing Daily Facts from APIs...")
    daily_categories = ["random", "food", "time", "countries", "general"]
    
    for category in daily_categories:
        print(f"\n📡 Fetching {category} daily fact...")
        daily_result = get_daily_fact(category)
        print(f"✅ {daily_result['fact']}")
        print(f"   Source: {daily_result['source']}")
        print(f"   Category: {daily_result['category']}")
    
    # Generate trivia with WOW facts
    print("\n🔄 Generating trivia question with WOW facts...")
    trivia_data = load_trivia_data()
    
    # Create demo trivia with WOW fact
    wow_fact_result = get_wow_fact("space")
    wow_fact = wow_fact_result.get('fact', '🚀 **AMAZING FACT:** The Sun makes up 99.86% of our solar system\'s mass!')
    
    demo_trivia = {
        "question": "Based on this SPACE fact: 'The Sun makes up 99.86% of our solar system's mass!', which statement is TRUE?",
        "options": {
            "A": "This space fact is completely accurate",
            "B": "This space fact has been proven false", 
            "C": "This space fact is still being debated by scientists"
        },
        "correct_answer": "A",
        "category": "space",
        "explanation": "This is a verified space fact that has been confirmed by multiple astronomical observations and calculations.",
        "wow_fact": wow_fact,
        "fact_source": wow_fact_result.get('source', 'demo'),
        "date": datetime.now().strftime("%d.%m.%Y")
    }
    
    trivia_data["current"] = demo_trivia
    save_trivia_data(trivia_data)
    
    print(f"✅ Generated trivia: {demo_trivia['question']}")
    print(f"🌟 WOW Fact: {demo_trivia['wow_fact']}")
    
    # Get today's daily fact
    daily_fact = get_todays_fact()
    print(f"💡 Daily Fact: {daily_fact['fact']}")
    
    # Create demo leaderboard
    demo_leaderboard = {
        "demo_user1": {
            "current_streak": 5,
            "total_correct": 12,
            "total_answered": 15,
            "last_answered": datetime.now().isoformat()
        },
        "demo_user2": {
            "current_streak": 3,
            "total_correct": 8,
            "total_answered": 10,
            "last_answered": datetime.now().isoformat()
        },
        "demo_user3": {
            "current_streak": 1,
            "total_correct": 3,
            "total_answered": 5,
            "last_answered": datetime.now().isoformat()
        }
    }
    
    save_leaderboard(demo_leaderboard)
    
    # Update README
    update_readme(trivia_data, demo_leaderboard)
    
    print("\n📊 Demo Data Created:")
    print(f"   - Trivia question: {demo_trivia['question']}")
    print(f"   - Correct answer: {demo_trivia['correct_answer']}) {demo_trivia['options'][demo_trivia['correct_answer']]}")
    print(f"   - WOW Fact: {demo_trivia['wow_fact']}")
    print(f"   - Daily Fact: {daily_fact['fact']}")
    print(f"   - Demo users: {len(demo_leaderboard)}")
    print(f"   - README updated with trivia, WOW facts, daily fact, and leaderboard")
    
    print("\n🎮 How to Test:")
    print("   1. Check the README.md file for the trivia question with WOW fact")
    print("   2. Look for the 'Did You Know?' section with daily fact")
    print("   3. The answer links will point to GitHub issues")
    print("   4. In a real setup, users would click these links to answer")
    print("   5. WOW facts and daily facts are fetched from real APIs when available")
    
    print("\n📁 Generated Files:")
    print("   - trivia.json (current trivia data with WOW facts)")
    print("   - daily_facts.json (daily facts data)")
    print("   - leaderboard.json (user statistics)")
    print("   - README.md (updated with trivia, WOW facts, daily fact, and leaderboard)")

def show_answer_links():
    """Show what the answer links would look like"""
    print("\n🔗 Answer Links (for demo):")
    print("   These would be the actual GitHub issue links:")
    
    base_url = f"https://github.com/{GITHUB_USERNAME}/{GITHUB_REPO}"
    links = {
        "A": f"{base_url}/issues/new?title=Trivia+Answer+A&body={ISSUE_TEMPLATE.format(answer='A')}",
        "B": f"{base_url}/issues/new?title=Trivia+Answer+B&body={ISSUE_TEMPLATE.format(answer='B')}", 
        "C": f"{base_url}/issues/new?title=Trivia+Answer+C&body={ISSUE_TEMPLATE.format(answer='C')}"
    }
    
    for option, link in links.items():
        print(f"   {option}) {link}")

def test_wow_facts_module():
    """Test the WOW facts module independently"""
    print("\n🧪 Testing WOW Facts Module")
    print("=" * 40)
    
    # Test different categories
    categories = ["science", "space", "animals", "human_body", "general"]
    
    for category in categories:
        print(f"\n📡 Fetching {category} fact...")
        result = get_wow_fact(category)
        print(f"✅ {result['fact']}")
        print(f"   Source: {result['source']}")
        print(f"   Category: {result['category']}")

def test_daily_facts_module():
    """Test the daily facts module independently"""
    print("\n🧪 Testing Daily Facts Module")
    print("=" * 40)
    
    # Test different categories
    categories = ["random", "food", "time", "countries", "general"]
    
    for category in categories:
        print(f"\n📡 Fetching {category} daily fact...")
        result = get_daily_fact(category)
        print(f"✅ {result['fact']}")
        print(f"   Source: {result['source']}")
        print(f"   Category: {result['category']}")
    
    # Test today's fact
    print(f"\n📅 Today's fact:")
    today_fact = get_todays_fact()
    print(f"✅ {today_fact['fact']}")
    print(f"   Date: {today_fact['date']}")
    print(f"   Source: {today_fact['source']}")

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
    test_wow_facts_module()
    test_daily_facts_module()
    show_configuration()
    
    print("\n🎉 Demo complete! Check the generated files to see the trivia system with WOW facts and daily facts in action.")
    print("🌟 The system now fetches AMAZING facts from real APIs and adds a daily 'Did You Know?' section!")
    print("💡 Every day, users will see a new interesting fact alongside the trivia question!") 