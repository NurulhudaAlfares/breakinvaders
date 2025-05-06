"""
Spaceship Module

This module contains the Spaceship class for player control.
"""

import pygame
from pygame import mixer
from .explosion import Explosion
from .bullets import Bullets

class Spaceship(pygame.sprite.Sprite):
    def __init__(self, x, y, health):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/spaceship.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.health_start = health
        self.health_remaining = health
        self.last_shot = pygame.time.get_ticks()
        self.speed = 8
        self.bw_image = self.image.copy()  # Create a copy for black and white version
        
        # Convert to black and white
        for x in range(self.bw_image.get_width()):
            for y in range(self.bw_image.get_height()):
                color = self.bw_image.get_at((x, y))
                gray = (color[0] + color[1] + color[2]) // 3
                self.bw_image.set_at((x, y), (gray, gray, gray, color[3]))

    def update(self, screen, current_state, cooldown_intensity, base_laser_volume, laser_fx, bullet_group, explosion_group):
        # Check if spaceship is destroyed
        if self.health_remaining <= 0:
            # Create explosion at spaceship's position
            explosion = Explosion(self.rect.centerx, self.rect.centery, 3)
            explosion_group.add(explosion)
            self.kill()  # Remove the spaceship
            return -1  # Signal game over

        # Get key press
        key = pygame.key.get_pressed()
        
        # Adjust speed based on cooldown intensity
        current_speed = self.speed
        if current_state == "CooldownActive":
            current_speed = max(2, self.speed - (cooldown_intensity / 20))  # Reduce speed based on cooldown
        
        if key[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= current_speed
        if key[pygame.K_RIGHT] and self.rect.right < screen.get_width():
            self.rect.x += current_speed
            
        # Record current time
        time_now = pygame.time.get_ticks()
        
        # Shoot
        if key[pygame.K_SPACE] and time_now - self.last_shot > 500:  # 500ms cooldown between shots
            # Adjust cooldown based on cooldown intensity
            if current_state == "CooldownActive":
                self.last_shot = time_now + (cooldown_intensity * 5)  # Add delay based on cooldown
            else:
                self.last_shot = time_now
                
            # Adjust laser volume based on cooldown
            if current_state == "CooldownActive":
                laser_fx.set_volume(max(0.1, base_laser_volume - (cooldown_intensity / 200)))
            else:
                laser_fx.set_volume(base_laser_volume)
                
            laser_fx.play()
            
            # Create bullet
            bullet = Bullets(self.rect.centerx, self.rect.top)
            bullet_group.add(bullet)
            
        # Update mask
        self.mask = pygame.mask.from_surface(self.image)
        
        # Draw health bar
        pygame.draw.rect(screen, (255, 0, 0), (self.rect.x, (self.rect.bottom + 10), self.rect.width, 15))
        if self.health_remaining > 0:
            pygame.draw.rect(screen, (0, 255, 0), (self.rect.x, (self.rect.bottom + 10), int(self.rect.width * (self.health_remaining / self.health_start)), 15))

        # Return 0 to indicate game is still running
        return 0 