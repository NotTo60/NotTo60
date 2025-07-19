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
    - Pattern repeats every 7 days: 10-day = +1, 13-day = +1, 17-day = +1, 20-day = +1, etc.
    - Example: Day 3=2pts, Day 7=3pts, Day 10=2pts, Day 13=2pts, Day 14=3pts, Day 17=2pts, Day 20=2pts
    """
    if streak <= 0:
        return 0
    
    # Base point for correct answer
    points = 1
    
    # Calculate bonus points based on streak milestones
    # 3-day milestone bonus (3, 10, 13, 17, 20, 24, 27, etc.)
    if streak == 3 or (streak > 7 and (streak - 3) % 7 == 0) or (streak > 7 and (streak - 6) % 7 == 0):
        points += 1
    
    # 7-day milestone bonus (and every 7 days after: 14, 21, 28, etc.)
    if streak % 7 == 0:
        points += 1
    
    return points

def get_streak_bonus_info(streak):
    """
    Get information about current streak and next bonus milestones
    """
    current_points = calculate_points_for_streak(streak)
    
    # Find next 3-day bonus (3, 10, 17, 24, etc.)
    next_3_day = 0
    if streak < 3:
        next_3_day = 3 - streak
    elif streak < 10:
        next_3_day = 10 - streak
    else:
        # Find next 3-day bonus in the cycle
        cycle_position = (streak - 3) % 7
        next_3_day = 7 - cycle_position
    
    # Find next 7-day bonus
    next_7_day = max(0, 7 - (streak % 7)) if streak % 7 != 0 else 7
    
    return {
        'current_points': current_points,
        'next_3_day_bonus': next_3_day,
        'next_7_day_bonus': next_7_day,
        'has_3_day_bonus': streak == 3 or (streak > 7 and (streak - 3) % 7 == 0),
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