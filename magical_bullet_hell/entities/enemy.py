"""
Enemy classes: Fairy, Witch, and Spirit types.
"""
import pygame
import math
import random
from config.settings import (
    PLAYFIELD_X, PLAYFIELD_Y, PLAYFIELD_WIDTH, PLAYFIELD_HEIGHT,
    ENEMY_FAIRY_HP, ENEMY_FAIRY_SCORE, ENEMY_FAIRY_SHOOT_DELAY,
    ENEMY_WITCH_HP, ENEMY_WITCH_SCORE, ENEMY_WITCH_SHOOT_DELAY,
    ENEMY_SPIRIT_HP, ENEMY_SPIRIT_SCORE, ENEMY_SPIRIT_SHOOT_DELAY,
    COLOR_FAIRY, COLOR_WITCH, COLOR_SPIRIT,
    ENEMY_BULLET_SPEED_SLOW, ENEMY_BULLET_SPEED_MEDIUM, ENEMY_BULLET_SPEED_FAST,
    FPS, STATUS_TICK_RATE
)
from utils.renderer import draw_glow_circle, draw_star, draw_diamond
from utils.math_helpers import angle_to, wave_value


class Enemy(pygame.sprite.Sprite):
    """Base enemy class."""

    def __init__(self, x, y, hp, score_value, color, shoot_delay):
        super().__init__()
        self.x = float(x)
        self.y = float(y)
        self.hp = hp
        self.max_hp = hp
        self.score_value = score_value
        self.color = color
        self.shoot_delay = shoot_delay
        self.shoot_timer = random.randint(0, shoot_delay)
        self.anim_timer = random.randint(0, 100)
        self.alive_timer = 0
        self.status_effects = {}

        # Movement
        self.vx = 0.0
        self.vy = 0.0
        self.target_x = x
        self.target_y = y
        self.move_phase = 0  # 0=enter, 1=idle, 2=exit
        self.enter_speed = 3.5  # Faster entry
        self.idle_timer = 0
        self.idle_duration = random.randint(600, 1200)  # 10-20 seconds

        # Visual
        self.sprite_size = 32
        self.image = pygame.Surface((self.sprite_size, self.sprite_size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        self.radius = 12

    def take_damage(self, damage):
        """Take damage, return True if destroyed."""
        self.hp -= damage
        return self.hp <= 0

    def apply_status_effect(self, effect_name, duration_frames, damage_percent):
        """Apply a status effect. Now supports stacking by allowing multiple entries of the same type."""
        tick_frames = int(STATUS_TICK_RATE * FPS)
        if effect_name not in self.status_effects:
            self.status_effects[effect_name] = []
            
        self.status_effects[effect_name].append({
            'timer': duration_frames,
            'tick_timer': tick_frames,
            'damage_percent': damage_percent
        })

    def process_status_effects(self):
        """Process all active status effect stacks. Returns True if enemy dies."""
        from config.settings import FPS
        died = False
        
        for effect_name, stacks in list(self.status_effects.items()):
            active_stacks = []
            for data in stacks:
                data['timer'] -= 1
                data['tick_timer'] -= 1
                
                if data['tick_timer'] <= 0:
                    tick_dmg = self.max_hp * data['damage_percent']
                    if self.take_damage(tick_dmg):
                        died = True
                    data['tick_timer'] = int(STATUS_TICK_RATE * FPS)
                    
                if data['timer'] > 0:
                    active_stacks.append(data)
            
            if active_stacks:
                self.status_effects[effect_name] = active_stacks
            else:
                del self.status_effects[effect_name]
                
        return died

    def can_shoot(self):
        """Check if enemy can fire."""
        return (self.shoot_timer <= 0 and
                self.move_phase == 1 and
                PLAYFIELD_X < self.x < PLAYFIELD_X + PLAYFIELD_WIDTH and
                PLAYFIELD_Y < self.y < PLAYFIELD_Y + PLAYFIELD_HEIGHT)

    def get_bullet_params(self, player_x, player_y):
        """Override in subclass: return list of (speed, angle, color_idx, size, type)."""
        return []

    def update_movement(self):
        """Update enemy movement based on phase."""
        if self.move_phase == 0:
            # Moving to target position
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < 3:
                self.move_phase = 1
                self.idle_timer = self.idle_duration
            else:
                self.x += (dx / dist) * self.enter_speed
                self.y += (dy / dist) * self.enter_speed
        elif self.move_phase == 1:
            # Idling (slight drift)
            self.x += wave_value(self.anim_timer, 0.02, 0.3)
            self.idle_timer -= 1
            if self.idle_timer <= 0:
                self.move_phase = 2
        elif self.move_phase == 2:
            # Exiting
            self.y -= 1.5
            if self.y < PLAYFIELD_Y - 40:
                self.kill()

    def update(self):
        self.anim_timer += 1
        self.alive_timer += 1
        self.update_movement()

        if self.shoot_timer > 0:
            self.shoot_timer -= 1

        self.rect.center = (int(self.x), int(self.y))
        self._draw_sprite()

    def _draw_sprite(self):
        """Override in subclass for custom visuals."""
        pass

    def reset_shoot_timer(self):
        self.shoot_timer = self.shoot_delay


class Fairy(Enemy):
    """Basic fairy enemy - simple aimed shots."""

    def __init__(self, x, y, target_x, target_y, difficulty_mult=1.0):
        hp = int(ENEMY_FAIRY_HP * difficulty_mult)
        super().__init__(x, y, hp, ENEMY_FAIRY_SCORE, COLOR_FAIRY, ENEMY_FAIRY_SHOOT_DELAY)
        self.target_x = target_x
        self.target_y = target_y
        self.difficulty_mult = difficulty_mult

    def get_bullet_params(self, player_x, player_y):
        angle = angle_to(self.x, self.y, player_x, player_y)
        params = []
        if self.difficulty_mult >= 1.5:
            # 3-way aimed spread for harder difficulties
            spread = 0.2
            params.append((ENEMY_BULLET_SPEED_SLOW * self.difficulty_mult, angle - spread, 1, 4, "circle"))
            params.append((ENEMY_BULLET_SPEED_SLOW * self.difficulty_mult, angle, 1, 4, "circle"))
            params.append((ENEMY_BULLET_SPEED_SLOW * self.difficulty_mult, angle + spread, 1, 4, "circle"))
        else:
            params.append((ENEMY_BULLET_SPEED_SLOW * self.difficulty_mult, angle, 1, 4, "circle"))
        return params

    def _draw_sprite(self):
        self.image = pygame.Surface((self.sprite_size, self.sprite_size), pygame.SRCALPHA)
        cx, cy = self.sprite_size // 2, self.sprite_size // 2

        # Glow
        draw_glow_circle(self.image, self.color, (cx, cy), 8, 0.3)

        # Wings
        wing_bob = wave_value(self.anim_timer, 0.15, 2)
        for side in [-1, 1]:
            wing = [
                (cx + side * 3, cy),
                (cx + side * 12, cy - 6 + wing_bob),
                (cx + side * 10, cy + 4 + wing_bob),
            ]
            pygame.draw.polygon(self.image, (*self.color, 160), wing)

        # Body
        pygame.draw.circle(self.image, self.color, (cx, cy), 6)
        pygame.draw.circle(self.image, (255, 255, 255), (cx, cy), 3)


class Witch(Enemy):
    """Medium witch enemy - spiral bullet patterns."""

    def __init__(self, x, y, target_x, target_y, difficulty_mult=1.0):
        hp = int(ENEMY_WITCH_HP * difficulty_mult)
        super().__init__(x, y, hp, ENEMY_WITCH_SCORE, COLOR_WITCH, ENEMY_WITCH_SHOOT_DELAY)
        self.target_x = target_x
        self.target_y = target_y
        self.difficulty_mult = difficulty_mult
        self.spiral_angle = 0

    def get_bullet_params(self, player_x, player_y):
        params = []
        # Scale count with difficulty
        count = int(3 + (self.difficulty_mult - 1) * 4)
        count = max(3, count)
        for i in range(count):
            angle = self.spiral_angle + (2 * math.pi * i / count)
            params.append(
                (ENEMY_BULLET_SPEED_MEDIUM * self.difficulty_mult * 0.8, angle, 3, 5, "circle")
            )
        self.spiral_angle += 0.4
        return params

    def _draw_sprite(self):
        self.image = pygame.Surface((self.sprite_size, self.sprite_size), pygame.SRCALPHA)
        cx, cy = self.sprite_size // 2, self.sprite_size // 2

        # Glow
        draw_glow_circle(self.image, self.color, (cx, cy), 10, 0.4)

        # Rotating star
        draw_star(self.image, (*self.color, 200), (cx, cy), 12, 6, 5,
                  self.anim_timer * 0.03)

        # Inner circle
        pygame.draw.circle(self.image, (255, 220, 255), (cx, cy), 5)
        pygame.draw.circle(self.image, (255, 255, 255), (cx, cy), 2)


class Spirit(Enemy):
    """Fast spirit enemy - aimed fast shots."""

    def __init__(self, x, y, target_x, target_y, difficulty_mult=1.0):
        hp = int(ENEMY_SPIRIT_HP * difficulty_mult)
        super().__init__(x, y, hp, ENEMY_SPIRIT_SCORE, COLOR_SPIRIT, ENEMY_SPIRIT_SHOOT_DELAY)
        self.target_x = target_x
        self.target_y = target_y
        self.difficulty_mult = difficulty_mult
        self.enter_speed = 2.5

    def get_bullet_params(self, player_x, player_y):
        angle = angle_to(self.x, self.y, player_x, player_y)
        params = []
        # Fewer clusters for high difficulty
        clusters = 1 + int((self.difficulty_mult - 1) * 0.7)
        for c in range(clusters):
            offset = (c - (clusters-1)/2) * 0.15
            params.append((ENEMY_BULLET_SPEED_FAST * self.difficulty_mult * 0.8, angle + offset, 4, 4, "diamond"))
        return params

    def _draw_sprite(self):
        self.image = pygame.Surface((self.sprite_size, self.sprite_size), pygame.SRCALPHA)
        cx, cy = self.sprite_size // 2, self.sprite_size // 2

        # Glow
        phase = self.anim_timer * 0.1
        draw_glow_circle(self.image, self.color, (cx, cy), 8,
                         0.3 + 0.2 * math.sin(phase))

        # Diamond body
        draw_diamond(self.image, (*self.color, 220), (cx, cy), 10)

        # Trail effect (small dots behind)
        for i in range(3):
            ty = cy + 4 + i * 4
            alpha = 150 - i * 45
            pygame.draw.circle(self.image, (*self.color, max(0, alpha)),
                               (cx, ty), 3 - i)


class Slime(Enemy):
    """Bouncing enemy - erratic movement."""

    def __init__(self, x, y, target_x, target_y, difficulty_mult=1.0):
        hp = int(40 * difficulty_mult)
        super().__init__(x, y, hp, 250, (100, 255, 150), 80)
        self.target_x = target_x
        self.target_y = target_y
        self.difficulty_mult = difficulty_mult
        self.enter_speed = 1.0

    def update_movement(self):
        super().update_movement()
        if self.move_phase == 1:
            # Bounce
            self.y += math.sin(self.anim_timer * 0.1) * 1.5
            self.x += math.cos(self.anim_timer * 0.05) * 2.0

    def get_bullet_params(self, player_x, player_y):
        angle = angle_to(self.x, self.y, player_x, player_y)
        if self.difficulty_mult >= 1.8:
            return [
                (3.0 * self.difficulty_mult, angle - 0.15, 5, 5, "circle"),
                (3.0 * self.difficulty_mult, angle + 0.15, 5, 5, "circle"),
            ]
        else:
            return [(3.0 * self.difficulty_mult, angle, 5, 5, "circle")]

    def _draw_sprite(self):
        self.image = pygame.Surface((self.sprite_size, self.sprite_size), pygame.SRCALPHA)
        cx, cy = self.sprite_size // 2, self.sprite_size // 2
        
        # Stretch/squash animation
        stretch = 1.0 + 0.2 * math.sin(self.anim_timer * 0.1)
        width = int(12 * (2.0 - stretch))
        height = int(12 * stretch)
        
        pygame.draw.ellipse(self.image, self.color, (cx - width, cy - height + 4, width * 2, height * 2))
        pygame.draw.circle(self.image, (255, 255, 255), (cx - 4, cy - 2), 2)
        pygame.draw.circle(self.image, (255, 255, 255), (cx + 4, cy - 2), 2)


class AquaSpirit(Enemy):
    """Fast water spirit - rapid bursts."""

    def __init__(self, x, y, target_x, target_y, difficulty_mult=1.0):
        hp = int(35 * difficulty_mult)
        super().__init__(x, y, hp, 350, (100, 200, 255), 40)
        self.target_x = target_x
        self.target_y = target_y
        self.difficulty_mult = difficulty_mult
        self.enter_speed = 3.0

    def get_bullet_params(self, player_x, player_y):
        angle = angle_to(self.x, self.y, player_x, player_y)
        return [
            (5.0 * self.difficulty_mult, angle, 4, 3, "diamond"),
        ]

    def _draw_sprite(self):
        self.image = pygame.Surface((self.sprite_size, self.sprite_size), pygame.SRCALPHA)
        cx, cy = self.sprite_size // 2, self.sprite_size // 2
        
        # Swirling water effect
        for i in range(2):
            angle = self.anim_timer * 0.2 + i * math.pi
            px = cx + math.cos(angle) * 8
            py = cy + math.sin(angle) * 8
            draw_glow_circle(self.image, self.color, (int(px), int(py)), 6, 0.4)
        
        pygame.draw.circle(self.image, (255, 255, 255), (cx, cy), 4)
