#!/usr/bin/env python3
"""
Points System Module - Handles streak bonuses and point calculations
"""

def calculate_points_for_streak(streak):
    """
    Calculate points based on streak length with new bonus system:
    - 1 point for correct answer
    - +1 bonus point for every 3-day streak (3, 6, 9, ...)
    - +1 bonus point for every 6-day streak (6, 12, 18, ...)
    - At 6, 12, 18, ... you get +1 (for 3) and +1 (for 6), so total 3 points at 6, 12, ...
    """
    if streak <= 0:
        return 0
    points = 1
    if streak % 3 == 0:
        points += 1
    if streak % 6 == 0:
        points += 1
    return points

def get_streak_bonus_info(streak):
    """
    Get information about current streak and next bonus milestones for 3 and 6 day streaks
    """
    current_points = calculate_points_for_streak(streak)
    # Next 3-day bonus
    if streak % 3 == 0:
        next_3_day = 3
    else:
        next_3_day = 3 - (streak % 3)
    # Next 6-day bonus
    if streak % 6 == 0:
        next_6_day = 6
    else:
        next_6_day = 6 - (streak % 6)
    return {
        'current_points': current_points,
        'next_3_day_bonus': next_3_day,
        'next_6_day_bonus': next_6_day,
        'has_3_day_bonus': streak % 3 == 0 and streak > 0,
        'has_6_day_bonus': streak % 6 == 0 and streak > 0
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