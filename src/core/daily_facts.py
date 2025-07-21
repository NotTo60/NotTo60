#!/usr/bin/env python3
"""
Daily Facts Module - Fetches interesting daily facts for "Did You Know?" section
"""

import requests
import random
import json
import os
from datetime import datetime
from typing import Dict, Optional
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.config import *
from core.database import TriviaDatabase

def fetch_random_fact() -> Optional[str]:
    """Fetch a random fact from uselessfacts API"""
    try:
        response = requests.get(DAILY_FACT_SOURCES["random_facts"], timeout=API_TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            return data.get('text', '')
    except Exception as e:
        print(f"Error fetching random fact: {e}")
    return None

def generate_fallback_daily_fact() -> str:
    """Generate a fallback daily fact when APIs are unavailable"""
    fallback_facts = [
        "The shortest war in history lasted only 38 minutes between Britain and Zanzibar in 1896!",
        "Honey never spoils - archaeologists have found pots of honey in ancient Egyptian tombs!",
        "A day on Venus is longer than its year!",
        "There are more possible games of chess than atoms in the universe!",
        "The average person spends 6 months of their lifetime waiting for red lights!",
        "Bananas are radioactive due to their potassium content!",
        "A group of flamingos is called a 'flamboyance'!",
        "Octopuses have three hearts and blue blood!",
        "Your brain uses 20% of your body's total energy!",
        "The Great Wall of China is not visible from space with the naked eye!",
        "There are more stars in the universe than grains of sand on Earth!",
        "The Sun makes up 99.86% of our solar system's mass!",
        "One million Earths could fit inside the Sun!",
        "The footprints on the Moon will last for 100 million years!",
        "A day-old baby kangaroo is the size of a jellybean!",
        "Elephants are the only mammals that can't jump!",
        "A cat's purr vibrates at a frequency that promotes bone healing!",
        "You shed about 600,000 particles of skin every hour!",
        "Your heart beats about 100,000 times every day!",
        "You have enough blood vessels to circle the Earth 2.5 times!",
        "Your body contains enough carbon to fill 900 pencils!",
        "The human body contains enough iron to make a 3-inch nail!",
        "A day on Mars is only 37 minutes longer than a day on Earth!",
        "There are more atoms in a glass of water than glasses of water in all the oceans!"
    ]
    return random.choice(fallback_facts)

def get_daily_fact() -> Dict[str, str]:
    """Get a daily fact from the random facts API only."""
    for _ in range(MAX_RETRIES):
        try:
            fact = fetch_random_fact()
            if fact and 10 < len(fact) < 200:
                template = random.choice(DAILY_FACT_TEMPLATES)
                formatted_fact = template.format(fact=fact)
                return {
                    "fact": formatted_fact,
                    "source": "fetch_random_fact",
                    "category": "random",
                    "raw_fact": fact
                }
        except Exception as e:
            print(f"Error with fetch_random_fact: {e}")
            continue
    # Fallback to generated fact
    fallback_fact = generate_fallback_daily_fact()
    template = random.choice(DAILY_FACT_TEMPLATES)
    formatted_fact = template.format(fact=fallback_fact)
    return {
        "fact": formatted_fact,
        "source": "fallback_generated",
        "category": "random",
        "raw_fact": fallback_fact
    }

def load_daily_facts():
    """Load existing daily facts data from database"""
    try:
        db = TriviaDatabase()
        return db.get_daily_facts()
    except Exception as e:
        print(f"Error loading daily facts from database: {e}")
        # Return empty facts as fallback
        return {}

def save_daily_facts(daily_facts_data):
    """Save daily facts data to database"""
    try:
        db = TriviaDatabase()
        db.update_daily_facts(daily_facts_data)
        db.export_compressed_data()
    except Exception as e:
        print(f"Error saving daily facts to database: {e}")
        # Continue without saving if database fails

def get_todays_fact() -> Dict[str, str]:
    """Get today's fact, generating a new one if needed, ensuring uniqueness. Never override if exists."""
    db = TriviaDatabase()
    facts = db.get_daily_facts()
    today = datetime.now().strftime('%Y-%m-%d')
    # Find the latest fact by timestamp
    if facts:
        latest = max(facts.values(), key=lambda f: f.get('timestamp', ''))
        latest_date = latest['timestamp'][:10]
        print(f"[DEBUG] Latest fact timestamp: {latest['timestamp']}, date: {latest_date}")
        if latest_date == today:
            print(f"🌞 Fact for today ({today}) already exists:")
            print(f"    {latest['fact']}")
            print(f"    (added at {latest['timestamp']})")
            return latest
    print(f"[DEBUG] No fact for today, will fetch new.")
    # Only fetch if not exists
    previous_facts = set(fact['fact'] for fact in facts.values())
    max_api_attempts = 2
    new_fact = None
    for attempt in range(max_api_attempts):
        candidate = get_daily_fact()
        if candidate["fact"] not in previous_facts:
            new_fact = candidate
            break
    if not new_fact:
        local_facts = [
            {"fact": "Honey never spoils."},
            {"fact": "Bananas are berries, but strawberries aren't."},
            {"fact": "A group of flamingos is called a flamboyance."},
        ]
        unused_facts = [f for f in local_facts if f["fact"] not in previous_facts]
        if unused_facts:
            import random
            new_fact = random.choice(unused_facts)
        else:
            raise RuntimeError("No unique facts available from API or local fallback.")
    timestamp = datetime.now().isoformat()
    db.update_daily_facts({timestamp: {"fact": new_fact["fact"], "timestamp": timestamp}})
    db.export_compressed_data()
    print(f"[NEW-FACT] Added fact for {today}: {new_fact['fact']}")
    return {"fact": new_fact["fact"], "timestamp": timestamp}

if __name__ == "__main__":
    # Test the daily facts module
    print("🧪 Testing Daily Facts Module")
    print("=" * 40)
    
    # Test different categories
    categories = ["random", "food", "time", "countries", "general"]
    
    for category in categories:
        print(f"\n📡 Fetching {category} daily fact...")
        result = get_daily_fact()
        print(f"✅ {result['fact']}")
        print(f"   Source: {result['source']}")
        print(f"   Category: {result['category']}")
    
    # Test today's fact
    print(f"\n📅 Today's fact:")
    today_fact = get_todays_fact()
    print(f"✅ {today_fact['fact']}")
    print(f"   Date: {today_fact['timestamp'][:10]}")
    print(f"   Source: {today_fact['source']}") 