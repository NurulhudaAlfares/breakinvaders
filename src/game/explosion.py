"""
Explosion Module

This module contains the Explosion class for visual effects.
"""

import pygame
import random

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 6):
            img = pygame.image.load(f"img/exp{num}.png")
            if size == 1:
                img = pygame.transform.scale(img, (20, 20))
            if size == 2:
                img = pygame.transform.scale(img, (40, 40))
            if size == 3:
                img = pygame.transform.scale(img, (160, 160))
            self.images.append(img)
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.counter = 0
        self.bw_images = []  # Store black and white versions
        
        # Create black and white versions of all explosion frames
        for img in self.images:
            bw_img = img.copy()
            for x in range(bw_img.get_width()):
                for y in range(bw_img.get_height()):
                    color = bw_img.get_at((x, y))
                    gray = (color[0] + color[1] + color[2]) // 3
                    bw_img.set_at((x, y), (gray, gray, gray, color[3]))
            self.bw_images.append(bw_img)

    def update(self):
        explosion_speed = 3
        self.counter += 1
        if self.counter >= explosion_speed and self.index < len(self.images) - 1:
            self.counter = 0
            self.index += 1
            self.image = self.images[self.index]
        if self.index >= len(self.images) - 1 and self.counter >= explosion_speed:
            self.kill() 