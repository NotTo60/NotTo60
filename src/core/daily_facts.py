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
import logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=2, max=10), retry=retry_if_exception_type(Exception))
def requests_get_with_retries(*args, **kwargs):
    import requests
    return requests.get(*args, **kwargs)

def fetch_random_fact() -> Optional[str]:
    """Fetch a random fact from uselessfacts API"""
    try:
        response = requests_get_with_retries(DAILY_FACT_SOURCES["random_facts"], timeout=API_TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            return data.get('text', '')
    except Exception as e:
        logging.error("[daily_facts.py] [fetch_random_fact] API failed after retries: %s", e)
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
        "There are more atoms in a glass of water than glasses of water in all the oceans!",
        "The Eiffel Tower can be 15 cm taller during hot days.",
        "Wombat poop is cube-shaped.",
        "The inventor of the Frisbee was turned into a Frisbee after he died.",
        "A group of crows is called a murder.",
        "The unicorn is the national animal of Scotland.",
        "Sloths can hold their breath longer than dolphins can.",
        "The dot over the letter 'i' is called a tittle.",
        "A snail can sleep for three years.",
        "The longest wedding veil was the same length as 63.5 football fields.",
        "Some turtles can breathe through their butts.",
        "The inventor of the microwave only received $2 for his discovery.",
        "A group of porcupines is called a prickle.",
        "The first computer mouse was made of wood.",
        "A jiffy is an actual unit of time.",
        "The world’s largest grand piano was built by a 15-year-old in New Zealand.",
        "The tongue of a blue whale weighs as much as an elephant.",
        "The Twitter bird actually has a name – Larry.",
        "A group of frogs is called an army.",
        "The inventor of the Rubik’s Cube couldn’t solve it for over a month.",
        "The hottest spot on the planet is in Libya.",
        "The inventor of the Super Soaker was a NASA engineer.",
        "A group of owls is called a parliament.",
        "The first oranges weren’t orange.",
        "A group of ferrets is called a business.",
        "The world’s largest desert is not the Sahara, but Antarctica.",
        "Venus is the only planet to spin clockwise.",
        "A group of ravens is called an unkindness.",
        "The inventor of the telephone never called his wife or mother because they were deaf.",
        "A group of flamingos is called a stand.",
        "The only letter not in any U.S. state name is Q.",
        "The first alarm clock could only ring at 4 a.m.",
        "A group of giraffes is called a tower.",
        "The inventor of the trampoline called it a rebound tumbler.",
        "The first person convicted of speeding was going 8 mph.",
        "The world’s largest snowflake was 15 inches wide.",
        "A group of hippos is called a bloat.",
        "The inventor of the lightbulb also invented the phonograph.",
        "The world’s deepest postbox is in Susami Bay, Japan.",
        "A group of jellyfish is called a smack.",
        "The inventor of the Popsicle was 11 years old.",
        "The first webcam watched a coffee pot.",
        "A group of zebras is called a dazzle.",
        "The inventor of the crossword puzzle was a journalist named Arthur Wynne."
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
            logging.error("[daily_facts.py] [get_daily_fact] Error with fetch_random_fact: %s", e)
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
        facts = db.get_daily_facts()
        return facts
    except Exception as e:
        logging.error("[daily_facts.py] [load_daily_facts] Error loading daily facts: %s", e)
        return {}

def save_daily_facts(facts):
    """Save daily facts data to database"""
    try:
        db = TriviaDatabase()
        db.update_daily_facts(facts)
        # db.export_compressed_data()  # Removed: export should be explicit in workflow
    except Exception as e:
        logging.error("[daily_facts.py] [save_daily_facts] Error saving daily facts: %s", e)

def get_todays_fact() -> Dict[str, str]:
    """Get today's fact, generating a new one if needed, ensuring uniqueness. Never override if exists."""
    today = datetime.now().strftime("%Y-%m-%d")
    facts = load_daily_facts()
    if today in facts:
        fact = facts[today]
        logging.info("[daily_facts.py] [get_todays_fact] Fact for today (%s) already exists: %s (added at %s)", today, fact.get('fact'), fact.get('timestamp'))
        return fact
    logging.info("[daily_facts.py] [get_todays_fact] No fact for today, will fetch new.")
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
    # Save using today as the key and timestamp
    db = TriviaDatabase()
    db.update_daily_facts({today: {"fact": new_fact["fact"], "timestamp": today}})
    logging.info("[daily_facts.py] [get_todays_fact] Added fact for %s: %s", today, new_fact['fact'])
    return {"fact": new_fact["fact"], "timestamp": today}

if __name__ == "__main__":
    # Test the daily facts module
    logging.info("🧪 Testing Daily Facts Module")
    logging.info("=" * 40)
    
    # Test different categories
    categories = ["random", "food", "time", "countries", "general"]
    
    for category in categories:
        logging.info("\n📡 Fetching %s daily fact...", category)
        result = get_daily_fact()
        logging.info("✅ %s", result['fact'])
        logging.info("   Source: %s", result['source'])
        logging.info("   Category: %s", result['category'])
    
    # Test today's fact
    logging.info("\n📅 Today's fact:")
    today_fact = get_todays_fact()
    logging.info("✅ %s", today_fact['fact'])
    logging.info("   Date: %s", today_fact['timestamp'][:10])
    if 'source' in today_fact:
        logging.info("   Source: %s", today_fact['source']) 