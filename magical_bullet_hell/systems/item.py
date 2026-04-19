"""
Item system: power-ups, score items, life/bomb pieces.
"""
import pygame
import math
import random
from config.settings import (
    PLAYFIELD_X, PLAYFIELD_Y, PLAYFIELD_WIDTH, PLAYFIELD_HEIGHT,
    ITEM_FALL_SPEED, ITEM_AUTOCOLLECT_Y,
    ITEM_POWER_VALUE, ITEM_SCORE_VALUE, ITEM_BIG_POWER_VALUE,
    ITEM_LIFE_PIECE_VALUE, ITEM_BOMB_PIECE_VALUE,
)
from utils.renderer import draw_star, draw_diamond


class Item(pygame.sprite.Sprite):
    """Base item class."""

    def __init__(self, x, y, item_type="power"):
        super().__init__()
        self.x = float(x)
        self.y = float(y)
        self.item_type = item_type
        self.radius = 8
        self.attracted = False
        self.attract_speed = 8.0
        self.fall_speed = ITEM_FALL_SPEED
        self.vy = -2.0  # Initial upward pop
        self.anim_timer = random.randint(0, 60)

        # Set color and size based on type
        self.colors = {
            "power":     (255, 100, 100),
            "big_power": (255, 50, 50),
            "point":     (100, 200, 255),
            "life":      (255, 100, 255),
            "bomb":      (100, 255, 100),
        }
        self.color = self.colors.get(item_type, (255, 255, 255))

        # Create surface
        self.sprite_size = 20
        self.image = pygame.Surface((self.sprite_size, self.sprite_size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))

    def update(self, player_x=None, player_y=None):
        self.anim_timer += 1

        if self.attracted and player_x is not None:
            # Move toward player
            dx = player_x - self.x
            dy = player_y - self.y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 1:
                self.x += (dx / dist) * self.attract_speed
                self.y += (dy / dist) * self.attract_speed
        else:
            # Fall down with initial pop
            self.vy = min(self.fall_speed, self.vy + 0.05)
            self.y += self.vy
            self.x += math.sin(self.anim_timer * 0.05) * 0.3

        # Auto-collect if player is high enough (handled externally)

        # Remove if below screen
        if self.y > PLAYFIELD_Y + PLAYFIELD_HEIGHT + 40:
            self.kill()

        self.rect.center = (int(self.x), int(self.y))
        self._draw_sprite()

    def _draw_sprite(self):
        self.image = pygame.Surface((self.sprite_size, self.sprite_size), pygame.SRCALPHA)
        cx, cy = self.sprite_size // 2, self.sprite_size // 2

        pulse = 0.7 + 0.3 * math.sin(self.anim_timer * 0.15)

        # Glow
        glow_r = int(8 * pulse)
        pygame.draw.circle(self.image, (*self.color[:3], 50), (cx, cy), glow_r)

        if self.item_type in ("power", "big_power"):
            # Red P shape (diamond)
            size = 5 if self.item_type == "power" else 7
            draw_diamond(self.image, self.color, (cx, cy), size)
        elif self.item_type == "point":
            # Blue dot
            pygame.draw.circle(self.image, self.color, (cx, cy), 4)
            pygame.draw.circle(self.image, (200, 240, 255), (cx, cy), 2)
        elif self.item_type == "life":
            # Pink star
            draw_star(self.image, self.color, (cx, cy), 6, 3, 5,
                      self.anim_timer * 0.05)
        elif self.item_type == "bomb":
            # Green star
            draw_star(self.image, self.color, (cx, cy), 6, 3, 4,
                      self.anim_timer * 0.04)

    def collect(self, player):
        """Apply item effect to player."""
        if self.item_type == "power":
            player.add_power(ITEM_POWER_VALUE)
            player.add_score(10)
        elif self.item_type == "big_power":
            player.add_power(ITEM_BIG_POWER_VALUE)
            player.add_score(50)
        elif self.item_type == "point":
            player.add_score(ITEM_SCORE_VALUE)
        elif self.item_type == "life":
            player.lives += ITEM_LIFE_PIECE_VALUE
        elif self.item_type == "bomb":
            player.bombs += ITEM_BOMB_PIECE_VALUE

        self.kill()


def spawn_enemy_drops(x, y, item_group, is_boss=False):
    """Spawn items when an enemy is killed. Power-ups removed."""
    if is_boss:
        # Boss drops points, life, and bomb
        for _ in range(20):
            ox = x + random.uniform(-50, 50)
            oy = y + random.uniform(-40, 40)
            item_group.add(Item(ox, oy, "point"))
        item_group.add(Item(x, y - 10, "life"))
        item_group.add(Item(x + 15, y - 10, "bomb"))
    else:
        # Normal enemy drops
        roll = random.random()
        if roll < 0.7:
            item_group.add(Item(x, y, "point"))
        
        # Rare life/bomb drops
        if random.random() < 0.01:
            item_group.add(Item(x + 10, y, "life"))
        if random.random() < 0.01:
            item_group.add(Item(x - 10, y, "bomb"))
