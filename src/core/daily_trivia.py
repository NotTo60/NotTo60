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

def get_utc_today():
    return datetime.now(timezone.utc).strftime(DATE_FORMAT)

def get_utc_yesterday():
    return (datetime.now(timezone.utc) - timedelta(days=1)).strftime(DATE_FORMAT)

def setup_openai():
    """Initialize OpenAI client"""
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    return OpenAI(api_key=OPENAI_API_KEY)

def generate_trivia_question():
    """Generate a trivia question using OpenAI"""
    category = random.choice(TRIVIA_CATEGORIES)
    prompt = f"""Generate an INCREDIBLE standalone trivia question about {category}. 

    Requirements:
    - Create a completely original question NOT based on any specific fact
    - Make the question AMAZING and mind-blowing
    - Question should be engaging and create a strong effect
    - Provide exactly 3 multiple choice options (A, B, C)
    - One option must be correct
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
        "correct_answer": "A",
        "category": "{category}",
        "explanation": "FASCINATING explanation of why the answer is correct"
    }}
    
    Only return the JSON, no other text."""
    try:
        client = setup_openai()
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE
        )
        content = response.choices[0].message.content.strip()
        # Extract JSON from response
        if content.startswith('```json'):
            content = content[7:-3]
        elif content.startswith('```'):
            content = content[3:-3]
        trivia_data = json.loads(content)
        return trivia_data
    except Exception as e:
        print(f"Error generating trivia with OpenAI: {e}")
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
        }
    }
    
    # Get question for category or use general as fallback
    return category_questions.get(category, category_questions["general"])

def load_trivia_data():
    """Load existing trivia data from database"""
    try:
        db = TriviaDatabase()
        trivia_questions = db.get_trivia_questions()
        today = datetime.now().strftime(DATE_FORMAT)
        current = None
        history = []
        for date, question_data in trivia_questions.items():
            if date == today:
                current = question_data
            else:
                history.append(question_data)
        return {"current": current, "history": history}
    except Exception as e:
        print(f"Error loading trivia data from database: {e}")
        return {"current": None, "history": []}

def save_trivia_data(trivia_data):
    """Save trivia data to database"""
    try:
        db = TriviaDatabase()
        
        # Convert to database format
        trivia_questions = {}
        if trivia_data.get("current"):
            today = datetime.now().strftime(DATE_FORMAT)
            trivia_questions[today] = trivia_data["current"]
        
        for i, question in enumerate(trivia_data.get("history", [])):
            # Use a date format for history entries
            date = f"history_{i}"
            trivia_questions[date] = question
        
        db.update_trivia_questions(trivia_questions)
        db.export_compressed_data()
    except Exception as e:
        print(f"Error saving trivia data to database: {e}")
        # Continue without saving if database fails

def load_leaderboard():
    """Load leaderboard data from database"""
    try:
        db = TriviaDatabase()
        return db.get_leaderboard()
    except Exception as e:
        print(f"Error loading leaderboard from database: {e}")
        # Return empty leaderboard as fallback
        return {}

def save_leaderboard(leaderboard):
    """Save leaderboard data to database"""
    try:
        db = TriviaDatabase()
        db.update_leaderboard(leaderboard)
        db.export_compressed_data()
    except Exception as e:
        print(f"Error saving leaderboard to database: {e}")
        # Continue without saving if database fails

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
    trivia_date = current_trivia.get("date")
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

def get_wikipedia_link(answer_text, question_text):
    """Use OpenAI to get a Wikipedia link for the answer in the context of the question."""
    try:
        client = setup_openai()
        prompt = (
            f"give me a wikipedia link to this answer: {answer_text} for this question: {question_text} "
            "for further reading or support that shows the answer is correct. "
            "Return only the full Wikipedia URL, nothing else."
        )
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.2
        )
        url = response.choices[0].message.content.strip()
        if url.startswith("http"):
            return url
    except Exception as e:
        print(f"Error getting Wikipedia link from OpenAI: {e}")
    # Fallback: heuristic
    import urllib.parse
    clean = str(answer_text).strip().replace(' ', '_')
    return f"https://en.wikipedia.org/wiki/{urllib.parse.quote(clean)}"

