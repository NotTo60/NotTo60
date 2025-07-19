#!/usr/bin/env python3
"""
Generate interactive HTML UI for the trivia system
"""

import json
import os
from datetime import datetime
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.config import GITHUB_USERNAME, GITHUB_REPO

def load_json_data(filename):
    """Load data from JSON file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def generate_html_ui():
    """Generate the HTML UI with real data"""
    
    # Load current data
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    trivia_data = load_json_data(os.path.join(data_dir, 'trivia.json'))
    daily_facts_data = load_json_data(os.path.join(data_dir, 'daily_facts.json'))
    leaderboard_data = load_json_data(os.path.join(data_dir, 'leaderboard.json'))
    
    # Get current trivia
    if trivia_data and 'current' in trivia_data:
        current_trivia = trivia_data['current']
        question = current_trivia.get('question', 'Loading question...')
        options = current_trivia.get('options', [])
        correct_answer = current_trivia.get('correct_answer', 0)
        explanation = current_trivia.get('explanation', '')
    else:
        question = "Loading today's trivia..."
        options = ["Loading...", "Loading...", "Loading..."]
        correct_answer = 0
        explanation = ""
    
    # Get WOW fact
    wow_fact = "Loading amazing fact..."
    if daily_facts_data and 'wow_fact' in daily_facts_data:
        wow_fact = daily_facts_data['wow_fact']
    
    # Get daily fact
    daily_fact = "Loading interesting fact..."
    if daily_facts_data and 'daily_fact' in daily_facts_data:
        daily_fact = daily_facts_data['daily_fact']
    
    # Get leaderboard
    leaderboard = []
    if leaderboard_data:
        # Sort by total_correct descending and take top 5
        sorted_leaderboard = sorted(leaderboard_data.items(), 
                                  key=lambda x: x[1]['total_correct'], reverse=True)[:5]
        for i, (player, data) in enumerate(sorted_leaderboard, 1):
            leaderboard.append({
                'rank': i,
                'player': player,
                'score': data['total_correct']
            })
    
    # Get current streak (from leaderboard data)
    current_streak = 0
    if leaderboard_data and GITHUB_USERNAME in leaderboard_data:
        current_streak = leaderboard_data[GITHUB_USERNAME].get('current_streak', 0)
    
    # Generate the HTML
    html_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎯 Daily Trivia Challenge</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}

        .container {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            max-width: 600px;
            width: 100%;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}

        .container::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4, #feca57);
            animation: rainbow 3s ease-in-out infinite;
        }}

        @keyframes rainbow {{
            0%, 100% {{ transform: translateX(0); }}
            50% {{ transform: translateX(100%); }}
        }}

        .header {{
            margin-bottom: 30px;
        }}

        .title {{
            font-size: 2.5em;
            font-weight: bold;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
        }}

        .subtitle {{
            color: #666;
            font-size: 1.1em;
            margin-bottom: 20px;
        }}

        .streak {{
            display: inline-block;
            background: linear-gradient(45deg, #ff6b6b, #ffa726);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            margin-bottom: 20px;
            animation: pulse 2s infinite;
        }}

        @keyframes pulse {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.05); }}
        }}

        .question-card {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            border: 2px solid #f0f0f0;
            transition: all 0.3s ease;
        }}

        .question-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
        }}

        .question {{
            font-size: 1.3em;
            font-weight: 600;
            color: #333;
            margin-bottom: 25px;
            line-height: 1.5;
        }}

        .options {{
            display: grid;
            gap: 15px;
        }}

        .option-btn {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 15px 20px;
            border-radius: 12px;
            font-size: 1.1em;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }}

        .option-btn::before {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
            transition: left 0.5s;
        }}

        .option-btn:hover::before {{
            left: 100%;
        }}

        .option-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        }}

        .option-btn:active {{
            transform: translateY(0);
        }}

        .option-btn.correct {{
            background: linear-gradient(135deg, #4ecdc4, #44a08d);
            animation: correctAnswer 0.6s ease;
        }}

        .option-btn.incorrect {{
            background: linear-gradient(135deg, #ff6b6b, #ee5a52);
            animation: incorrectAnswer 0.6s ease;
        }}

        @keyframes correctAnswer {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.05); }}
        }}

        @keyframes incorrectAnswer {{
            0%, 100% {{ transform: scale(1); }}
            25% {{ transform: scale(0.95); }}
            50% {{ transform: scale(1.05); }}
        }}

        .result {{
            margin-top: 20px;
            padding: 20px;
            border-radius: 12px;
            font-weight: 600;
            display: none;
        }}

        .result.correct {{
            background: linear-gradient(135deg, #4ecdc4, #44a08d);
            color: white;
        }}

        .result.incorrect {{
            background: linear-gradient(135deg, #ff6b6b, #ee5a52);
            color: white;
        }}

        .explanation {{
            margin-top: 15px;
            font-size: 0.95em;
            opacity: 0.9;
        }}

        .leaderboard {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-top: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }}

        .leaderboard h3 {{
            color: #333;
            margin-bottom: 20px;
            font-size: 1.4em;
        }}

        .leaderboard-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid #f0f0f0;
        }}

        .leaderboard-item:last-child {{
            border-bottom: none;
        }}

        .rank {{
            font-weight: bold;
            color: #667eea;
            min-width: 30px;
        }}

        .player {{
            flex: 1;
            text-align: left;
            margin-left: 15px;
        }}

        .score {{
            font-weight: bold;
            color: #333;
        }}

        .facts-section {{
            margin-top: 30px;
            display: grid;
            gap: 20px;
        }}

        .fact-card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            border-left: 4px solid #667eea;
        }}

        .fact-title {{
            font-size: 1.2em;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .fact-content {{
            color: #666;
            line-height: 1.6;
        }}

        .loading {{
            display: none;
            text-align: center;
            padding: 20px;
        }}

        .spinner {{
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 0 auto 15px;
        }}

        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}

        .footer {{
            margin-top: 30px;
            color: #666;
            font-size: 0.9em;
        }}

        .github-link {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            text-decoration: none;
            padding: 12px 24px;
            border-radius: 25px;
            font-weight: 600;
            margin-top: 15px;
            transition: all 0.3s ease;
        }}

        .github-link:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        }}

        @media (max-width: 768px) {{
            .container {{
                padding: 20px;
                margin: 10px;
            }}
            
            .title {{
                font-size: 2em;
            }}
            
            .question {{
                font-size: 1.1em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="title">🎯 Daily Trivia Challenge</h1>
            <p class="subtitle">Test your knowledge with today's AI-generated question!</p>
            <div class="streak">🔥 Current Streak: <span id="streak">{current_streak}</span> days</div>
        </div>

        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>Loading today's trivia...</p>
        </div>

        <div id="trivia-content" style="display: none;">
            <div class="question-card">
                <div class="question" id="question">{question}</div>
                <div class="options" id="options">
                    <!-- Options will be populated here -->
                </div>
                <div class="result" id="result">
                    <div id="result-text"></div>
                    <div class="explanation" id="explanation"></div>
                </div>
            </div>
        </div>

        <div class="facts-section">
            <div class="fact-card">
                <div class="fact-title">
                    <span>🤯</span>
                    WOW Fact of the Day
                </div>
                <div class="fact-content" id="wow-fact">
                    {wow_fact}
                </div>
            </div>

            <div class="fact-card">
                <div class="fact-title">
                    <span>💡</span>
                    Did You Know?
                </div>
                <div class="fact-content" id="daily-fact">
                    {daily_fact}
                </div>
            </div>
        </div>

        <div class="leaderboard">
            <h3>🏆 Leaderboard</h3>
            <div id="leaderboard-content">
                <!-- Leaderboard will be populated here -->
            </div>
        </div>

        <div class="footer">
            <p>🌟 Powered by AI • Updated daily at midnight UTC</p>
            <p>💡 Click an answer to test your knowledge!</p>
            <a href="https://github.com/{GITHUB_USERNAME}/{GITHUB_REPO}" class="github-link" target="_blank">
                🚀 View on GitHub
            </a>
        </div>
    </div>

    <script>
        // Real data from the backend
        const triviaData = {{
            question: `{question}`,
            options: {json.dumps(options)},
            correctAnswer: {correct_answer},
            explanation: `{explanation}`,
            wowFact: `{wow_fact}`,
            dailyFact: `{daily_fact}`,
            streak: {current_streak},
            leaderboard: {json.dumps(leaderboard)}
        }};

        function initializeUI() {{
            // Show loading initially
            document.getElementById('loading').style.display = 'block';
            document.getElementById('trivia-content').style.display = 'none';

            // Simulate loading time
            setTimeout(() => {{
                document.getElementById('loading').style.display = 'none';
                document.getElementById('trivia-content').style.display = 'block';
                
                // Populate question and options
                document.getElementById('question').textContent = triviaData.question;
                document.getElementById('streak').textContent = triviaData.streak;
                document.getElementById('wow-fact').textContent = triviaData.wowFact;
                document.getElementById('daily-fact').textContent = triviaData.dailyFact;

                const optionsContainer = document.getElementById('options');
                optionsContainer.innerHTML = '';

                triviaData.options.forEach((option, index) => {{
                    const button = document.createElement('button');
                    button.className = 'option-btn';
                    button.textContent = option;
                    button.onclick = () => selectAnswer(index);
                    optionsContainer.appendChild(button);
                }});

                // Populate leaderboard
                populateLeaderboard();
            }}, 1500);
        }}

        function selectAnswer(selectedIndex) {{
            const buttons = document.querySelectorAll('.option-btn');
            const result = document.getElementById('result');
            const resultText = document.getElementById('result-text');
            const explanation = document.getElementById('explanation');

            // Disable all buttons
            buttons.forEach(btn => btn.disabled = true);

            // Show result
            if (selectedIndex === triviaData.correctAnswer) {{
                buttons[selectedIndex].classList.add('correct');
                result.className = 'result correct';
                resultText.textContent = '🎉 Correct! Well done!';
                explanation.textContent = triviaData.explanation;
            }} else {{
                buttons[selectedIndex].classList.add('incorrect');
                buttons[triviaData.correctAnswer].classList.add('correct');
                result.className = 'result incorrect';
                resultText.textContent = '❌ Incorrect!';
                explanation.textContent = triviaData.explanation;
            }}

            result.style.display = 'block';

            // Send answer to GitHub (simulate the issue creation)
            const answerLabels = ['A', 'B', 'C'];
            const githubUrl = `https://github.com/{GITHUB_USERNAME}/{GITHUB_REPO}/issues/new?title=Trivia+Answer+${{answerLabels[selectedIndex]}}&body=I+choose+${{answerLabels[selectedIndex]}}`;
            
            // Open GitHub issue in new tab
            setTimeout(() => {{
                window.open(githubUrl, '_blank');
            }}, 2000);
        }}

        function populateLeaderboard() {{
            const leaderboardContent = document.getElementById('leaderboard-content');
            leaderboardContent.innerHTML = '';

            if (triviaData.leaderboard.length === 0) {{
                leaderboardContent.innerHTML = '<p style="color: #666; font-style: italic;">No scores yet. Be the first to play!</p>';
                return;
            }}

            triviaData.leaderboard.forEach(item => {{
                const leaderboardItem = document.createElement('div');
                leaderboardItem.className = 'leaderboard-item';
                leaderboardItem.innerHTML = `
                    <div class="rank">#${{item.rank}}</div>
                    <div class="player">${{item.player}}</div>
                    <div class="score">${{item.score}} pts</div>
                `;
                leaderboardContent.appendChild(leaderboardItem);
            }});
        }}

        // Initialize the UI when the page loads
        document.addEventListener('DOMContentLoaded', initializeUI);
    </script>
</body>
</html>'''
    
    # Write the HTML file
    html_path = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "trivia_ui.html")
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    print("✅ Interactive HTML UI generated successfully!")
    print(f"📁 File: trivia_ui.html")
    print(f"🌐 Open in browser to see the beautiful UI with real buttons!")

if __name__ == "__main__":
    generate_html_ui() 