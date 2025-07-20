import os

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# GitHub Configuration
GITHUB_TOKEN = os.getenv('GH_TOKEN')
GITHUB_USERNAME = os.getenv('GITHUB_USERNAME', 'NotTo60')
GITHUB_REPO = os.getenv('GITHUB_REPO', 'NotTo60')

# Daily "Did You Know?" Fact Sources
DAILY_FACT_SOURCES = {
    "random_facts": "https://uselessfacts.jsph.pl/api/v2/facts/random",
    "joke_facts": "https://v2.jokeapi.dev/joke/Any?safe-mode",
    "quote_facts": "https://api.quotable.io/random",
    "word_facts": "https://api.dictionaryapi.dev/api/v2/entries/en/",
    "weather_facts": "https://api.openweathermap.org/data/2.5/weather",
    "time_facts": "https://worldtimeapi.org/api/timezone/",
    "country_facts": "https://restcountries.com/v3.1/name/",
    "food_facts": "https://www.themealdb.com/api/json/v1/1/random.php",
    "book_facts": "https://openlibrary.org/works/",
    "movie_facts": "http://www.omdbapi.com/"
}

# Trivia Configuration
TRIVIA_CATEGORIES = [
    "science", "history", "geography", "literature", "sports", 
    "entertainment", "technology", "nature", "art", "music",
    "space", "animals", "human_body", "oceans", "mountains",
    "inventions", "discoveries", "records", "extremes", "mysteries"
]

# Daily Fact Categories for "Did You Know?"
DAILY_FACT_CATEGORIES = [
    "science", "history", "nature", "technology", "space", "animals", 
    "human_body", "geography", "culture", "food", "language", "art",
    "music", "sports", "inventions", "discoveries", "records", "mysteries",
    "weather", "time", "countries", "books", "movies", "random"
]

# File paths
TRIVIA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "trivia.json")
LEADERBOARD_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "leaderboard.json")
DAILY_FACTS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "daily_facts.json")

# Streak configuration
MIN_STREAK_FOR_LEADERBOARD = 1
MAX_LEADERBOARD_ENTRIES = 10

# API Request Configuration
API_TIMEOUT = 10  # seconds
MAX_RETRIES = 3

# Trivia Generation Settings
MAX_TOKENS = 400
TEMPERATURE = 0.8
# Auto-detect latest model
def get_latest_model():
    """Get the latest available GPT model"""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        models = client.models.list()
        
        # Priority order for latest models
        latest_models = [
            "gpt-4o",           # Latest flagship model
            "gpt-4o-mini",      # Latest mini model
            "gpt-4-turbo",      # Previous flagship
            "gpt-3.5-turbo"     # Fallback
        ]
        
        available_models = [model.id for model in models.data]
        
        for model in latest_models:
            if model in available_models:
                return model
        
        return "gpt-4o-mini"  # Default fallback
    except:
        return "gpt-4o-mini"  # Fallback if API call fails

MODEL = get_latest_model()

# GitHub Issue Configuration
ISSUE_LABEL = "trivia"
ISSUE_TEMPLATE = "🎯 Just click 'Submit new issue' to submit your answer! No need to change anything else - your choice is already in the title! 🚀\n\n**Answer:** {answer_text}"

# Display Configuration
EMOJI_MAPPING = {
    "science": "🔬",
    "history": "📚",
    "geography": "🌍",
    "literature": "📖",
    "sports": "⚽",
    "entertainment": "🎬",
    "technology": "💻",
    "nature": "🌿",
    "art": "🎨",
    "music": "🎵",
    "space": "🚀",
    "animals": "🐾",
    "human_body": "🧬",
    "oceans": "🌊",
    "mountains": "⛰️",
    "inventions": "💡",
    "discoveries": "🔍",
    "records": "🏆",
    "extremes": "🔥",
    "mysteries": "🔮",
    "culture": "🏛️",
    "food": "🍕",
    "language": "🗣️",
    "weather": "🌤️",
    "time": "⏰",
    "countries": "🏳️",
    "books": "📚",
    "movies": "🎭",
    "random": "🎲"
}

