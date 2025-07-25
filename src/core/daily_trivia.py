#!/usr/bin/env python3
"""
Interactive AI-Powered Trivia GitHub Profile
Generates daily trivia questions using OpenAI and WOW facts from APIs
"""

import json
import os
import random
from datetime import datetime, timedelta, timezone
from openai import OpenAI
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.config import *
from core.daily_facts import get_todays_fact
from core.database import TriviaDatabase
from core.points_system import get_streak_emoji, format_points_display
import difflib
from typing import Dict
import logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

def get_utc_today():
    return datetime.now(timezone.utc).strftime(DATE_FORMAT)

def get_utc_yesterday():
    return (datetime.now(timezone.utc) - timedelta(days=1)).strftime(DATE_FORMAT)

def setup_openai():
    """Initialize OpenAI client"""
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    return OpenAI(api_key=OPENAI_API_KEY)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=2, max=10), retry=retry_if_exception_type(Exception))
def openai_with_retries(client, *args, **kwargs):
    try:
        resp = client.chat.completions.create(*args, **kwargs)
        # OpenAI returns errors as exceptions, but check for rate limit in response if present
        if hasattr(resp, 'status_code') and resp.status_code == 429:
            logging.error("[daily_trivia.py] [openai_with_retries] OpenAI API rate limit hit (429). Retrying...")
        return resp
    except Exception as e:
        if 'rate limit' in str(e).lower() or '429' in str(e):
            logging.error("[daily_trivia.py] [openai_with_retries] OpenAI API rate limit hit (429). Retrying...")
        elif '5' in str(e) and 'server' in str(e).lower():
            logging.error(f"[daily_trivia.py] [openai_with_retries] OpenAI API server error. Retrying...")
        else:
            logging.error(f"[daily_trivia.py] [openai_with_retries] Exception: {e}")
        raise

def generate_trivia_question():
    """Generate a trivia question using OpenAI"""
    category = random.choice(TRIVIA_CATEGORIES)
    correct_letter = random.choice(["A", "B", "C"])
    prompt = f"""Generate an INCREDIBLE standalone trivia question about {category}. 

    Requirements:
    - Create a completely original question NOT based on any specific fact
    - Make the question AMAZING and mind-blowing
    - Question should be engaging and create a strong effect
    - Provide exactly 3 multiple choice options (A, B, C)
    - The correct answer must be option {correct_letter}
    - Make the incorrect options plausible but wrong
    - Keep the question and answers concise but fascinating
    - Use exciting language to make it engaging
    - DO NOT reference any specific fact or say "Based on this fact"
    
    Format your response as JSON:
    {{
        "question": "Your AMAZING standalone question here?",
        "options": {{
            "A": "First option",
            "B": "Second option", 
            "C": "Third option"
        }},
        "correct_answer": "{correct_letter}",
        "category": "{category}",
        "explanation": "FASCINATING explanation of why the answer is correct"
    }}
    
    Only return the JSON, no other text."""
    try:
        client = setup_openai()
        try:
            response = openai_with_retries(
                client,
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE
            )
        except Exception as e:
            logging.error("[daily_trivia.py] [generate_trivia_question] OpenAI API failed after retries: %s", e)
            raise
        content = response.choices[0].message.content.strip()
        # Robustly extract JSON from response
        import re
        def extract_json(text):
            # Try to find the first {...} block
            match = re.search(r'\{[\s\S]*\}', text)
            if match:
                try:
                    return json.loads(match.group(0))
                except Exception as e:
                    logging.error(f"[daily_trivia.py] [generate_trivia_question] JSON extraction failed: {e}")
            raise ValueError("No valid JSON found in OpenAI response")
        try:
            trivia_data = extract_json(content)
        except Exception as e:
            logging.error(f"[daily_trivia.py] [generate_trivia_question] Could not extract valid JSON: {e}\nRaw content: {content}")
            raise
        return trivia_data
    except Exception as e:
        logging.error("[daily_trivia.py] [generate_trivia_question] Failed to generate trivia: %s", e)
        sys.exit(1)

