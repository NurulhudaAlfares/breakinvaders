import pygame
from pygame import mixer
from pygame.locals import *
import random
import time
import datetime
import json
import os
from rest_logic import save_game_stats, calculate_break_trigger_time, save_session_duration

pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

# Define fps
clock = pygame.time.Clock()
fps = 60

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

# Define colours
red = (255, 0, 0)
green = (0, 255, 0)
white = (255, 255, 255)
blue = (0, 0, 255)
light_blue = (173, 216, 230)
yellow = (255, 255, 0)
gray = (128, 128, 128)

# Break-aware system variables
# Game States
STATE_NORMAL_PLAY = "NormalPlay"
STATE_BREAK_REMINDER = "BreakReminder"
STATE_BREAK_TAKEN = "BreakTaken"
STATE_COOLDOWN_ACTIVE = "CooldownActive"
STATE_ENFORCED_COOLDOWN = "EnforcedCooldown"
STATE_LEADERBOARD_MINI = "LeaderboardMini"

# Game Modes
MODE_NORMAL = "Normal"
MODE_BREAK_AWARE = "BreakAware"

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
dynamic_break_threshold = 300 # Default 5 minutes, will be calculated later

# Progressive cooldown variables
breaks_ignored_count = 0
cooldown_intensity = 0  # 0-100 scale for intensity
continuous_play_time = 0  # Time in cooldown state
max_cooldown_intensity = 100
hide_progression = False  # Flag to hide progression display
hide_score = False  # Flag to hide score display
black_and_white = False  # Flag for black and white mode

# Scores and statistics
score = 0
high_score = 0
current_level = 1
max_level_reached = 1
weekly_stats = {
    "games_played": 0,
    "breaks_taken": 0,
    "breaks_ignored": 0,
    "total_play_time": 0,
    "high_score": 0,
    "max_level": 1,
    "last_leaderboard_check": time.time()
}

# Load image
bg = pygame.image.load("img/bg.png")

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

# Add current break message variable
current_break_message = ""

# Create cached overlay surface
break_overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
break_overlay.fill((0, 0, 0, 180))  # Semi-transparent black

# Cache for rendered text surfaces and their positions
text_cache = {}
message_cache = {}

def get_cached_text(text, font, color):
    key = (text, font, color)
    if key not in text_cache:
        text_cache[key] = font.render(text, True, color)
    return text_cache[key]

def get_cached_message(message):
    if message not in message_cache:
        # Split message into lines
        words = message.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            if font20.size(test_line)[0] < screen_width - 100:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        
        # Cache the lines
        message_cache[message] = lines
    return message_cache[message]

def draw_bg():
    screen.blit(bg, (0, 0))

# Define function for creating text
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# Draw level and progression info
def draw_progression_info():
    # Draw level info at top right
    level_text = f"LEVEL: {current_level}"
    draw_text(level_text, font30, yellow, screen_width - 150, 30)
    
    # Draw max level reached
    max_level_text = f"MAX LEVEL: {max_level_reached}"
    draw_text(max_level_text, font20, white, screen_width - 150, 60)
    
    # Draw aliens remaining
    aliens_text = f"Aliens: {len(alien_group)}/{rows*cols}"
    draw_text(aliens_text, font20, white, screen_width - 150, 90)

# Load or create leaderboard data
def load_leaderboard():
    global weekly_stats, max_level_reached
    try:
        if os.path.exists("leaderboard.json"):
            with open("leaderboard.json", "r") as f:
                data = json.load(f)
                # Update max level reached from saved data
                if "max_level" in data:
                    max_level_reached = data["max_level"]
                return data
    except:
        pass
    return weekly_stats

def save_leaderboard():
    # Update max level in stats before saving
    weekly_stats["max_level"] = max(weekly_stats["max_level"], max_level_reached)
    
    with open("leaderboard.json", "w") as f:
        json.dump(weekly_stats, f)

# Check if it's time for weekly leaderboard
def check_weekly_leaderboard():
    global weekly_stats, current_state
    
    # Check if a week has passed since last leaderboard check
    current_time = time.time()
    one_week_seconds = 7 * 24 * 60 * 60
    
    if current_time - weekly_stats["last_leaderboard_check"] >= one_week_seconds:
        weekly_stats["last_leaderboard_check"] = current_time
        save_leaderboard()
        current_state = STATE_LEADERBOARD_MINI
        return True
    return False