def update_readme(trivia_data, leaderboard):
    """Update the README with current trivia, daily fact, and leaderboard"""
    try:
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
            if t.get("date") == yesterday_date:
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
            print("[DEBUG] README.md has changed. Diff summary:")
            diff = difflib.unified_diff(
                old_content.splitlines(),
                readme_content.splitlines(),
                fromfile='README.md (old)',
                tofile='README.md (new)',
                lineterm='' 
            )
            for line in diff:
                print(line)
        else:
            print("[DEBUG] README.md is unchanged.")
    except Exception as e:
        print(f"Error in update_readme: {e}")
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
    print("⚠️ Could not generate unique trivia after several attempts.")
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
        print(f"🌞 Fact for today ({today}) already exists:")
        print(f"    {fact['fact']}")
        print(f"    (added at {fact.get('timestamp', 'unknown time')})")
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
    print(f"[NEW-FACT] Added fact for {today}: {new_fact['fact']}")
    return daily_facts_data[today]

# --- For trivia ---
def main():
    print("🎯 Generating daily trivia and daily fact...")
    client = setup_openai()
    trivia_data = load_trivia_data()
    leaderboard = load_leaderboard()
    today = get_utc_today()
    current_trivia = trivia_data.get("current")
    trivia_changed = False
    # Check if trivia for today exists BEFORE any API call
    if current_trivia and current_trivia.get("date") == today:
        print(f"🌞 Trivia for today ({today}) already exists:")
        print(f"    {current_trivia['question']}")
        print(f"    (category: {current_trivia.get('category', 'unknown')})")
        print(f"    (added at {current_trivia.get('timestamp', 'unknown time')})")
        return  # Do not generate or overwrite
    else:
        print("🔄 Generating new trivia question...")
        if current_trivia and current_trivia.get("date"):
            trivia_data.setdefault("history", []).append(current_trivia)
        new_trivia = generate_unique_trivia(current_trivia, max_tries=3)
        if not current_trivia or new_trivia['question'] != current_trivia.get('question'):
            new_trivia["date"] = today
            new_trivia["timestamp"] = datetime.now().isoformat()
            if isinstance(new_trivia["date"], str) and "-" in new_trivia["date"]:
                try:
                    date_obj = datetime.strptime(new_trivia["date"], "%Y-%m-%d")
                    new_trivia["date"] = date_obj.strftime(DATE_FORMAT)
                except ValueError:
                    new_trivia["date"] = today
            trivia_data["current"] = new_trivia
            save_trivia_data(trivia_data)
            print(f"✅ Generated new trivia: {new_trivia['question']}")
            trivia_changed = True
        else:
            print("⚠️ New trivia is still identical to previous trivia after 3 attempts. Not updating.")
    # Get today's daily fact
    daily_facts_data = None
    try:
        from core.daily_facts import load_daily_facts
        daily_facts_data = load_daily_facts()
    except Exception:
        daily_facts_data = None
    # Try up to 3 times to get a different fact
    fact_changed = True
    prev_fact = None
    if daily_facts_data:
        today = datetime.now().strftime(DATE_FORMAT)
        yesterday = (datetime.now() - timedelta(days=1)).strftime(DATE_FORMAT)
        prev_fact = daily_facts_data.get(yesterday, {}).get('fact') if yesterday in daily_facts_data else None
    for attempt in range(3):
        daily_fact = get_todays_fact()
        if prev_fact and daily_fact['fact'] == prev_fact:
            print(f"⚠️ New daily fact is identical to previous fact. Retrying... (attempt {attempt+1})")
            fact_changed = False
            continue
        else:
            fact_changed = True
            break
    else:
        print("⚠️ New daily fact is still identical to previous fact after 3 attempts. Not updating.")
    print(f"💡 Daily Fact: {daily_fact['fact']}")
    # Update README only if trivia or fact changed
    if trivia_changed or fact_changed:
        update_readme(trivia_data, leaderboard)
        print("✅ README updated successfully with trivia and daily fact!")
    else:
        print("ℹ️ No update to README needed (trivia and fact unchanged).")

if __name__ == "__main__":
    main() 