# Response Messages
CORRECT_MESSAGES = [
    "🎉 **WOW! You're absolutely right!**",
    "🌟 **AMAZING! You nailed it!**",
    "🔥 **INCREDIBLE! Perfect answer!**",
    "💫 **FANTASTIC! You're on fire!**",
    "🚀 **OUTSTANDING! You're unstoppable!**"
]

INCORRECT_MESSAGES = [
    "❌ **Oh no! That's not quite right.**",
    "😅 **Not this time, but great try!**",
    "🤔 **Close, but not quite!**",
    "💭 **Interesting guess, but...**",
    "🎯 **Almost there, but not quite!**"
]

# Daily Fact Templates
DAILY_FACT_TEMPLATES = [
    "Did you know? {fact}",
    "Fun fact: {fact}",
    "Here's something interesting: {fact}",
    "Today's discovery: {fact}",
    "Mind-blowing fact: {fact}",
    "Amazing discovery: {fact}",
    "Incredible fact: {fact}",
    "Fascinating tidbit: {fact}",
    "Surprising fact: {fact}",
    "Little known fact: {fact}"
]

# README Content Templates
README_TEMPLATE = """
# 🧠 Daily trivia. Unknown facts. One leaderboard.

👋 Welcome to my GitHub! Every day, unlock a surprising fact and test your brain with a fresh trivia challenge — beat the streak, top the leaderboard! 🧠🔥

---

## 💡 Did You Know? • {today}

{daily_fact}

---

## 🎯 Today's Trivia • {today}

**{question}**

**Options:**
- **[Answer A]({answer_link_a})** - {option_a}
- **[Answer B]({answer_link_b})** - {option_b}
- **[Answer C]({answer_link_c})** - {option_c}

📝 *Click a button above to submit your answer!*

---

## 🏆 Leaderboard

| Rank | User | Streak | Points | Total Correct | Day Joined |
|------|------|--------|--------|---------------|------------|
{leaderboard_rows}
{no_participants_row}
---

{yesterday_stats}
{how_to_play}
{points_system}

*Questions and facts are automatically generated daily at 12:00 AM UTC!*"""

YESTERDAY_STATS_TEMPLATE = """
### 📊 Yesterday's Results • {yesterday_date}

**Question:** {question}
**Correct Answer:** {correct_letter}) {correct_text} ([Wikipedia]({wiki_link}))
**Explanation:** {explanation}
"""

HOW_TO_PLAY_TEMPLATE = """
## 🎮 How to Play

1. **Read the daily trivia question** above
2. **Click one of the answer options** (A, B, or C)
3. **Submit your answer** via the GitHub issue that opens
4. **Check back tomorrow** to see if you were correct and view the leaderboard!
"""

POINTS_SYSTEM_TEMPLATE = """
## 🔥 Points & Streak System

- **Correct Answer:** +1 point
- **3-Day Streak:** +1 bonus point (every 3, 6, 9, 12, ... days)
- **6-Day Streak:** +1 bonus point (every 6, 12, 18, ... days)
  - At 6, 12, 18, ... you get both bonuses: +1 (for 3) and +1 (for 6), for a total of 3 points!
- **Wrong Answer:** Streak resets to 0
- **Miss a Day:** Streak continues (no penalty)
- **Leaderboard:** Top {max_leaderboard_entries} users with highest total points
---
"""

# GitHub Actions Schedule
DAILY_CRON = "0 0 * * *"  # Daily at midnight UTC
HOURLY_CRON = "0 * * * *"  # Every hour (for testing)
WEEKLY_CRON = "0 0 * * 1"  # Weekly on Monday

# Timezone and Grace Period Settings
TIMEZONE = "UTC"  # Default timezone for date calculations
GRACE_PERIOD_HOURS = 2  # Grace period for timezone differences

# Date Format Settings
DATE_FORMAT = "%d.%m.%Y"  # DD.MM.YYYY format
DATETIME_FORMAT = "%d.%m.%Y %H:%M:%S"  # DD.MM.YYYY HH:MM:SS format 