# 🧠 Daily Trivia System - Architecture Documentation

## 📋 Overview

A fully automated daily trivia system with leaderboards, points, and streak bonuses. Users answer trivia questions via GitHub issues, and the system automatically processes answers, calculates points, and updates the README.

---

**Recent Updates:**
- Daily facts are now fetched only from the uselessfacts API (random facts); all other sources have been removed.
- The system tries at least twice to fetch a unique fact for the day; if all attempts return a duplicate, it falls back to a local list of unused facts.
- Leaderboard now excludes users with zero answers; only users who have answered at least once are shown.
- Usernames are validated as UUIDs; only valid UUIDs are processed for the leaderboard.
- README.md and the database are passed as artifacts between workflow jobs to ensure consistency across steps.

---

## 🏗️ System Architecture

### **Core Components**

```
src/core/
├── database.py          # SQLite database with gzip compression
├── daily_trivia.py      # Main trivia generation and README updates
├── process_answers.py   # GitHub issue processing and scoring
├── points_system.py     # Points calculation and streak bonuses
├── daily_facts.py       # Daily fact generation from uselessfacts API only
└── config.py           # Configuration and constants
```

### **Data Flow**

1. **Daily Generation** → `daily_trivia.py` generates new trivia + facts
2. **User Participation** → Users click answer links → GitHub issues created
3. **Answer Processing** → `process_answers.py` processes issues → updates leaderboard
4. **README Update** → Leaderboard and content refreshed automatically
5. **Database Sync** → Compressed data exported to git for persistence

---

## 🗄️ Database System

### **SQLite with Gzip Compression**

- **Main Database**: `src/data/trivia.db` (local only)
- **Compressed Export**: `src/data/trivia_database.db.gz` (tracked in git)
- **Auto-Import**: Fresh databases automatically import compressed data

### **Tables**

```sql
leaderboard (
    username TEXT PRIMARY KEY,  -- Must be a valid UUID
    current_streak INTEGER,
    total_correct INTEGER,
    total_points INTEGER,
    total_answered INTEGER,  -- Users with 0 answers are excluded
    last_answered TEXT,
    last_trivia_date TEXT,
    answer_history TEXT  -- Gzipped JSON
)

daily_facts (
    date TEXT PRIMARY KEY,
    fact TEXT,
    timestamp TEXT
)

trivia_questions (
    date TEXT PRIMARY KEY,
    question TEXT,
    options TEXT,  -- Gzipped JSON
    correct_answer TEXT,
    explanation TEXT,
    timestamp TEXT
)
```

---

## 🎯 Points & Streak System

### **Scoring Rules**
- **Correct Answer**: +1 base point
- **3-Day Streak Bonus**: +1 point (and all multiples of 3: 3, 6, 9, 12, 15, 18, 21, 24, 27, etc.)
- **7-Day Streak Bonus**: +1 point (total 3 points for 7th day)
- **Wrong Answer**: Streak resets to 0
- **Miss a Day**: Streak continues (no penalty)

### **Example Scoring**
- Day 1: 1 point (base)
- Day 2: 1 point (base)
- Day 3: 3 points (base + 3-day bonus)
- Day 4: 1 point (base)
- Day 5: 1 point (base)
- Day 6: 3 points (base + 3-day bonus)
- Day 7: 4 points (base + 3-day bonus + 7-day bonus)

---

## 🤖 GitHub Actions Workflow

### **Automated Daily Process**

- README.md and the database are passed as artifacts between jobs to ensure all steps use the latest data.

### **Workflow Steps**
1. **Generate Content**: New trivia question + daily fact (tries twice for uniqueness, then falls back to local list)
2. **Process Answers**: Close GitHub issues + update user stats (only valid UUIDs, no users with 0 answers)
3. **Update README**: Refresh leaderboard and content
4. **Database Export**: Compress and commit data history

---

## 📊 Leaderboard System

