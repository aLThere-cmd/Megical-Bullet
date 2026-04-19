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
    """The Magical Girl player character."""

    def __init__(self, bullet_group):
        super().__init__()
        self.bullet_group = bullet_group

        # Position
        self.x = float(PLAYFIELD_X + PLAYFIELD_WIDTH // 2)
        self.y = float(PLAYFIELD_Y + PLAYFIELD_HEIGHT - 80)

        # Create visual surface
        self.base_size = 40
        self.image = pygame.Surface((self.base_size, self.base_size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))

        # State
        self.lives = PLAYER_START_LIVES
        self.bombs = PLAYER_START_BOMBS
        self.power = PLAYER_START_POWER
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
            self.use_bomb()

    def use_bomb(self):
        """Activate spell card (bomb)."""
        if self.bombs > 0 and self.bomb_timer <= 0:
            self.bombs -= 1
            self.bomb_timer = PLAYER_BOMB_DURATION
            self.invincible_timer = max(self.invincible_timer, PLAYER_BOMB_INVINCIBLE)
            from systems.audio import audio
            audio.play("bomb")
            return True
        return False

    def die(self):
        """Player death."""
        if self.invincible_timer > 0:
            return False
        self.lives -= 1
        self.dead = True
        self.death_timer = 60
        self.power = max(1.0, self.power - 0.5)
        return True

    def respawn(self):
        """Respawn player after death."""
        self.dead = False
        self.x = float(PLAYFIELD_X + PLAYFIELD_WIDTH // 2)
        self.y = float(PLAYFIELD_Y + PLAYFIELD_HEIGHT - PLAYER_RESPAWN_Y_OFFSET)
        self.invincible_timer = PLAYER_INVINCIBLE_TIME
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
        damage = PLAYER_BULLET_DAMAGE

        # Central shot always
        self.bullet_group.add(
            PlayerBullet(self.x, self.y - 10, 0, -speed, damage)
        )

        if power_level >= 2:
            # Add side shots
            spread = 0.15
            self.bullet_group.add(
                PlayerBullet(self.x - 8, self.y - 5,
                             math.sin(-spread) * speed * 0.3, -speed, damage * 0.7)
            )
            self.bullet_group.add(
                PlayerBullet(self.x + 8, self.y - 5,
                             math.sin(spread) * speed * 0.3, -speed, damage * 0.7)
            )

        if power_level >= 3:
            spread2 = 0.25
            self.bullet_group.add(
                PlayerBullet(self.x - 16, self.y,
                             math.sin(-spread2) * speed * 0.5, -speed, damage * 0.5)
            )
            self.bullet_group.add(
                PlayerBullet(self.x + 16, self.y,
                             math.sin(spread2) * speed * 0.5, -speed, damage * 0.5)
            )

        if power_level >= 4:
            self.bullet_group.add(
                PlayerBullet(self.x, self.y - 10, 0, -speed * 1.2, damage * 1.2)
            )

    def _shoot_focused(self, power_level):
        """Focused concentrated shot pattern."""
        speed = PLAYER_FOCUS_BULLET_SPEED
        damage = PLAYER_FOCUS_BULLET_DAMAGE

        # Tight forward shots
        self.bullet_group.add(
            PlayerBullet(self.x - 3, self.y - 10, 0, -speed, damage, focused=True)
        )
        self.bullet_group.add(
            PlayerBullet(self.x + 3, self.y - 10, 0, -speed, damage, focused=True)
        )

        if power_level >= 2:
            self.bullet_group.add(
                PlayerBullet(self.x - 7, self.y - 5, 0, -speed * 0.95, damage * 0.8, focused=True)
            )
            self.bullet_group.add(
                PlayerBullet(self.x + 7, self.y - 5, 0, -speed * 0.95, damage * 0.8, focused=True)
            )

        if power_level >= 3:
            self.bullet_group.add(
                PlayerBullet(self.x - 12, self.y, 0.3, -speed * 0.9, damage * 0.7, focused=True)
            )
            self.bullet_group.add(
                PlayerBullet(self.x + 12, self.y, -0.3, -speed * 0.9, damage * 0.7, focused=True)
            )

        if power_level >= 4:
            self.bullet_group.add(
                PlayerBullet(self.x, self.y - 15, 0, -speed * 1.1, damage * 1.5, focused=True)
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
        """Add power to the player."""
        self.power = min(PLAYER_MAX_POWER, self.power + amount)

    def add_score(self, amount):
        """Add score."""
        self.score += amount

    def add_graze(self):
        """Register a graze."""
        self.graze_count += 1

    @property
    def is_bombing(self):
        return self.bomb_timer > 0
