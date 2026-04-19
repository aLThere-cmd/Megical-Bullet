"""
Bullet pattern generators for creating complex bullet formations.
"""
import math
from entities.bullet import EnemyBullet


def spawn_bullets(group, x, y, params_list):
    """
    Spawn enemy bullets from a list of parameter tuples.
    Each tuple: (speed, angle, color_idx, size, bullet_type, [opt_x, opt_y])
    """
    for params in params_list:
        if len(params) >= 7:
            speed, angle, color_idx, size, bullet_type, sx, sy = params[:7]
            bullet = EnemyBullet(sx, sy, speed, angle, color_idx, size, bullet_type)
        else:
            speed, angle, color_idx, size, bullet_type = params
            bullet = EnemyBullet(x, y, speed, angle, color_idx, size, bullet_type)
        group.add(bullet)


def create_circle_pattern(x, y, count, speed, color_idx=0, size=5,
                           bullet_type="circle", angle_offset=0):
    """Create bullets in a circle pattern."""
    params = []
    for i in range(count):
        angle = angle_offset + (2 * math.pi * i / count)
        params.append((speed, angle, color_idx, size, bullet_type))
    return params


def create_spiral_pattern(x, y, arms, speed, base_angle, color_idx=0,
                           size=5, bullet_type="circle"):
    """Create a single frame of a spiral pattern. Call repeatedly with changing base_angle."""
    params = []
    for i in range(arms):
        angle = base_angle + (2 * math.pi * i / arms)
        params.append((speed, angle, color_idx, size, bullet_type))
    return params


def create_aimed_pattern(x, y, target_x, target_y, count, spread,
                          speed, color_idx=0, size=5, bullet_type="circle"):
    """Create aimed bullets spread around the direction to target."""
    base_angle = math.atan2(target_y - y, target_x - x)
    params = []
    if count == 1:
        params.append((speed, base_angle, color_idx, size, bullet_type))
    else:
        for i in range(count):
            offset = (i - (count - 1) / 2) * spread
            params.append((speed, base_angle + offset, color_idx, size, bullet_type))
    return params


def create_fan_pattern(x, y, count, total_angle, direction_angle, speed,
                        color_idx=0, size=5, bullet_type="circle"):
    """Create a fan of bullets."""
    params = []
    if count == 1:
        params.append((speed, direction_angle, color_idx, size, bullet_type))
    else:
        start_angle = direction_angle - total_angle / 2
        step = total_angle / (count - 1)
        for i in range(count):
            angle = start_angle + step * i
            params.append((speed, angle, color_idx, size, bullet_type))
    return params


def create_random_burst(x, y, count, min_speed, max_speed,
                         color_idx=0, size=5, bullet_type="circle"):
    """Create a random burst of bullets."""
    import random
    params = []
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(min_speed, max_speed)
        params.append((speed, angle, color_idx, size, bullet_type))
    return params
