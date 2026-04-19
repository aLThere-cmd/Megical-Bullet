"""
Boss class with multiple phases and spell card patterns.
"""
import pygame
import math
import random
from config.settings import (
    PLAYFIELD_X, PLAYFIELD_Y, PLAYFIELD_WIDTH, PLAYFIELD_HEIGHT,
    BOSS_PHASE_HP, BOSS_PHASE_TIME, BOSS_MOVE_SPEED, BOSS_SCORE,
    ENEMY_BULLET_SPEED_SLOW, ENEMY_BULLET_SPEED_MEDIUM, ENEMY_BULLET_SPEED_FAST,
    BULLET_COLORS, FPS,
)
from utils.renderer import draw_glow_circle, draw_star
from utils.math_helpers import angle_to, wave_value, lerp


class Boss(pygame.sprite.Sprite):
    """Boss enemy with multiple spell card phases."""

    def __init__(self, difficulty_mult=1.0):
        super().__init__()
        self.sprite_size = 64
        self.image = pygame.Surface((self.sprite_size, self.sprite_size), pygame.SRCALPHA)

        # Position
        self.x = float(PLAYFIELD_X + PLAYFIELD_WIDTH // 2)
        self.y = float(PLAYFIELD_Y - 40)
        self.target_x = self.x
        self.target_y = float(PLAYFIELD_Y + 100)
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))
        self.radius = 20

        # Phases
        self.difficulty_mult = difficulty_mult
        self.phase = 0
        self.max_phases = len(BOSS_PHASE_HP)
        self.hp = int(BOSS_PHASE_HP[0] * difficulty_mult)
        self.max_hp = self.hp
        self.phase_timer = BOSS_PHASE_TIME[0]
        self.score_value = BOSS_SCORE

        # State
        self.entering = True
        self.is_alive = True
        self.defeated = False
        self.anim_timer = 0
        self.shoot_timer = 0
        self.pattern_timer = 0
        self.pattern_angle = 0.0
        self.move_timer = 0
        self.status_effects = {}

        # Visual
        self.flash_timer = 0
        self.body_color = (220, 140, 255)
        self.color = self.body_color
        self.glow_color = (255, 180, 255)

    @property
    def phase_name(self):
        names = ["Non-Spell", "Spell Card 1: Starfall Cascade", "Spell Card 2: Galaxy Spiral"]
        if self.phase < len(names):
            return names[self.phase]
        return f"Phase {self.phase + 1}"

    @property
    def is_spell_card(self):
        return self.phase > 0

    @property
    def hp_ratio(self):
        return max(0, self.hp / self.max_hp) if self.max_hp > 0 else 0

    def take_damage(self, damage):
        """Take damage, returns True if phase ends."""
        if self.entering or self.defeated:
            return False

        self.hp -= damage
        self.flash_timer = 3

        if self.hp <= 0:
            return self._next_phase()
        return False

    def apply_status_effect(self, effect_name, duration_frames, damage_percent):
        from config.settings import FPS
        self.status_effects[effect_name] = {
            'timer': duration_frames,
            'tick_timer': FPS,
            'damage_percent': damage_percent
        }

    def process_status_effects(self):
        """Process active status effects. Returns True if phase ends/boss dies."""
        from config.settings import FPS
        effects_to_remove = []
        phase_ended = False
        
        for effect_name, data in self.status_effects.items():
            data['timer'] -= 1
            data['tick_timer'] -= 1
            
            if data['tick_timer'] <= 0:
                tick_dmg = self.max_hp * data['damage_percent']
                if self.take_damage(tick_dmg):
                    phase_ended = True
                data['tick_timer'] = FPS
                
            if data['timer'] <= 0:
                effects_to_remove.append(effect_name)
                
        for effect_name in effects_to_remove:
            del self.status_effects[effect_name]
            
        return phase_ended

    def _next_phase(self):
        """Advance to next phase. Returns True if boss is defeated."""
        self.phase += 1
        if self.phase >= self.max_phases:
            self.defeated = True
            self.is_alive = False
            return True

        self.hp = int(BOSS_PHASE_HP[self.phase] * self.difficulty_mult)
        self.max_hp = self.hp
        self.phase_timer = BOSS_PHASE_TIME[self.phase]
        self.pattern_timer = 0
        self.pattern_angle = 0
        self.flash_timer = 15
        # Move to center
        self.target_x = float(PLAYFIELD_X + PLAYFIELD_WIDTH // 2)
        self.target_y = float(PLAYFIELD_Y + 100)
        return False

    def get_bullet_params(self, player_x, player_y):
        """Get bullets based on current phase."""
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
        """Non-spell: aimed bursts + circle sprays."""
        params = []

        if self.pattern_timer % 30 == 0:
            # Aimed burst
            angle = angle_to(self.x, self.y, player_x, player_y)
            for i in range(3):
                spread = (i - 1) * 0.12
                speed = ENEMY_BULLET_SPEED_MEDIUM * self.difficulty_mult * (1.0 - i * 0.1)
                params.append((speed, angle + spread, 0, 5, "circle"))

        if self.pattern_timer % 60 == 30:
            # Circle spray
            count = 12 + int(4 * self.difficulty_mult)
            for i in range(count):
                angle = self.pattern_angle + (2 * math.pi * i / count)
                params.append(
                    (ENEMY_BULLET_SPEED_SLOW * self.difficulty_mult, angle, 5, 4, "circle")
                )
            self.pattern_angle += 0.15

        self.shoot_timer = 4
        return params

    def _pattern_spell1(self, player_x, player_y):
        """Spell Card 1: Starfall Cascade - dense circular patterns with aimed streams."""
        params = []

        if self.pattern_timer % 8 == 0:
            # Rotating dense circle
            count = 6 + int(4 * self.difficulty_mult)
            for i in range(count):
                angle = self.pattern_angle + (2 * math.pi * i / count)
                speed = ENEMY_BULLET_SPEED_MEDIUM * self.difficulty_mult * 0.9
                params.append((speed, angle, 1, 5, "circle"))

                # Counter-rotating layer
                angle2 = -self.pattern_angle + (2 * math.pi * i / count) + math.pi / count
                params.append(
                    (speed * 0.7, angle2, 3, 4, "diamond")
                )
            self.pattern_angle += 0.12

        if self.pattern_timer % 45 == 0:
            # Aimed fast shots
            angle = angle_to(self.x, self.y, player_x, player_y)
            for i in range(5):
                spread = (i - 2) * 0.08
                params.append(
                    (ENEMY_BULLET_SPEED_FAST * self.difficulty_mult * 0.7,
                     angle + spread, 6, 6, "circle")
                )

        self.shoot_timer = 3
        return params

    def _pattern_spell2(self, player_x, player_y):
        """Spell Card 2: Galaxy Spiral - double spirals with random bursts."""
        params = []

        if self.pattern_timer % 4 == 0:
            # Double spiral
            for arm in range(2):
                angle = self.pattern_angle + arm * math.pi
                speed = ENEMY_BULLET_SPEED_MEDIUM * self.difficulty_mult
                color_idx = 3 if arm == 0 else 7
                params.append((speed, angle, color_idx, 5, "circle"))

            # Third spiral on harder difficulties
            if self.difficulty_mult >= 1.3:
                for arm in range(3):
                    angle = -self.pattern_angle * 0.7 + arm * (2 * math.pi / 3)
                    params.append(
                        (ENEMY_BULLET_SPEED_SLOW * self.difficulty_mult,
                         angle, 4, 4, "diamond")
                    )

            self.pattern_angle += 0.08 + 0.02 * self.difficulty_mult

        if self.pattern_timer % 90 == 0:
            # Random burst
            count = 20 + int(10 * self.difficulty_mult)
            for i in range(count):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(1.0, 3.5) * self.difficulty_mult
                params.append((speed, angle, random.randint(0, 7), 4, "circle"))

        self.shoot_timer = 2
        return params

    def update(self):
        self.anim_timer += 1
        if self.shoot_timer > 0:
            self.shoot_timer -= 1
        if not self.entering and not self.defeated:
            self.pattern_timer += 1
        if self.flash_timer > 0:
            self.flash_timer -= 1

        # Enter animation
        if self.entering:
            dy = self.target_y - self.y
            if abs(dy) < 2:
                self.entering = False
                self.y = self.target_y
            else:
                self.y += dy * 0.03
        else:
            # Phase timer
            if not self.defeated:
                self.phase_timer -= 1
                if self.phase_timer <= 0:
                    self._next_phase()

            # Boss movement - drift toward target
            self.move_timer += 1
            if self.move_timer > 120:
                self.move_timer = 0
                padding = 60
                self.target_x = random.uniform(
                    PLAYFIELD_X + padding,
                    PLAYFIELD_X + PLAYFIELD_WIDTH - padding
                )
                self.target_y = random.uniform(
                    PLAYFIELD_Y + 60,
                    PLAYFIELD_Y + 180
                )

            dx = self.target_x - self.x
            dy = self.target_y - self.y
            self.x += dx * 0.02
            self.y += dy * 0.02

        self.rect.center = (int(self.x), int(self.y))
        self._draw_sprite()

    def _draw_sprite(self):
        """Draw boss sprite."""
        self.image = pygame.Surface((self.sprite_size, self.sprite_size), pygame.SRCALPHA)
        cx, cy = self.sprite_size // 2, self.sprite_size // 2

        # Flash on damage
        if self.flash_timer > 0:
            pygame.draw.circle(self.image, (255, 255, 255, 180), (cx, cy), 28)

        # Aura
        aura_pulse = 0.6 + 0.4 * math.sin(self.anim_timer * 0.05)
        aura_color = self.glow_color if not self.is_spell_card else (255, 220, 100)
        draw_glow_circle(self.image, aura_color, (cx, cy), 22, 0.5 * aura_pulse)

        # Rotating magical circle (outer ring)
        ring_r = 24 + wave_value(self.anim_timer, 0.03, 2)
        for i in range(8):
            angle = self.anim_timer * 0.04 + i * math.pi / 4
            px = cx + math.cos(angle) * ring_r
            py = cy + math.sin(angle) * ring_r
            dot_color = (*aura_color[:3], 150)
            pygame.draw.circle(self.image, dot_color, (int(px), int(py)), 2)

        # Outer ring line
        pygame.draw.circle(self.image, (*aura_color[:3], 60), (cx, cy), int(ring_r), 1)

        # Wings
        wing_phase = wave_value(self.anim_timer, 0.06, 4)
        for side in [-1, 1]:
            wing_pts = [
                (cx + side * 6, cy - 2),
                (cx + side * 22, cy - 14 + wing_phase),
                (cx + side * 26, cy + 2 + wing_phase),
                (cx + side * 18, cy + 10),
                (cx + side * 6, cy + 4),
            ]
            wing_col = (*self.body_color[:3], 140)
            pygame.draw.polygon(self.image, wing_col, wing_pts)

        # Body
        pygame.draw.circle(self.image, self.body_color, (cx, cy), 10)

        # Crown/star
        star_col = (255, 255, 200) if not self.is_spell_card else (255, 200, 100)
        draw_star(self.image, star_col, (cx, cy - 14), 6, 3, 5,
                  self.anim_timer * 0.03)

        # Inner detail
        pygame.draw.circle(self.image, (255, 220, 255), (cx, cy), 5)
        pygame.draw.circle(self.image, (255, 255, 255), (cx, cy), 2)