def create_standalone_trivia(category):
    """Create standalone trivia question without being based on facts"""
    category_questions = {
        "space": {
            "question": "What is the largest planet in our solar system?",
            "options": {"A": "Jupiter", "B": "Saturn", "C": "Neptune"},
            "correct_answer": "A",
            "category": "space",
            "explanation": "Jupiter is the largest planet in our solar system, with a mass more than twice that of Saturn."
        },
        "science": {
            "question": "What is the chemical symbol for gold?",
            "options": {"A": "Au", "B": "Ag", "C": "Fe"},
            "correct_answer": "A",
            "category": "science",
            "explanation": "Au comes from the Latin word 'aurum' which means gold."
        },
        "animals": {
            "question": "Which animal has the longest lifespan?",
            "options": {"A": "Greenland Shark", "B": "Giant Tortoise", "C": "Bowhead Whale"},
            "correct_answer": "A",
            "category": "animals",
            "explanation": "Greenland sharks can live for over 400 years, making them the longest-living vertebrates."
        },
        "human_body": {
            "question": "How many bones are in the adult human body?",
            "options": {"A": "206", "B": "212", "C": "198"},
            "correct_answer": "A",
            "category": "human_body",
            "explanation": "The adult human body has exactly 206 bones."
        },
        "general": {
            "question": "What year did the first iPhone launch?",
            "options": {"A": "2007", "B": "2005", "C": "2009"},
            "correct_answer": "A",
            "category": "general",
            "explanation": "The first iPhone was launched by Apple in 2007."
        },
        "history": {
            "question": "Who was the first President of the United States?",
            "options": {"A": "George Washington", "B": "Thomas Jefferson", "C": "Abraham Lincoln"},
            "correct_answer": "A",
            "category": "history",
            "explanation": "George Washington served as the first U.S. President from 1789 to 1797."
        },
        "geography": {
            "question": "What is the longest river in the world?",
            "options": {"A": "Nile", "B": "Amazon", "C": "Yangtze"},
            "correct_answer": "A",
            "category": "geography",
            "explanation": "The Nile River is generally regarded as the longest river in the world."
        },
        "literature": {
            "question": "Who wrote 'Romeo and Juliet'?",
            "options": {"A": "William Shakespeare", "B": "Jane Austen", "C": "Charles Dickens"},
            "correct_answer": "A",
            "category": "literature",
            "explanation": "William Shakespeare is the author of 'Romeo and Juliet'."
        },
        "sports": {
            "question": "Which country won the FIFA World Cup in 2018?",
            "options": {"A": "France", "B": "Brazil", "C": "Germany"},
            "correct_answer": "A",
            "category": "sports",
            "explanation": "France won the 2018 FIFA World Cup."
        },
        "entertainment": {
            "question": "Who played Iron Man in the Marvel Cinematic Universe?",
            "options": {"A": "Robert Downey Jr.", "B": "Chris Evans", "C": "Mark Ruffalo"},
            "correct_answer": "A",
            "category": "entertainment",
            "explanation": "Robert Downey Jr. played Tony Stark/Iron Man."
        },
        "technology": {
            "question": "What does 'HTTP' stand for?",
            "options": {"A": "HyperText Transfer Protocol", "B": "High Tech Transfer Protocol", "C": "Hyperlink Transfer Protocol"},
            "correct_answer": "A",
            "category": "technology",
            "explanation": "HTTP stands for HyperText Transfer Protocol."
        },
        "nature": {
            "question": "What is the tallest type of grass?",
            "options": {"A": "Bamboo", "B": "Wheat", "C": "Sugarcane"},
            "correct_answer": "A",
            "category": "nature",
            "explanation": "Bamboo is the tallest type of grass, with some species growing over 30 meters tall."
        },
        "art": {
            "question": "Who painted the Mona Lisa?",
            "options": {"A": "Leonardo da Vinci", "B": "Vincent van Gogh", "C": "Pablo Picasso"},
            "correct_answer": "A",
            "category": "art",
            "explanation": "Leonardo da Vinci painted the Mona Lisa."
        },
        "music": {
            "question": "Which composer became deaf later in life but continued to compose music?",
            "options": {"A": "Ludwig van Beethoven", "B": "Wolfgang Amadeus Mozart", "C": "Johann Sebastian Bach"},
            "correct_answer": "A",
            "category": "music",
            "explanation": "Beethoven composed some of his greatest works after losing his hearing."
        },
        "oceans": {
            "question": "What is the largest ocean on Earth?",
            "options": {"A": "Pacific Ocean", "B": "Atlantic Ocean", "C": "Indian Ocean"},
            "correct_answer": "A",
            "category": "oceans",
            "explanation": "The Pacific Ocean is the largest ocean on Earth."
        },
        "mountains": {
            "question": "What is the highest mountain in the world?",
            "options": {"A": "Mount Everest", "B": "K2", "C": "Kangchenjunga"},
            "correct_answer": "A",
            "category": "mountains",
            "explanation": "Mount Everest is the highest mountain above sea level."
        },
        "inventions": {
            "question": "Who invented the telephone?",
            "options": {"A": "Alexander Graham Bell", "B": "Thomas Edison", "C": "Nikola Tesla"},
            "correct_answer": "A",
            "category": "inventions",
            "explanation": "Alexander Graham Bell is credited with inventing the telephone."
        },
        "discoveries": {
            "question": "Who discovered penicillin?",
            "options": {"A": "Alexander Fleming", "B": "Marie Curie", "C": "Louis Pasteur"},
            "correct_answer": "A",
            "category": "discoveries",
            "explanation": "Alexander Fleming discovered penicillin in 1928."
        },
        "records": {
            "question": "What is the fastest land animal?",
            "options": {"A": "Cheetah", "B": "Lion", "C": "Pronghorn"},
            "correct_answer": "A",
            "category": "records",
            "explanation": "The cheetah is the fastest land animal, capable of speeds up to 70 mph (113 km/h)."
        },
        "extremes": {
            "question": "What is the hottest planet in our solar system?",
            "options": {"A": "Venus", "B": "Mercury", "C": "Mars"},
            "correct_answer": "A",
            "category": "extremes",
            "explanation": "Venus is the hottest planet due to its thick, heat-trapping atmosphere."
        },
        "mysteries": {
            "question": "What is the name of the mysterious area in the western part of the North Atlantic Ocean where ships and planes have disappeared?",
            "options": {"A": "Bermuda Triangle", "B": "Devil's Sea", "C": "Sargasso Sea"},
            "correct_answer": "A",
            "category": "mysteries",
            "explanation": "The Bermuda Triangle is famous for mysterious disappearances of ships and planes."
        }
    }
    # Get question for category or use general as fallback
    return category_questions.get(category, category_questions["general"])

