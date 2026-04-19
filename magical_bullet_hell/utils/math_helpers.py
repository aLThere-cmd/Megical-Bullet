"""
Math helper functions for angle calculations, vectors, and easing.
"""
import math
import random


def angle_to(x1, y1, x2, y2):
    """Calculate angle from (x1,y1) to (x2,y2) in radians."""
    return math.atan2(y2 - y1, x2 - x1)


def distance(x1, y1, x2, y2):
    """Calculate distance between two points."""
    dx = x2 - x1
    dy = y2 - y1
    return math.sqrt(dx * dx + dy * dy)


def normalize(vx, vy):
    """Normalize a 2D vector."""
    mag = math.sqrt(vx * vx + vy * vy)
    if mag == 0:
        return 0.0, 0.0
    return vx / mag, vy / mag


def lerp(a, b, t):
    """Linear interpolation between a and b."""
    return a + (b - a) * t


def lerp_color(c1, c2, t):
    """Linearly interpolate between two RGB colors."""
    t = max(0.0, min(1.0, t))
    return (
        int(lerp(c1[0], c2[0], t)),
        int(lerp(c1[1], c2[1], t)),
        int(lerp(c1[2], c2[2], t)),
    )


def ease_out_quad(t):
    """Ease-out quadratic."""
    return 1.0 - (1.0 - t) * (1.0 - t)


def ease_in_out_sine(t):
    """Ease in-out sine."""
    return -(math.cos(math.pi * t) - 1.0) / 2.0


def point_on_circle(cx, cy, radius, angle):
    """Get a point on a circle."""
    return cx + math.cos(angle) * radius, cy + math.sin(angle) * radius


def random_in_range(low, high):
    """Random float in range."""
    return random.uniform(low, high)


def clamp(value, min_val, max_val):
    """Clamp value between min and max."""
    return max(min_val, min(max_val, value))


def wave_value(time_val, speed=1.0, amplitude=1.0):
    """Get a sine wave value, useful for bobbing effects."""
    return math.sin(time_val * speed) * amplitude
