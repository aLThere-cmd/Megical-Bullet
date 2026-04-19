"""
Player (Magical Girl) class with movement, shooting, focus mode, and bombs.
"""
import pygame
import math
from config.settings import (
    PLAYFIELD_X, PLAYFIELD_Y, PLAYFIELD_WIDTH, PLAYFIELD_HEIGHT,
    PLAYER_SPEED, PLAYER_FOCUS_SPEED, PLAYER_HITBOX_RADIUS, PLAYER_GRAZE_RADIUS,
    PLAYER_START_LIVES, PLAYER_START_BOMBS, PLAYER_START_POWER, PLAYER_MAX_POWER,
    PLAYER_SHOOT_DELAY, PLAYER_FOCUS_SHOOT_DELAY, PLAYER_INVINCIBLE_TIME,
    PLAYER_BOMB_DURATION, PLAYER_BOMB_INVINCIBLE, PLAYER_RESPAWN_Y_OFFSET,
    PLAYER_BULLET_SPEED, PLAYER_BULLET_DAMAGE,
    PLAYER_FOCUS_BULLET_SPEED, PLAYER_FOCUS_BULLET_DAMAGE,
    COLOR_PLAYER_BODY, COLOR_PLAYER_WING, COLOR_PLAYER_GLOW,
    COLOR_HITBOX, COLOR_HITBOX_RING,
    KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_SHOOT, KEY_BOMB, KEY_FOCUS,
)
from entities.bullet import PlayerBullet
from utils.renderer import draw_glow_circle, draw_star
from utils.math_helpers import clamp, wave_value