def load_trivia_data():
    """Load existing trivia data from database (timestamp-only schema)"""
    try:
        db = TriviaDatabase()
        trivia_questions = db.get_trivia_questions()
        today = datetime.now().strftime('%Y-%m-%d')
        current = None
        history = []
        for timestamp, question_data in trivia_questions.items():
            # Compare date part of timestamp
            if question_data['timestamp'][:10] == today:
                current = question_data
            else:
                history.append(question_data)
        return {"current": current, "history": history}
    except Exception as e:
        logging.error("[daily_trivia.py] [load_trivia_data] Error loading trivia data from database: %s", e)
        return {"current": None, "history": []}

def save_trivia_data(trivia_data):
    """
    Save trivia data to database (timestamp-only schema).
    MUST be called after any change to trivia data to ensure the database and exported compressed file are up to date.
    The README updater always loads from the latest DB state.
    """
    try:
        db = TriviaDatabase()
        trivia_questions = {}
        # Ensure 'timestamp' exists for current trivia
        if trivia_data.get("current"):
            current = trivia_data["current"]
            if "timestamp" not in current:
                current["timestamp"] = datetime.now().isoformat()
            trivia_questions[current["timestamp"]] = current
        # Ensure 'timestamp' exists for all history trivia
        for q in trivia_data.get("history", []):
            if "timestamp" not in q:
                q["timestamp"] = datetime.now().isoformat()
            trivia_questions[q["timestamp"]] = q
        db.update_trivia_questions(trivia_questions)
        # db.export_compressed_data()  # Removed: export should be explicit in workflow
    except Exception as e:
        logging.error("[daily_trivia.py] [save_trivia_data] Error saving trivia data to database: %s", e)

def load_leaderboard():
    """Load leaderboard data from database"""
    try:
        db = TriviaDatabase()
        return db.get_leaderboard()
    except Exception as e:
        logging.error("[daily_trivia.py] [load_leaderboard] Error loading leaderboard from database: %s", e)
        # Return empty leaderboard as fallback
        return {}

