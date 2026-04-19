"""
Collision detection system: hitbox collision, graze detection, and item collection.
"""
import math
from config.settings import (
    PLAYER_HITBOX_RADIUS, PLAYER_GRAZE_RADIUS, PLAYER_COLLECT_RADIUS,
    GRAZE_SCORE, GRAZE_POWER,
)
from utils.math_helpers import distance


def check_player_enemy_bullet_collision(player, enemy_bullets, particles):
    """
    Check collision between player and enemy bullets.
    Returns True if player was hit.
    """
    if player.dead or player.invincible_timer > 0:
        return False

    px, py = player.x, player.y
    hit = False

    for bullet in enemy_bullets:
        dist = distance(px, py, bullet.x, bullet.y)

        # Hitbox collision (tiny radius)
        if dist < PLAYER_HITBOX_RADIUS + bullet.radius * 0.3:
            hit = True
            bullet.kill()
            break

    return hit


def check_graze(player, enemy_bullets):
    """
    Check for graze (bullets passing close to player).
    Returns a list of bullets that were grazed this frame.
    """
    if player.dead:
        return []

    px, py = player.x, player.y
    grazed_bullets = []

    for bullet in enemy_bullets:
        if bullet.grazed:
            continue

        dist = distance(px, py, bullet.x, bullet.y)

        if dist < PLAYER_GRAZE_RADIUS:
            bullet.grazed = True
            grazed_bullets.append(bullet)

    return grazed_bullets


def check_player_bullet_enemy_collision(player_bullets, enemies, particles):
    """
    Check collision between player bullets and enemies.
    Returns list of (enemy, was_killed) tuples.
    """
    results = []

    for bullet in list(player_bullets):
        for enemy in enemies:
            dist = distance(bullet.x, bullet.y, enemy.x, enemy.y)
            if dist < enemy.radius + bullet.radius:
                killed = enemy.take_damage(bullet.damage)
                
                if hasattr(bullet, 'status_effect') and bullet.status_effect:
                    from config.settings import FPS, BURN_DAMAGE_PERCENT, BLUE_FLAME_DAMAGE_PERCENT, BOSS_STATUS_DAMAGE_MULT
                    from entities.boss import Boss
                    
                    dmg_mult = BOSS_STATUS_DAMAGE_MULT if isinstance(enemy, Boss) else 1.0
                    
                    if bullet.status_effect == "burn":
                        enemy.apply_status_effect("burn", 3 * FPS, BURN_DAMAGE_PERCENT * dmg_mult)
                    elif bullet.status_effect == "blue_flame":
                        enemy.apply_status_effect("blue_flame", 5 * FPS, BLUE_FLAME_DAMAGE_PERCENT * dmg_mult)
                        
                bullet.kill()
                particles.emit_sparkle(bullet.x, bullet.y, bullet.color)
                if killed:
                    results.append(enemy)
                break

    return results


def check_item_collection(player, items):
    """
    Check if player collects items.
    Returns list of collected items.
    """
    if player.dead:
        return []

    px, py = player.x, player.y
    collected = []

    for item in items:
        dist = distance(px, py, item.x, item.y)
        if dist < PLAYER_COLLECT_RADIUS + item.radius:
            collected.append(item)
        elif item.attracted:
            # Already being attracted
            collected_check = dist < PLAYER_COLLECT_RADIUS + item.radius + 10
            if collected_check:
                collected.append(item)

    return collected
