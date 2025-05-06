import pygame
from pygame import mixer
import random
import time
import os
import json
from src.game.spaceship import Spaceship
from src.game.bullets import Bullets, Alien_Bullets
from src.game.aliens import Aliens
from src.game.explosion import Explosion
from src.game.game_manager import create_aliens, reset_game, save_game_state, save_session_duration, save_game_stats
from src.ui.button import Button
from src.ui.game_ui import (
    draw_text, draw_bg, draw_progression_info, draw_mode_selection,
    draw_leaderboard, draw_break_reminder, draw_break_screen,
    draw_cooldown_overlay, draw_enforced_cooldown, draw_game_over
)
from src.states.game_states import *
from src.states.state_manager import (
    check_weekly_leaderboard, handle_break_reminder, handle_break_taken,
    handle_enforced_cooldown, handle_cooldown_active
)
from src.utils.game_utils import *

def initialize_break_threshold():
    """Initialize the break threshold based on session data."""
    try:
        # First try to use session_data.json for recent sessions
        if os.path.exists('session_data.json'):
            with open('session_data.json', 'r') as f:
                session_data = json.load(f)
                if session_data:
                    # Calculate average session duration
                    avg_duration = sum(session_data) / len(session_data)
                    # Use 60% of average as threshold
                    threshold = avg_duration * 0.6
                    print(f"[Break] Initialized dynamic threshold from session data: {threshold:.2f} seconds")
                    return threshold
        
        # If no session data, try to use game_data.json
        if os.path.exists('game_data.json'):
            with open('game_data.json', 'r') as f:
                game_data = json.load(f)
                if game_data:
                    # Calculate average session duration from game data
                    session_durations = [session['duration'] for session in game_data]
                    avg_duration = sum(session_durations) / len(session_durations)
                    # Use 60% of average as threshold
                    threshold = avg_duration * 0.6
                    print(f"[Break] Initialized dynamic threshold from game data: {threshold:.2f} seconds")
                    return threshold
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    
    # Default to 20 seconds for testing
    print("[Break] No session or game data found, using default 20s threshold")
    return 20