### **Display Features**
- **Top 5 Users**: Sorted by points → streak → correct answers
- **No users with 0 answers**: Only users who have answered at least once are shown
- **Streak Emojis**: 🔥 (1-2), 🔥🔥 (3-6), 🔥🔥🔥 (7+)
- **Points Display**: Formatted with bonus indicators
- **Real-time Updates**: Automatic refresh with each workflow run

### **User Data Tracking**
- Current streak length
- Total points earned
- Total correct answers
- Answer history (last 30 days)
- Last participation date
- **Usernames are validated as UUIDs**

---

## 🔧 Configuration

### **Key Settings**
- **Max Leaderboard Entries**: 5 users
- **Database Compression**: Gzip with 3:1 ratio
- **Answer History**: 30 days retention
- **Daily Schedule**: 12:00 AM UTC
- **API Timeout**: 10 seconds
- **Max Retries**: 3 attempts

### **Environment Variables**
- `OPENAI_API_KEY`: For trivia generation
- `GITHUB_TOKEN`: For issue processing
- `GITHUB_USERNAME`: Repository owner
- `GITHUB_REPO`: Repository name

---

## 🚀 Deployment

### **Requirements**
- Python 3.9+
- SQLite3
- GitHub repository with Actions enabled
- OpenAI API key (for trivia generation)

### **Setup Steps**
1. Clone repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set GitHub secrets (API keys)
4. Enable GitHub Actions
5. Trigger initial workflow run

---

## 📈 Performance Metrics

### **Storage Efficiency**
- **Original Size**: ~2,178 bytes (JSON)
- **Compressed Size**: ~733 bytes (gzip)
- **Compression Ratio**: 3:1
- **Database Size**: ~300-500 bytes (compressed)

### **Processing Speed**
- **Trivia Generation**: ~5-10 seconds
- **Answer Processing**: ~1-2 seconds per answer
- **README Update**: ~1 second
- **Total Workflow**: ~60-90 seconds

---

## 🔒 Data Integrity

### **Safety Features**
- **ACID Compliance**: SQLite transactions
- **Daily Snapshots**: Compressed exports in git history
- **Crash Recovery**: Automatic database journaling
- **Version Control**: Complete audit trail
- **Auto-Import**: Fresh databases load existing data

### **Error Handling**
- **Graceful Fallbacks**: Continue operation on API failures
- **Retry Logic**: Automatic retry for transient errors
- **Data Validation**: Input sanitization and validation
- **Logging**: Detailed error tracking and debugging

---

## 🎮 User Experience

### **Participation Flow**
1. User visits README
2. Clicks answer option (A, B, or C)
3. GitHub issue opens with pre-filled answer
4. User submits issue (no editing required)
5. System processes answer automatically
6. Issue closes with feedback and points earned
7. Leaderboard updates on next workflow run

### **Feedback System**
- **Correct Answers**: Celebration message + points breakdown
- **Wrong Answers**: Correct answer + explanation + encouragement
- **Streak Bonuses**: Detailed bonus point explanations
- **Next Milestones**: Progress toward next streak bonus

---

## 🔄 Maintenance

### **Daily Operations**
- Automatic trivia generation
- Answer processing
- Leaderboard updates
- Database compression
- Git commits

### **Monitoring**
- Workflow success/failure tracking
- Database size monitoring
- User participation metrics
- API usage tracking

---

## 🔒 Database Encryption (Anti-Cheat)

- The compressed database file (`trivia_database.db.gz`) is encrypted using AES (Fernet) with a password.
- The password must be set as a GitHub Actions secret: `TRIVIA_DB_PASSWORD`.
- All workflow steps that access the database require this secret.
- If the password is missing or incorrect, the workflow will fail to read/write the database.
- This prevents users from extracting trivia answers or leaderboard data from the repo.

### **How to Set Up**
1. Go to your GitHub repository → Settings → Secrets and variables → Actions → New repository secret.
2. Name: `TRIVIA_DB_PASSWORD`
3. Value: (choose a strong password)
4. Save.

**Note:** If you ever change the password, you must re-encrypt the database with the new password locally and commit the new encrypted file.

---

*This system provides a complete, automated trivia experience with robust data persistence, engaging gamification, and seamless GitHub integration.* 