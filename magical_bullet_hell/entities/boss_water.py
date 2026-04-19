import pygame
import math
import random
from config.settings import (
    PLAYFIELD_X, PLAYFIELD_Y, PLAYFIELD_WIDTH, PLAYFIELD_HEIGHT,
    BOSS_PHASE_HP, BOSS_PHASE_TIME, BOSS_MOVE_SPEED, BOSS_SCORE,
    ENEMY_BULLET_SPEED_SLOW, ENEMY_BULLET_SPEED_MEDIUM,
    BULLET_COLORS, FPS,
)
from utils.renderer import draw_glow_circle, draw_star, draw_diamond
from utils.math_helpers import angle_to, wave_value, lerp
from entities.boss import Boss

class WaterBoss(Boss):
    """Water-themed boss for Stage 2."""

    def __init__(self, difficulty_mult=1.0):
        super().__init__(difficulty_mult)
        self.body_color = (100, 180, 255) # Light Blue
        self.color = self.body_color
        self.glow_color = (150, 220, 255) # Cyan Glow
        self.rain_timer = 0
        
    @property
    def phase_name(self):
        names = ["Non-Spell: Tides", "Spell Card 1: Torrential Downpour", "Spell Card 2: Abyssal Whirlpool"]
        if self.phase < len(names):
            return names[self.phase]
        return f"Phase {self.phase + 1}"

    def update(self):
        super().update()
        if self.phase == 1 and not self.defeated and not self.entering:
            self.rain_timer += 1
            
    def get_bullet_params(self, player_x, player_y):
        if self.entering or self.defeated:
            return []

        if self.shoot_timer > 0:
            return []

        if self.phase == 0:
            return self._pattern_non_spell(player_x, player_y)
        elif self.phase == 1:
            return self._pattern_spell1(player_x, player_y)
        elif self.phase == 2:
            return self._pattern_spell2(player_x, player_y)
        return []

    def _pattern_non_spell(self, player_x, player_y):
        """Hydro Pump style streams."""
        params = []
        if self.pattern_timer % 40 == 0:
            angle = angle_to(self.x, self.y, player_x, player_y)
            for i in range(5):
                speed = ENEMY_BULLET_SPEED_MEDIUM * self.difficulty_mult * (1.2 + i * 0.1)
                params.append((speed, angle, 4, 6, "circle")) # Blue bullets
        
        if self.pattern_timer % 60 == 30:
            count = 10
            for i in range(count):
                angle = self.pattern_angle + (2 * math.pi * i / count)
                params.append((ENEMY_BULLET_SPEED_SLOW * self.difficulty_mult, angle, 1, 4, "circle"))
            self.pattern_angle += 0.2
            
        self.shoot_timer = 5
        return params

    def take_damage(self, damage):
        # Phase 1 is a survival phase (Invincible)
        if self.phase == 1 and not self.entering:
            return False
        return super().take_damage(damage)

    def _pattern_spell1(self, player_x, player_y):
        """Rain Dance - survival phase with falling rain."""
        params = []
        
        # Spiral pattern (less dense to focus on rain)
        if self.pattern_timer % 30 == 0:
            count = 6 + int(2 * self.difficulty_mult)
            for i in range(count):
                angle = self.pattern_angle + (2 * math.pi * i / count)
                params.append((2.5 * self.difficulty_mult, angle, 4, 4, "circle"))
            self.pattern_angle += 0.2

        # RAIN EFFECT: Falling drops from top
        # We use a trick: bullets spawned at y = -200 with vy = 5 will fall into view
        if self.pattern_timer % 3 == 0:
            for _ in range(3 + int(self.difficulty_mult)):
                rx = random.uniform(PLAYFIELD_X, PLAYFIELD_X + PLAYFIELD_WIDTH)
                # Position relative to boss to use the existing spawn_bullets
                rel_x = rx - self.x
                rel_y = (PLAYFIELD_Y - 20) - self.y
                # In systems/bullet_patterns.py, I should update it to support absolute pos 
                # or I can just pass relative pos and handle it in the bullet class.
                # Actually, I'll just return (speed, angle, color, size, type, x, y) 
                # and update spawn_bullets.
                params.append((random.uniform(4, 6), math.pi/2, 4, 3, "diamond", rx, PLAYFIELD_Y - 10))
                
        self.shoot_timer = 2
        return params

    def _pattern_spell2(self, player_x, player_y):
        """Abyssal Whirlpool - dense inward/outward spirals."""
        params = []
        if self.pattern_timer % 6 == 0:
            count = 8 + int(4 * self.difficulty_mult)
            for i in range(count):
                angle = self.pattern_angle + (2 * math.pi * i / count)
                # Outward spiral
                params.append((2.5 * self.difficulty_mult, angle, 4, 5, "circle"))
                # Reverse spiral
                params.append((2.0 * self.difficulty_mult, -self.pattern_angle + (2 * math.pi * i / count), 0, 4, "circle"))
            self.pattern_angle += 0.1
            
        self.shoot_timer = 3
        return params

    def _draw_sprite(self):
        super()._draw_sprite()
        # Add water-specific visuals (bubbles)
        cx, cy = self.sprite_size // 2, self.sprite_size // 2
        for i in range(3):
            angle = self.anim_timer * 0.05 + i * (2 * math.pi / 3)
            r = 15 + math.sin(self.anim_timer * 0.1 + i) * 5
            bx = cx + math.cos(angle) * r
            by = cy + math.sin(angle) * r
            pygame.draw.circle(self.image, (200, 240, 255, 150), (int(bx), int(by)), 4, 1)
