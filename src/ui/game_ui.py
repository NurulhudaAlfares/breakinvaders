"""
Game UI Module

This module contains functions for drawing game UI elements.
"""

import pygame
import random
from .button import Button

def draw_text(screen, text, font, text_col, x, y):
    """Draw text on the screen."""
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def draw_bg(screen, bg):
    """Draw the background."""
    screen.blit(bg, (0, 0))

def draw_progression_info(screen, font30, font20, yellow, white, current_level, max_level_reached, alien_group, rows, cols):
    """Draw progression information."""
    # Draw level info at top right
    level_text = f"LEVEL: {current_level}"
    draw_text(screen, level_text, font30, yellow, screen.get_width() - 150, 30)
    
    # Draw max level reached
    max_level_text = f"MAX LEVEL: {max_level_reached}"
    draw_text(screen, max_level_text, font20, white, screen.get_width() - 150, 60)
    
    # Draw aliens remaining
    aliens_text = f"Aliens: {len(alien_group)}/{rows*cols}"
    draw_text(screen, aliens_text, font20, white, screen.get_width() - 150, 90)

def draw_mode_selection(screen, font40, font30, font20, white, normal_button, break_aware_button):
    """Draw mode selection screen."""
    # Draw title
    draw_text(screen, "SELECT GAME MODE", font40, white, screen.get_width()//2 - 180, screen.get_height()//2 - 100)
    
    # Draw mode descriptions
    draw_text(screen, "Normal Mode: Classic gameplay", font20, white, screen.get_width()//2 - 150, screen.get_height()//2 - 40)
    draw_text(screen, "Break-Aware Mode: Encourages healthy gaming habits", font20, white, screen.get_width()//2 - 150, screen.get_height()//2 + 30)
    
    # Draw buttons
    normal_button.draw(screen, font30, white)
    break_aware_button.draw(screen, font30, white)

def draw_leaderboard(screen, font40, font30, font20, yellow, white, weekly_stats):
    """Draw leaderboard screen."""
    # Draw title
    draw_text(screen, "WEEKLY STATS", font40, yellow, screen.get_width()//2 - 150, 50)
    
    # Draw stats
    y_pos = 150
    draw_text(screen, f"High Score: {weekly_stats['high_score']}", font30, white, screen.get_width()//2 - 150, y_pos)
    y_pos += 50
    draw_text(screen, f"Games Played: {weekly_stats['games_played']}", font30, white, screen.get_width()//2 - 150, y_pos)
    y_pos += 50
    draw_text(screen, f"Max Level: {weekly_stats['max_level']}", font30, white, screen.get_width()//2 - 150, y_pos)
    y_pos += 50
    draw_text(screen, f"Breaks Taken: {weekly_stats['breaks_taken']}", font30, white, screen.get_width()//2 - 150, y_pos)
    y_pos += 50
    draw_text(screen, f"Breaks Ignored: {weekly_stats['breaks_ignored']}", font30, white, screen.get_width()//2 - 150, y_pos)
    
    # Draw instruction
    draw_text(screen, "Press any key to continue", font20, yellow, screen.get_width()//2 - 120, screen.get_height() - 50)

def draw_break_reminder(screen, font40, font20, white, current_break_message, break_messages, take_break_button, ignore_break_button):
    """Draw break reminder screen."""
    # Create semi-transparent overlay
    overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))  # Semi-transparent black
    screen.blit(overlay, (0, 0))
    
    # Draw title
    draw_text(screen, "BREAK TIME!", font40, white, screen.get_width()//2 - 100, screen.get_height()//2 - 150)
    
    # Select and draw random message if none is set
    if not current_break_message:
        current_break_message = random.choice(break_messages)
    
    # Draw message with word wrap
    words = current_break_message.split()
    lines = []
    current_line = []
    for word in words:
        current_line.append(word)
        test_line = " ".join(current_line)
        if font20.size(test_line)[0] > screen.get_width() - 200:
            current_line.pop()
            lines.append(" ".join(current_line))
            current_line = [word]
    if current_line:
        lines.append(" ".join(current_line))
    
    y_pos = screen.get_height()//2 - 80
    for line in lines:
        draw_text(screen, line, font20, white, screen.get_width()//2 - 150, y_pos)
        y_pos += 30
    
    # Draw buttons
    take_break_button.draw(screen, font20, white)
    ignore_break_button.draw(screen, font20, white)

def draw_break_screen(screen, font40, font30, white, break_duration, break_start_time, resume_button):
    """Draw break screen."""
    # Create semi-transparent overlay
    overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))  # Semi-transparent black
    screen.blit(overlay, (0, 0))
    
    # Draw title
    draw_text(screen, "TAKING A BREAK", font40, white, screen.get_width()//2 - 150, screen.get_height()//2 - 150)
    
    # Calculate remaining time
    remaining_time = max(0, break_duration - (pygame.time.get_ticks() - break_start_time) / 1000)
    draw_text(screen, f"Time remaining: {int(remaining_time)}s", font30, white, screen.get_width()//2 - 100, screen.get_height()//2 - 50)
    
    # Draw resume button if break is over
    if remaining_time <= 0:
        resume_button.draw(screen, font30, white)

def draw_cooldown_overlay(screen, font20, red, cooldown_intensity):
    """Draw cooldown overlay."""
    # Create semi-transparent red overlay based on cooldown intensity
    overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
    overlay.fill((255, 0, 0, int(cooldown_intensity * 1.28)))  # Max alpha is 128 at 100% intensity
    screen.blit(overlay, (0, 0))
    
    # Draw cooldown warning
    draw_text(screen, f"COOLDOWN ACTIVE - Intensity: {int(cooldown_intensity)}%", font20, red, 10, screen.get_height() - 30)

def draw_enforced_cooldown(screen, font40, font30, font20, white, break_duration, break_start_time, cooldown_intensity):
    """Draw enforced cooldown screen."""
    # Create semi-transparent overlay
    overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
    overlay.fill((255, 0, 0, int(cooldown_intensity * 1.28)))  # Red overlay based on intensity
    screen.blit(overlay, (0, 0))
    
    # Draw title
    draw_text(screen, "ENFORCED BREAK", font40, white, screen.get_width()//2 - 150, screen.get_height()//2 - 150)
    
    # Calculate and draw remaining time
    remaining_time = max(0, break_duration - (pygame.time.get_ticks() - break_start_time) / 1000)
    draw_text(screen, f"Time remaining: {int(remaining_time)}s", font30, white, screen.get_width()//2 - 100, screen.get_height()//2 - 50)
    
    # Draw message
    draw_text(screen, "Too many breaks ignored. Please take a moment to rest.", font20, white, screen.get_width()//2 - 200, screen.get_height()//2)

def draw_game_over(screen, score, high_score):
    """Draw the game over screen with final score and high score."""
    # Create fonts
    font40 = pygame.font.SysFont('Constantia', 40)
    font30 = pygame.font.SysFont('Constantia', 30)
    
    # Define colors
    white = (255, 255, 255)
    yellow = (255, 255, 0)
    
    # Draw game over text
    draw_text(screen, "GAME OVER", font40, white, int(screen.get_width() / 2 - 100), int(screen.get_height() / 2 - 100))
    
    # Draw final score
    draw_text(screen, f"FINAL SCORE: {score}", font30, white, int(screen.get_width() / 2 - 100), int(screen.get_height() / 2 - 50))
    
    # Draw high score
    draw_text(screen, f"HIGH SCORE: {high_score}", font30, yellow, int(screen.get_width() / 2 - 100), int(screen.get_height() / 2)) 