# Create spaceship class
class Spaceship(pygame.sprite.Sprite):
    def __init__(self, x, y, health):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/spaceship.png")
        self.bw_image = pygame.image.load("img/bw/spaceship_bw_cleaned_final.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.health_start = health
        self.health_remaining = health
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        # Set movement speed
        speed = 8
        # Set a cooldown variable
        cooldown = 500  # milliseconds
        game_over = 0

        # Get key press
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= speed
        if key[pygame.K_RIGHT] and self.rect.right < screen_width:
            self.rect.x += speed

        # Record current time
        time_now = pygame.time.get_ticks()
        
        # Shoot - cooldown mechanics don't affect gameplay efficiency
        if key[pygame.K_SPACE] and time_now - self.last_shot > cooldown:
            # Adjust sound volume based on cooldown intensity
            if current_state == STATE_COOLDOWN_ACTIVE:
                # Volume decreases gradually with intensity (100% to 0%)
                volume_multiplier = (100.0 - cooldown_intensity) / 100.0
                laser_fx.set_volume(base_laser_volume * volume_multiplier)
            else:
                laser_fx.set_volume(base_laser_volume)
                
            laser_fx.play()
            bullet = Bullets(self.rect.centerx, self.rect.top)
            bullet_group.add(bullet)
            self.last_shot = time_now

        # Update mask
        self.mask = pygame.mask.from_surface(self.image)

        # Draw health bar
        pygame.draw.rect(screen, red, (self.rect.x, (self.rect.bottom + 10), self.rect.width, 15))
        if self.health_remaining > 0:
            pygame.draw.rect(screen, green, (self.rect.x, (self.rect.bottom + 10), int(self.rect.width * (self.health_remaining / self.health_start)), 15))
        elif self.health_remaining <= 0:
            explosion = Explosion(self.rect.centerx, self.rect.centery, 3)
            explosion_group.add(explosion)
            self.kill()
            game_over = -1
        return game_over

# Create Bullets class
class Bullets(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/bullet.png")
        self.bw_image = pygame.image.load("img/bw/bullet_bw_cleaned_final.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        self.rect.y -= 5
        if self.rect.bottom < 0:
            self.kill()
        if pygame.sprite.spritecollide(self, alien_group, True):
            self.kill()
            
            # Adjust sound volume based on cooldown state
            if current_state == STATE_COOLDOWN_ACTIVE:
                # Volume decreases gradually with intensity (100% to 0%)
                volume_multiplier = (100.0 - cooldown_intensity) / 100.0
                explosion_fx.set_volume(base_explosion_volume * volume_multiplier)
            else:
                explosion_fx.set_volume(base_explosion_volume)
                
            explosion_fx.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)
            
            # Increase score
            global score
            score += 10

# Create Aliens class
class Aliens(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        alien_num = str(random.randint(1, 5))
        self.image = pygame.image.load(f"img/alien{alien_num}.png")
        self.bw_image = pygame.image.load(f"img/bw/alien{alien_num}_bw_cleaned_final.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.move_counter = 0
        self.move_direction = 1
        
        # Speed increases with level
        self.base_speed = 1
        self.speed_multiplier = 1 + (current_level - 1) * 0.2  # 20% faster per level

    def update(self):
        # No slowdown during cooldown - maintain gameplay efficiency
        # But increase speed based on level
        move_speed = self.base_speed * self.speed_multiplier
            
        self.rect.x += self.move_direction * move_speed
        self.move_counter += 1
        if abs(self.move_counter) > 75:
            self.move_direction *= -1
            self.move_counter *= self.move_direction

# Create Alien Bullets class
class Alien_Bullets(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/alien_bullet.png")
        self.bw_image = pygame.image.load("img/bw/alien_bullet_bw_cleaned_final.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        
        # Speed increases with level
        self.base_speed = 2
        self.speed_multiplier = 1 + (current_level - 1) * 0.15  # 15% faster per level

    def update(self):
        # No slowdown during cooldown - maintain gameplay efficiency
        # But increase speed based on level
        bullet_speed = self.base_speed * self.speed_multiplier
            
        self.rect.y += bullet_speed
        if self.rect.top > screen_height:
            self.kill()
        if pygame.sprite.spritecollide(self, spaceship_group, False, pygame.sprite.collide_mask):
            self.kill()
            
            # Adjust sound volume based on cooldown state
            if current_state == STATE_COOLDOWN_ACTIVE:
                # Volume decreases gradually with intensity (100% to 0%)
                volume_multiplier = (100.0 - cooldown_intensity) / 100.0
                explosion2_fx.set_volume(base_explosion2_volume * volume_multiplier)
            else:
                explosion2_fx.set_volume(base_explosion2_volume)
                
            explosion2_fx.play()
            # Reduce spaceship health
            spaceship.health_remaining -= 1
            explosion = Explosion(self.rect.centerx, self.rect.centery, 1)
            explosion_group.add(explosion)

# Create Explosion class
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.bw_images = []
        for num in range(1, 6):
            img = pygame.image.load(f"img/exp{num}.png")
            bw_img = pygame.image.load(f"img/bw/exp{num}_bw_cleaned_final.png")
            if size == 1:
                img = pygame.transform.scale(img, (20, 20))
                bw_img = pygame.transform.scale(bw_img, (20, 20))
            if size == 2:
                img = pygame.transform.scale(img, (40, 40))
                bw_img = pygame.transform.scale(bw_img, (40, 40))
            if size == 3:
                img = pygame.transform.scale(img, (160, 160))
                bw_img = pygame.transform.scale(bw_img, (160, 160))
            # Add the images to the lists
            self.images.append(img)
            self.bw_images.append(bw_img)
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.counter = 0

    def update(self):
        explosion_speed = 3
        # Update explosion animation
        self.counter += 1

        if self.counter >= explosion_speed and self.index < len(self.images) - 1:
            self.counter = 0
            self.index += 1
            self.image = self.images[self.index]

        # If the animation is complete, delete explosion
        if self.index >= len(self.images) - 1 and self.counter >= explosion_speed:
            self.kill()

# Create Button class for UI
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.hovered = False
        
    def draw(self):
        color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, white, self.rect, 2, border_radius=10)  # Border
        
        text_surf = font30.render(self.text, True, white)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)
        return self.hovered
        
    def check_click(self, pos, click):
        return self.rect.collidepoint(pos) and click

# Create mode selection buttons
normal_button = Button(screen_width//2 - 150, screen_height//2, 300, 50, "Normal Mode", green, (0, 200, 0))
break_aware_button = Button(screen_width//2 - 150, screen_height//2 + 70, 300, 50, "Break-Aware Mode", blue, light_blue)

# Create break reminder buttons
take_break_button = Button(screen_width//2 - 150, screen_height//2, 300, 50, "Take a Break", green, (0, 200, 0))
ignore_break_button = Button(screen_width//2 - 150, screen_height//2 + 70, 300, 50, "Continue Playing", red, (200, 0, 0))

# Create resume button for after break
resume_button = Button(screen_width//2 - 150, screen_height//2 + 70, 300, 50, "Resume Game", green, (0, 200, 0))

# Create end of session buttons
new_game_button = Button(screen_width//2 - 150, screen_height//2 + 50, 300, 50, "Return", green, (0, 200, 0))
quit_button = Button(screen_width//2 - 150, screen_height//2 + 120, 300, 50, "Quit", red, (200, 0, 0))

# Create sprite groups
spaceship_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
alien_group = pygame.sprite.Group()
alien_bullet_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()

def create_aliens():
    # Generate aliens - number increases with level
    global rows, cols
    
    # Increase number of aliens based on level
    base_rows = 5
    base_cols = 5
    
    # Add more rows and columns as level increases
    rows = min(base_rows + (current_level - 1) // 2, 8)  # Max 8 rows
    cols = min(base_cols + (current_level - 1) // 3, 8)  # Max 8 columns
    
    for row in range(rows):
        for item in range(cols):
            alien = Aliens(100 + item * 100, 100 + row * 70)
            alien_group.add(alien)

# Create player
spaceship = Spaceship(int(screen_width / 2), screen_height - 100, 3)
spaceship_group.add(spaceship)

# Draw break reminder overlay
def draw_break_reminder():
    global current_break_message
    
    # Use cached overlay
    screen.blit(break_overlay, (0, 0))
    
    # Break reminder text
    title_text = "Time for a Break!"
    title_surface = get_cached_text(title_text, font40, white)
    title_width = title_surface.get_width()
    screen.blit(title_surface, ((screen_width - title_width) // 2, screen_height//2 - 120))
    
    # Set a new message if we don't have one
    if not current_break_message:
        current_break_message = random.choice(break_messages)
    
    # Get cached message lines
    lines = get_cached_message(current_break_message)
    
    # Draw each line of the message centered
    y_pos = screen_height//2 - 50
    for line in lines:
        line_surface = get_cached_text(line, font20, white)
        line_width = line_surface.get_width()
        screen.blit(line_surface, ((screen_width - line_width) // 2, y_pos))
        y_pos += 30
    
    # Draw buttons with proper spacing
    button_y = screen_height//2 + 50
    take_break_button.rect.y = button_y
    ignore_break_button.rect.y = button_y + 70
    
    take_break_button.draw()
    ignore_break_button.draw()

# Draw break screen
def draw_break_screen():
    # Semi-transparent overlay
    overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 100, 180))  # Semi-transparent blue
    screen.blit(overlay, (0, 0))
    
    # Break text
    draw_text("Taking a Break", font40, white, screen_width//2 - 130, screen_height//2 - 100)
    
    # Countdown timer
    time_remaining = max(0, break_duration - (time.time() - break_start_time))
    draw_text(f"Returning in: {int(time_remaining)} seconds", font30, white, screen_width//2 - 180, screen_height//2 - 30)
    
    if time_remaining <= 0:
        resume_button.draw()

# Draw cooldown overlay
def draw_cooldown_overlay():
    # Draw cooldown message centered at top
    cooldown_text = "Cooldown Mode Activated"
    text_width = font20.size(cooldown_text)[0]
    draw_text(cooldown_text, font20, red, (screen_width - text_width) // 2, 30)
    
    # Draw volume percentage below
    volume_text = f"Volume: {int(100 - cooldown_intensity)}%"
    volume_width = font20.size(volume_text)[0]
    draw_text(volume_text, font20, red, (screen_width - volume_width) // 2, 60)
    
    # Draw take break instruction text
    takebreak_text = "Take a break to restore full sound"
    takebreak_width = font20.size(takebreak_text)[0]
    draw_text(takebreak_text, font20, red, (screen_width - takebreak_width) // 2, 90)

    # Draw press p instruction text
    pressp_text = "Press P to voluntarily take a break"
    pressp_width = font20.size(pressp_text)[0]
    draw_text(pressp_text, font20, red, (screen_width - pressp_width) // 2, 120)

# Draw enforced cooldown screen
def draw_enforced_cooldown():
    # Semi-transparent overlay
    overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    overlay.fill((200, 0, 0, 180))  # Semi-transparent red
    screen.blit(overlay, (0, 0))
    
    # Break text
    draw_text("Enforced Break", font40, white, screen_width//2 - 130, screen_height//2 - 100)
    draw_text("Please take a moment to rest your eyes", font20, white, screen_width//2 - 180, screen_height//2 - 50)
    
    # Countdown timer
    time_remaining = max(0, break_duration - (time.time() - break_start_time))
    draw_text(f"Returning in: {int(time_remaining)} seconds", font30, white, screen_width//2 - 180, screen_height//2)
    
    # Display information about cooldown that will follow
    draw_text("Reduced immersion will follow this break", font20, white, screen_width//2 - 180, screen_height//2 + 50)
    draw_text(f"Starting intensity: {int(cooldown_intensity)}%", font20, white, screen_width//2 - 180, screen_height//2 + 80)

# Draw leaderboard screen
def draw_leaderboard():
    # Semi-transparent overlay
    overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 220))  # Semi-transparent black
    screen.blit(overlay, (0, 0))
    
    # Leaderboard title
    draw_text("Weekly Summary", font40, yellow, screen_width//2 - 130, 100)
    
    # Display stats
    y_pos = 200
    draw_text(f"Games Played: {weekly_stats['games_played']}", font30, white, 100, y_pos)
    y_pos += 50
    draw_text(f"Breaks Taken: {weekly_stats['breaks_taken']}", font30, white, 100, y_pos)
    y_pos += 50
    draw_text(f"Breaks Ignored: {weekly_stats['breaks_ignored']}", font30, white, 100, y_pos)
    y_pos += 50
    
    # Format playtime nicely
    hours = weekly_stats['total_play_time'] // 3600
    minutes = (weekly_stats['total_play_time'] % 3600) // 60
    seconds = weekly_stats['total_play_time'] % 60
    time_str = f"{hours}h {minutes}m {seconds}s"
    draw_text(f"Total Play Time: {time_str}", font30, white, 100, y_pos)
    y_pos += 50
    
    draw_text(f"High Score: {weekly_stats['high_score']}", font30, yellow, 100, y_pos)
    y_pos += 100
    
    draw_text("Press any key to continue", font30, white, screen_width//2 - 150, y_pos)

# Draw mode selection screen
def draw_mode_selection():
    # Background
    screen.fill((0, 0, 50))  # Dark blue background
    
    # Title
    draw_text("Space Invaders - Break Aware", font40, white, screen_width//2 - 220, 100)
    
    # Description
    draw_text("Select Game Mode:", font30, white, screen_width//2 - 100, screen_height//2 - 70)
    
    # Draw buttons
    normal_button.draw()
    break_aware_button.draw()
    
    # Mode descriptions
    draw_text("Normal: Standard gameplay with break reminders", font20, white, screen_width//2 - 210, screen_height//2 + 140)
    draw_text("Break-Aware: Enforces breaks when ignored", font20, white, screen_width//2 - 210, screen_height//2 + 170)

# Reset game function
def reset_game():
    global game_over, countdown, score, current_state, play_start_time, spaceship, spaceship_group, last_break_reminder, game_over_time
    
    # Clear all sprite groups
    bullet_group.empty()
    alien_group.empty()
    alien_bullet_group.empty()
    explosion_group.empty()
    spaceship_group.empty()  # Clear spaceship group
    
    # Reset game variables but preserve cooldown and level
    game_over = 0
    countdown = 3
    score = 0
    # Don't reset black_and_white here, only reset it when taking a break
    
    # Create new aliens for current level
    create_aliens()
    
    # Reset player
    spaceship = Spaceship(int(screen_width / 2), screen_height - 100, 3)  # Create a new spaceship
    spaceship_group.add(spaceship)  # Add to sprite group
    
    # Reset break-aware system but preserve cooldown state
    if current_state != STATE_COOLDOWN_ACTIVE:
        current_state = STATE_NORMAL_PLAY
    play_start_time = time.time()
    
    # If we were in game over state, adjust last_break_reminder to account for the pause
    if game_over_time > 0:
        pause_duration = time.time() - game_over_time
        last_break_reminder += pause_duration
        game_over_time = 0
    
    # Update stats
    weekly_stats["games_played"] += 1

def update_session_average():
    """Update the average session time based on all sessions"""
    try:
        # Load existing data
        with open('game_data.json', 'r') as f:
            data = json.load(f)
        
        # Get all session times
        session_times = [session['duration'] for session in data['sessions']]
        
        # Calculate new average
        if session_times:
            data['average_session_time'] = sum(session_times) / len(session_times)
            
            # Update break threshold based on average (1.5x the average)
            data['break_threshold'] = data['average_session_time'] * 1.5
            
            # Save updated data
            with open('game_data.json', 'w') as f:
                json.dump(data, f, indent=4)
            
            # Update the global break threshold
            global dynamic_break_threshold
            dynamic_break_threshold = data['break_threshold']
            
            print(f"Updated average session time: {data['average_session_time']:.2f} seconds")
            print(f"Updated break threshold: {data['break_threshold']:.2f} seconds")
    except Exception as e:
        print(f"Error updating session average: {e}")

# Initialize break threshold from session data
def initialize_break_threshold():
    global dynamic_break_threshold
    try:
        # Load session data
        with open('session_data.json', 'r') as f:
            session_data = json.load(f)
        
        if session_data:
            # Calculate average session duration
            avg_duration = sum(session_data) / len(session_data)
            # Set break threshold to 60% of average
            dynamic_break_threshold = avg_duration * 0.6  # Changed from 1.5 to 0.6 (60% of average)
        else:
            dynamic_break_threshold = 20  # Set to 20 seconds for fresh start testing
    except (FileNotFoundError, json.JSONDecodeError):
        dynamic_break_threshold = 20  # Set to 20 seconds for fresh start testing

# Call initialization at game start
initialize_break_threshold()

# Main game loop
weekly_stats = load_leaderboard()
create_aliens()
# play_start_time = time.time() # Initialized later when gameplay starts
# last_break_reminder = play_start_time # Initialized later when gameplay starts
session_start_time = time.time()
first_game_start = True  # Flag to track if this is the first game start
game_over_time = 0  # Track when game over state started

run = True
while run:
    clock.tick(fps)
    
    # Check for weekly leaderboard trigger
    check_weekly_leaderboard()
    
    # Get mouse position and click state
    mouse_pos = pygame.mouse.get_pos()
    mouse_click = False
    
    # Event handlers
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # Save stats before quitting
            weekly_stats["total_play_time"] += int(time.time() - session_start_time)
            if score > weekly_stats["high_score"]:
                weekly_stats["high_score"] = score
            save_leaderboard()
            run = False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse_click = True
                
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_l:  # Press L to show leaderboard
                current_state = STATE_LEADERBOARD_MINI
            elif event.key == pygame.K_ESCAPE:  # Press ESC to exit game
                # Save stats before quitting
                weekly_stats["total_play_time"] += int(time.time() - session_start_time)
                if score > weekly_stats["high_score"]:
                    weekly_stats["high_score"] = score
                save_leaderboard()
                run = False
            elif current_state == STATE_LEADERBOARD_MINI:
                current_state = STATE_NORMAL_PLAY
                # Ensure spaceship is in the sprite group when returning from leaderboard
                if len(spaceship_group) == 0 and spaceship.health_remaining > 0:
                    spaceship_group.add(spaceship)
    
    # Mode selection screen
    if not game_mode_selected:
        draw_mode_selection()
        
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
        draw_leaderboard()
        
    else:
        # Draw background
        draw_bg()
        
        # Draw score if not hidden
        if not hide_score:
            draw_text(f"SCORE: {score}", font30, white, 10, 30)
        
        # Draw progression info if not hidden
        if not hide_progression:
            draw_progression_info()
        
        # Draw level
        draw_text(f"LEVEL: {current_level}", font30, white, 10, 70)
        
        # Check if current session time exceeds the break threshold
        current_session_time = time.time() - session_start_time
        if current_session_time > dynamic_break_threshold and not show_break_message:
            show_break_message = True
            break_start_time = time.time()
            game_paused = True
        
        # State transitions based on timers
        current_time = time.time()
        
        # Check for break reminder only during normal play after countdown
        if countdown == 0 and game_over == 0:  # Check regardless of state
            elapsed_play_time = current_time - play_start_time
            print(f"Current state: {current_state}, Elapsed time: {elapsed_play_time:.2f}s, Last reminder: {current_time - last_break_reminder:.2f}s ago")
            
            # Check if we have session data
            has_session_data = False
            try:
                if os.path.exists('session_data.json'):
                    with open('session_data.json', 'r') as f:
                        session_data = json.load(f)
                        has_session_data = len(session_data) > 0
                        print(f"Session data exists: {has_session_data}, Number of sessions: {len(session_data)}")
                        
                        # Calculate dynamic threshold if we have session data
                        if has_session_data:
                            avg_duration = sum(session_data) / len(session_data)
                            dynamic_break_threshold = avg_duration * 0.6  # Changed from 1.5 to 0.6 (60% of average)
                            print(f"Dynamic threshold calculated: {dynamic_break_threshold:.2f} seconds")
            except (FileNotFoundError, json.JSONDecodeError):
                has_session_data = False
                print("No session data found")
            
            # Use dynamic timing if session data exists, otherwise use 20-second intervals
            if has_session_data:
                if (current_time - last_break_reminder) >= dynamic_break_threshold and current_state in [STATE_NORMAL_PLAY, STATE_COOLDOWN_ACTIVE]:
                    current_state = STATE_BREAK_REMINDER
                    # Don't update last_break_reminder here - it will be updated when player makes a choice
                    print(f"Dynamic break reminder triggered at {current_time - play_start_time:.2f} seconds")
            else:
                if (current_time - last_break_reminder) >= 20 and current_state in [STATE_NORMAL_PLAY, STATE_COOLDOWN_ACTIVE]:  # Fixed 20-second interval for fresh start
                    current_state = STATE_BREAK_REMINDER
                    # Don't update last_break_reminder here - it will be updated when player makes a choice
                    print(f"Fresh start break reminder triggered at {current_time - play_start_time:.2f} seconds")
        
        # Handle different game states
        if current_state == STATE_BREAK_REMINDER:
            print(f"In break reminder state, time since reminder: {current_time - last_break_reminder:.2f}s")
            # Check if player has ignored break for too long
            if current_time - last_break_reminder >= ignore_duration_threshold:
                current_state = STATE_COOLDOWN_ACTIVE
                cooldown_start_time = current_time
                weekly_stats["breaks_ignored"] += 1
                print("Break ignored, entering cooldown state")
        
        elif current_state == STATE_BREAK_TAKEN:
            print(f"In break taken state, time since break start: {current_time - break_start_time:.2f}s")
            if current_time - break_start_time >= break_duration:
                current_state = STATE_NORMAL_PLAY
                play_start_time = current_time
                last_break_reminder = current_time  # Reset the break reminder timer
                print("Break completed, returning to normal play")
                # Reset cooldown intensity and breaks ignored count after a proper break
                cooldown_intensity = 0
                breaks_ignored_count = 0
                hide_progression = False
                hide_score = False
                black_and_white = False  # Reset black and white effect
                
                # Reset sound volumes to baseline
                explosion_fx.set_volume(base_explosion_volume)
                explosion2_fx.set_volume(base_explosion2_volume)
                laser_fx.set_volume(base_laser_volume)
                
                # Ensure spaceship is in the sprite group after break
                if len(spaceship_group) == 0 and spaceship.health_remaining > 0:
                    spaceship_group.add(spaceship)
        
        elif current_state == STATE_ENFORCED_COOLDOWN:
            # Check if enforced break is over
            if current_time - break_start_time >= break_duration:
                current_state = STATE_COOLDOWN_ACTIVE
                cooldown_start_time = current_time
                # Ensure spaceship is in the sprite group after enforced cooldown
                if len(spaceship_group) == 0 and spaceship.health_remaining > 0:
                    spaceship_group.add(spaceship)
        
        elif current_state == STATE_COOLDOWN_ACTIVE:
            # Check for voluntary break during cooldown
            key = pygame.key.get_pressed()
            if key[pygame.K_p]:  # P key for pause/break
                current_state = STATE_BREAK_TAKEN
                break_start_time = current_time
                weekly_stats["breaks_taken"] += 1
            # Only return to normal play after the full cooldown duration
            elif current_time - cooldown_start_time >= ignore_duration_threshold:
                current_state = STATE_NORMAL_PLAY
                print(f"Cooldown completed - returning to normal play")

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
                alien_bullet = Alien_Bullets(attacking_alien.rect.centerx, attacking_alien.rect.bottom)
                alien_bullet_group.add(alien_bullet)
                last_alien_shot = time_now

            # Check if all the aliens have been killed
            if len(alien_group) == 0:
                # Level completed
                if current_level == max_level_reached:
                    # Update max level reached if this is a new level
                    max_level_reached += 1
                    weekly_stats["max_level"] = max_level_reached
                
                # Advance to next level
                current_level += 1
                
                # Create new aliens for next level
                create_aliens()
                
                # Display level up message
                level_up_message = f"LEVEL {current_level}!"
                draw_text(level_up_message, font40, yellow, int(screen_width / 2 - 100), int(screen_height / 2))
                pygame.display.update()
                pygame.time.delay(1000)  # Show message for 1 second
                
                # Reset player position for new level
                spaceship.rect.center = [int(screen_width / 2), screen_height - 100]

            if game_over == 0:
                # Only update game elements if not in break reminder or break taken states
                if current_state not in [STATE_BREAK_REMINDER, STATE_BREAK_TAKEN, STATE_ENFORCED_COOLDOWN]:
                    # Update spaceship
                    game_over = spaceship.update()

                    # Update sprite groups
                    bullet_group.update()
                    alien_group.update()
                    alien_bullet_group.update()
            else:
                # If this is the first frame of game over, record the time
                if game_over_time == 0:
                    game_over_time = current_time
                
                # Draw more prominent end of session overlay
                overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 200))  # Darker semi-transparent black for better contrast
                screen.blit(overlay, (0, 0))
                
                # Draw a highlighted box for the end session message
                message_box = pygame.Rect(screen_width//2 - 200, screen_height//2 - 150, 400, 300)
                pygame.draw.rect(screen, (50, 50, 50), message_box)
                pygame.draw.rect(screen, yellow, message_box, 3)  # Yellow border
                
                if game_over == -1:
                    draw_text('GAME OVER!', font40, red, int(screen_width / 2 - 120), int(screen_height / 2 - 120))
                if game_over == 1:
                    draw_text('YOU WIN!', font40, green, int(screen_width / 2 - 100), int(screen_height / 2 - 120))


                # Display score with more prominence
                draw_text(f'Final Score: {score}', font30, yellow, int(screen_width / 2 - 100), int(screen_height / 2 - 50))
                
                # Add instruction text
                draw_text('Choose an option:', font30, white, int(screen_width / 2 - 120), int(screen_height / 2))
                
                # Draw end of session buttons
                new_game_button.draw()
                quit_button.draw()
                
                # Check button hovers
                new_game_button.check_hover(mouse_pos)
                quit_button.check_hover(mouse_pos)
                
                # Check button clicks
                if new_game_button.check_click(mouse_pos, mouse_click):
                    # Update high score before reset
                    if score > weekly_stats["high_score"]:
                        weekly_stats["high_score"] = score
                    reset_game()
                
                if quit_button.check_click(mouse_pos, mouse_click):
                    # Save stats before quitting
                    weekly_stats["total_play_time"] += int(time.time() - session_start_time)
                    if score > weekly_stats["high_score"]:
                        weekly_stats["high_score"] = score
                    save_leaderboard()
                    run = False

        if countdown > 0:
            draw_text('GET READY!', font40, white, int(screen_width / 2 - 110), int(screen_height / 2 + 50))
            draw_text(str(countdown), font40, white, int(screen_width / 2 - 10), int(screen_height / 2 + 100))
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
            draw_bg()
            
            # Draw score and progression first (they should remain in color)
            if not hide_score:
                draw_text(f"SCORE: {score}", font30, white, 10, 30)
            if not hide_progression:
                draw_progression_info()
            
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
            draw_bg()
            if not hide_score:
                draw_text(f"SCORE: {score}", font30, white, 10, 30)
            if not hide_progression:
                draw_progression_info()
            spaceship_group.draw(screen)
            bullet_group.draw(screen)
            alien_group.draw(screen)
            alien_bullet_group.draw(screen)
            explosion_group.draw(screen)
            
            # Draw game over messages if needed
            if game_over != 0:
                # Draw more prominent end of session overlay
                overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 200))  # Darker semi-transparent black for better contrast
                screen.blit(overlay, (0, 0))
                
                # Draw a highlighted box for the end session message
                message_box = pygame.Rect(screen_width//2 - 200, screen_height//2 - 150, 400, 300)
                pygame.draw.rect(screen, (50, 50, 50), message_box)
                pygame.draw.rect(screen, yellow, message_box, 3)  # Yellow border
                
                if game_over == -1:
                    draw_text('GAME OVER!', font40, red, int(screen_width / 2 - 120), int(screen_height / 2 - 120))
                if game_over == 1:
                    draw_text('YOU WIN!', font40, green, int(screen_width / 2 - 100), int(screen_height / 2 - 120))
                
                # Display score with more prominence
                draw_text(f'Final Score: {score}', font30, yellow, int(screen_width / 2 - 100), int(screen_height / 2 - 50))
                
                # Add instruction text
                draw_text('Choose an option:', font30, white, int(screen_width / 2 - 120), int(screen_height / 2))
                
                # Draw end of session buttons
                new_game_button.draw()
                quit_button.draw()
                
                # Check button hovers
                new_game_button.check_hover(mouse_pos)
                quit_button.check_hover(mouse_pos)
                
                # Check button clicks
                if new_game_button.check_click(mouse_pos, mouse_click):
                    # Update high score before reset
                    if score > weekly_stats["high_score"]:
                        weekly_stats["high_score"] = score
                    reset_game()
                
                if quit_button.check_click(mouse_pos, mouse_click):
                    # Save stats before quitting
                    weekly_stats["total_play_time"] += int(time.time() - session_start_time)
                    if score > weekly_stats["high_score"]:
                        weekly_stats["high_score"] = score
                    save_leaderboard()
                    run = False

        # Draw state-specific overlays last to ensure they stay on top
        if current_state == STATE_BREAK_REMINDER:
            draw_break_reminder()
            
            # Check button hovers
            take_break_button.check_hover(mouse_pos)
            ignore_break_button.check_hover(mouse_pos)
            
            # Check button clicks
            if take_break_button.check_click(mouse_pos, mouse_click):
                print("Take break button clicked")
                current_state = STATE_BREAK_TAKEN
                break_start_time = current_time
                last_break_reminder = current_time  # Only update last_break_reminder when player makes a choice
                weekly_stats["breaks_taken"] += 1
                current_break_message = ""  # Reset message
                
            if ignore_break_button.check_click(mouse_pos, mouse_click):
                print("Ignore break button clicked")
                breaks_ignored_count += 1
                weekly_stats["breaks_ignored"] += 1
                last_break_reminder = current_time  # Only update last_break_reminder when player makes a choice
                
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
                
        elif current_state == STATE_COOLDOWN_ACTIVE:
            # Draw cooldown overlay last to ensure it stays on top
            draw_cooldown_overlay()
            
        elif current_state == STATE_ENFORCED_COOLDOWN:
            draw_enforced_cooldown()
            
        elif current_state == STATE_BREAK_TAKEN:
            draw_break_screen()
            
            # Check if break is over
            if current_time - break_start_time >= break_duration:
                current_state = STATE_NORMAL_PLAY
                play_start_time = current_time
                last_break_reminder = current_time
                print("Break completed, returning to normal play")
                # Reset cooldown intensity and breaks ignored count after a proper break
                cooldown_intensity = 0
                breaks_ignored_count = 0
                hide_progression = False
                hide_score = False
                black_and_white = False  # Reset black and white effect
                
                # Reset sound volumes to baseline
                explosion_fx.set_volume(base_explosion_volume)
                explosion2_fx.set_volume(base_explosion2_volume)
                laser_fx.set_volume(base_laser_volume)
                
                # Ensure spaceship is in the sprite group after break
                if len(spaceship_group) == 0 and spaceship.health_remaining > 0:
                    spaceship_group.add(spaceship)

    pygame.display.update()

# Save stats before quitting
weekly_stats["total_play_time"] += int(time.time() - session_start_time)
if score > weekly_stats["high_score"]:
    weekly_stats["high_score"] = score
save_leaderboard()

# Calculate session duration at the end
session_end_time = time.time()
# session_start_time should have been initialized at the actual start of the session
session_duration = int(session_end_time - session_start_time)

save_session_duration(session_duration)

save_game_stats(
    mode=current_mode,
    duration=session_duration,
    took_break=weekly_stats["breaks_taken"] > 0,
    level=weekly_stats["max_level"],
    breaks_ignored=weekly_stats["breaks_ignored"]
)

pygame.quit()