def save_leaderboard(leaderboard):
    """
    Save leaderboard data to database.
    MUST be called after any change to leaderboard data to ensure the database and exported compressed file are up to date.
    The README updater always loads from the latest DB state.
    """
    try:
        db = TriviaDatabase()
        db.update_leaderboard(leaderboard)
        # db.export_compressed_data()  # Removed: export should be explicit in workflow
    except Exception as e:
        logging.error("[daily_trivia.py] [save_leaderboard] Error saving leaderboard to database: %s", e)

def get_top_leaderboard(leaderboard, max_entries=MAX_LEADERBOARD_ENTRIES):
    """Get top users from leaderboard sorted by points, then streak"""
    sorted_users = sorted(
        leaderboard.items(), 
        key=lambda x: (x[1]['total_points'], x[1]['current_streak'], x[1]['total_correct']), 
        reverse=True
    )
    return sorted_users[:max_entries]

def create_answer_links(trivia_data=None):
    """Create GitHub issue links for answer buttons"""
    import urllib.parse
    
    base_url = f"https://github.com/{GITHUB_USERNAME}/{GITHUB_REPO}"
    
    # Load current trivia to get answer texts if not provided
    if trivia_data is None:
        trivia_data = load_trivia_data()
    current_trivia = trivia_data.get("current", {})
    # Ensure date is set
    trivia_date = current_trivia.get("timestamp")[:10]
    if not trivia_date:
        trivia_date = datetime.now().strftime(DATE_FORMAT)
    options = current_trivia.get("options", {"A": "A", "B": "B", "C": "C"})
    def issue_body(option):
        return urllib.parse.quote(
            ISSUE_TEMPLATE.format(answer_text=options[option]) + f"\n\n**Trivia Date:** {trivia_date}"
        )
    
    return {
        "A": f"{base_url}/issues/new?title=Trivia+Answer+A&body={issue_body('A')}",
        "B": f"{base_url}/issues/new?title=Trivia+Answer+B&body={issue_body('B')}", 
        "C": f"{base_url}/issues/new?title=Trivia+Answer+C&body={issue_body('C')}"
    }

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=2, max=10), retry=retry_if_exception_type(Exception))
def openai_wiki_with_retries(client, *args, **kwargs):
    return client.chat.completions.create(*args, **kwargs)

def get_wikipedia_link(answer_text, question_text):
    """Use OpenAI to get a Wikipedia link for the answer in the context of the question."""
    try:
        client = setup_openai()
        prompt = (
            f"give me a wikipedia link to this answer: {answer_text} for this question: {question_text} "
            "for further reading or support that shows the answer is correct. "
            "Return only the full Wikipedia URL, nothing else."
        )
        try:
            response = openai_wiki_with_retries(
                client,
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.2
            )
        except Exception as e:
            logging.error("[daily_trivia.py] [get_wikipedia_link] OpenAI API failed after retries: %s", e)
            raise
        url = response.choices[0].message.content.strip()
        if url.startswith("http"):
            return url
    except Exception as e:
        logging.error("[daily_trivia.py] [get_wikipedia_link] Error getting Wikipedia link from OpenAI: %s", e)
    # Fallback: heuristic
    import urllib.parse
    clean = str(answer_text).strip().replace(' ', '_')
    return f"https://en.wikipedia.org/wiki/{urllib.parse.quote(clean)}"

