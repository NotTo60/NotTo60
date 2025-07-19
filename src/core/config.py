import os

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# GitHub Configuration
GITHUB_TOKEN = os.getenv('GH_TOKEN')
GITHUB_USERNAME = os.getenv('GITHUB_USERNAME', 'NotTo60')
GITHUB_REPO = os.getenv('GITHUB_REPO', 'NotTo60')

# API Endpoints for WOW Facts
WOW_FACT_APIS = {
    "numbers_api": "http://numbersapi.com/random/trivia",
    "cat_facts": "https://cat-fact.herokuapp.com/facts/random",
    "dog_facts": "https://dog-fact.herokuapp.com/facts/random",
    "space_facts": "https://api.spaceflightnewsapi.net/v3/articles",
    "animal_facts": "https://zoo-animal-api.herokuapp.com/animals/rand",
    "history_facts": "https://api.fungenerators.com/facts/history",
    "science_facts": "https://api.fungenerators.com/facts/science",
    "geography_facts": "https://api.fungenerators.com/facts/geography",
    "sports_facts": "https://api.fungenerators.com/facts/sports",
    "technology_facts": "https://api.fungenerators.com/facts/technology"
}

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

# WOW Effect Keywords for Fact Enhancement
WOW_KEYWORDS = [
    "incredible", "amazing", "unbelievable", "astonishing", "mind-blowing",
    "extraordinary", "remarkable", "fascinating", "stunning", "spectacular",
    "phenomenal", "incredible", "breathtaking", "jaw-dropping", "mind-boggling",
    "outrageous", "fantastic", "marvelous", "wonderful", "magnificent"
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
MAX_LEADERBOARD_ENTRIES = 5

# API Request Configuration
API_TIMEOUT = 10  # seconds
MAX_RETRIES = 3

# Trivia Generation Settings
MAX_TOKENS = 400
TEMPERATURE = 0.8
MODEL = "gpt-3.5-turbo"

# GitHub Issue Configuration
ISSUE_LABEL = "trivia-answer"
ISSUE_TEMPLATE = "I choose {answer}"

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

# GitHub Actions Schedule
DAILY_CRON = "0 0 * * *"  # Daily at midnight UTC
HOURLY_CRON = "0 * * * *"  # Every hour (for testing)
WEEKLY_CRON = "0 0 * * 1"  # Weekly on Monday 