def main():
    # Initialize pygame
    pygame.mixer.pre_init(44100, -16, 2, 512)
    mixer.init()
    pygame.init()

    # Define fps
    clock = pygame.time.Clock()
    fps = 60

    # Global variables for break timing
    game_over_break_time = None
    break_reminder_time = None  # Initialize break reminder time
    break_message_start_time = None  # Track when break message first appeared
    max_break_message_duration = 300  # 5 minutes max for break message
    break_cooldown = 10  # 10 seconds cooldown after resetting break timer
    last_break_reset = 0  # Track when break timer was last reset
    last_break_check_time = 0  # Track last time we printed break check
    last_threshold_print_time = 0  # Track last time we printed threshold

    # Screen setup
    screen_width = 600
    screen_height = 800
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption('Space Invaders - Break Aware')

    # Define fonts
    font30 = pygame.font.SysFont('Constantia', 30)
    font40 = pygame.font.SysFont('Constantia', 40)
    font20 = pygame.font.SysFont('Constantia', 20)

    # Load sounds
    explosion_fx = pygame.mixer.Sound("img/explosion.wav")
    explosion_fx.set_volume(0.25)

    explosion2_fx = pygame.mixer.Sound("img/explosion2.wav")
    explosion2_fx.set_volume(0.25)

    laser_fx = pygame.mixer.Sound("img/laser.wav")
    laser_fx.set_volume(0.25)

    # Base sound volumes for adjusting during cooldown
    base_explosion_volume = 0.25
    base_explosion2_volume = 0.25
    base_laser_volume = 0.25

    # Define game variables
    rows = 5
    cols = 5
    alien_cooldown = 1000  # bullet cooldown in milliseconds
    last_alien_shot = pygame.time.get_ticks()
    countdown = 3
    last_count = pygame.time.get_ticks()
    game_over = 0  # 0 is no game over, 1 means player has won, -1 means player has lost
    show_break_message = False  # Flag to track if break message has been shown
    game_paused = False  # Flag to track if game is paused for break
    level = 1  # Initialize level
    score = 0  # Initialize score
    high_score = 0  # Initialize high score
    max_level_reached = 1  # Initialize max level reached
    weekly_stats = load_leaderboard()  # Initialize weekly stats
    session_start_time = time.time()  # Initialize session start time
    first_game_start = True  # Initialize first game start flag
    game_over_time = 0  # Initialize game over time
    level_transition_start = 0  # Initialize level transition timer
    showing_level_transition = False  # Flag for level transition state

    # Define break messages
    break_messages = [
        "You've been doing great! How about a short break to recharge your mind?",
        "Nice streak! Taking a 5-minute pause might help you come back sharper.",
        "You're on fire! Let's take a moment to breathe and reset.",
        "Still enjoying it? That's awesome. Just checking in—would now be a good time to rest your eyes?",
        "Time flies when you're in the zone. Would you like to pause and stretch a little?",
        "Balance is part of the game too. Take a quick break, and we'll be here when you return.",
        "Stretch. Hydrate. Breathe. A quick break now could boost your next round.",
        "Gaming feels better when you feel better. Take care of your body as well as your score!",
        "Great choice taking a break! Your focus bar just leveled up.",
        "Well done for stepping back! Champions know when to pause.",
        "You chose to pause—smart move. See you soon, sharper than ever!"
    ]
    current_break_message = ""  # Initialize current break message

    # Define colours
    red = (255, 0, 0)
    green = (0, 255, 0)
    white = (255, 255, 255)
    blue = (0, 0, 255)
    light_blue = (173, 216, 230)
    yellow = (255, 255, 0)
    gray = (128, 128, 128)

    # Current state and mode
    current_state = STATE_NORMAL_PLAY
    current_mode = MODE_NORMAL
    game_mode_selected = False

    # Timers
    play_start_time = 0
    cooldown_start_time = 0
    break_start_time = 0
    break_duration = 10  # seconds for break (reduced for testing, normally would be longer)
    ignore_duration_threshold = 60  # seconds before cooldown if ignored
    last_break_reminder = 0  # Track last break reminder time
    dynamic_break_threshold = initialize_break_threshold()

    # Progressive cooldown variables
    breaks_ignored_count = 0
    cooldown_intensity = 0  # 0-100 scale for intensity
    continuous_play_time = 0  # Time in cooldown state
    max_cooldown_intensity = 100
    hide_progression = False  # Flag to hide progression display
    hide_score = False  # Flag to hide score display
    black_and_white = False  # Flag for black and white mode

    # Load image
    bg = pygame.image.load("img/bg.png")

    # Create sprite groups
    spaceship_group = pygame.sprite.Group()
    bullet_group = pygame.sprite.Group()
    alien_group = pygame.sprite.Group()
    alien_bullet_group = pygame.sprite.Group()
    explosion_group = pygame.sprite.Group()

    # Create initial game elements
    rows, cols = create_aliens(alien_group, level, screen_width)
    spaceship = Spaceship(int(screen_width / 2), screen_height - 100, 3)
    spaceship_group.add(spaceship)

    # Create buttons
    return_button = Button(screen_width//2 - 150, screen_height//2 + 50, 300, 50, "Return", green, (0, 200, 0))
    quit_button = Button(screen_width//2 - 150, screen_height//2 + 120, 300, 50, "Quit", red, (200, 0, 0))
    normal_button = Button(screen_width//2 - 150, screen_height//2, 300, 50, "Normal Mode", green, (0, 200, 0))
    break_aware_button = Button(screen_width//2 - 150, screen_height//2 + 70, 300, 50, "Break-Aware Mode", blue, light_blue)
    take_break_button = Button(screen_width//2 - 150, screen_height//2, 300, 50, "Take a Break", green, (0, 200, 0))
    ignore_break_button = Button(screen_width//2 - 150, screen_height//2 + 70, 300, 50, "Continue Playing", red, (200, 0, 0))
    resume_button = Button(screen_width//2 - 150, screen_height//2 + 70, 300, 50, "Resume Game", green, (0, 200, 0))

    # Game loop
    run = True
    while run:
        clock.tick(fps)
        
        # Check for weekly leaderboard trigger
        show_leaderboard, current_state = check_weekly_leaderboard(weekly_stats, current_state)
        
        # Get mouse position and click state
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = False
        
        # Event handlers
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_game_state(weekly_stats, session_start_time, score)
                run = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_click = True
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_l:  # Press L to show leaderboard
                    current_state = STATE_LEADERBOARD_MINI
                elif event.key == pygame.K_ESCAPE:  # Press ESC to exit game
                    save_game_state(weekly_stats, session_start_time, score)
                    run = False
                elif current_state == STATE_LEADERBOARD_MINI:
                    current_state = STATE_NORMAL_PLAY
                    # Ensure spaceship is in the sprite group when returning from leaderboard
                    if len(spaceship_group) == 0 and spaceship.health_remaining > 0:
                        spaceship_group.add(spaceship)
        
        # Mode selection screen
        if not game_mode_selected:
            draw_mode_selection(screen, font40, font30, font20, white, normal_button, break_aware_button)
            
            # Check button hovers
            normal_button.check_hover(mouse_pos)
            break_aware_button.check_hover(mouse_pos)
            
            # Check button clicks
            if normal_button.check_click(mouse_pos, mouse_click):
                current_mode = MODE_NORMAL
                game_mode_selected = True
                play_start_time = time.time()
            
            if break_aware_button.check_click(mouse_pos, mouse_click):
                current_mode = MODE_BREAK_AWARE
                game_mode_selected = True
                play_start_time = time.time()
            
        # Main game
        elif current_state == STATE_LEADERBOARD_MINI:
            draw_leaderboard(screen, font40, font30, font20, yellow, white, weekly_stats)
        
        else:
            # Draw background
            draw_bg(screen, bg)
            
            # Draw score and lives
            draw_text(screen, f"SCORE: {score}", font30, white, 10, 30)
            draw_text(screen, f"LIVES: {spaceship.health_remaining}", font30, white, 10, 70)
            
            # Draw progression info if not hidden
            if not hide_progression:
                draw_progression_info(screen, font30, font20, yellow, white, level, level, alien_group, rows, cols)
            
            # Check if current session time exceeds the break threshold
            current_session_time = time.time() - session_start_time
            if current_session_time > dynamic_break_threshold and not show_break_message:
                show_break_message = True
                break_start_time = time.time()
                game_paused = True
            
            # State transitions based on timers
            current_time = time.time()
            
            # If we're in break reminder state, pause the game
            if current_state == STATE_BREAK_REMINDER:
                # Draw the break reminder
                draw_break_reminder(screen, font40, font30, font20, white, current_break_message, break_messages, take_break_button, ignore_break_button)
                
                # Check button hovers
                take_break_button.check_hover(mouse_pos)
                ignore_break_button.check_hover(mouse_pos)
                
                # Check button clicks
                if take_break_button.check_click(mouse_pos, mouse_click):
                    current_state = STATE_BREAK_TAKEN
                    break_start_time = current_time
                    last_break_reminder = current_time  # Reset break timer when taking a break
                    last_break_reset = current_time  # Update last reset time
                    print(f"\n[Break] Taken - Timer reset")
                    weekly_stats["breaks_taken"] += 1
                    current_break_message = ""  # Reset message
                    break_reminder_time = None  # Reset break reminder time
                    break_message_start_time = None  # Reset message start time
                
                if ignore_break_button.check_click(mouse_pos, mouse_click):
                    breaks_ignored_count += 1
                    weekly_stats["breaks_ignored"] += 1
                    last_break_reminder = current_time  # Reset break timer when ignoring (fresh start)
                    last_break_reset = current_time  # Update last reset time
                    print(f"\n[Break] Ignored - Timer reset (Ignored: {breaks_ignored_count})")
                    break_reminder_time = None  # Reset break reminder time
                    break_message_start_time = None  # Reset message start time
                    
                    # Then check if we need to enter cooldown
                    if current_mode == MODE_BREAK_AWARE:
                        current_state = STATE_ENFORCED_COOLDOWN
                        break_start_time = current_time
                    else:
                        current_state = STATE_COOLDOWN_ACTIVE
                        cooldown_start_time = current_time
                    
                    # Set cooldown intensity based on number of ignored breaks
                    if breaks_ignored_count == 1:
                        cooldown_intensity = 25
                    elif breaks_ignored_count == 2:
                        cooldown_intensity = 50
                    elif breaks_ignored_count == 3:
                        black_and_white = True
                    elif breaks_ignored_count == 4:
                        cooldown_intensity = 75
                    elif breaks_ignored_count == 5:
                        cooldown_intensity = 100
                    elif breaks_ignored_count == 6:
                        hide_progression = True
                    elif breaks_ignored_count == 7:
                        hide_score = True
                    
                    current_break_message = ""  # Reset message
                
                # Update display and continue to next frame
                pygame.display.update()
                continue  # Skip all game updates
            
            # Check for break reminder only during normal play after countdown
            if countdown == 0 and game_over == 0:  # Check regardless of state
                elapsed_play_time = current_time - play_start_time
                
                # If we're in game over state, use the stored break time
                if game_over == -1 and 'game_over_break_time' in globals():
                    time_since_last_break = current_time - game_over_break_time
                else:
                    time_since_last_break = current_time - last_break_reminder
                
                # Only check for breaks if we're past the cooldown period and not in break reminder state
                if current_time - last_break_reset > break_cooldown and current_state != STATE_BREAK_REMINDER:
                    # Only print every second to reduce log spam
                    if int(current_time) != int(last_break_check_time):
                        print(f"\n[Break] Time since last break: {int(time_since_last_break)}s")
                        last_break_check_time = current_time
                    
                    # Check if we have session data
                    has_session_data = False
                    try:
                        # First try session_data.json
                        if os.path.exists('session_data.json'):
                            with open('session_data.json', 'r') as f:
                                session_data = json.load(f)
                                has_session_data = len(session_data) > 0
                                
                                # Calculate dynamic threshold if we have session data
                                if has_session_data:
                                    avg_duration = sum(session_data) / len(session_data)
                                    dynamic_break_threshold = avg_duration * 0.6  # 60% of average
                                    if int(current_time) != int(last_threshold_print_time):
                                        print(f"[Break] Current threshold from session data: {dynamic_break_threshold:.2f}s")
                                        last_threshold_print_time = current_time
                        
                        # If no session data, try game_data.json
                        if not has_session_data and os.path.exists('game_data.json'):
                            with open('game_data.json', 'r') as f:
                                game_data = json.load(f)
                                has_session_data = len(game_data) > 0
                                
                                if has_session_data:
                                    session_durations = [session['duration'] for session in game_data]
                                    avg_duration = sum(session_durations) / len(session_durations)
                                    dynamic_break_threshold = avg_duration * 0.6  # 60% of average
                                    if int(current_time) != int(last_threshold_print_time):
                                        print(f"[Break] Current threshold from game data: {dynamic_break_threshold:.2f}s")
                                        last_threshold_print_time = current_time
                    except (FileNotFoundError, json.JSONDecodeError):
                        has_session_data = False
                        print("[Break] Error reading session/game data, using default threshold")
                    
                    # Use dynamic timing if session data exists, otherwise use 20-second intervals
                    if has_session_data:
                        if time_since_last_break >= dynamic_break_threshold and current_state in [STATE_NORMAL_PLAY, STATE_COOLDOWN_ACTIVE]:
                            print("[Break] Triggering reminder")
                            current_state = STATE_BREAK_REMINDER
                            # Initialize break message if needed
                            if not current_break_message:
                                current_break_message = random.choice(break_messages)
                                if break_reminder_time is None:
                                    break_reminder_time = last_break_reminder
                                    break_message_start_time = current_time
                    else:
                        if time_since_last_break >= 20 and current_state in [STATE_NORMAL_PLAY, STATE_COOLDOWN_ACTIVE]:
                            print("[Break] Triggering reminder")
                            current_state = STATE_BREAK_REMINDER
                            # Initialize break message if needed
                            if not current_break_message:
                                current_break_message = random.choice(break_messages)
                                if break_reminder_time is None:
                                    break_reminder_time = last_break_reminder
                                    break_message_start_time = current_time
            
            # Handle different game states
            current_state = handle_break_reminder(current_state, current_time, last_break_reminder, dynamic_break_threshold, ignore_duration_threshold, weekly_stats)
            
            current_state, play_start_time, last_break_reminder, cooldown_intensity, breaks_ignored_count, hide_progression, hide_score, black_and_white = handle_break_taken(
                current_state, current_time, break_start_time, break_duration, play_start_time, last_break_reminder,
                cooldown_intensity, breaks_ignored_count, hide_progression, hide_score, black_and_white,
                explosion_fx, explosion2_fx, laser_fx, base_explosion_volume, base_explosion2_volume, base_laser_volume,
                spaceship_group, spaceship
            )
            
            current_state, cooldown_start_time = handle_enforced_cooldown(
                current_state, current_time, break_start_time, break_duration, cooldown_start_time,
                spaceship_group, spaceship
            )
            
            current_state, break_start_time = handle_cooldown_active(
                current_state, current_time, cooldown_start_time, ignore_duration_threshold, break_start_time, weekly_stats
            )

            if countdown == 0:
                # Create random alien bullets
                time_now = pygame.time.get_ticks()
                
                # Adjust alien shooting frequency based on state
                current_alien_cooldown = alien_cooldown
                if current_state == STATE_COOLDOWN_ACTIVE:
                    current_alien_cooldown = alien_cooldown * 1.5  # Slower alien shooting during cooldown
                
                # Shoot
                if time_now - last_alien_shot > current_alien_cooldown and len(alien_bullet_group) < 5 and len(alien_group) > 0:
                    attacking_alien = random.choice(alien_group.sprites())
                    alien_bullet = Alien_Bullets(attacking_alien.rect.centerx, attacking_alien.rect.bottom, level)
                    alien_bullet_group.add(alien_bullet)
                    last_alien_shot = time_now

                # Check if all the aliens have been killed
                if len(alien_group) == 0 and game_over == 0:  # Only advance level if not game over
                    print("\n[Level] All aliens cleared!")
                    print(f"[Level] Advancing to level {level + 1}")
                    
                    # Level completed
                    if level == max_level_reached:
                        # Update max level reached if this is a new level
                        max_level_reached += 1
                        weekly_stats["max_level"] = max_level_reached
                        print(f"[Level] New max level reached: {max_level_reached}")
                    
                    # Advance to next level
                    level += 1
                    
                    # Create new aliens for next level
                    rows, cols = create_aliens(alien_group, level, screen_width)
                    print(f"[Level] Created {rows}x{cols} aliens for level {level}")
                    
                    # Reset player lives for new level
                    spaceship.health_remaining = 3
                    print(f"[Level] Player lives reset to 3 for level {level}")
                    
                    # Start level transition
                    showing_level_transition = True
                    level_transition_start = pygame.time.get_ticks()
                    print("[Level] Starting level transition")
                    
                    # Reset player position for new level
                    spaceship.rect.center = [int(screen_width / 2), screen_height - 100]
                    print(f"[Level] Player position reset for level {level}")

                # Handle level transition display
                if showing_level_transition:
                    current_time = pygame.time.get_ticks()
                    if current_time - level_transition_start < 3000:  # Show for 3 seconds
                        # Draw background
                        draw_bg(screen, bg)
                        
                        # Draw semi-transparent black background
                        s = pygame.Surface((screen_width, screen_height))
                        s.set_alpha(128)
                        s.fill((0, 0, 0))
                        screen.blit(s, (0, 0))
                        
                        # Draw level up message
                        level_up_message = f"LEVEL {level}!"
                        draw_text(screen, level_up_message, font40, yellow, int(screen_width / 2 - 100), int(screen_height / 2 - 50))
                        draw_text(screen, "GET READY!", font30, white, int(screen_width / 2 - 80), int(screen_height / 2 + 20))
                        
                        # Draw score and level info
                        if not hide_score:
                            draw_text(screen, f"SCORE: {score}", font30, white, 10, 30)
                        draw_text(screen, f"LEVEL: {level}", font30, white, 10, 70)
                        
                        pygame.display.update()
                    else:
                        showing_level_transition = False
                        print("[Level] Level transition finished")
                    continue  # Skip the rest of the game loop during transition

                # Normal game state
                if game_over == 0:
                    # Only update game elements if not in break reminder or break taken states
                    if current_state not in [STATE_BREAK_REMINDER, STATE_BREAK_TAKEN, STATE_ENFORCED_COOLDOWN]:
                        # Update spaceship
                        spaceship_result = spaceship.update(screen, current_state, cooldown_intensity, base_laser_volume, laser_fx, bullet_group, explosion_group)
                        if spaceship_result == -1:  # Game over condition
                            game_over = -1
                            game_over_time = current_time
                            # Clear all sprite groups when game over occurs
                            bullet_group.empty()
                            alien_bullet_group.empty()
                            alien_group.empty()
                            explosion_group.empty()
                            continue  # Skip the rest of the game loop

                        # Update sprite groups
                        bullet_group.update(screen, alien_group, explosion_group, explosion_fx, base_explosion_volume, current_state, cooldown_intensity)
                        alien_group.update()
                        alien_bullet_result = alien_bullet_group.update(screen, spaceship_group, explosion_group, explosion2_fx, base_explosion2_volume, current_state, cooldown_intensity)
                        
                        # Check for game over from alien bullets
                        if alien_bullet_result == -1:
                            game_over = -1
                            game_over_time = current_time
                            # Clear all sprite groups when game over occurs
                            bullet_group.empty()
                            alien_bullet_group.empty()
                            alien_group.empty()
                            explosion_group.empty()
                            continue  # Skip the rest of the game loop

                # Handle game over state
                if game_over == -1:
                    print("\n" + "="*50)
                    print("GAME OVER STATE ENTERED")
                    print("="*50)
                    print(f"Current time: {current_time:.2f}")
                    print(f"Last break reminder: {last_break_reminder:.2f}")
                    print(f"Time since last break: {current_time - last_break_reminder:.2f}s")
                    print(f"Current state: {current_state}")
                    print("="*50 + "\n")
                    
                    # Store the last break reminder time when entering game over
                    if game_over_break_time is None:
                        game_over_break_time = last_break_reminder
                    
                    # Clear all sprite groups
                    spaceship_group.empty()
                    alien_group.empty()
                    alien_bullet_group.empty()
                    bullet_group.empty()
                    explosion_group.empty()
                    
                    # Draw game over screen
                    draw_game_over(screen, score, high_score)
                    
                    # Get mouse position and click state
                    mouse_pos = pygame.mouse.get_pos()
                    mouse_click = False
                    
                    # Check for mouse click
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            save_game_state(weekly_stats, session_start_time, score)
                            run = False
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            if event.button == 1:  # Left mouse button
                                mouse_click = True
                    
                    # Handle game over buttons
                    return_button.check_hover(mouse_pos)
                    quit_button.check_hover(mouse_pos)
                    
                    if return_button.check_click(mouse_pos, mouse_click):
                        print("\n" + "="*50)
                        print("RETURNING TO GAME")
                        print("="*50)
                        # Reset game state
                        game_over = 0
                        score = 0
                        level = 1
                        spaceship = Spaceship(int(screen_width / 2), screen_height - 100, 3)
                        spaceship_group.add(spaceship)
                        rows, cols = create_aliens(alien_group, level, screen_width)
                        
                        # Restore the last break reminder time from before game over
                        last_break_reminder = game_over_break_time
                        game_over_break_time = None  # Reset the game over break time
                        
                        print(f"Restored last_break_reminder to: {last_break_reminder:.2f}")
                        print("="*50 + "\n")
                    
                    if quit_button.check_click(mouse_pos, mouse_click):
                        save_game_state(weekly_stats, session_start_time, score)
                        run = False
                    
                    # Draw the buttons
                    return_button.draw(screen, font30, white)
                    quit_button.draw(screen, font30, white)
                    
                    pygame.display.update()
                    continue

            if countdown > 0:
                draw_text(screen, 'GET READY!', font40, white, int(screen_width / 2 - 110), int(screen_height / 2 + 50))
                draw_text(screen, str(countdown), font40, white, int(screen_width / 2 - 10), int(screen_height / 2 + 100))
                count_timer = pygame.time.get_ticks()
                if count_timer - last_count > 1000:
                    countdown -= 1
                    last_count = count_timer
                    if countdown == 0:
                        play_start_time = time.time()  # Reset play timer when game actually starts
                        if first_game_start:  # Only reset break reminder timer on first game start
                            last_break_reminder = play_start_time
                            first_game_start = False

            # Update explosion group    
            explosion_group.update()

            # Draw sprite groups
            if black_and_white and game_over == 0:  # Only apply black and white during normal play
                # Draw background normally
                draw_bg(screen, bg)
                
                # Draw score and progression first (they should remain in color)
                if not hide_score:
                    draw_text(screen, f"SCORE: {score}", font30, white, 10, 30)
                if not hide_progression:
                    draw_progression_info(screen, font30, font20, yellow, white, level, level, alien_group, rows, cols)
                
                # Draw game elements with black and white images
                for sprite in spaceship_group:
                    screen.blit(sprite.bw_image, sprite.rect)
                
                for sprite in bullet_group:
                    screen.blit(sprite.bw_image, sprite.rect)
                
                for sprite in alien_group:
                    screen.blit(sprite.bw_image, sprite.rect)
                
                for sprite in alien_bullet_group:
                    screen.blit(sprite.bw_image, sprite.rect)
                
                for sprite in explosion_group:
                    screen.blit(sprite.bw_images[sprite.index], sprite.rect)
            else:
                # Draw everything normally
                draw_bg(screen, bg)
                if not hide_score:
                    draw_text(screen, f"SCORE: {score}", font30, white, 10, 30)
                if not hide_progression:
                    draw_progression_info(screen, font30, font20, yellow, white, level, level, alien_group, rows, cols)
                spaceship_group.draw(screen)
                bullet_group.draw(screen)
                alien_group.draw(screen)
                alien_bullet_group.draw(screen)
                explosion_group.draw(screen)

            # Draw lives after all other elements
            draw_text(screen, f"LIVES: {spaceship.health_remaining}", font30, white, 10, 70)

            # Draw state-specific overlays last to ensure they stay on top
            if current_state == STATE_BREAK_REMINDER:
                # Initialize a new message if we're just entering the break reminder state
                if not current_break_message:
                    current_break_message = random.choice(break_messages)
                    # Store the last break reminder time when entering break reminder state
                    if break_reminder_time is None:
                        break_reminder_time = last_break_reminder
                        break_message_start_time = current_time  # Store when message first appeared
                        print(f"\n[Break] Time since last break: {int(current_time - last_break_reminder)}s")
                        # Pause the game by not updating game elements
                        continue  # Skip the rest of the game loop to prevent updates
                
                # Check if user has been away too long
                if break_message_start_time and (current_time - break_message_start_time) > max_break_message_duration:
                    print(f"\n[Break] Message timeout after {int(current_time - break_message_start_time)}s")
                    # Reset everything and return to normal play
                    current_state = STATE_NORMAL_PLAY
                    last_break_reminder = current_time  # Reset break timer
                    break_reminder_time = None
                    break_message_start_time = None
                    current_break_message = ""
                    continue
                
                draw_break_reminder(screen, font40, font30, font20, white, current_break_message, break_messages, take_break_button, ignore_break_button)
                
                # Check button hovers
                take_break_button.check_hover(mouse_pos)
                ignore_break_button.check_hover(mouse_pos)
                
                # Check button clicks
                if take_break_button.check_click(mouse_pos, mouse_click):
                    current_state = STATE_BREAK_TAKEN
                    break_start_time = current_time
                    last_break_reminder = current_time  # Reset break timer when taking a break
                    last_break_reset = current_time  # Update last reset time
                    print(f"\n[Break] Taken - Timer reset")
                    weekly_stats["breaks_taken"] += 1
                    current_break_message = ""  # Reset message
                    break_reminder_time = None  # Reset break reminder time
                    break_message_start_time = None  # Reset message start time
                
                if ignore_break_button.check_click(mouse_pos, mouse_click):
                    breaks_ignored_count += 1
                    weekly_stats["breaks_ignored"] += 1
                    last_break_reminder = current_time  # Reset break timer when ignoring (fresh start)
                    last_break_reset = current_time  # Update last reset time
                    print(f"\n[Break] Ignored - Timer reset (Ignored: {breaks_ignored_count})")
                    break_reminder_time = None  # Reset break reminder time
                    break_message_start_time = None  # Reset message start time
                    
                    # Then check if we need to enter cooldown
                    if current_mode == MODE_BREAK_AWARE:
                        current_state = STATE_ENFORCED_COOLDOWN
                        break_start_time = current_time
                    else:
                        current_state = STATE_COOLDOWN_ACTIVE
                        cooldown_start_time = current_time
                    
                    # Set cooldown intensity based on number of ignored breaks
                    if breaks_ignored_count == 1:
                        cooldown_intensity = 25
                    elif breaks_ignored_count == 2:
                        cooldown_intensity = 50
                    elif breaks_ignored_count == 3:
                        black_and_white = True
                    elif breaks_ignored_count == 4:
                        cooldown_intensity = 75
                    elif breaks_ignored_count == 5:
                        cooldown_intensity = 100
                    elif breaks_ignored_count == 6:
                        hide_progression = True
                    elif breaks_ignored_count == 7:
                        hide_score = True
                    
                    current_break_message = ""  # Reset message
                
                # Skip the rest of the game loop to prevent updates while in break reminder state
                pygame.display.update()
                continue
            
            elif current_state == STATE_COOLDOWN_ACTIVE:
                # Draw cooldown overlay last to ensure it stays on top
                draw_cooldown_overlay(screen, font20, red, cooldown_intensity)
            
            elif current_state == STATE_ENFORCED_COOLDOWN:
                draw_enforced_cooldown(screen, font40, font30, font20, white, break_duration, break_start_time, cooldown_intensity)
            
            elif current_state == STATE_BREAK_TAKEN:
                draw_break_screen(screen, font40, font30, white, break_duration, break_start_time, resume_button)

        pygame.display.update()

    # Save stats before quitting
    weekly_stats["total_play_time"] += int(time.time() - session_start_time)
    if score > weekly_stats["high_score"]:
        weekly_stats["high_score"] = score
    save_leaderboard(weekly_stats)

    # Calculate session duration at the end
    session_end_time = time.time()
    session_duration = int(session_end_time - session_start_time)

    # Save session duration
    save_session_duration(session_start_time)

    # Save game stats
    save_game_stats(weekly_stats, session_start_time, score)

    # Save final game state
    save_game_state(weekly_stats, session_start_time, score)

    pygame.quit()

if __name__ == '__main__':
    main() 