def update_readme(trivia_data, leaderboard):
    """
    Update the README with current trivia, daily fact, and leaderboard.
    This function always loads from the latest DB state, so all data must be saved to the DB before calling.
    """
    try:
        # Debug: print loaded data
        logging.debug("[daily_trivia.py] [update_readme] Loaded trivia_data: %s", json.dumps(trivia_data, indent=2, default=str))
        logging.debug("[daily_trivia.py] [update_readme] Loaded leaderboard: %s", json.dumps(leaderboard, indent=2, default=str))
        from core.daily_facts import load_daily_facts
        fact_data = load_daily_facts()
        logging.debug("[daily_trivia.py] [update_readme] Loaded fact_data: %s", json.dumps(fact_data, indent=2, default=str))
        today = datetime.now().strftime(DATE_FORMAT)
        current_trivia = trivia_data.get("current")
        if not current_trivia:
            return
        daily_fact = get_todays_fact()
        answer_links = create_answer_links(trivia_data)
        top_users = get_top_leaderboard(leaderboard)
        category = current_trivia.get('category', 'general')
        emoji = EMOJI_MAPPING.get(category, "💡")
        yesterday_stats = ""
        yesterday_date = get_utc_yesterday()
        yesterday_trivia = None
        for t in reversed(trivia_data.get("history", [])):
            if t.get("timestamp")[:10] == yesterday_date:
                yesterday_trivia = t
                break
        if yesterday_trivia:
            question = yesterday_trivia['question']
            correct_letter = yesterday_trivia['correct_answer']
            correct_text = yesterday_trivia['options'][correct_letter]
            explanation = yesterday_trivia['explanation']
            wiki_link = get_wikipedia_link(correct_text, question)
            yesterday_stats = YESTERDAY_STATS_TEMPLATE.format(
                yesterday_date=yesterday_date,
                question=question,
                correct_letter=correct_letter,
                correct_text=correct_text,
                wiki_link=wiki_link,
                explanation=explanation
            )
        # Leaderboard rows
        leaderboard_rows = ""
        for i, (username, stats) in enumerate(top_users, 1):
            streak_emoji = get_streak_emoji(stats['current_streak'])
            points_display = format_points_display(stats['total_points'])
            day_joined = stats.get('first_correct_date', '-') or '-'
            leaderboard_rows += f"| {i} | @{username} | {streak_emoji} {stats['current_streak']} | {points_display} | \u2705 {stats['total_correct']} | {day_joined} |\n"
        no_participants_row = ""
        if not top_users:
            no_participants_row = "| - | *No participants yet* | - | - | - | - |\n"
        # How to play and points system
        how_to_play = HOW_TO_PLAY_TEMPLATE
        points_system = POINTS_SYSTEM_TEMPLATE.format(max_leaderboard_entries=MAX_LEADERBOARD_ENTRIES)
        # README content
        readme_content = README_TEMPLATE.format(
            today=today,
            daily_fact=daily_fact['fact'],
            question=current_trivia['question'],
            answer_link_a=answer_links['A'],
            answer_link_b=answer_links['B'],
            answer_link_c=answer_links['C'],
            option_a=current_trivia['options']['A'],
            option_b=current_trivia['options']['B'],
            option_c=current_trivia['options']['C'],
            leaderboard_rows=leaderboard_rows,
            no_participants_row=no_participants_row,
            yesterday_stats=yesterday_stats,
            how_to_play=how_to_play,
            points_system=points_system
        )
        readme_path = "README.md"
        old_content = ""
        if os.path.exists(readme_path):
            with open(readme_path, "r") as f:
                old_content = f.read()
        with open(readme_path, "w") as f:
            f.write(readme_content)
        # Debug: print what changed
        if old_content != readme_content:
            logging.info("[daily_trivia.py] [update_readme] README.md has changed. Diff summary:")
            diff = difflib.unified_diff(
                old_content.splitlines(),
                readme_content.splitlines(),
                fromfile='README.md (old)',
                tofile='README.md (new)',
                lineterm=''
            )
            for line in diff:
                logging.info(line)
            logging.info("[daily_trivia.py] [update_readme] README updated.")
        else:
            logging.info("[daily_trivia.py] [update_readme] README.md is unchanged.")
            logging.info("[daily_trivia.py] [update_readme] No update needed.")
    except Exception as e:
        logging.error("[daily_trivia.py] [update_readme] Error in update_readme: %s", e)
        import traceback
        traceback.print_exc()

def generate_unique_trivia(current_trivia, max_tries=3):
    tried_categories = set()
    for attempt in range(max_tries):
        trivia = generate_trivia_question()
        if not current_trivia or trivia['question'] != current_trivia.get('question'):
            return trivia
        tried_categories.add(trivia['category'])
        # Remove tried category from pool for next attempt
        available = [c for c in TRIVIA_CATEGORIES if c not in tried_categories]
        if available:
            # Force next category for fallback
            trivia = create_standalone_trivia(random.choice(available))
            if not current_trivia or trivia['question'] != current_trivia.get('question'):
                return trivia
    logging.warning("⚠️ Could not generate unique trivia after several attempts.")
    return trivia  # Return last tried

# --- For daily facts ---
from core.daily_facts import load_daily_facts, save_daily_facts, get_daily_fact

