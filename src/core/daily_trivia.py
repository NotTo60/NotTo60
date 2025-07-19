#!/usr/bin/env python3
"""
Interactive AI-Powered Trivia GitHub Profile
Generates daily trivia questions using OpenAI and WOW facts from APIs
"""

import json
import os
import random
from datetime import datetime, timedelta
from openai import OpenAI
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.config import *
from core.wow_facts import get_wow_fact, create_trivia_from_wow_fact
from core.daily_facts import get_todays_fact

def setup_openai():
    """Initialize OpenAI client"""
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    return OpenAI(api_key=OPENAI_API_KEY)

def generate_trivia_question():
    """Generate a trivia question using OpenAI and WOW facts"""
    category = random.choice(TRIVIA_CATEGORIES)
    
    # First, try to get a WOW fact from APIs
    wow_fact_result = get_wow_fact(category)
    wow_fact = wow_fact_result.get('fact', '')
    fact_source = wow_fact_result.get('source', '')
    
    # Create enhanced prompt for standalone trivia
    prompt = f"""Generate an INCREDIBLE standalone trivia question about {category}. 

    Requirements:
    - Create a completely original question NOT based on any specific fact
    - Make the question AMAZING and mind-blowing
    - Question should be engaging and create a "WOW" effect
    - Provide exactly 3 multiple choice options (A, B, C)
    - One option must be correct
    - Make the incorrect options plausible but wrong
    - Keep the question and answers concise but fascinating
    - Use {random.choice(WOW_KEYWORDS)} language to make it exciting
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
        
        # Add WOW fact if not already included
        if 'wow_fact' not in trivia_data:
            trivia_data['wow_fact'] = wow_fact
            trivia_data['fact_source'] = fact_source
            
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
    """Load existing trivia data"""
    if os.path.exists(TRIVIA_FILE):
        with open(TRIVIA_FILE, 'r') as f:
            return json.load(f)
    return {"current": None, "history": []}

def save_trivia_data(trivia_data):
    """Save trivia data to file"""
    with open(TRIVIA_FILE, 'w') as f:
        json.dump(trivia_data, f, indent=2)

def load_leaderboard():
    """Load leaderboard data"""
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_leaderboard(leaderboard):
    """Save leaderboard data"""
    with open(LEADERBOARD_FILE, 'w') as f:
        json.dump(leaderboard, f, indent=2)

def get_top_leaderboard(leaderboard, max_entries=MAX_LEADERBOARD_ENTRIES):
    """Get top users from leaderboard"""
    sorted_users = sorted(
        leaderboard.items(), 
        key=lambda x: (x[1]['current_streak'], x[1]['total_correct']), 
        reverse=True
    )
    return sorted_users[:max_entries]

def create_answer_links():
    """Create GitHub issue links for answer buttons"""
    import urllib.parse
    
    base_url = f"https://github.com/{GITHUB_USERNAME}/{GITHUB_REPO}"
    encoded_body = urllib.parse.quote(ISSUE_TEMPLATE)
    
    return {
        "A": f"{base_url}/issues/new?title=Trivia+Answer+A&body={encoded_body}&labels=trivia",
        "B": f"{base_url}/issues/new?title=Trivia+Answer+B&body={encoded_body}&labels=trivia", 
        "C": f"{base_url}/issues/new?title=Trivia+Answer+C&body={encoded_body}&labels=trivia"
    }

def update_readme(trivia_data, leaderboard):
    """Update the README with current trivia, daily fact, and leaderboard"""
    today = datetime.now().strftime(DATE_FORMAT)
    
    # Get current trivia
    current_trivia = trivia_data.get("current")
    if not current_trivia:
        return
    
    # Get today's daily fact
    daily_fact = get_todays_fact()
    
    # Create answer links
    answer_links = create_answer_links()
    
    # Get top leaderboard
    top_users = get_top_leaderboard(leaderboard)
    
    # Get category emoji
    category = current_trivia.get('category', 'general')
    emoji = EMOJI_MAPPING.get(category, "💡")
    
    # Yesterday's stats
    yesterday_stats = ""
    if trivia_data.get("history"):
        yesterday = trivia_data["history"][-1]
        yesterday_emoji = EMOJI_MAPPING.get(yesterday.get('category', 'general'), "💡")
        yesterday_stats = f"""
### 📊 Yesterday's Results • {yesterday['date']}

{yesterday.get('wow_fact', '')}

**Question:** {yesterday['question']}
**Correct Answer:** {yesterday['correct_answer']}) {yesterday['options'][yesterday['correct_answer']]}
**Explanation:** {yesterday['explanation']}
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

| Rank | User | Current Streak | Total Correct |
|------|------|----------------|---------------|
"""
    
    for i, (username, stats) in enumerate(top_users, 1):
        readme_content += f"| {i} | @{username} | 🔥 {stats['current_streak']} | ✅ {stats['total_correct']} |\n"
    
    if not top_users:
        readme_content += "| - | *No participants yet* | - | - |\n"
    
    readme_content += f"""
---

{yesterday_stats}
## 🎮 How to Play

1. **Read the daily trivia question** above
2. **Click one of the answer options** (A, B, or C)
3. **Submit your answer** via the GitHub issue that opens
4. **Check back tomorrow** to see if you were correct and view the leaderboard!

## 🔥 Streak System

- **Correct Answer:** +1 to your streak
- **Wrong Answer:** Streak resets to 0
- **Miss a Day:** Streak continues (no penalty)
- **Leaderboard:** Top {MAX_LEADERBOARD_ENTRIES} users with highest current streaks

---

*Questions and facts are automatically generated daily at 12:00 AM UTC!*
"""
    
    with open("README.md", "w") as f:
        f.write(readme_content)

def main():
    """Main function to generate and update trivia"""
    print("🎯 Generating daily trivia with WOW facts and daily fact...")
    
    # Setup OpenAI
    client = setup_openai()
    
    # Load existing data
    trivia_data = load_trivia_data()
    leaderboard = load_leaderboard()
    
    # Check if we need to generate new trivia
    today = datetime.now().strftime(DATE_FORMAT)
    current_trivia = trivia_data.get("current")
    
    if current_trivia and current_trivia.get("date") == today:
        print(f"✅ Trivia already exists for {today}")
    else:
        print("🔄 Generating new trivia question with WOW facts...")
        
        # Move current trivia to history if it exists
        if current_trivia:
            current_trivia["date"] = today
            trivia_data["history"].append(current_trivia)
        
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
        
        # Ensure no WOW fact references
        if 'wow_fact' in new_trivia:
            del new_trivia['wow_fact']
        if 'fact_source' in new_trivia:
            del new_trivia['fact_source']
        
        trivia_data["current"] = new_trivia
        
        # Save trivia data
        save_trivia_data(trivia_data)
        print(f"✅ Generated new trivia: {new_trivia['question']}")
        print(f"🌟 WOW Fact: {new_trivia.get('wow_fact', 'N/A')}")
    
    # Get today's daily fact
    daily_fact = get_todays_fact()
    print(f"💡 Daily Fact: {daily_fact['fact']}")
    
    # Update README
    update_readme(trivia_data, leaderboard)
    print("✅ README updated successfully with trivia, WOW facts, and daily fact!")

if __name__ == "__main__":
    main() 