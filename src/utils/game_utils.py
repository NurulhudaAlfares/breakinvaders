"""
Game Utilities Module

This module contains utility functions for the game.
"""

import pygame
import json
import os
import time

def draw_text(screen, text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def draw_bg(screen, bg):
    screen.blit(bg, (0, 0))

def draw_progression_info(screen, font30, font20, yellow, white, current_level, max_level_reached, alien_group, rows, cols):
    # Draw level info at top right
    level_text = f"LEVEL: {current_level}"
    draw_text(screen, level_text, font30, yellow, screen.get_width() - 150, 30)
    
    # Draw max level reached
    max_level_text = f"MAX LEVEL: {max_level_reached}"
    draw_text(screen, max_level_text, font20, white, screen.get_width() - 150, 60)
    
    # Draw aliens remaining
    aliens_text = f"Aliens: {len(alien_group)}/{rows*cols}"
    draw_text(screen, aliens_text, font20, white, screen.get_width() - 150, 90)

def load_leaderboard():
    """
    Load the weekly leaderboard data.
    
    Returns:
        dict: Dictionary containing weekly statistics
    """
    try:
        with open('weekly_stats.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Return default stats if file doesn't exist or is corrupted
        return {
            "high_score": 0,
            "total_play_time": 0,
            "games_played": 0,
            "max_level": 1,
            "breaks_taken": 0,
            "breaks_ignored": 0,
            "last_leaderboard_check": time.time()
        }

def save_leaderboard(weekly_stats):
    """
    Save the weekly leaderboard data.
    
    Args:
        weekly_stats (dict): Dictionary containing weekly statistics
    """
    with open('weekly_stats.json', 'w') as f:
        json.dump(weekly_stats, f)

def check_weekly_leaderboard(weekly_stats, current_state):
    # Check if a week has passed since last leaderboard check
    current_time = time.time()
    one_week_seconds = 7 * 24 * 60 * 60
    
    if current_time - weekly_stats["last_leaderboard_check"] >= one_week_seconds:
        weekly_stats["last_leaderboard_check"] = current_time
        save_leaderboard(weekly_stats)
        current_state = "LeaderboardMini"
        return True, current_state
    return False, current_state

def initialize_break_threshold():
    """
    Initialize the break threshold based on session data.
    
    Returns:
        float: Initial break threshold in seconds
    """
    try:
        if os.path.exists('session_data.json'):
            with open('session_data.json', 'r') as f:
                session_data = json.load(f)
                if session_data:
                    # Use 60% of average session duration as threshold
                    return sum(session_data) / len(session_data) * 0.6
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    
    # Default to 20 minutes if no session data
    return 20 * 60

def save_session_duration(session_start_time):
    """
    Save the duration of the current session.
    
    Args:
        session_start_time (float): Start time of the session
    """
    session_duration = time.time() - session_start_time
    
    try:
        # Load existing session data
        if os.path.exists('session_data.json'):
            with open('session_data.json', 'r') as f:
                session_data = json.load(f)
        else:
            session_data = []
            
        # Add new session duration
        session_data.append(session_duration)
        
        # Keep only last 10 sessions
        if len(session_data) > 10:
            session_data = session_data[-10:]
            
        # Save updated session data
        with open('session_data.json', 'w') as f:
            json.dump(session_data, f)
            
    except (FileNotFoundError, json.JSONDecodeError):
        # If file doesn't exist or is corrupted, create new one
        with open('session_data.json', 'w') as f:
            json.dump([session_duration], f)

def save_game_stats(weekly_stats, session_start_time, score):
    """
    Save game statistics and update weekly stats.
    
    Args:
        weekly_stats (dict): Weekly statistics dictionary
        session_start_time (float): Start time of the session
        score (int): Current game score
    """
    # Update high score if necessary
    if score > weekly_stats["high_score"]:
        weekly_stats["high_score"] = score
    
    # Save weekly stats
    save_leaderboard(weekly_stats)
    
    # Update total play time
    session_duration = time.time() - session_start_time
    weekly_stats["total_play_time"] += int(session_duration)

    # Save to game_data.json
    try:
        if os.path.exists('game_data.json'):
            with open('game_data.json', 'r') as f:
                game_data = json.load(f)
        else:
            game_data = []
        
        # Add new game stats
        game_data.append({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "mode": "normal" if weekly_stats.get("breaks_taken", 0) == 0 else "break-aware",
            "duration": session_duration,
            "took_break": weekly_stats.get("breaks_taken", 0) > 0,
            "level": weekly_stats.get("max_level", 1),
            "breaks_ignored": weekly_stats.get("breaks_ignored", 0)
        })
        
        with open('game_data.json', 'w') as f:
            json.dump(game_data, f, indent=2)
    except (FileNotFoundError, json.JSONDecodeError):
        # If file doesn't exist or is corrupted, create new
        with open('game_data.json', 'w') as f:
            json.dump([{
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "mode": "normal" if weekly_stats.get("breaks_taken", 0) == 0 else "break-aware",
                "duration": session_duration,
                "took_break": weekly_stats.get("breaks_taken", 0) > 0,
                "level": weekly_stats.get("max_level", 1),
                "breaks_ignored": weekly_stats.get("breaks_ignored", 0)
            }], f, indent=2) 