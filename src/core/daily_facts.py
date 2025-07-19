#!/usr/bin/env python3
"""
Daily Facts Module - Fetches interesting daily facts for "Did You Know?" section
"""

import requests
import random
import json
import os
from datetime import datetime
from typing import Dict, Optional, List
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.config import *

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

def fetch_joke_fact() -> Optional[str]:
    """Fetch a joke that could be educational"""
    try:
        response = requests.get(DAILY_FACT_SOURCES["joke_facts"], timeout=API_TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            if data.get('type') == 'single':
                return data.get('joke', '')
            elif data.get('type') == 'twopart':
                setup = data.get('setup', '')
                delivery = data.get('delivery', '')
                return f"{setup} {delivery}"
    except Exception as e:
        print(f"Error fetching joke fact: {e}")
    return None

def fetch_quote_fact() -> Optional[str]:
    """Fetch an inspiring quote"""
    try:
        response = requests.get(DAILY_FACT_SOURCES["quote_facts"], timeout=API_TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            quote = data.get('content', '')
            author = data.get('author', 'Unknown')
            return f'"{quote}" - {author}'
    except Exception as e:
        print(f"Error fetching quote fact: {e}")
    return None

def fetch_food_fact() -> Optional[str]:
    """Fetch a random food fact"""
    try:
        response = requests.get(DAILY_FACT_SOURCES["food_facts"], timeout=API_TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            meal = data.get('meals', [{}])[0]
            name = meal.get('strMeal', 'This dish')
            category = meal.get('strCategory', 'food')
            return f"{name} is a {category} that originated from {meal.get('strArea', 'unknown region')}!"
    except Exception as e:
        print(f"Error fetching food fact: {e}")
    return None

def fetch_time_fact() -> Optional[str]:
    """Fetch an interesting time-related fact"""
    try:
        # Get current time in a random timezone
        timezones = ["America/New_York", "Europe/London", "Asia/Tokyo", "Australia/Sydney"]
        timezone = random.choice(timezones)
        response = requests.get(f"{DAILY_FACT_SOURCES['time_facts']}{timezone}", timeout=API_TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            datetime_str = data.get('datetime', '')
            timezone_name = data.get('timezone', '')
            return f"Right now in {timezone_name}, it's {datetime_str[:19]}!"
    except Exception as e:
        print(f"Error fetching time fact: {e}")
    return None

def fetch_country_fact() -> Optional[str]:
    """Fetch a random country fact"""
    try:
        countries = ["japan", "brazil", "egypt", "australia", "iceland", "madagascar"]
        country = random.choice(countries)
        response = requests.get(f"{DAILY_FACT_SOURCES['country_facts']}{country}", timeout=API_TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            if data:
                country_data = data[0]
                name = country_data.get('name', {}).get('common', country.title())
                capital = country_data.get('capital', ['Unknown'])[0]
                population = country_data.get('population', 0)
                return f"{name}'s capital is {capital} and has a population of {population:,} people!"
    except Exception as e:
        print(f"Error fetching country fact: {e}")
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

def get_daily_fact(category: str = None) -> Dict[str, str]:
    """Get a daily fact from various sources"""
    
    # Define fact sources based on category
    category_fact_sources = {
        "random": [fetch_random_fact, fetch_joke_fact, fetch_quote_fact],
        "food": [fetch_food_fact],
        "time": [fetch_time_fact],
        "countries": [fetch_country_fact],
        "general": [fetch_random_fact, fetch_joke_fact, fetch_quote_fact, fetch_food_fact]
    }
    
    # If no category specified, try all sources
    if not category:
        all_sources = [
            fetch_random_fact,
            fetch_joke_fact,
            fetch_quote_fact,
            fetch_food_fact,
            fetch_time_fact,
            fetch_country_fact
        ]
    else:
        all_sources = category_fact_sources.get(category, [fetch_random_fact])
    
    # Try to fetch a fact from available sources
    for _ in range(MAX_RETRIES):
        for source_func in all_sources:
            try:
                fact = source_func()
                if fact and len(fact) > 10 and len(fact) < 200:  # Ensure fact has meaningful content and isn't too long
                    # Choose a random template
                    template = random.choice(DAILY_FACT_TEMPLATES)
                    formatted_fact = template.format(fact=fact)
                    
                    return {
                        "fact": formatted_fact,
                        "source": source_func.__name__,
                        "category": category or "general",
                        "raw_fact": fact
                    }
            except Exception as e:
                print(f"Error with fact source {source_func.__name__}: {e}")
                continue
    
    # Fallback to generated fact
    fallback_fact = generate_fallback_daily_fact()
    template = random.choice(DAILY_FACT_TEMPLATES)
    formatted_fact = template.format(fact=fallback_fact)
    
    return {
        "fact": formatted_fact,
        "source": "fallback_generated",
        "category": category or "general",
        "raw_fact": fallback_fact
    }

def load_daily_facts():
    """Load existing daily facts data"""
    if os.path.exists(DAILY_FACTS_FILE):
        with open(DAILY_FACTS_FILE, 'r') as f:
            return json.load(f)
    return {"current": None, "history": []}

def save_daily_facts(daily_facts_data):
    """Save daily facts data to file"""
    with open(DAILY_FACTS_FILE, 'w') as f:
        json.dump(daily_facts_data, f, indent=2)

def get_todays_fact() -> Dict[str, str]:
    """Get today's fact, generating a new one if needed"""
    daily_facts_data = load_daily_facts()
    today = datetime.now().strftime(DATE_FORMAT)
    
    current_fact = daily_facts_data.get("current")
    
    # Check if we already have a fact for today
    if current_fact and current_fact.get("date") == today:
        return current_fact
    
    # Move current fact to history if it exists
    if current_fact:
        current_fact["date"] = today
        daily_facts_data["history"].append(current_fact)
    
    # Generate new fact
    new_fact = get_daily_fact()
    new_fact["date"] = today
    
    # Save to data
    daily_facts_data["current"] = new_fact
    save_daily_facts(daily_facts_data)
    
    return new_fact

if __name__ == "__main__":
    # Test the daily facts module
    print("🧪 Testing Daily Facts Module")
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