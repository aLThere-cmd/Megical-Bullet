"""
Bullet classes for player and enemy projectiles.
"""
import pygame
import math
from config.settings import (
    PLAYFIELD_X, PLAYFIELD_Y, PLAYFIELD_WIDTH, PLAYFIELD_HEIGHT,
    BULLET_OFFSCREEN_MARGIN, COLOR_BULLET_PLAYER, COLOR_BULLET_PLAYER_FOCUS,
    BULLET_COLORS
)
from utils.renderer import draw_glow_bullet, draw_diamond


class PlayerBullet(pygame.sprite.Sprite):
    """Bullet fired by the player."""

    def __init__(self, x, y, vx, vy, damage=10, focused=False):
        super().__init__()
        self.radius = 4 if not focused else 3
        size = self.radius * 6
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        self.color = COLOR_BULLET_PLAYER_FOCUS if focused else COLOR_BULLET_PLAYER
        self.focused = focused
        self.damage = damage

        # Draw bullet
        center = (size // 2, size // 2)
        draw_glow_bullet(self.image, self.color, center, self.radius)

        self.rect = self.image.get_rect(center=(int(x), int(y)))
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.rect.center = (int(self.x), int(self.y))

        # Remove if out of playfield
        if (self.x < PLAYFIELD_X - BULLET_OFFSCREEN_MARGIN or
            self.x > PLAYFIELD_X + PLAYFIELD_WIDTH + BULLET_OFFSCREEN_MARGIN or
            self.y < PLAYFIELD_Y - BULLET_OFFSCREEN_MARGIN or
            self.y > PLAYFIELD_Y + PLAYFIELD_HEIGHT + BULLET_OFFSCREEN_MARGIN):
            self.kill()


class EnemyBullet(pygame.sprite.Sprite):
    """Bullet fired by enemies or bosses."""

    def __init__(self, x, y, speed, angle, color_idx=0, size=5, bullet_type="circle"):
        super().__init__()
        self.radius = size
        self.color = BULLET_COLORS[color_idx % len(BULLET_COLORS)]
        self.bullet_type = bullet_type
        self.grazed = False  # Whether player has already grazed this bullet

        surf_size = int(self.radius * 6)
        self.image = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
        center = (surf_size // 2, surf_size // 2)

        if bullet_type == "diamond":
            draw_diamond(self.image, self.color, center, self.radius)
            # Add glow
            glow_surf = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*self.color[:3], 40), center, int(self.radius * 1.8))
            self.image.blit(glow_surf, (0, 0), special_flags=pygame.BLEND_ADD)
        else:
            draw_glow_bullet(self.image, self.color, center, self.radius)

        self.rect = self.image.get_rect(center=(int(x), int(y)))
        self.x = float(x)
        self.y = float(y)
        self.speed = speed
        self.angle = angle
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed

        # Optional: angular velocity for curving bullets
        self.angular_vel = 0.0
        # Optional: acceleration
        self.accel = 0.0

    def update(self):
        if self.angular_vel != 0:
            self.angle += self.angular_vel
            self.vx = math.cos(self.angle) * self.speed
            self.vy = math.sin(self.angle) * self.speed

        if self.accel != 0:
            self.speed += self.accel
            self.vx = math.cos(self.angle) * self.speed
            self.vy = math.sin(self.angle) * self.speed

        self.x += self.vx
        self.y += self.vy
        self.rect.center = (int(self.x), int(self.y))

        # Remove if far out of playfield
        margin = BULLET_OFFSCREEN_MARGIN * 2
        if (self.x < PLAYFIELD_X - margin or
            self.x > PLAYFIELD_X + PLAYFIELD_WIDTH + margin or
            self.y < PLAYFIELD_Y - margin or
            self.y > PLAYFIELD_Y + PLAYFIELD_HEIGHT + margin):
            self.kill()
