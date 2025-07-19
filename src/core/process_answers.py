#!/usr/bin/env python3
"""
Process GitHub issues to score trivia answers and update leaderboard
"""

import json
import os
import re
from datetime import datetime, timedelta
import requests
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.config import *
import random

def get_github_issues():
    """Fetch recent trivia answer issues from GitHub"""
    if not GITHUB_TOKEN:
        print("⚠️  No GitHub token provided, skipping answer processing")
        return []
    
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/issues"
    params = {
        'state': 'open',
        'labels': ISSUE_LABEL,
        'per_page': 100
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching issues: {e}")
        return []

def parse_answer_from_issue(issue):
    """Extract answer choice from issue title"""
    title = issue.get('title', '')
    body = issue.get('body', '')
    
    # Look for answer in title
    if 'Trivia Answer A' in title:
        return 'A'
    elif 'Trivia Answer B' in title:
        return 'B'
    elif 'Trivia Answer C' in title:
        return 'C'
    
    # Look for answer in body
    if 'I choose A' in body:
        return 'A'
    elif 'I choose B' in body:
        return 'B'
    elif 'I choose C' in body:
        return 'C'
    
    return None

def load_trivia_data():
    """Load current trivia data"""
    if os.path.exists(TRIVIA_FILE):
        with open(TRIVIA_FILE, 'r') as f:
            return json.load(f)
    return {"current": None, "history": []}

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

def can_user_answer_today(leaderboard, username, current_trivia_date):
    """Check if user can answer today's trivia with timezone and grace period handling"""
    user_stats = leaderboard.get(username, {})
    last_trivia_date = user_stats.get('last_trivia_date')
    
    # If user has never answered, they can answer
    if not last_trivia_date:
        return True, None
    
    # If user already answered this exact trivia date, they cannot answer again
    if last_trivia_date == current_trivia_date:
        return False, f"Already answered trivia for {current_trivia_date}"
    
    # Check if user answered recently (grace period for timezone differences)
    last_answered = user_stats.get('last_answered')
    if last_answered:
        try:
            last_time = datetime.fromisoformat(last_answered)
            current_time = datetime.now()
            time_diff = current_time - last_time
            
            # If answered within grace period and it's the same calendar day, prevent duplicate
            if time_diff < timedelta(hours=GRACE_PERIOD_HOURS):
                last_date = last_time.date()
                current_date = current_time.date()
                if last_date == current_date:
                    return False, f"Answered recently (within {GRACE_PERIOD_HOURS} hours grace period)"
        except Exception as e:
            print(f"Error parsing last_answered time for {username}: {e}")
    
    return True, None

def update_user_stats(leaderboard, username, is_correct, trivia_date=None):
    """Update user statistics in leaderboard with trivia date tracking"""
    if username not in leaderboard:
        leaderboard[username] = {
            'current_streak': 0,
            'total_correct': 0,
            'total_answered': 0,
            'last_answered': None,
            'last_trivia_date': None,
            'answer_history': []
        }
    
    user_stats = leaderboard[username]
    user_stats['total_answered'] += 1
    user_stats['last_answered'] = datetime.now().isoformat()
    
    # Track which trivia date this answer is for
    if trivia_date:
        user_stats['last_trivia_date'] = trivia_date
    
    # Add to answer history
    answer_record = {
        'date': trivia_date or datetime.now().strftime(DATE_FORMAT),
        'timestamp': datetime.now().isoformat(),
        'correct': is_correct
    }
    user_stats['answer_history'].append(answer_record)
    
    # Keep only last 30 days of history
    if len(user_stats['answer_history']) > 30:
        user_stats['answer_history'] = user_stats['answer_history'][-30:]
    
    if is_correct:
        user_stats['current_streak'] += 1
        user_stats['total_correct'] += 1
    else:
        user_stats['current_streak'] = 0

def close_issue(issue_number, comment):
    """Close a GitHub issue with a comment"""
    if not GITHUB_TOKEN:
        return
    
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    # Add comment
    comment_url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/issues/{issue_number}/comments"
    requests.post(comment_url, headers=headers, json={'body': comment})
    
    # Close issue
    close_url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/issues/{issue_number}"
    requests.patch(close_url, headers=headers, json={'state': 'closed'})

def process_answers():
    """Main function to process all trivia answers"""
    print("🔍 Processing trivia answers...")
    
    # Load data
    trivia_data = load_trivia_data()
    leaderboard = load_leaderboard()
    
    current_trivia = trivia_data.get("current")
    if not current_trivia:
        print("❌ No current trivia found")
        return
    
    correct_answer = current_trivia['correct_answer']
    current_trivia_date = current_trivia.get('date', datetime.now().strftime(DATE_FORMAT))
    
    # Get GitHub issues
    issues = get_github_issues()
    processed_count = 0
    
    for issue in issues:
        issue_number = issue['number']
        username = issue['user']['login']
        answer = parse_answer_from_issue(issue)
        
        if not answer:
            print(f"⚠️  Could not parse answer from issue #{issue_number}")
            continue
        
        # Check if user can answer today's trivia
        can_answer, reason = can_user_answer_today(leaderboard, username, current_trivia_date)
        
        if not can_answer:
            # User cannot answer, close issue with explanation
            close_issue(issue_number, f"@{username} {reason}! Come back tomorrow for a new question.")
            continue
        
        # Process answer
        is_correct = answer == correct_answer
        update_user_stats(leaderboard, username, is_correct, current_trivia_date)
        
        # Get WOW fact if available
        wow_fact = current_trivia.get('wow_fact', '')
        wow_fact_display = f"\n\n{wow_fact}" if wow_fact else ""
        
        # Create response comment with WOW effect
        if is_correct:
            correct_message = random.choice(CORRECT_MESSAGES)
            comment = f"""{correct_message} @{username}

Your answer **{answer}) {current_trivia['options'][answer]}** is absolutely right!

**Explanation:** {current_trivia['explanation']}{wow_fact_display}

🔥 Your current streak: **{leaderboard[username]['current_streak']}**
✅ Total correct answers: **{leaderboard[username]['total_correct']}**

Come back tomorrow for another AMAZING question!"""
        else:
            incorrect_message = random.choice(INCORRECT_MESSAGES)
            comment = f"""{incorrect_message} @{username}

Your answer **{answer}) {current_trivia['options'][answer]}** was wrong.

**Correct Answer:** {correct_answer}) {current_trivia['options'][correct_answer]}

**Explanation:** {current_trivia['explanation']}{wow_fact_display}

💔 Your streak has reset to 0, but don't give up!

Come back tomorrow for another chance!"""
        
        # Close issue with comment
        close_issue(issue_number, comment)
        processed_count += 1
    
    # Save updated leaderboard
    save_leaderboard(leaderboard)
    print(f"✅ Processed {processed_count} answers")

def main():
    """Main function"""
    process_answers()

if __name__ == "__main__":
    main() 