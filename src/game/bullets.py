"""
Bullets Module

This module contains the Bullets and Alien_Bullets classes for player and enemy projectiles.
"""

import pygame
import random
from .explosion import Explosion

class Bullets(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/bullet.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.bw_image = self.image.copy()  # Create a copy for black and white version
        
        # Convert to black and white
        for x in range(self.bw_image.get_width()):
            for y in range(self.bw_image.get_height()):
                color = self.bw_image.get_at((x, y))
                gray = (color[0] + color[1] + color[2]) // 3
                self.bw_image.set_at((x, y), (gray, gray, gray, color[3]))

    def update(self, screen, alien_group, explosion_group, explosion_fx, base_explosion_volume, current_state, cooldown_intensity):
        self.rect.y -= 5
        if self.rect.bottom < 0:
            self.kill()
        if pygame.sprite.spritecollide(self, alien_group, True):
            # Adjust explosion volume based on cooldown
            if current_state == "CooldownActive":
                explosion_fx.set_volume(max(0.1, base_explosion_volume - (cooldown_intensity / 200)))
            else:
                explosion_fx.set_volume(base_explosion_volume)
            explosion_fx.play()
            self.kill()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)

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