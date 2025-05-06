"""
Aliens Module

This module contains the Aliens class for enemy entities.
"""

import pygame
import random
from .explosion import Explosion

class Aliens(pygame.sprite.Sprite):
    def __init__(self, x, y, level):
        pygame.sprite.Sprite.__init__(self)
        alien_num = str(random.randint(1, 5))
        self.image = pygame.image.load(f"img/alien{alien_num}.png")
        self.bw_image = pygame.image.load(f"img/bw/alien{alien_num}_bw_cleaned_final.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.move_counter = 0
        self.move_direction = 1
        
        # Speed increases with level
        self.base_speed = 2  # Increased from 1 to 2
        self.speed_multiplier = 1 + (level - 1) * 0.1  # Reduced from 0.2 to 0.1 for smoother progression

    def update(self, *args, **kwargs):
        # If no arguments are provided, just do basic movement
        if len(args) == 0:
            move_speed = self.base_speed * self.speed_multiplier
            self.rect.x += self.move_direction * move_speed
            self.move_counter += 1
            if abs(self.move_counter) > 75:
                self.move_direction *= -1
                self.move_counter *= self.move_direction
            return

        # Otherwise, handle full update with all parameters
        screen, alien_bullet_group, explosion2_fx, base_explosion2_volume, current_state, cooldown_intensity, level = args
        
        # No slowdown during cooldown - maintain gameplay efficiency
        # But increase speed based on level
        move_speed = self.base_speed * self.speed_multiplier
            
        self.rect.x += self.move_direction * move_speed
        self.move_counter += 1
        if abs(self.move_counter) > 75:
            self.move_direction *= -1
            self.move_counter *= self.move_direction

class Alien_Bullets(pygame.sprite.Sprite):
    def __init__(self, x, y, current_level):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/alien_bullet.png")
        self.bw_image = pygame.image.load("img/bw/alien_bullet_bw_cleaned_final.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        
        # Speed increases with level
        self.base_speed = 2
        self.speed_multiplier = 1 + (current_level - 1) * 0.15  # 15% faster per level

    def update(self, screen, spaceship_group, explosion_group, explosion2_fx, base_explosion2_volume, current_state, cooldown_intensity):
        # No slowdown during cooldown - maintain gameplay efficiency
        # But increase speed based on level
        bullet_speed = self.base_speed * self.speed_multiplier
            
        self.rect.y += bullet_speed
        if self.rect.top > screen.get_height():
            self.kill()
        if pygame.sprite.spritecollide(self, spaceship_group, False, pygame.sprite.collide_mask):
            self.kill()
            
            # Adjust sound volume based on cooldown state
            if current_state == "CooldownActive":
                # Volume decreases gradually with intensity (100% to 0%)
                volume_multiplier = (100.0 - cooldown_intensity) / 100.0
                explosion2_fx.set_volume(base_explosion2_volume * volume_multiplier)
            else:
                explosion2_fx.set_volume(base_explosion2_volume)
                
            explosion2_fx.play()
            
            # Reduce spaceship health
            for spaceship in spaceship_group:
                spaceship.health_remaining -= 1
            
            # Create explosion at bullet's position
            explosion = Explosion(self.rect.centerx, self.rect.centery, 1)
            explosion_group.add(explosion) 