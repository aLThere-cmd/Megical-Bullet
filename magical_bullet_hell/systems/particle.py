"""
Particle effect system for explosions, sparkles, trails, and graze effects.
"""
import pygame
import math
import random
from utils.math_helpers import lerp, lerp_color


# Cache for particle surfaces to avoid creating them every frame
_particle_cache = {}


def get_particle_surface(color, size, alpha):
    """Get a pre-rendered particle surface from cache or create one."""
    # Quantize alpha and size to keep cache size manageable
    q_alpha = int(alpha / 16) * 16
    q_size = round(size, 1)
    
    if q_alpha <= 0 or q_size < 1:
        return None
        
    key = (tuple(color[:3]), q_size, q_alpha)
    if key in _particle_cache:
        return _particle_cache[key]
        
    r = int(max(1, q_size * 3))
    s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)

    # Glow
    pygame.draw.circle(s, (*color[:3], min(255, q_alpha // 3)), (r, r), r)
    # Core
    pygame.draw.circle(s, (*color[:3], min(255, q_alpha)), (r, r), int(q_size))
    
    _particle_cache[key] = s
    return s


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
            
        alpha = self.alpha
        if alpha <= 0:
            return

        s = get_particle_surface(self.color, self.current_size, alpha)
        if s:
            r = s.get_width() // 2
            surface.blit(s, (int(self.x) - r + offset_x, int(self.y) - r + offset_y), 
                         special_flags=pygame.BLEND_ADD)


class TextParticle(Particle):
    """A particle that displays text."""
    def __init__(self, x, y, vx, vy, text, color, lifetime, font, size=20):
        super().__init__(x, y, vx, vy, color, lifetime, size, fade=True, shrink=False)
        self.text = text
        self.font = font
        self.surf = None
        self._pre_render()
        
    def _pre_render(self):
        """Pre-render text to avoid doing it every frame."""
        self.surf = self.font.render(self.text, True, self.color)

    def draw(self, surface, offset_x=0, offset_y=0):
        if not self.alive or not self.surf: return
        alpha = self.alpha
        if alpha <= 0: return
        
        self.surf.set_alpha(alpha)
        surface.blit(self.surf, (int(self.x) - self.surf.get_width()//2 + offset_x, 
                                 int(self.y) - self.surf.get_height()//2 + offset_y))

class ParticleSystem:
    """Manages all particles in the game."""
    def __init__(self):
        self.particles = []
        self.font = None

    def init_fonts(self):
        if not self.font:
            self.font = pygame.font.Font(None, 24)

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

    def emit_text(self, x, y, text, color=(255, 255, 255)):
        """Emit a rising text particle."""
        self.init_fonts()
        self.particles.append(
            TextParticle(x, y, 0, -1.5, text, color, 40, self.font)
        )

    def emit_explosion(self, x, y, color, count=25, speed=4.0, lifetime=35):
        """Enhanced explosion effect."""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            spd = random.uniform(0.5, speed)
            vx = math.cos(angle) * spd
            vy = math.sin(angle) * spd
            size = random.uniform(2, 6)
            lt = int(lifetime * random.uniform(0.6, 1.2))
            r = max(0, min(255, color[0] + random.randint(-40, 40)))
            g = max(0, min(255, color[1] + random.randint(-40, 40)))
            b = max(0, min(255, color[2] + random.randint(-40, 40)))
            self.particles.append(
                Particle(x, y, vx, vy, (r, g, b), lt, size, gravity=0.03)
            )

    def emit_sparkle(self, x, y, color=(255, 255, 200), count=8):
        """Improved sparkle effect."""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            spd = random.uniform(0.5, 2.5)
            vx = math.cos(angle) * spd
            vy = math.sin(angle) * spd
            lt = random.randint(15, 35)
            self.particles.append(
                Particle(x, y, vx, vy, color, lt, random.uniform(1, 4))
            )

    def emit_graze(self, x, y):
        """Juicier graze spark effect."""
        for _ in range(5):
            angle = random.uniform(0, 2 * math.pi)
            spd = random.uniform(2, 5)
            vx = math.cos(angle) * spd
            vy = math.sin(angle) * spd
            color = random.choice([(255, 255, 255), (100, 200, 255), (255, 150, 255)])
            self.particles.append(Particle(x, y, vx, vy, color, 15, 3))
        self.emit_text(x, y - 20, "GRAZE!", (200, 255, 255))

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