class Player(pygame.sprite.Sprite):
    """The Magical Girl (or Muscular Man) player character."""

    def __init__(self, bullet_group, enemy_bullet_group=None, character_id="magical_girl"):
        super().__init__()
        self.bullet_group = bullet_group
        self.enemy_bullet_group = enemy_bullet_group
        self.character_id = character_id

        # Position
        self.x = float(PLAYFIELD_X + PLAYFIELD_WIDTH // 2)
        self.y = float(PLAYFIELD_Y + PLAYFIELD_HEIGHT - 80)

        # Create visual surface
        self.base_size = 40
        self.image = pygame.Surface((self.base_size, self.base_size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))

        # State
        self.lives = PLAYER_START_LIVES
        self.bombs = 3 if self.character_id == "magical_girl" else 1
        self.power = 4.0  # Powerups removed, start at max power
        self.score = 0
        self.graze_count = 0
        self.focused = False
        self.shooting = False
        self.shoot_timer = 0
        self.invincible_timer = 0
        self.bomb_timer = 0
        self.dead = False
        self.death_timer = 0
        self.anim_timer = 0
        self.base_damage_mult = 0.20 if self.character_id == "magical_girl" else 1.0
        self.damage_multiplier = self.base_damage_mult
        
        # Apply passives
        if self.character_id == "muscular_man":
            self.lives += 2

    @property
    def hitbox_radius(self):
        return PLAYER_HITBOX_RADIUS

    @property
    def graze_radius(self):
        return PLAYER_GRAZE_RADIUS

    def handle_input(self, keys):
        """Process player input."""
        if self.dead:
            return

        # Movement
        dx, dy = 0.0, 0.0
        if keys[KEY_UP]:
            dy -= 1
        if keys[KEY_DOWN]:
            dy += 1
        if keys[KEY_LEFT]:
            dx -= 1
        if keys[KEY_RIGHT]:
            dx += 1

        # Normalize diagonal movement
        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071

        # Focus mode
        self.focused = keys[KEY_FOCUS]
        speed = PLAYER_FOCUS_SPEED if self.focused else PLAYER_SPEED

        self.x += dx * speed
        self.y += dy * speed

        # Clamp to playfield
        margin = 8
        self.x = clamp(self.x, PLAYFIELD_X + margin, PLAYFIELD_X + PLAYFIELD_WIDTH - margin)
        self.y = clamp(self.y, PLAYFIELD_Y + margin, PLAYFIELD_Y + PLAYFIELD_HEIGHT - margin)

        # Shooting
        self.shooting = keys[KEY_SHOOT]

        # Bomb
        if keys[KEY_BOMB]:
            return self.use_bomb()
        return False

    def use_bomb(self):
        """Activate spell card (bomb)."""
        if self.bombs > 0 and self.bomb_timer <= 0:
            self.bombs -= 1
            if self.character_id == "magical_girl":
                self.bomb_timer = PLAYER_BOMB_DURATION
                # Gradual clear handled in game.py _process_bomb for better visual
            elif self.character_id == "muscular_man":
                # Phoenix form lasts 5 seconds
                self.bomb_timer = PLAYER_BOMB_DURATION
                self.invincible_timer = max(self.invincible_timer, PLAYER_BOMB_DURATION)
                
            self.damage_multiplier = self.base_damage_mult * (1.3 if self.character_id == "muscular_man" else 1.0)
            from systems.audio import audio
            audio.play("bomb")
            return True
        return False

    def die(self):
        """Player death. Auto-bomb if possible."""
        if self.invincible_timer > 0:
            return False
            
        # AUTO-BOMB (Muscular Man only)
        if self.character_id == "muscular_man" and self.bombs > 0 and not self.is_bombing:
            if self.use_bomb():
                # Flash or effect for auto-bomb
                self.invincible_timer = max(self.invincible_timer, 60)
                return False

        self.lives -= 1
        self.dead = True
        self.death_timer = 60
        # self.power = max(1.0, self.power - 0.5) # Removed power loss
        return True

    def respawn(self):
        """Respawn player after death."""
        self.dead = False
        self.x = float(PLAYFIELD_X + PLAYFIELD_WIDTH // 2)
        self.y = float(PLAYFIELD_Y + PLAYFIELD_HEIGHT - PLAYER_RESPAWN_Y_OFFSET)
        self.invincible_timer = PLAYER_INVINCIBLE_TIME
        # Reset bombs per life (3 for Magical Girl, 1 for Muscular Man)
        self.bombs = 3 if self.character_id == "magical_girl" else 1
        self.bomb_timer = 0

    def shoot(self):
        """Fire bullets based on power level and focus mode."""
        if not self.shooting or self.dead:
            return

        delay = PLAYER_FOCUS_SHOOT_DELAY if self.focused else PLAYER_SHOOT_DELAY
        if self.shoot_timer > 0:
            return

        self.shoot_timer = delay
        power_level = int(self.power)

        from systems.audio import audio
        audio.play("shoot")

        if self.focused:
            # Focused: concentrated forward shots
            self._shoot_focused(power_level)
        else:
            # Unfocused: spread shots
            self._shoot_spread(power_level)

    def _shoot_spread(self, power_level):
        """Unfocused spread shot pattern."""
        speed = PLAYER_BULLET_SPEED
        move_type = "homing_sine" if self.character_id == "magical_girl" else "linear"
        # Muscular man does 0 impact damage, only applies status effect
        damage = (PLAYER_BULLET_DAMAGE * self.damage_multiplier) if self.character_id != "muscular_man" else 0
        stat_effect = "burn" if self.character_id == "muscular_man" else None

        # Central shot always
        self.bullet_group.add(
            PlayerBullet(self.x, self.y - 10, 0, -speed, damage, movement_type=move_type, status_effect=stat_effect)
        )

        if power_level >= 2:
            # Add side shots
            spread = 0.15
            self.bullet_group.add(
                PlayerBullet(self.x - 8, self.y - 5,
                             math.sin(-spread) * speed * 0.3, -speed, damage * 0.7, movement_type=move_type, status_effect=stat_effect)
            )
            self.bullet_group.add(
                PlayerBullet(self.x + 8, self.y - 5,
                             math.sin(spread) * speed * 0.3, -speed, damage * 0.7, movement_type=move_type, status_effect=stat_effect)
            )

        if power_level >= 3:
            spread2 = 0.25
            self.bullet_group.add(
                PlayerBullet(self.x - 16, self.y,
                             math.sin(-spread2) * speed * 0.5, -speed, damage * 0.5, movement_type=move_type, status_effect=stat_effect)
            )
            self.bullet_group.add(
                PlayerBullet(self.x + 16, self.y,
                             math.sin(spread2) * speed * 0.5, -speed, damage * 0.5, movement_type=move_type, status_effect=stat_effect)
            )

        if power_level >= 4:
            self.bullet_group.add(
                PlayerBullet(self.x, self.y - 10, 0, -speed * 1.2, damage * 1.2, movement_type=move_type, status_effect=stat_effect)
            )

    def _shoot_focused(self, power_level):
        """Focused concentrated shot pattern."""
        speed = PLAYER_FOCUS_BULLET_SPEED
        damage = PLAYER_FOCUS_BULLET_DAMAGE * self.damage_multiplier

        if self.character_id == "magical_girl":
            # Laser beams
            self.bullet_group.add(
                PlayerBullet(self.x - 3, self.y - 10, 0, -speed, damage * 1.1, focused=True, width_mult=0.4)
            )
            self.bullet_group.add(
                PlayerBullet(self.x + 3, self.y - 10, 0, -speed, damage * 1.1, focused=True, width_mult=0.4)
            )

            if power_level >= 2:
                self.bullet_group.add(
                    PlayerBullet(self.x - 7, self.y - 5, 0, -speed * 0.95, damage * 1.2, focused=True, width_mult=0.4)
                )
                self.bullet_group.add(
                    PlayerBullet(self.x + 7, self.y - 5, 0, -speed * 0.95, damage * 1.2, focused=True, width_mult=0.4)
                )

            if power_level >= 3:
                self.bullet_group.add(
                    PlayerBullet(self.x - 12, self.y, 0, -speed * 0.9, damage * 1.0, focused=True, width_mult=0.4)
                )
                self.bullet_group.add(
                    PlayerBullet(self.x + 12, self.y, 0, -speed * 0.9, damage * 1.0, focused=True, width_mult=0.4)
                )

            if power_level >= 4:
                self.bullet_group.add(
                    PlayerBullet(self.x, self.y - 15, 0, -speed * 1.1, damage * 2.0, focused=True, width_mult=0.5)
                )
        elif self.character_id == "muscular_man":
            # Fire breath (flamethrower) - 0 damage, applies blue_flame
            import random
            for i in range(2 + int(power_level)):
                vx = random.uniform(-1.5, 1.5)
                vy = -random.uniform(speed * 0.6, speed * 1.2)
                self.bullet_group.add(
                    PlayerBullet(self.x, self.y - 10, vx, vy, damage=0, focused=True, status_effect="blue_flame")
                )

    def update(self):
        """Update player state."""
        self.anim_timer += 1

        if self.dead:
            self.death_timer -= 1
            if self.death_timer <= 0:
                if self.lives > 0:
                    self.respawn()
            return

        # Timers
        if self.shoot_timer > 0:
            self.shoot_timer -= 1
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
        if self.bomb_timer > 0:
            self.bomb_timer -= 1
            if self.bomb_timer == 0:
                self.damage_multiplier = self.base_damage_mult # Reset damage multiplier when bomb ends

        self.shoot()
        self.rect.center = (int(self.x), int(self.y))

        # Redraw sprite
        self._draw_sprite()

    def _draw_sprite(self):
        """Redraw the player sprite each frame for animation."""
        self.image = pygame.Surface((self.base_size, self.base_size), pygame.SRCALPHA)
        cx, cy = self.base_size // 2, self.base_size // 2

        # Flicker when invincible
        if self.invincible_timer > 0 and self.anim_timer % 6 < 3:
            return

        # Wing glow (pulsing)
        pulse = 0.7 + 0.3 * math.sin(self.anim_timer * 0.1)

        if self.character_id == "magical_girl":
            # Wings (triangles)
            wing_spread = 10 + wave_value(self.anim_timer, 0.08, 3)
            left_wing = [
                (cx - 4, cy),
                (cx - wing_spread - 6, cy - 8),
                (cx - wing_spread - 2, cy + 6),
            ]
            right_wing = [
                (cx + 4, cy),
                (cx + wing_spread + 6, cy - 8),
                (cx + wing_spread + 2, cy + 6),
            ]
            wing_color = (*COLOR_PLAYER_WING[:3], int(180 * pulse))
            pygame.draw.polygon(self.image, wing_color, left_wing)
            pygame.draw.polygon(self.image, wing_color, right_wing)

            # Body glow
            draw_glow_circle(self.image, COLOR_PLAYER_GLOW, (cx, cy), 8, 0.4 * pulse)

            # Body (small triangle pointing up)
            body_pts = [
                (cx, cy - 10),
                (cx - 6, cy + 5),
                (cx + 6, cy + 5),
            ]
            pygame.draw.polygon(self.image, COLOR_PLAYER_BODY, body_pts)
            pygame.draw.polygon(self.image, (255, 220, 240), body_pts, 1)

            # Star on top
            star_y = cy - 12
            star_pulse = 0.8 + 0.2 * math.sin(self.anim_timer * 0.15)
            draw_star(self.image, (255, 255, 200, int(255 * star_pulse)),
                      (cx, star_y), 4, 2, 4, self.anim_timer * 0.05)
        elif self.character_id == "muscular_man":
            from config.settings import COLOR_PLAYER2_BODY, COLOR_PLAYER2_SHIRT, COLOR_PLAYER2_HEAD, COLOR_PLAYER2_COMB
            
            if self.is_bombing:
                # Phoenix glow
                draw_glow_circle(self.image, (255, 100, 50), (cx, cy), 20, 0.6 * pulse)
                # Phoenix wings
                wing_spread = 15 + wave_value(self.anim_timer, 0.2, 5)
                for side in [-1, 1]:
                    wing_pts = [
                        (cx + side * 5, cy),
                        (cx + side * wing_spread, cy - 15),
                        (cx + side * (wing_spread - 5), cy + 10)
                    ]
                    pygame.draw.polygon(self.image, (255, 150, 50, 180), wing_pts)

            # Muscular arms
            arm_w = 4 + int(wave_value(self.anim_timer, 0.1, 1))
            pygame.draw.rect(self.image, COLOR_PLAYER2_BODY, (cx - 12, cy - 2, arm_w, 12), border_radius=2)
            pygame.draw.rect(self.image, COLOR_PLAYER2_BODY, (cx + 12 - arm_w, cy - 2, arm_w, 12), border_radius=2)
            
            # Torso (Orange tank top)
            pygame.draw.rect(self.image, COLOR_PLAYER2_SHIRT, (cx - 8, cy - 5, 16, 14), border_radius=3)
            
            # Chicken Head
            pygame.draw.circle(self.image, COLOR_PLAYER2_HEAD, (cx, cy - 12), 6)
            # Beak
            pygame.draw.polygon(self.image, (255, 200, 50), [(cx + 2, cy - 12), (cx + 8, cy - 10), (cx + 2, cy - 8)])
            # Comb
            pygame.draw.polygon(self.image, COLOR_PLAYER2_COMB, [(cx - 3, cy - 16), (cx, cy - 20), (cx + 3, cy - 16)])

        # Focus mode hitbox indicator
        if self.focused:
            # Rotating ring
            ring_alpha = int(150 + 50 * math.sin(self.anim_timer * 0.2))
            pygame.draw.circle(self.image, (*COLOR_HITBOX_RING, ring_alpha),
                               (cx, cy), PLAYER_HITBOX_RADIUS + 6, 1)
            # Hitbox dot
            pygame.draw.circle(self.image, (*COLOR_HITBOX, 230),
                               (cx, cy), PLAYER_HITBOX_RADIUS)
            # Rotating markers
            for i in range(4):
                angle = self.anim_timer * 0.08 + i * math.pi / 2
                mx = cx + math.cos(angle) * 10
                my = cy + math.sin(angle) * 10
                pygame.draw.circle(self.image, (*COLOR_HITBOX_RING, 180),
                                   (int(mx), int(my)), 2)

    def add_power(self, amount):
        """Powerups are removed, this does nothing."""
        pass

    def add_score(self, amount):
        """Add score."""
        self.score += amount

    def add_graze(self):
        """Register a graze."""
        self.graze_count += 1

    @property
    def is_bombing(self):
        return self.bomb_timer > 0
