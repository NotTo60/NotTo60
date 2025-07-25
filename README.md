
# 🧠 Daily trivia. Unknown facts. One leaderboard.

👋 Welcome to my GitHub! Every day, unlock a surprising fact and test your brain with a fresh trivia challenge — beat the streak, top the leaderboard! 🧠🔥

---

## 💡 Did You Know? • 24.07.2025

Incredible fact: A `jiffy` is a unit of time for 1/100th of a second.

---

## 🎯 Today's Trivia • 24.07.2025

**In a stunning twist of fate, which fictional character is rumored to have once received a handwritten letter from their own creator, urging them to rebel against the narrative?**

**Options:**
- **[Answer A](https://github.com/NotTo60/NotTo60/issues/new?title=Trivia+Answer+A&body=%F0%9F%8E%AF%20Just%20click%20%27Submit%20new%20issue%27%20to%20submit%20your%20answer%21%20No%20need%20to%20change%20anything%20else%20-%20your%20choice%20is%20already%20in%20the%20title%21%20%F0%9F%9A%80%0A%0A%2A%2AAnswer%3A%2A%2A%20The%20Time-Traveling%20Detective%0A%0A%2A%2ATrivia%20Date%3A%2A%2A%202025-07-24)** - The Time-Traveling Detective
- **[Answer B](https://github.com/NotTo60/NotTo60/issues/new?title=Trivia+Answer+B&body=%F0%9F%8E%AF%20Just%20click%20%27Submit%20new%20issue%27%20to%20submit%20your%20answer%21%20No%20need%20to%20change%20anything%20else%20-%20your%20choice%20is%20already%20in%20the%20title%21%20%F0%9F%9A%80%0A%0A%2A%2AAnswer%3A%2A%2A%20The%20Enchanted%20Sorceress%0A%0A%2A%2ATrivia%20Date%3A%2A%2A%202025-07-24)** - The Enchanted Sorceress
- **[Answer C](https://github.com/NotTo60/NotTo60/issues/new?title=Trivia+Answer+C&body=%F0%9F%8E%AF%20Just%20click%20%27Submit%20new%20issue%27%20to%20submit%20your%20answer%21%20No%20need%20to%20change%20anything%20else%20-%20your%20choice%20is%20already%20in%20the%20title%21%20%F0%9F%9A%80%0A%0A%2A%2AAnswer%3A%2A%2A%20The%20Galactic%20Smuggler%0A%0A%2A%2ATrivia%20Date%3A%2A%2A%202025-07-24)** - The Galactic Smuggler

📝 *Click a button above to submit your answer!*

---

## 🏆 Leaderboard

| Rank | User | Streak | Points | Total Correct | Day Joined |
|------|------|--------|--------|---------------|------------|

| - | *No participants yet* | - | - | - | - |

---



## 🎮 How to Play

1. **Read the daily trivia question** above
2. **Click one of the answer options** (A, B, or C)
3. **Submit your answer** via the GitHub issue that opens
4. **Check back tomorrow** to see if you were correct and view the leaderboard!


## 🔥 Points & Streak System

- **Correct Answer:** +1 point
- **3-Day Streak:** +1 bonus point (every 3, 6, 9, 12, ... days)
- **6-Day Streak:** +1 bonus point (every 6, 12, 18, ... days)
  - At 6, 12, 18, ... you get both bonuses: +1 (for 3) and +1 (for 6), for a total of 3 points!
- **Wrong Answer:** Streak resets to 0
- **Miss a Day:** Streak continues (no penalty)
- **Leaderboard:** Top 10 users with highest total points
---


*Questions and facts are automatically generated daily at 12:00 AM UTC!*

> **⏰ Timezone Note:**
> - All daily cutoffs and leaderboard resets are based on **UTC (Coordinated Universal Time)**.
> - If you are in a different timezone, the new trivia and fact may appear in your morning, afternoon, or evening depending on your local time.
> - Answers are accepted for the UTC day only. If you answer just before or after midnight UTC, your answer may count for the previous or next day's question.

## FAQ

**Q: Why did my answer not count for today?**
- A: All answers are matched to the UTC day. If you submit an answer just before or after midnight UTC, it may count for the previous or next day's question. Check the UTC time and try to answer after the new question is posted (12:00 AM UTC).

## 🚀 Deployment

### **Requirements**
- Python 3.9+
- SQLite3
- GitHub repository with Actions enabled
- OpenAI API key (for trivia generation)
- **Environment variables (required):**
  - `OPENAI_API_KEY`: For trivia generation
  - `GITHUB_TOKEN`: For issue processing (must be set in workflow)
  - `GITHUB_USERNAME`: Repository owner (set in workflow)
  - `GITHUB_REPO`: Repository name (set in workflow)

### **Setup Steps**
1. Clone repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set GitHub secrets (API keys)
4. Enable GitHub Actions
5. Trigger initial workflow run

---

## 🛠️ Troubleshooting & Recovery

### Common Issues

- **Missing environment variable error:**
  - Ensure all required variables (`OPENAI_API_KEY`, `GITHUB_TOKEN`, `GITHUB_USERNAME`, `GITHUB_REPO`) are set in your environment or workflow.

- **Lost database password or salt:**
  - If you lose `TRIVIA_DB_PASSWORD` or `TRIVIA_DB_SALT`, you cannot decrypt the database. You must restore from a previous backup or start a new database.
  - Always keep a secure backup of your secrets.

- **Corrupted or unreadable database:**
  - If the DB file is corrupted, restore from the latest working backup in your git history or artifact storage.
  - If you see decryption errors, check that your password and salt are correct and match the ones used to encrypt the DB.

- **API failures (OpenAI, GitHub):**
  - The system will retry failed API calls with exponential backoff. If rate limits are hit, the logs will show clear messages.
  - If failures persist, check your API keys, network, and service status.

- **Schema migration/version errors:**
  - If you see errors about schema version, ensure you are running the latest code and that the DB is not from an unsupported future version.
  - The system will auto-migrate older DBs to the current schema version when possible.

### Recovery Steps

1. **Restore from backup:**
   - Use a previous version of `src/data/trivia_database.db.gz` from your git history or artifact storage.
2. **Reset secrets:**
   - If secrets are lost, set new ones and re-encrypt the DB if needed.
3. **Check logs:**
   - Review workflow and application logs for detailed error messages and troubleshooting hints.
4. **Contact support/community:**
   - If you are stuck, open an issue on the repository or ask for help in the project community.

---

## Running Tests

1. **Create and activate a virtual environment:**
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```
2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
3. **Run the test suite:**
   ```sh
   PYTHONPATH=src python3 src/core/test_import_real_db.py
   ```

## Dependencies

- All dependencies are listed in `requirements.txt`.
- Notable: `tenacity` is used for robust retries/backoff on all API calls (OpenAI, GitHub, facts APIs).

## Troubleshooting

- If you see `ImportError` for a package, make sure your virtual environment is activated and dependencies are installed.
- If you see `ModuleNotFoundError: No module named 'core'`, use `PYTHONPATH=src` when running scripts from the project root.
- If you see `zsh: command not found: python`, use `python3` instead of `python`.