def get_todays_fact() -> Dict[str, str]:
    """Get today's fact, generating a new one if needed, ensuring uniqueness. Never override if exists."""
    daily_facts_data = load_daily_facts()
    today = datetime.now().strftime(DATE_FORMAT)
    # Check if we already have a fact for today
    if today in daily_facts_data:
        fact = daily_facts_data[today]
        logging.info(f"🌞 Fact for today ({today}) already exists:")
        logging.info(f"    {fact['fact']}")
        logging.info(f"    (added at {fact.get('timestamp', 'unknown time')})")
        return fact
    # Only fetch if not exists
    previous_facts = set(fact_data['fact'] for date, fact_data in daily_facts_data.items())
    attempts = 0
    max_api_attempts = 2
    new_fact = None
    for attempt in range(max_api_attempts):
        candidate = get_daily_fact()
        if candidate["fact"] not in previous_facts:
            new_fact = candidate
            break
        attempts += 1
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
    daily_facts_data[today] = {
        "fact": new_fact["fact"],
        "timestamp": datetime.now().isoformat()
    }
    save_daily_facts(daily_facts_data)
    logging.info(f"[NEW-FACT] Added fact for {today}: {new_fact['fact']}")
    return daily_facts_data[today]

# --- For trivia ---
def main():
    print("🎯 Generating daily trivia and daily fact...")
    db = TriviaDatabase()
    trivia_questions = db.get_trivia_questions()
    today = datetime.now().strftime('%Y-%m-%d')
    logging.info(f"[DEBUG] Checking for existing trivia for today: {today}")
    found_today = False
    for t in trivia_questions.values():
        logging.debug(f"[DEBUG] Trivia entry: timestamp={t.get('timestamp')}, question={t.get('question')}")
        if t.get('timestamp', '')[:10] == today:
            logging.debug(f"[DEBUG] Found trivia for today: {t.get('question')} (timestamp: {t.get('timestamp')})")
            found_today = True
    # Check if trivia for today exists
    trivia_changed = False
    if trivia_questions:
        latest = max(trivia_questions.values(), key=lambda t: t.get('timestamp', ''))
        latest_date = latest['timestamp'][:10]
        logging.debug(f"[DEBUG] Latest trivia timestamp: {latest['timestamp']}, date: {latest_date}")
        if latest_date == today:
            logging.info(f"🌞 Trivia for today ({today}) already exists:")
            logging.info(f"    {latest['question']}")
            logging.info(f"    (category: {latest.get('category', 'unknown')})")
            logging.info(f"    (added at {latest['timestamp']})")
        else:
            logging.debug(f"[DEBUG] No trivia for today, will generate new.")
            logging.info("🔄 Generating new trivia question...")
            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            # Generate new trivia (reuse your existing logic here)
            # ...
            # For demonstration, we'll use a placeholder
            question = "Placeholder question?"
            options = {"A": "Option A", "B": "Option B", "C": "Option C"}
            correct_answer = "A"
            explanation = "Placeholder explanation."
            new_trivia = {
                "question": question,
                "options": options,
                "correct_answer": correct_answer,
                "explanation": explanation
            }
            if "timestamp" not in new_trivia:
                new_trivia["timestamp"] = datetime.now().isoformat()
            save_trivia_data({"current": new_trivia, "history": []})
            db.export_compressed_data()
            logging.info(f"[NEW-TRIVIA] Added trivia for {today}: {question}")
            trivia_changed = True
    else:
        # No trivia at all, so add new
        logging.debug(f"[DEBUG] No trivia in database yet, will generate new.")
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        question = "Placeholder question?"
        options = {"A": "Option A", "B": "Option B", "C": "Option C"}
        correct_answer = "A"
        explanation = "Placeholder explanation."
        new_trivia = {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "explanation": explanation
        }
        if "timestamp" not in new_trivia:
            new_trivia["timestamp"] = datetime.now().isoformat()
        save_trivia_data({"current": new_trivia, "history": []})
        db.export_compressed_data()
        logging.info(f"[NEW-TRIVIA] Added trivia for {today}: {question}")
        trivia_changed = True

    # Fact logic: get_todays_fact already handles skip/fetch logic and updates DB
    fact = get_todays_fact()
    # Only update README if new trivia or fact was added
    if trivia_changed or fact.get('new', False):
        # You may want to set 'new': True in get_todays_fact when a new fact is added
        logging.info("[README] Updating README with new trivia/fact...")
        # update_readme(...)  # Uncomment and fill in as needed
    else:
        logging.info("ℹ️ No update needed; today's trivia and fact already exist.")

if __name__ == "__main__":
    main() 