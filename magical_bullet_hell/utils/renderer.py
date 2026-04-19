"""
Rendering utilities for glow effects, trails, and shape drawing.
"""
import pygame
import math


# Cache for glow surfaces to avoid creating them every frame
_glow_cache = {}


def draw_glow_circle(surface, color, center, radius, intensity=1.0):
    """Draw a circle with a soft glow effect."""
    # Use cache for common intensities/radii to avoid surface creation
    # Intensity rounded to 0.1 to keep cache size reasonable
    cache_key = ("circle", tuple(color[:3]), radius, round(intensity, 1))
    
    if cache_key in _glow_cache:
        glow_surf = _glow_cache[cache_key]
        glow_radius = glow_surf.get_width() // 2
    else:
        glow_radius = int(radius * 3)
        glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)

        for i in range(3):
            r = glow_radius - i * (glow_radius // 3)
            alpha = int(30 * intensity * (1.0 - i / 3.0))
            alpha = max(0, min(255, alpha))
            c = (*color[:3], alpha)
            pygame.draw.circle(glow_surf, c, (glow_radius, glow_radius), r)

        # Core
        alpha_core = int(200 * intensity)
        alpha_core = max(0, min(255, alpha_core))
        pygame.draw.circle(glow_surf, (*color[:3], alpha_core), (glow_radius, glow_radius), int(radius))

        # Bright center
        bright = tuple(min(255, c + 60) for c in color[:3])
        pygame.draw.circle(glow_surf, (*bright, min(255, int(255 * intensity))),
                           (glow_radius, glow_radius), max(1, int(radius * 0.5)))
        
        _glow_cache[cache_key] = glow_surf

    surface.blit(glow_surf, (center[0] - glow_radius, center[1] - glow_radius))


def draw_glow_bullet(surface, color, center, radius):
    """Draw a bullet with glow effect."""
    cache_key = ("bullet", tuple(color[:3]), radius)
    
    if cache_key in _glow_cache:
        glow_surf = _glow_cache[cache_key]
        glow_r = glow_surf.get_width() // 2
    else:
        glow_r = int(radius * 2.5)
        glow_surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)

        # Outer glow
        pygame.draw.circle(glow_surf, (*color[:3], 40), (glow_r, glow_r), glow_r)
        pygame.draw.circle(glow_surf, (*color[:3], 80), (glow_r, glow_r), int(glow_r * 0.7))

        # Core
        pygame.draw.circle(glow_surf, (*color[:3], 220), (glow_r, glow_r), int(radius))

        # White center
        white_r = max(1, int(radius * 0.4))
        pygame.draw.circle(glow_surf, (255, 255, 255, 200), (glow_r, glow_r), white_r)
        
        _glow_cache[cache_key] = glow_surf

    surface.blit(glow_surf, (center[0] - glow_r, center[1] - glow_r))


def draw_star(surface, color, center, outer_radius, inner_radius, points=5, angle_offset=0):
    """Draw a star shape."""
    pts = []
    for i in range(points * 2):
        r = outer_radius if i % 2 == 0 else inner_radius
        a = angle_offset + (math.pi * 2 * i) / (points * 2) - math.pi / 2
        x = center[0] + math.cos(a) * r
        y = center[1] + math.sin(a) * r
        pts.append((x, y))
    if len(pts) >= 3:
        pygame.draw.polygon(surface, color, pts)


def draw_diamond(surface, color, center, size):
    """Draw a diamond/rhombus shape."""
    cx, cy = center
    pts = [
        (cx, cy - size),
        (cx + size * 0.6, cy),
        (cx, cy + size),
        (cx - size * 0.6, cy),
    ]
    pygame.draw.polygon(surface, color, pts)


def create_gradient_surface(width, height, color_top, color_bottom):
    """Create a vertical gradient surface."""
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    for y in range(height):
        t = y / max(1, height - 1)
        r = int(color_top[0] + (color_bottom[0] - color_top[0]) * t)
        g = int(color_top[1] + (color_bottom[1] - color_top[1]) * t)
        b = int(color_top[2] + (color_bottom[2] - color_top[2]) * t)
        pygame.draw.line(surf, (r, g, b), (0, y), (width - 1, y))
    return surf
