#!/usr/bin/env python3
"""
Points System Module - Handles streak bonuses and point calculations
"""

def calculate_points_for_streak(streak):
    """
    Calculate points based on streak length with bonus system:
    - 1 point for correct answer
    - +1 bonus point for 3-day streak
    - +1 bonus point for 7-day streak (total 3 points for 7th day)
    - After 7 days, cycle repeats: +1 for 10-day streak, +1 for 14-day streak, etc.
    """
    if streak <= 0:
        return 0
    
    # Base point for correct answer
    points = 1
    
    # Calculate bonus points based on streak milestones
    # 3-day milestone bonus
    if streak >= 3:
        points += 1
    
    # 7-day milestone bonus (and every 7 days after)
    if streak % 7 == 0:
        points += 1
    
    return points

def get_streak_bonus_info(streak):
    """
    Get information about current streak and next bonus milestones
    """
    current_points = calculate_points_for_streak(streak)
    next_3_day = max(0, 3 - streak) if streak < 3 else 0
    next_7_day = max(0, 7 - (streak % 7)) if streak % 7 != 0 else 0
    
    if streak >= 7:
        next_7_day = 7  # After 7 days, next 7-day bonus is in 7 more days
    
    return {
        'current_points': current_points,
        'next_3_day_bonus': next_3_day,
        'next_7_day_bonus': next_7_day,
        'has_3_day_bonus': streak >= 3,
        'has_7_day_bonus': streak % 7 == 0 and streak > 0
    }

def format_points_display(points):
    """Format points for display in leaderboard"""
    if points == 1:
        return "1 point"
    else:
        return f"{points} points"

def get_streak_emoji(streak):
    """Get appropriate emoji for streak length"""
    if streak == 0:
        return "❄️"
    elif streak < 3:
        return "🔥"
    elif streak < 7:
        return "🔥🔥"
    elif streak < 14:
        return "🔥🔥🔥"
    elif streak < 21:
        return "🔥🔥🔥🔥"
    else:
        return "🔥🔥🔥🔥🔥" 