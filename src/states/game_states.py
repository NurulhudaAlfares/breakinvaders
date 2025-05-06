"""
Game States Module

This module contains constants for different game states.
"""

import pygame
import random
import time
from src.ui.game_ui import draw_text
from src.ui.button import Button

# Game states
STATE_NORMAL_PLAY = "NormalPlay"
STATE_BREAK_REMINDER = "BreakReminder"
STATE_BREAK_TAKEN = "BreakTaken"
STATE_COOLDOWN_ACTIVE = "CooldownActive"
STATE_ENFORCED_COOLDOWN = "EnforcedCooldown"
STATE_LEADERBOARD_MINI = "LeaderboardMini"

# Game modes
MODE_NORMAL = "Normal"
MODE_BREAK_AWARE = "BreakAware"

def draw_break_reminder(screen, font40, font30, font20, white, current_break_message, break_messages, take_break_button, ignore_break_button):
    # Use cached overlay
    overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # Semi-transparent black
    screen.blit(overlay, (0, 0))
    
    # Break reminder text
    title_text = "Time for a Break!"
    title_surface = font40.render(title_text, True, white)
    title_width = title_surface.get_width()
    screen.blit(title_surface, ((screen.get_width() - title_width) // 2, screen.get_height()//2 - 120))
    
    # Set a new message if we don't have one
    if not current_break_message:
        current_break_message = random.choice(break_messages)
    
    # Split message into lines
    words = current_break_message.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + " " + word if current_line else word
        if font20.size(test_line)[0] < screen.get_width() - 100:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    
    # Draw each line of the message centered
    y_pos = screen.get_height()//2 - 50
    for line in lines:
        line_surface = font20.render(line, True, white)
        line_width = line_surface.get_width()
        screen.blit(line_surface, ((screen.get_width() - line_width) // 2, y_pos))
        y_pos += 30
    
    # Draw buttons with proper spacing
    button_y = screen.get_height()//2 + 50
    take_break_button.rect.y = button_y
    ignore_break_button.rect.y = button_y + 70
    
    take_break_button.draw(screen, font30, white)
    ignore_break_button.draw(screen, font30, white)

def draw_break_screen(screen, font40, font30, white, break_duration, break_start_time, resume_button):
    # Semi-transparent overlay
    overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
    overlay.fill((0, 0, 100, 180))  # Semi-transparent blue
    screen.blit(overlay, (0, 0))
    
    # Break text
    draw_text(screen, "Taking a Break", font40, white, screen.get_width()//2 - 130, screen.get_height()//2 - 100)
    
    # Countdown timer
    time_remaining = max(0, break_duration - (time.time() - break_start_time))
    draw_text(screen, f"Returning in: {int(time_remaining)} seconds", font30, white, screen.get_width()//2 - 180, screen.get_height()//2 - 30)
    
    if time_remaining <= 0:
        resume_button.draw(screen, font30, white)

def draw_cooldown_overlay(screen, font20, red, cooldown_intensity):
    # Draw cooldown message centered at top
    cooldown_text = "Cooldown Mode Activated"
    text_width = font20.size(cooldown_text)[0]
    draw_text(screen, cooldown_text, font20, red, (screen.get_width() - text_width) // 2, 30)
    
    # Draw volume percentage below
    volume_text = f"Volume: {int(100 - cooldown_intensity)}%"
    volume_width = font20.size(volume_text)[0]
    draw_text(screen, volume_text, font20, red, (screen.get_width() - volume_width) // 2, 60)
    
    # Draw take break instruction text
    takebreak_text = "Take a break to restore full sound"
    takebreak_width = font20.size(takebreak_text)[0]
    draw_text(screen, takebreak_text, font20, red, (screen.get_width() - takebreak_width) // 2, 90)

    # Draw press p instruction text
    pressp_text = "Press P to voluntarily take a break"
    pressp_width = font20.size(pressp_text)[0]
    draw_text(screen, pressp_text, font20, red, (screen.get_width() - pressp_width) // 2, 120)

def draw_enforced_cooldown(screen, font40, font30, font20, white, break_duration, break_start_time, cooldown_intensity):
    # Semi-transparent overlay
    overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
    overlay.fill((200, 0, 0, 180))  # Semi-transparent red
    screen.blit(overlay, (0, 0))
    
    # Break text
    draw_text(screen, "Enforced Break", font40, white, screen.get_width()//2 - 130, screen.get_height()//2 - 100)
    draw_text(screen, "Please take a moment to rest your eyes", font20, white, screen.get_width()//2 - 180, screen.get_height()//2 - 50)
    
    # Countdown timer
    time_remaining = max(0, break_duration - (time.time() - break_start_time))
    draw_text(screen, f"Returning in: {int(time_remaining)} seconds", font30, white, screen.get_width()//2 - 180, screen.get_height()//2)
    
    # Display information about cooldown that will follow
    draw_text(screen, "Reduced immersion will follow this break", font20, white, screen.get_width()//2 - 180, screen.get_height()//2 + 50)
    draw_text(screen, f"Starting intensity: {int(cooldown_intensity)}%", font20, white, screen.get_width()//2 - 180, screen.get_height()//2 + 80)

def draw_leaderboard(screen, font40, font30, font20, yellow, white, weekly_stats):
    # Semi-transparent overlay
    overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 220))  # Semi-transparent black
    screen.blit(overlay, (0, 0))
    
    # Leaderboard title
    draw_text(screen, "Weekly Summary", font40, yellow, screen.get_width()//2 - 130, 100)
    
    # Display stats
    y_pos = 200
    draw_text(screen, f"Games Played: {weekly_stats['games_played']}", font30, white, 100, y_pos)
    y_pos += 50
    draw_text(screen, f"Breaks Taken: {weekly_stats['breaks_taken']}", font30, white, 100, y_pos)
    y_pos += 50
    draw_text(screen, f"Breaks Ignored: {weekly_stats['breaks_ignored']}", font30, white, 100, y_pos)
    y_pos += 50
    
    # Format playtime nicely
    hours = weekly_stats['total_play_time'] // 3600
    minutes = (weekly_stats['total_play_time'] % 3600) // 60
    seconds = weekly_stats['total_play_time'] % 60
    time_str = f"{hours}h {minutes}m {seconds}s"
    draw_text(screen, f"Total Play Time: {time_str}", font30, white, 100, y_pos)
    y_pos += 50
    
    draw_text(screen, f"High Score: {weekly_stats['high_score']}", font30, yellow, 100, y_pos)
    y_pos += 100
    
    draw_text(screen, "Press any key to continue", font30, white, screen.get_width()//2 - 150, y_pos)

def draw_mode_selection(screen, font40, font30, font20, white, normal_button, break_aware_button):
    # Background
    screen.fill((0, 0, 50))  # Dark blue background
    
    # Title
    draw_text(screen, "Space Invaders - Break Aware", font40, white, screen.get_width()//2 - 220, 100)
    
    # Description
    draw_text(screen, "Select Game Mode:", font30, white, screen.get_width()//2 - 100, screen.get_height()//2 - 70)
    
    # Draw buttons
    normal_button.draw(screen, font30, white)
    break_aware_button.draw(screen, font30, white)
    
    # Mode descriptions
    draw_text(screen, "Normal: Standard gameplay with break reminders", font20, white, screen.get_width()//2 - 210, screen.get_height()//2 + 140)
    draw_text(screen, "Break-Aware: Enforces breaks when ignored", font20, white, screen.get_width()//2 - 210, screen.get_height()//2 + 170) 