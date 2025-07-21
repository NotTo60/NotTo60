#!/usr/bin/env python3
"""
Process GitHub issues to score trivia answers and update leaderboard
"""

import json
import os
import re
from datetime import datetime, timedelta, timezone
import requests
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.config import *
from core.database import TriviaDatabase
from core.points_system import calculate_points_for_streak, get_streak_bonus_info, format_points_display
import random
import uuid

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
    """Extract answer choice from issue title and body"""
    title = issue.get('title', '')
    body = issue.get('body', '')
    
    # Look for answer in title
    if 'Trivia Answer A' in title:
        return 'A'
    elif 'Trivia Answer B' in title:
        return 'B'
    elif 'Trivia Answer C' in title:
        return 'C'
    
    # Look for answer in body (new format with actual answer text)
    # First check for letter format
    if '**Answer:** A' in body:
        return 'A'
    elif '**Answer:** B' in body:
        return 'B'
    elif '**Answer:** C' in body:
        return 'C'
    
    # Then check for actual answer text (like "2007", "Jupiter", etc.)
    trivia_data = load_trivia_data()
    current_trivia = trivia_data.get("current", {})
    options = current_trivia.get("options", {})
    
    for option, text in options.items():
        if f'**Answer:** {text}' in body:
            return option
    
    # Look for answer in body (old format)
    if 'I choose A' in body:
        return 'A'
    elif 'I choose B' in body:
        return 'B'
    elif 'I choose C' in body:
        return 'C'
    
    return None

def parse_trivia_date_from_issue(issue):
    body = issue.get('body', '')
    match = re.search(r'\*\*Trivia Date:\*\* ([0-9.]+)', body)
    if match:
        return match.group(1)
    return None

def load_trivia_data():
    """Load current trivia data from database"""
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

def get_utc_today():
    return datetime.now(timezone.utc).strftime(DATE_FORMAT)

