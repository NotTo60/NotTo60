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
        # Fallback to standalone trivia
        return create_standalone_trivia(category)

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
        
        # Convert to expected format
        current = None
        history = []
        
        for date, question_data in trivia_questions.items():
            if current is None:
                current = question_data
            else:
                history.append(question_data)
        
        return {"current": current, "history": history}
    except Exception as e:
        print(f"Error loading trivia data from database: {e}")
        # Return empty data structure as fallback
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
    options = current_trivia.get("options", {"A": "A", "B": "B", "C": "C"})
    
    return {
        "A": f"{base_url}/issues/new?title=Trivia+Answer+A&body={urllib.parse.quote(ISSUE_TEMPLATE.format(answer_text=options['A']))}",
        "B": f"{base_url}/issues/new?title=Trivia+Answer+B&body={urllib.parse.quote(ISSUE_TEMPLATE.format(answer_text=options['B']))}", 
        "C": f"{base_url}/issues/new?title=Trivia+Answer+C&body={urllib.parse.quote(ISSUE_TEMPLATE.format(answer_text=options['C']))}"
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
        
        # Get current trivia
        current_trivia = trivia_data.get("current")
        if not current_trivia:
            return
        
        # Get today's daily fact
        daily_fact = get_todays_fact()
        
        # Create answer links
        answer_links = create_answer_links(trivia_data)
        
        # Get top leaderboard
        top_users = get_top_leaderboard(leaderboard)
        
        # Get category emoji
        category = current_trivia.get('category', 'general')
        emoji = EMOJI_MAPPING.get(category, "💡")
        
        # Yesterday's stats
        yesterday_stats = ""
        yesterday_date = get_utc_yesterday()
        # Find the trivia in history with yesterday's date
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
            yesterday_stats = f"""
### 📊 Yesterday's Results • {yesterday_date}

**Question:** {question}
**Correct Answer:** {correct_letter}) {correct_text} ([Wikipedia]({wiki_link}))
**Explanation:** {explanation}
"""
        
        readme_content = f"""# 🧠 Daily trivia. Unknown facts. One leaderboard. Can you stay on top? 🔥

👋 Welcome to my GitHub! Every day, unlock a surprising fact and test your brain with a fresh trivia challenge — beat the streak, top the leaderboard! 🧠🔥

---

## 💡 Did You Know? • {today}

{daily_fact['fact']}

---

## 🎯 Today's Trivia • {today}

**{current_trivia['question']}**

**Options:**
- **[Answer A]({answer_links['A']})** - {current_trivia['options']['A']}
- **[Answer B]({answer_links['B']})** - {current_trivia['options']['B']}
- **[Answer C]({answer_links['C']})** - {current_trivia['options']['C']}

📝 *Click a button above to submit your answer!*

---

## 🏆 Leaderboard

| Rank | User | Streak | Points | Total Correct |
|------|------|--------|--------|---------------|
"""
        
        for i, (username, stats) in enumerate(top_users, 1):
            streak_emoji = get_streak_emoji(stats['current_streak'])
            points_display = format_points_display(stats['total_points'])
            readme_content += f"| {i} | @{username} | {streak_emoji} {stats['current_streak']} | {points_display} | ✅ {stats['total_correct']} |\n"
        
        if not top_users:
            readme_content += "| - | *No participants yet* | - | - | - |\n"
        
        readme_content += f"""
---

{yesterday_stats}
## 🎮 How to Play

1. **Read the daily trivia question** above
2. **Click one of the answer options** (A, B, or C)
3. **Submit your answer** via the GitHub issue that opens
4. **Check back tomorrow** to see if you were correct and view the leaderboard!

## 🔥 Points & Streak System

- **Correct Answer:** +1 point + streak bonus
- **3-Day Streak:** +1 bonus point 🏆 (and all multiples of 3: 3, 6, 9, 12, 15, 18, 21, 24, 27, etc.)
- **7-Day Streak:** +1 bonus point 🏆🏆 (total 3 points for 7th day)
- **Wrong Answer:** Streak resets to 0
- **Miss a Day:** Streak continues (no penalty)
- **Leaderboard:** Top {MAX_LEADERBOARD_ENTRIES} users with highest total points

---

*Questions and facts are automatically generated daily at 12:00 AM UTC!*
"""
        
        with open("README.md", "w") as f:
            f.write(readme_content)
    except Exception as e:
        print(f"Error in update_readme: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function to generate and update trivia"""
    print("🎯 Generating daily trivia and daily fact...")
    
    # Setup OpenAI
    client = setup_openai()
    
    # Load existing data
    trivia_data = load_trivia_data()
    leaderboard = load_leaderboard()
    
    # Check if we need to generate new trivia
    today = get_utc_today()
    current_trivia = trivia_data.get("current")
    
    if current_trivia and current_trivia.get("date") == today:
        print(f"✅ Trivia already exists for {today}")
    else:
        print("🔄 Generating new trivia question with WOW facts...")
        
        # Only move current trivia to history if it has a date
        if current_trivia and current_trivia.get("date"):
            trivia_data.setdefault("history", []).append(current_trivia)
        
        # Generate new trivia
        new_trivia = generate_trivia_question()
        new_trivia["date"] = today
        
        # Ensure the date is in DD.MM.YYYY format
        if isinstance(new_trivia["date"], str) and "-" in new_trivia["date"]:
            # Convert YYYY-MM-DD to DD.MM.YYYY if needed
            try:
                date_obj = datetime.strptime(new_trivia["date"], "%Y-%m-%d")
                new_trivia["date"] = date_obj.strftime(DATE_FORMAT)
            except ValueError:
                new_trivia["date"] = today
        
        trivia_data["current"] = new_trivia
        
        # Save trivia data
        save_trivia_data(trivia_data)
        print(f"✅ Generated new trivia: {new_trivia['question']}")
    
    # Get today's daily fact
    daily_fact = get_todays_fact()
    print(f"💡 Daily Fact: {daily_fact['fact']}")
    
    # Update README
    update_readme(trivia_data, leaderboard)
    print("✅ README updated successfully with trivia, WOW facts, and daily fact!")

if __name__ == "__main__":
    main() 