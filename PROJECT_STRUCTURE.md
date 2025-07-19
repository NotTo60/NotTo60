# 📁 Project Structure

## 🏗️ Organized Folder Structure

```
git_readme/
├── 📁 src/                          # Source code
│   ├── 📁 core/                     # Core functionality
│   │   ├── config.py               # Configuration and constants
│   │   ├── daily_trivia.py         # Main trivia generation
│   │   ├── process_answers.py      # Answer processing
│   │   ├── wow_facts.py            # WOW facts from APIs
│   │   └── daily_facts.py          # Daily facts from APIs
│   ├── 📁 ui/                       # User interface
│   │   └── generate_ui.py          # Interactive HTML UI generator
│   ├── 📁 data/                     # Data storage
│   │   ├── trivia.json             # Current and historical trivia
│   │   ├── daily_facts.json        # Daily facts data
│   │   └── leaderboard.json        # User scores and streaks
│   └── 📁 utils/                    # Utility functions (future)
├── 📁 assets/                       # Static assets
│   ├── trivia_ui.html              # Interactive UI file
│   ├── 📁 images/                   # Images (future)
│   └── 📁 styles/                   # CSS styles (future)
├── 📁 scripts/                      # Utility scripts
│   └── demo.py                     # Demo and testing script
├── 📁 docs/                         # Documentation
│   └── UI_README.md                # Interactive UI documentation
├── 📁 tests/                        # Test files (future)
├── 📁 .github/                      # GitHub configuration
│   └── 📁 workflows/
│       └── update-trivia.yml       # Daily automation workflow
├── main.py                         # Main entry point
├── README.md                       # Main README
├── PROJECT_STRUCTURE.md            # This file
├── FINAL_FEATURES.md               # Feature documentation
├── requirements.txt                # Python dependencies
└── .gitignore                      # Git ignore rules
```

## 🎯 Folder Purposes

### 📁 `src/` - Source Code
**Core application logic and functionality**

#### 📁 `src/core/` - Core Modules
- **`config.py`**: All constants, API endpoints, and configuration
- **`daily_trivia.py`**: Main trivia generation with OpenAI integration
- **`process_answers.py`**: GitHub issue processing and scoring
- **`wow_facts.py`**: WOW facts fetching from multiple APIs
- **`daily_facts.py`**: Daily "Did You Know?" facts from APIs

#### 📁 `src/ui/` - User Interface
- **`generate_ui.py`**: Generates beautiful interactive HTML UI

#### 📁 `src/data/` - Data Storage
- **`trivia.json`**: Current trivia question and historical data
- **`daily_facts.json`**: WOW facts and daily facts data
- **`leaderboard.json`**: User scores, streaks, and statistics

#### 📁 `src/utils/` - Utilities
- Future utility functions and helpers

### 📁 `assets/` - Static Assets
**Static files served to users**

- **`trivia_ui.html`**: Beautiful interactive trivia interface
- **`images/`**: Future image assets
- **`styles/`**: Future CSS stylesheets

### 📁 `scripts/` - Utility Scripts
**Development and testing tools**

- **`demo.py`**: Comprehensive demo and testing script

### 📁 `docs/` - Documentation
**Project documentation**

- **`UI_README.md`**: Interactive UI features and usage

### 📁 `tests/` - Testing
**Test files and test data**

- Future unit tests and integration tests

### 📁 `.github/` - GitHub Configuration
**GitHub-specific configuration**

- **`workflows/update-trivia.yml`**: Daily automation workflow

## 🚀 Usage

### Main Entry Point
```bash
# Generate daily trivia
python main.py trivia

# Process answers
python main.py process

# Generate interactive UI
python main.py ui

# Run demo
python main.py demo

# Test modules
python main.py test
```

### Direct Module Usage
```bash
# Core modules
python src/core/daily_trivia.py
python src/core/process_answers.py
python src/ui/generate_ui.py

# Demo script
python scripts/demo.py
```

## 🔧 Configuration

### Environment Variables
- `OPENAI_API_KEY`: OpenAI API key for trivia generation
- `GITHUB_USERNAME`: Your GitHub username
- `GITHUB_REPO`: Repository name
- `GH_TOKEN`: GitHub token for issue processing

### File Paths
All file paths are automatically configured relative to the project structure:
- Data files: `src/data/`
- UI files: `assets/`
- Configuration: `src/core/config.py`

## 📊 Data Flow

1. **Daily Generation** (`src/core/daily_trivia.py`)
   - Fetches WOW facts from APIs
   - Generates trivia with OpenAI
   - Updates `src/data/trivia.json`
   - Updates README.md

2. **Answer Processing** (`src/core/process_answers.py`)
   - Processes GitHub issues
   - Updates `src/data/leaderboard.json`
   - Calculates scores and streaks

3. **UI Generation** (`src/ui/generate_ui.py`)
   - Reads data from `src/data/`
   - Generates `assets/trivia_ui.html`
   - Creates beautiful interactive interface

4. **Automation** (`.github/workflows/update-trivia.yml`)
   - Runs daily at midnight UTC
   - Executes all core modules
   - Commits changes automatically

## 🎨 Benefits of This Structure

### ✅ **Organization**
- Clear separation of concerns
- Easy to find and modify files
- Logical grouping of related functionality

### ✅ **Maintainability**
- Modular design for easy updates
- Centralized configuration
- Clear data flow

### ✅ **Scalability**
- Easy to add new features
- Separate UI and core logic
- Extensible structure

### ✅ **Professional**
- Industry-standard organization
- Clear documentation
- Easy onboarding for contributors

### ✅ **Deployment Ready**
- GitHub Actions integration
- Proper file paths
- Automated workflows

## 🔄 Migration Notes

### Updated Import Paths
All imports now use relative paths:
```python
# Old
from config import *

# New
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from core.config import *
```

### Updated File Paths
All file operations use absolute paths:
```python
# Old
TRIVIA_FILE = "trivia.json"

# New
TRIVIA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "trivia.json")
```

### GitHub Actions
Updated workflow paths:
```yaml
# Old
python daily_trivia.py

# New
python src/core/daily_trivia.py
```

---

**🎉 This organized structure makes the project professional, maintainable, and easy to extend!** 