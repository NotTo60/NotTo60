# 🚀 Quick Setup Guide

## 📋 Prerequisites

- Python 3.8+
- GitHub account
- OpenAI API key (optional, for AI-generated questions)

## ⚡ Quick Start

### 1. Clone and Setup
```bash
# Clone your repository
git clone https://github.com/NotTo60/NotTo60.git
cd NotTo60

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Set your OpenAI API key (optional)
export OPENAI_API_KEY="your-openai-api-key"

# Or create a .env file
echo "OPENAI_API_KEY=your-openai-api-key" > .env
```

### 3. Test the System
```bash
# Run the demo
python main.py demo

# Generate interactive UI
python main.py ui

# Open the beautiful UI
open assets/trivia_ui.html
```

## 🎯 Available Commands

### Main Entry Point
```bash
python main.py <command>
```

**Commands:**
- `trivia` - Generate daily trivia
- `process` - Process answers
- `ui` - Generate interactive UI
- `demo` - Run comprehensive demo
- `test` - Test all modules

### Direct Module Usage
```bash
# Core functionality
python src/core/daily_trivia.py
python src/core/process_answers.py
python src/ui/generate_ui.py

# Demo and testing
python scripts/demo.py
```

## 🔧 Configuration

### Environment Variables
- `OPENAI_API_KEY`: OpenAI API key for AI-generated questions
- `GITHUB_USERNAME`: Your GitHub username (defaults to "NotTo60")
- `GITHUB_REPO`: Repository name (defaults to "NotTo60")
- `GH_TOKEN`: GitHub token for issue processing

### File Structure
```
src/
├── core/           # Core functionality
├── ui/             # User interface
├── data/           # Data storage
└── utils/          # Utilities

assets/             # Static files
scripts/            # Utility scripts
docs/               # Documentation
```

## 🌐 GitHub Profile Setup

### 1. Create Repository
- Create a repository named exactly like your username (e.g., "NotTo60")
- Make it **Public**
- Don't initialize with README

### 2. Upload Files
- Upload all files from this project to your repository
- The README.md will automatically appear on your profile

### 3. Configure Secrets
- Go to Settings → Secrets and variables → Actions
- Add `OPENAI_API_KEY` secret with your OpenAI API key

### 4. Enable Issues
- Go to Settings → Features
- Enable Issues

### 5. Test the System
```bash
# Run demo to generate initial content
python main.py demo

# Commit and push
git add .
git commit -m "🎯 Initial trivia profile setup"
git push
```

## 🎮 Using the Interactive UI

1. **Open the UI**: Click the "🎮 Play Interactive Version" link in your README
2. **Answer Questions**: Click the beautiful buttons to answer
3. **See Results**: Get immediate feedback with animations
4. **Check Leaderboard**: View top players and scores

## 🔄 Daily Automation

The system automatically updates daily at 12:00 AM UTC via GitHub Actions:

1. **Fetches new WOW facts** from real APIs
2. **Generates new trivia** with AI
3. **Updates daily facts** with interesting tidbits
4. **Processes answers** from GitHub issues
5. **Updates leaderboard** with scores and streaks
6. **Regenerates UI** with fresh content

## 🛠️ Development

### Adding New Features
1. **Core functionality**: Add to `src/core/`
2. **UI components**: Add to `src/ui/`
3. **Data models**: Add to `src/data/`
4. **Utilities**: Add to `src/utils/`

### Testing
```bash
# Test all modules
python main.py test

# Run specific tests
python scripts/demo.py
```

### Documentation
- **Project structure**: `PROJECT_STRUCTURE.md`
- **Features**: `FINAL_FEATURES.md`
- **UI documentation**: `docs/UI_README.md`

## 🎉 Success!

Your GitHub profile now features:
- ✅ **Daily AI-generated trivia** with WOW facts
- ✅ **Beautiful interactive UI** with real buttons
- ✅ **Real-time leaderboard** with streaks
- ✅ **Daily "Did You Know?" facts**
- ✅ **Automated daily updates**
- ✅ **Professional organized structure**

---

**🌟 Your GitHub profile is now the most engaging trivia profile on GitHub!** 