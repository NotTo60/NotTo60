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
import logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=2, max=10), retry=retry_if_exception_type(Exception))
def requests_with_retries(method, *args, **kwargs):
    import requests
    try:
        resp = getattr(requests, method)(*args, **kwargs)
        if resp.status_code == 429:
            logging.error("[process_answers.py] [requests_with_retries] GitHub API rate limit hit (429). Retrying...")
        elif 500 <= resp.status_code < 600:
            logging.error(f"[process_answers.py] [requests_with_retries] GitHub API server error ({resp.status_code}). Retrying...")
        return resp
    except Exception as e:
        logging.error(f"[process_answers.py] [requests_with_retries] Exception: {e}")
        raise

def get_github_issues():
    """Fetch recent trivia answer issues from GitHub"""
    if not GITHUB_TOKEN:
        logging.warning("[process_answers.py] [get_github_issues] No GitHub token provided, skipping answer processing")
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
        response = requests_with_retries('get', url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.error("[process_answers.py] [get_github_issues] API failed after retries: %s", e)
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
    import re
    # Try bold markdown first (DD.MM.YYYY or YYYY-MM-DD)
    match = re.search(r'\*\*Trivia Date:\*\*\s*([0-9.\-]+)', body)
    if match:
        return match.group(1)
    # Fallback: plain text (DD.MM.YYYY or YYYY-MM-DD)
    match = re.search(r'Trivia Date:\s*([0-9.\-]+)', body)
    if match:
        return match.group(1)
    # Try to find any date-like string (YYYY-MM-DD or DD.MM.YYYY)
    match = re.search(r'([0-9]{4}-[0-9]{2}-[0-9]{2})', body)
    if match:
        return match.group(1)
    match = re.search(r'([0-9]{2}\.[0-9]{2}\.[0-9]{4})', body)
    if match:
        return match.group(1)
    logging.warning(f"[process_answers.py] [parse_trivia_date_from_issue] Could not find trivia date in issue body for issue #{issue.get('number', '?')}: {body}")
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
        logging.error("[process_answers.py] [load_trivia_data] Error loading trivia data from database: %s", e)
        # Return empty data structure as fallback
        return {"current": None, "history": []}

def load_leaderboard():
    """Load leaderboard data from database"""
    try:
        db = TriviaDatabase()
        return db.get_leaderboard()
    except Exception as e:
        logging.error("[process_answers.py] [load_leaderboard] Error loading leaderboard from database: %s", e)
        # Return empty leaderboard as fallback
        return {}

def save_leaderboard(leaderboard):
    """Save leaderboard data to database"""
    try:
        db = TriviaDatabase()
        db.update_leaderboard(leaderboard)
        db.export_compressed_data()
    except Exception as e:
        logging.error("[process_answers.py] [save_leaderboard] Error saving leaderboard to database: %s", e)
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
            logging.error("[process_answers.py] [can_user_answer_today] Error parsing last_answered time for %s: %s", username, e)
    
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
        logging.error("[process_answers.py] [close_issue] No GitHub token provided, cannot close issue.")
        return
    
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    # Add comment
    comment_url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/issues/{issue_number}/comments"
    try:
        resp = requests_with_retries('post', comment_url, headers=headers, json={'body': comment})
        resp.raise_for_status()
        logging.info("[process_answers.py] [close_issue] Commented on issue #%s", issue_number)
    except Exception as e:
        logging.error("[process_answers.py] [close_issue] API failed after retries (comment): %s", e)
    
    # Close issue
    close_url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/issues/{issue_number}"
    try:
        resp = requests_with_retries('patch', close_url, headers=headers, json={'state': 'closed'})
        resp.raise_for_status()
        logging.info("[process_answers.py] [close_issue] Closed issue #%s", issue_number)
    except Exception as e:
        logging.error("[process_answers.py] [close_issue] API failed after retries (close): %s", e)

def mark_unplanned_issues(issues, processed_issue_numbers):
    """Mark any remaining open issues as unplanned for the next day and close them."""
    for issue in issues:
        issue_number = issue['number']
        if issue_number in processed_issue_numbers:
            continue
        username = issue['user']['login']
        comment = (
            f"@{username} This issue could not be processed for today's trivia (invalid format, wrong date, or other error). "
            "It will be marked as unplanned and closed. Please submit a new answer for the next trivia!"
        )
        close_issue(issue_number, comment)

def process_answers():
    """Main function to process all trivia answers"""
    logging.info("[process_answers.py] [process_answers] Starting trivia answer processing.")
    
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
    processed_issue_numbers = set()
    
    for issue in issues:
        issue_number = issue['number']
        username = issue['user']['login']
        
        # Only process issues that look like trivia answers
        title = issue.get('title', '')
        if not title.startswith('Trivia Answer'):
            continue
        total_trivia_issues += 1
        
        answer = parse_answer_from_issue(issue)
        
        if not answer:
            logging.warning("[process_answers.py] [process_answers] Could not parse answer from issue #%s", issue_number)
            continue
        
        # Parse trivia date from issue
        trivia_date = parse_trivia_date_from_issue(issue)
        if not trivia_date or trivia_date not in trivia_questions_by_date:
            logging.warning("[process_answers.py] [process_answers] Could not determine trivia date for issue #%s", issue_number)
            continue
        trivia = trivia_questions_by_date[trivia_date]
        correct_answer = trivia['correct_answer']
        current_trivia_date = trivia_date
        
        # Check if user already answered this trivia date
        user_stats = leaderboard.get(username, {})
        if user_stats.get('last_trivia_date') == current_trivia_date:
            close_issue(issue_number, f"@{username} You have already submitted an answer for today's trivia. Only one answer per user per day is allowed!")
            continue
        
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
        processed_issue_numbers.add(issue_number)
    
    # Remove users with 0 total_answered
    to_remove = [user for user, stats in leaderboard.items() if stats.get('total_answered', 0) == 0]
    for user in to_remove:
        del leaderboard[user]

    # Remove users with 0 total_correct (never got a right answer)
    to_remove_zero_correct = [user for user, stats in leaderboard.items() if stats.get('total_correct', 0) == 0]
    for user in to_remove_zero_correct:
        del leaderboard[user]
    if to_remove_zero_correct:
        logging.debug("[process_answers.py] [process_answers] Removed users with 0 correct answers: %s", to_remove_zero_correct)

    # Save updated leaderboard
    save_leaderboard(leaderboard)
    logging.info("[process_answers.py] [process_answers] Processed trivia answer issues found: %s", total_trivia_issues)
    logging.info("[process_answers.py] [process_answers] Processed %s answers (Correct: %s)", processed_count, correct_count)
    logging.debug("[process_answers.py] [process_answers] Removed users with 0 answers: %s", to_remove)

    # After processing, mark and close any remaining open issues
    mark_unplanned_issues(issues, processed_issue_numbers)
    logging.info("[process_answers.py] [process_answers] Finished trivia answer processing.")

def main():
    """Main function"""
    process_answers()

if __name__ == "__main__":
    main() 