"""
Particle effect system for explosions, sparkles, trails, and graze effects.
"""
import pygame
import math
import random
from utils.math_helpers import lerp, lerp_color


class Particle:
    """A single particle."""

    def __init__(self, x, y, vx, vy, color, lifetime, size=3,
                 fade=True, shrink=True, gravity=0.0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        self.max_size = size
        self.fade = fade
        self.shrink = shrink
        self.gravity = gravity
        self.alive = True

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.vx *= 0.98  # Friction
        self.vy *= 0.98

        self.lifetime -= 1
        if self.lifetime <= 0:
            self.alive = False

    @property
    def alpha(self):
        if not self.fade:
            return 255
        t = self.lifetime / self.max_lifetime
        return int(255 * t)

    @property
    def current_size(self):
        if not self.shrink:
            return self.size
        t = self.lifetime / self.max_lifetime
        return max(1, self.size * t)

    def draw(self, surface, offset_x=0, offset_y=0):
        if not self.alive:
            return
        size = int(self.current_size)
        if size < 1:
            return

        alpha = self.alpha
        if alpha <= 0:
            return

        r = max(1, size * 3)
        s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)

        # Glow
        pygame.draw.circle(s, (*self.color[:3], min(255, alpha // 3)), (r, r), r)
        # Core
        pygame.draw.circle(s, (*self.color[:3], min(255, alpha)), (r, r), size)

        surface.blit(s, (int(self.x) - r + offset_x, int(self.y) - r + offset_y), special_flags=pygame.BLEND_ADD)


class ParticleSystem:
    """Manages all particles in the game."""

    def __init__(self):
        self.particles = []

    def update(self):
        self.particles = [p for p in self.particles if p.alive]
        for p in self.particles:
            p.update()

    def draw(self, surface, offset_x=0, offset_y=0):
        for p in self.particles:
            p.draw(surface, offset_x, offset_y)

    def clear(self):
        self.particles.clear()

    @property
    def count(self):
        return len(self.particles)

    # =========================================================================
    # Effect Generators
    # =========================================================================

    def emit_explosion(self, x, y, color, count=15, speed=3.0, lifetime=25):
        """Explosion effect when enemy dies."""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            spd = random.uniform(0.5, speed)
            vx = math.cos(angle) * spd
            vy = math.sin(angle) * spd
            size = random.uniform(2, 5)
            lt = int(lifetime * random.uniform(0.5, 1.0))
            # Vary color slightly
            r = max(0, min(255, color[0] + random.randint(-30, 30)))
            g = max(0, min(255, color[1] + random.randint(-30, 30)))
            b = max(0, min(255, color[2] + random.randint(-30, 30)))
            self.particles.append(
                Particle(x, y, vx, vy, (r, g, b), lt, size, gravity=0.02)
            )

    def emit_sparkle(self, x, y, color=(255, 255, 200), count=5):
        """Small sparkle effect."""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            spd = random.uniform(0.3, 1.5)
            vx = math.cos(angle) * spd
            vy = math.sin(angle) * spd
            lt = random.randint(10, 25)
            self.particles.append(
                Particle(x, y, vx, vy, color, lt, random.uniform(1, 3))
            )

    def emit_graze(self, x, y):
        """Graze spark effect."""
        for _ in range(3):
            angle = random.uniform(0, 2 * math.pi)
            spd = random.uniform(1, 3)
            vx = math.cos(angle) * spd
            vy = math.sin(angle) * spd
            color = random.choice([
                (255, 255, 255),
                (200, 220, 255),
                (255, 200, 255),
            ])
            self.particles.append(
                Particle(x, y, vx, vy, color, 12, 2)
            )

    def emit_trail(self, x, y, color, size=2):
        """Single trail particle behind moving objects."""
        self.particles.append(
            Particle(
                x + random.uniform(-2, 2),
                y + random.uniform(-2, 2),
                random.uniform(-0.2, 0.2),
                random.uniform(0.2, 0.8),
                color, 15, size,
            )
        )

    def emit_bomb_effect(self, cx, cy, radius, color=(255, 200, 255)):
        """Expanding circle of particles for bomb effect."""
        count = int(radius * 0.3)
        for i in range(count):
            angle = (2 * math.pi * i / count)
            x = cx + math.cos(angle) * radius
            y = cy + math.sin(angle) * radius
            vx = math.cos(angle) * 0.5
            vy = math.sin(angle) * 0.5
            self.particles.append(
                Particle(x, y, vx, vy, color, 20, 3)
            )

    def emit_item_collect(self, x, y, color):
        """Effect when collecting an item."""
        for _ in range(8):
            angle = random.uniform(0, 2 * math.pi)
            spd = random.uniform(1, 2.5)
            vx = math.cos(angle) * spd
            vy = math.sin(angle) * spd
            self.particles.append(
                Particle(x, y, vx, vy, color, 18, random.uniform(2, 4))
            )

    def emit_boss_defeat(self, x, y):
        """Large explosion for boss defeat."""
        colors = [
            (255, 200, 255), (255, 255, 200), (200, 220, 255),
            (255, 180, 180), (200, 255, 200),
        ]
        for _ in range(60):
            angle = random.uniform(0, 2 * math.pi)
            spd = random.uniform(1, 6)
            vx = math.cos(angle) * spd
            vy = math.sin(angle) * spd
            color = random.choice(colors)
            lt = random.randint(20, 50)
            self.particles.append(
                Particle(x, y, vx, vy, color, lt, random.uniform(3, 8), gravity=0.01)
            )
