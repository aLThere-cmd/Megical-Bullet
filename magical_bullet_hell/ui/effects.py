"""
Screen effects: shake, flash, bomb visual, background dimming.
"""
import pygame
import math
import random
from config.settings import (
    PLAYFIELD_X, PLAYFIELD_Y, PLAYFIELD_WIDTH, PLAYFIELD_HEIGHT,
    WINDOW_WIDTH, WINDOW_HEIGHT,
)


class ScreenEffects:
    """Manages screen-level visual effects."""

    def __init__(self):
        # Screen shake
        self.shake_x = 0
        self.shake_y = 0
        self.shake_intensity = 0
        self.shake_timer = 0

        # Flash
        self.flash_color = (255, 255, 255)
        self.flash_alpha = 0
        self.flash_timer = 0
        self.flash_duration = 0

        # Bomb visual
        self.bomb_active = False
        self.bomb_timer = 0
        self.bomb_max_timer = 0
        self.bomb_x = 0
        self.bomb_y = 0

        # Background dim for boss spells
        self.dim_alpha = 0
        self.dim_target = 0

    def start_shake(self, intensity=5, duration=10):
        """Start screen shake effect."""
        self.shake_intensity = intensity
        self.shake_timer = duration

    def start_flash(self, color=(255, 255, 255), duration=8):
        """Start screen flash effect."""
        self.flash_color = color
        self.flash_alpha = 255
        self.flash_timer = duration
        self.flash_duration = duration

    def start_bomb_visual(self, x, y, duration=60):
        """Start bomb visual effect."""
        self.bomb_active = True
        self.bomb_timer = duration
        self.bomb_max_timer = duration
        self.bomb_x = x
        self.bomb_y = y

    def set_dim(self, target_alpha):
        """Set target dim level for background."""
        self.dim_target = target_alpha

    def update(self):
        """Update all effects."""
        # Shake
        if self.shake_timer > 0:
            self.shake_timer -= 1
            intensity = self.shake_intensity * (self.shake_timer / max(1, self.shake_timer + 1))
            self.shake_x = random.uniform(-intensity, intensity)
            self.shake_y = random.uniform(-intensity, intensity)
        else:
            self.shake_x = 0
            self.shake_y = 0

        # Flash
        if self.flash_timer > 0:
            self.flash_timer -= 1
            t = self.flash_timer / max(1, self.flash_duration)
            self.flash_alpha = int(255 * t)
        else:
            self.flash_alpha = 0

        # Bomb
        if self.bomb_active:
            self.bomb_timer -= 1
            if self.bomb_timer <= 0:
                self.bomb_active = False

        # Dim interpolation
        if self.dim_alpha < self.dim_target:
            self.dim_alpha = min(self.dim_target, self.dim_alpha + 3)
        elif self.dim_alpha > self.dim_target:
            self.dim_alpha = max(self.dim_target, self.dim_alpha - 3)

    def draw(self, surface, offset_x=0, offset_y=0):
        """Draw all active effects."""
        # Background dim
        if self.dim_alpha > 0:
            dim_surf = pygame.Surface((PLAYFIELD_WIDTH, PLAYFIELD_HEIGHT), pygame.SRCALPHA)
            dim_surf.fill((0, 0, 20, int(self.dim_alpha)))
            surface.blit(dim_surf, (PLAYFIELD_X + offset_x, PLAYFIELD_Y + offset_y))

        # Bomb visual
        if self.bomb_active:
            self._draw_bomb(surface, offset_x, offset_y)

        # Flash
        if self.flash_alpha > 0:
            flash_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            flash_surf.fill((*self.flash_color[:3], min(255, self.flash_alpha)))
            surface.blit(flash_surf, (0, 0))

    def _draw_bomb(self, surface, offset_x=0, offset_y=0):
        """Draw bomb/spell card visual effect with stars and shockwaves."""
        t = 1.0 - (self.bomb_timer / max(1, self.bomb_max_timer))
        max_radius = max(PLAYFIELD_WIDTH, PLAYFIELD_HEIGHT) * 1.2
        cx, cy = int(self.bomb_x) + offset_x, int(self.bomb_y) + offset_y

        # Expanding rings
        for i in range(4):
            ring_t = max(0, t - i * 0.15)
            if ring_t <= 0 or ring_t >= 1.0: continue
            
            radius = int(ring_t * max_radius)
            alpha = int(200 * (1.0 - ring_t))
            
            # Draw shockwave circle
            color = [(255, 100, 255), (100, 200, 255), (255, 255, 255)][i % 3]
            pygame.draw.circle(surface, (*color, alpha), (cx, cy), radius, 2)
            
            # Draw rotating star shapes
            from utils.renderer import draw_star
            star_radius = int(radius * 0.3)
            star_color = (*color, int(alpha * 0.5))
            if star_radius > 5:
                for angle_off in range(5):
                    ang = self.bomb_timer * 0.05 + angle_off * (math.pi * 2 / 5)
                    sx = cx + math.cos(ang) * radius
                    sy = cy + math.sin(ang) * radius
                    draw_star(surface, star_color, (int(sx), int(sy)), star_radius, star_radius//2, 5, ang * 2)

        # Center flash
        if t < 0.3:
            glow_alpha = int(255 * (1.0 - t / 0.3))
            pygame.draw.circle(surface, (255, 255, 255, glow_alpha), (cx, cy), int(50 + t * 200))

    @property
    def offset(self):
        """Get shake offset as (x, y) tuple."""
        return (int(self.shake_x), int(self.shake_y))
