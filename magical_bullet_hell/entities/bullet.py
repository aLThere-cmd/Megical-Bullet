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

    def __init__(self, x, y, vx, vy, damage=10, focused=False, movement_type="linear", status_effect=None, width_mult=1.0):
        super().__init__()
        self.radius = 4 if not focused else 3
        
        # If it's a laser (narrow width), adjust size
        self.width_mult = width_mult
        width = int(self.radius * 6 * width_mult)
        height = int(self.radius * 6)
        
        # For very thin lasers, ensure min width
        width = max(2, width)
        
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Determine color based on status or focus
        if status_effect == "burn":
            from config.settings import COLOR_FIREBALL
            self.color = COLOR_FIREBALL
        elif status_effect == "blue_flame":
            from config.settings import COLOR_BLUE_FLAME
            self.color = COLOR_BLUE_FLAME
        else:
            self.color = COLOR_BULLET_PLAYER_FOCUS if focused else COLOR_BULLET_PLAYER
            
        self.focused = focused
        self.damage = damage
        self.movement_type = movement_type
        self.status_effect = status_effect

        # Draw bullet
        center = (width // 2, height // 2)
        if width_mult < 1.0:
            # Laser line
            pygame.draw.ellipse(self.image, self.color, (0, 0, width, height))
            pygame.draw.ellipse(self.image, (255, 255, 255), (width//2 - 1, 0, max(1, width//2), height))
        else:
            draw_glow_bullet(self.image, self.color, center, self.radius)

        self.rect = self.image.get_rect(center=(int(x), int(y)))
        self.x = float(x)
        self.base_x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.time_alive = 0

    def update(self, enemies=None):
        self.time_alive += 1
        
        # Homing behavior
        if (self.movement_type == "homing" or self.movement_type == "homing_sine") and enemies and self.time_alive > 5:
            nearest_enemy = None
            min_dist = 80 # Very narrow homing range
            for enemy in enemies:
                # Calculate distance
                dx = enemy.x - self.x
                dy = enemy.y - self.y
                dist = math.sqrt(dx * dx + dy * dy)
                if dist < min_dist:
                    min_dist = dist
                    nearest_enemy = enemy
            
            if nearest_enemy:
                # Steer towards enemy
                target_angle = math.atan2(nearest_enemy.y - self.y, nearest_enemy.x - self.x)
                current_angle = math.atan2(self.vy, self.vx)
                
                # Slowly rotate current angle towards target angle
                angle_diff = (target_angle - current_angle + math.pi) % (2 * math.pi) - math.pi
                steering_speed = 0.25 # Faster rotation for close-range snapping
                if abs(angle_diff) < steering_speed:
                    new_angle = target_angle
                else:
                    new_angle = current_angle + (steering_speed if angle_diff > 0 else -steering_speed)
                
                speed = math.sqrt(self.vx**2 + self.vy**2)
                self.vx = math.cos(new_angle) * speed
                self.vy = math.sin(new_angle) * speed

        self.base_x += self.vx
        self.y += self.vy
        
        if self.movement_type == "sine" or self.movement_type == "homing_sine":
            # Simple harmonic motion
            offset = math.sin(self.time_alive * 0.3) * 15
            self.x = self.base_x + offset
        else:
            self.x = self.base_x
            
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