def update_user_stats(leaderboard, username, is_correct, trivia_date=None):
    """Update user statistics in leaderboard with trivia date tracking and points system"""
    # Only add new user if correct
    if username not in leaderboard:
        if not is_correct:
            return 0, None  # Do not add user if answer is wrong
        leaderboard[username] = {
            'current_streak': 0,
            'total_correct': 0,
            'total_points': 0,
            'total_answered': 0,
            'last_answered': None,
            'last_trivia_date': None,
            'answer_history': [],
            'first_correct_date': None,  # Track first correct answer date
        }
    
    user_stats = leaderboard[username]
    user_stats['total_answered'] += 1
    user_stats['last_answered'] = datetime.now().isoformat()
    
    # Track which trivia date this answer is for
    if trivia_date:
        user_stats['last_trivia_date'] = trivia_date
    
    # Add to answer history
    answer_record = {
        'date': trivia_date or get_utc_today(),
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
        
        # Set first_correct_date if not already set
        if not user_stats.get('first_correct_date'):
            user_stats['first_correct_date'] = get_utc_today()
        
        # Calculate points with streak bonuses
        points_earned = calculate_points_for_streak(user_stats['current_streak'])
        user_stats['total_points'] += points_earned
        
        # Get bonus info for comment
        bonus_info = get_streak_bonus_info(user_stats['current_streak'])
        return points_earned, bonus_info
    else:
        user_stats['current_streak'] = 0
        return 0, None

def close_issue(issue_number, comment):
    """Close a GitHub issue with a comment"""
    if not GITHUB_TOKEN:
        print("❌ No GitHub token provided, cannot close issue.")
        return
    
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    # Add comment
    comment_url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/issues/{issue_number}/comments"
    resp = requests.post(comment_url, headers=headers, json={'body': comment})
    if resp.status_code >= 300:
        print(f"❌ Failed to comment on issue #{issue_number}: {resp.status_code} {resp.text}")
    else:
        print(f"✅ Commented on issue #{issue_number}")
    
    # Close issue
    close_url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/issues/{issue_number}"
    resp = requests.patch(close_url, headers=headers, json={'state': 'closed'})
    if resp.status_code >= 300:
        print(f"❌ Failed to close issue #{issue_number}: {resp.status_code} {resp.text}")
    else:
        print(f"✅ Closed issue #{issue_number}")

def process_answers():
    """Main function to process all trivia answers"""
    print("🔍 Processing trivia answers...")
    
    # Load data
    trivia_data = load_trivia_data()
    leaderboard = load_leaderboard()
    
    # Build a lookup for trivia by date
    trivia_questions = trivia_data.get("history", [])
    trivia_questions_by_date = {q.get("date"): q for q in trivia_questions}
    if trivia_data.get("current"):
        trivia_questions_by_date[trivia_data["current"].get("date")] = trivia_data["current"]

    # Get GitHub issues
    issues = get_github_issues()
    processed_count = 0
    correct_count = 0
    total_trivia_issues = 0
    
    for issue in issues:
        issue_number = issue['number']
        username = issue['user']['login']
        
        # Only process issues that look like trivia answers
        title = issue.get('title', '')
        if not title.startswith('Trivia Answer'):
            continue
        total_trivia_issues += 1
        
        # Validate username is a UUID
        if not is_valid_uuid(username):
            print(f"⚠️  Skipping user {username}: not a valid UUID")
            continue
        
        answer = parse_answer_from_issue(issue)
        
        if not answer:
            print(f"⚠️  Could not parse answer from issue #{issue_number}")
            continue
        
        # Parse trivia date from issue
        trivia_date = parse_trivia_date_from_issue(issue)
        if not trivia_date or trivia_date not in trivia_questions_by_date:
            print(f"⚠️  Could not determine trivia date for issue #{issue_number}")
            continue
        trivia = trivia_questions_by_date[trivia_date]
        correct_answer = trivia['correct_answer']
        current_trivia_date = trivia_date
        
        # Check if user can answer today's trivia (by date)
        can_answer, reason = can_user_answer_today(leaderboard, username, current_trivia_date)
        
        if not can_answer:
            # User cannot answer, close issue with explanation
            close_issue(issue_number, f"@{username} {reason}! Come back tomorrow for a new question.")
            continue
        
        # Process answer
        is_correct = answer == correct_answer
        points_earned, bonus_info = update_user_stats(leaderboard, username, is_correct, current_trivia_date)
        
        if is_correct:
            correct_count += 1
        
        # Create response comment with points system
        if is_correct:
            correct_message = random.choice(CORRECT_MESSAGES)
            streak = leaderboard[username]['current_streak']
            points_display = format_points_display(points_earned)
            
            comment = f"""{correct_message} @{username}

Your answer **{answer}) {trivia['options'][answer]}** is absolutely right!

**Explanation:** {trivia['explanation']}

🔥 Your current streak: **{streak}**
✅ Total correct answers: **{leaderboard[username]['total_correct']}**
🏆 Points earned: **{points_display}**
💎 Total points: **{leaderboard[username]['total_points']}**"""
            
            # Add bonus information
            if bonus_info and (bonus_info['has_3_day_bonus'] or bonus_info['has_6_day_bonus']):
                comment += "\n\n🎉 **Streak Bonuses:**\n"
                if bonus_info['has_3_day_bonus']:
                    comment += "• +1 point for 3-day streak! 🏆\n"
                if bonus_info['has_6_day_bonus']:
                    comment += "• +1 point for 6-day streak! 🏆\n"
            # Show next milestone
            if bonus_info['next_3_day_bonus'] > 0:
                comment += f"\n🎯 **Next 3-day bonus:** {bonus_info['next_3_day_bonus']} more day(s)\n"
            if bonus_info['next_6_day_bonus'] > 0:
                comment += f"🎯 **Next 6-day bonus:** {bonus_info['next_6_day_bonus']} more day(s)\n"
            comment += "\nAt 6, 12, 18, ... you get both bonuses for a total of 3 points!"
            comment += "\nCome back tomorrow for another AMAZING question!"
        else:
            incorrect_message = random.choice(INCORRECT_MESSAGES)
            comment = f"""{incorrect_message} @{username}

Your answer **{answer}) {trivia['options'][answer]}** was wrong.

**Correct Answer:** {correct_answer}) {trivia['options'][correct_answer]}

**Explanation:** {trivia['explanation']}

💔 Your streak has reset to 0, but don't give up!

Come back tomorrow for another chance!"""
        
        # Close issue with comment
        close_issue(issue_number, comment)
        processed_count += 1
    
    # Save updated leaderboard
    save_leaderboard(leaderboard)
    print(f"🧾 Total trivia answer issues found: {total_trivia_issues}")
    print(f"✅ Processed {processed_count} answers (Correct: {correct_count})")

def main():
    """Main function"""
    process_answers()

if __name__ == "__main__":
    main() 