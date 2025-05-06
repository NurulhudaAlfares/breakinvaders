"""
State Manager Module

This module contains functions for managing game states and transitions.
"""

import time
from .game_states import *

def check_weekly_leaderboard(weekly_stats, current_state):
    """
    Check if it's time to show the weekly leaderboard.
    
    Args:
        weekly_stats (dict): Weekly statistics
        current_state (str): Current game state
        
    Returns:
        tuple: (show_leaderboard, new_state)
    """
    # Check if a week has passed since last leaderboard check
    current_time = time.time()
    one_week_seconds = 7 * 24 * 60 * 60
    
    if current_time - weekly_stats.get("last_leaderboard_check", 0) >= one_week_seconds:
        weekly_stats["last_leaderboard_check"] = current_time
        return True, STATE_LEADERBOARD_MINI
    return False, current_state

def handle_break_reminder(current_state, current_time, last_break_reminder, dynamic_break_threshold, ignore_duration_threshold, weekly_stats):
    """
    Handle the break reminder state.
    
    Args:
        current_state (str): Current game state
        current_time (float): Current time
        last_break_reminder (float): Time of last break reminder
        dynamic_break_threshold (float): Dynamic break threshold
        ignore_duration_threshold (float): Threshold for enforced cooldown
        weekly_stats (dict): Weekly statistics
        
    Returns:
        str: New game state
    """
    if current_state == STATE_BREAK_REMINDER:
        # If player has been ignoring breaks for too long
        if current_time - last_break_reminder >= ignore_duration_threshold:
            return STATE_ENFORCED_COOLDOWN
    return current_state

def handle_break_taken(current_state, current_time, break_start_time, break_duration, play_start_time, last_break_reminder,
                      cooldown_intensity, breaks_ignored_count, hide_progression, hide_score, black_and_white,
                      explosion_fx, explosion2_fx, laser_fx, base_explosion_volume, base_explosion2_volume, base_laser_volume,
                      spaceship_group, spaceship):
    """
    Handle the break taken state.
    
    Args:
        Various state parameters
        
    Returns:
        tuple: Updated state values
    """
    if current_state == STATE_BREAK_TAKEN:
        # Check if break duration has passed
        if current_time - break_start_time >= break_duration:
            # Reset game state
            current_state = STATE_NORMAL_PLAY
            play_start_time = current_time
            last_break_reminder = current_time
            cooldown_intensity = 0
            breaks_ignored_count = 0
            hide_progression = False
            hide_score = False
            black_and_white = False
            
            # Reset sound volumes
            explosion_fx.set_volume(base_explosion_volume)
            explosion2_fx.set_volume(base_explosion2_volume)
            laser_fx.set_volume(base_laser_volume)
            
            # Add spaceship back if needed
            if len(spaceship_group) == 0 and spaceship.health_remaining > 0:
                spaceship_group.add(spaceship)
    
    return (current_state, play_start_time, last_break_reminder, cooldown_intensity,
            breaks_ignored_count, hide_progression, hide_score, black_and_white)

def handle_enforced_cooldown(current_state, current_time, break_start_time, break_duration, cooldown_start_time,
                           spaceship_group, spaceship):
    """
    Handle the enforced cooldown state.
    
    Args:
        Various state parameters
        
    Returns:
        tuple: (new_state, cooldown_start_time)
    """
    if current_state == STATE_ENFORCED_COOLDOWN:
        # Check if enforced break duration has passed
        if current_time - break_start_time >= break_duration:
            current_state = STATE_COOLDOWN_ACTIVE
            cooldown_start_time = current_time
            
            # Add spaceship back if needed
            if len(spaceship_group) == 0 and spaceship.health_remaining > 0:
                spaceship_group.add(spaceship)
    
    return current_state, cooldown_start_time

def handle_cooldown_active(current_state, current_time, cooldown_start_time, ignore_duration_threshold, break_start_time, weekly_stats):
    """
    Handle the cooldown active state.
    
    Args:
        Various state parameters
        
    Returns:
        tuple: (new_state, break_start_time)
    """
    if current_state == STATE_COOLDOWN_ACTIVE:
        # Check if cooldown duration has passed
        if current_time - cooldown_start_time >= ignore_duration_threshold:
            current_state = STATE_BREAK_TAKEN
            break_start_time = current_time
            weekly_stats["breaks_taken"] += 1
    
    return current_state, break_start_time 