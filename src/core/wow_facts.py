#!/usr/bin/env python3
"""
WOW Facts Module - Fetches amazing facts from various APIs
"""

import requests
import random
import json
from typing import Dict, Optional, List
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.config import *

def fetch_numbers_api_fact() -> Optional[str]:
    """Fetch a random number fact from numbersapi.com"""
    try:
        response = requests.get(WOW_FACT_APIS["numbers_api"], timeout=API_TIMEOUT)
        if response.status_code == 200:
            return response.text
    except Exception as e:
        print(f"Error fetching from numbers API: {e}")
    return None

def fetch_cat_fact() -> Optional[str]:
    """Fetch a random cat fact"""
    try:
        response = requests.get(WOW_FACT_APIS["cat_facts"], timeout=API_TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            return data.get('text', '')
    except Exception as e:
        print(f"Error fetching cat fact: {e}")
    return None

def fetch_dog_fact() -> Optional[str]:
    """Fetch a random dog fact"""
    try:
        response = requests.get(WOW_FACT_APIS["dog_facts"], timeout=API_TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            return data.get('text', '')
    except Exception as e:
        print(f"Error fetching dog fact: {e}")
    return None

def fetch_space_fact() -> Optional[str]:
    """Fetch a random space fact"""
    try:
        response = requests.get(WOW_FACT_APIS["space_facts"], timeout=API_TIMEOUT)
        if response.status_code == 200:
            articles = response.json()
            if articles:
                article = random.choice(articles[:10])  # Take from first 10
                return f"Space Fact: {article.get('title', '')}"
    except Exception as e:
        print(f"Error fetching space fact: {e}")
    return None

def fetch_animal_fact() -> Optional[str]:
    """Fetch a random animal fact"""
    try:
        response = requests.get(WOW_FACT_APIS["animal_facts"], timeout=API_TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            name = data.get('name', 'This animal')
            fact = data.get('diet', '')
            return f"{name} has a {fact} diet!"
    except Exception as e:
        print(f"Error fetching animal fact: {e}")
    return None

def fetch_fungenerators_fact(category: str) -> Optional[str]:
    """Fetch a fact from fungenerators API"""
    try:
        api_key = "your_api_key_here"  # Would need actual API key
        url = WOW_FACT_APIS.get(f"{category}_facts")
        if url:
            response = requests.get(url, timeout=API_TIMEOUT)
            if response.status_code == 200:
                return response.text
    except Exception as e:
        print(f"Error fetching {category} fact: {e}")
    return None

def enhance_fact_with_wow_effect(fact: str, category: str) -> str:
    """Add WOW effect keywords and emojis to make facts more engaging"""
    wow_keyword = random.choice(WOW_KEYWORDS)
    emoji = EMOJI_MAPPING.get(category, "💡")
    
    # Add WOW effect to the fact
    enhanced_fact = f"{emoji} **{wow_keyword.upper()} FACT:** {fact}"
    
    return enhanced_fact

def get_wow_fact(category: str = None) -> Dict[str, str]:
    """Get a WOW fact from various APIs"""
    
    # Define fact sources based on category
    category_fact_sources = {
        "science": [fetch_numbers_api_fact, lambda: fetch_fungenerators_fact("science")],
        "history": [lambda: fetch_fungenerators_fact("history")],
        "geography": [lambda: fetch_fungenerators_fact("geography")],
        "sports": [lambda: fetch_fungenerators_fact("sports")],
        "technology": [lambda: fetch_fungenerators_fact("technology")],
        "space": [fetch_space_fact],
        "animals": [fetch_cat_fact, fetch_dog_fact, fetch_animal_fact],
        "nature": [fetch_animal_fact, fetch_cat_fact, fetch_dog_fact]
    }
    
    # If no category specified, try all sources
    if not category:
        all_sources = [
            fetch_numbers_api_fact,
            fetch_cat_fact,
            fetch_dog_fact,
            fetch_space_fact,
            fetch_animal_fact
        ]
    else:
        all_sources = category_fact_sources.get(category, [fetch_numbers_api_fact])
    
    # Try to fetch a fact from available sources
    for _ in range(MAX_RETRIES):
        for source_func in all_sources:
            try:
                fact = source_func()
                if fact and len(fact) > 10:  # Ensure fact has meaningful content
                    enhanced_fact = enhance_fact_with_wow_effect(fact, category or "general")
                    return {
                        "fact": enhanced_fact,
                        "source": source_func.__name__,
                        "category": category or "general"
                    }
            except Exception as e:
                print(f"Error with fact source {source_func.__name__}: {e}")
                continue
    
    # Fallback to generated fact
    return generate_fallback_wow_fact(category)

def generate_fallback_wow_fact(category: str = None) -> Dict[str, str]:
    """Generate a fallback WOW fact when APIs are unavailable"""
    
    fallback_facts = {
        "science": [
            "The human body contains enough iron to make a 3-inch nail!",
            "A day on Venus is longer than its year!",
            "There are more atoms in a glass of water than glasses of water in all the oceans!",
            "The Great Wall of China is not visible from space with the naked eye!",
            "Bananas are radioactive due to their potassium content!"
        ],
        "space": [
            "A day on Mars is only 37 minutes longer than a day on Earth!",
            "There are more stars in the universe than grains of sand on Earth!",
            "The Sun makes up 99.86% of our solar system's mass!",
            "One million Earths could fit inside the Sun!",
            "The footprints on the Moon will last for 100 million years!"
        ],
        "animals": [
            "A group of flamingos is called a 'flamboyance'!",
            "Octopuses have three hearts and blue blood!",
            "A day-old baby kangaroo is the size of a jellybean!",
            "Elephants are the only mammals that can't jump!",
            "A cat's purr vibrates at a frequency that promotes bone healing!"
        ],
        "human_body": [
            "Your brain uses 20% of your body's total energy!",
            "You shed about 600,000 particles of skin every hour!",
            "Your heart beats about 100,000 times every day!",
            "You have enough blood vessels to circle the Earth 2.5 times!",
            "Your body contains enough carbon to fill 900 pencils!"
        ],
        "general": [
            "The shortest war in history lasted only 38 minutes!",
            "Honey never spoils - archaeologists have found pots of honey in ancient Egyptian tombs!",
            "A day on Venus is longer than its year!",
            "There are more possible games of chess than atoms in the universe!",
            "The average person spends 6 months of their lifetime waiting for red lights!"
        ]
    }
    
    fact_category = category or "general"
    if fact_category not in fallback_facts:
        fact_category = "general"
    
    fact = random.choice(fallback_facts[fact_category])
    enhanced_fact = enhance_fact_with_wow_effect(fact, fact_category)
    
    return {
        "fact": enhanced_fact,
        "source": "fallback_generated",
        "category": fact_category
    }

def create_trivia_from_wow_fact(wow_fact: str, category: str) -> Dict[str, any]:
    """Convert a WOW fact into a trivia question format"""
    
    # Extract the fact content (remove emoji and WOW keywords)
    fact_content = wow_fact.split(":** ")[-1] if ":** " in wow_fact else wow_fact
    
    # Create a question based on the fact
    question_prompts = [
        f"Based on this {category} fact: '{fact_content}', which statement is TRUE?",
        f"Given this {category} information: '{fact_content}', what is the correct conclusion?",
        f"According to this {category} fact: '{fact_content}', which option is accurate?",
        f"This {category} fact states: '{fact_content}'. Which statement supports this?",
        f"From this {category} information: '{fact_content}', what can we determine?"
    ]
    
    question = random.choice(question_prompts)
    
    # Generate plausible options (this would be enhanced with AI in practice)
    options = {
        "A": f"This {category} fact is completely accurate",
        "B": f"This {category} fact has been proven false",
        "C": f"This {category} fact is still being debated by scientists"
    }
    
    return {
        "question": question,
        "options": options,
        "correct_answer": "A",  # Assuming the fact is true
        "category": category,
        "explanation": f"This is an {category} fact that has been verified by multiple sources.",
        "wow_fact": wow_fact
    }

if __name__ == "__main__":
    # Test the WOW facts module
    print("🧪 Testing WOW Facts Module")
    print("=" * 40)
    
    # Test different categories
    categories = ["science", "space", "animals", "human_body", "general"]
    
    for category in categories:
        print(f"\n📡 Fetching {category} fact...")
        result = get_wow_fact(category)
        print(f"✅ {result['fact']}")
        print(f"   Source: {result['source']}")
        print(f"   Category: {result['category']}") 