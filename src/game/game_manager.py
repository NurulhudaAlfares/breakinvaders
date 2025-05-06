"""
Game Manager Module

This module contains functions for managing game state and setup.
"""

import pygame
import time
import json
import os
from src.game.spaceship import Spaceship
from src.game.aliens import Aliens
from src.utils.game_utils import save_leaderboard, save_session_duration, save_game_stats

def create_aliens(alien_group, current_level, screen_width):
    """
    Create aliens for the current level.
    
    Args:
        alien_group (pygame.sprite.Group): Group to add aliens to
        current_level (int): Current game level
        screen_width (int): Width of the game screen
        
    Returns:
        tuple: Number of rows and columns of aliens
    """
    rows = 5
    cols = 5
    
    # Clear any existing aliens
    alien_group.empty()
    
    # Create aliens
    for row in range(rows):
        for item in range(cols):
            alien = Aliens(100 + item * 100, 100 + row * 70, current_level)
            alien_group.add(alien)
            
    return rows, cols

def reset_game(game_over, countdown, score, current_state, play_start_time, spaceship, spaceship_group,
               last_break_reminder, game_over_time, bullet_group, alien_group, alien_bullet_group,
               explosion_group, screen_width, screen_height, current_level, weekly_stats):
    """
    Reset the game state for a new game.
    
    Args:
        Various game state parameters
        
    Returns:
        tuple: Updated game state values
    """
    # Reset game state
    game_over = 0
    countdown = 3
    score = 0
    current_state = "NormalPlay"
    play_start_time = pygame.time.get_ticks()
    
    # Reset spaceship
    spaceship.health_remaining = 3
    spaceship.rect.center = [int(screen_width / 2), screen_height - 100]
    spaceship_group.add(spaceship)
    
    # Reset timers
    last_break_reminder = play_start_time
    game_over_time = 0
    
    # Clear sprite groups
    bullet_group.empty()
    alien_group.empty()
    alien_bullet_group.empty()
    explosion_group.empty()
    
    # Create new aliens
    create_aliens(alien_group, current_level, screen_width)
    
    return (game_over, countdown, score, current_state, play_start_time, spaceship,
            last_break_reminder, game_over_time)

def save_game_state(weekly_stats, session_start_time, score):
    """
    Save the game state and update statistics.
    
    Args:
        weekly_stats (dict): Weekly statistics
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