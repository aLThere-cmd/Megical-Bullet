"""
Screen effects: shake, flash, bomb visual, background dimming.
"""
import pygame
import math
import random
from config.settings import (
    PLAYFIELD_X, PLAYFIELD_Y, PLAYFIELD_WIDTH, PLAYFIELD_HEIGHT,
    WINDOW_WIDTH, WINDOW_HEIGHT,
    COLOR_TEXT, COLOR_TEXT_HIGHLIGHT,
)
from utils.renderer import draw_star


class ScreenEffects:
    """Manages screen-level visual effects."""

    def __init__(self):
        # Screen shake
        self.shake_x = 0
        self.shake_y = 0
        self.shake_intensity = 0
        self.shake_timer = 0

        # Flash
        self.flash_color = (255, 255, 255)
        self.flash_alpha = 0
        self.flash_timer = 0
        self.flash_duration = 0
        
        # Spell Card Cut-in
        self.cutin_active = False
        self.cutin_timer = 0
        self.cutin_duration = 0
        self.cutin_portrait = None
        self.cutin_text = ""
        self.cutin_side = "left" # "left" or "right"

        # Bomb visual
        self.bomb_active = False
        self.bomb_timer = 0
        self.bomb_max_timer = 0
        self.bomb_x = 0
        self.bomb_y = 0

        # Background dim for boss spells
        self.dim_alpha = 0
        self.dim_target = 0
        
        # Pre-created surfaces for performance
        self.dim_surf = pygame.Surface((PLAYFIELD_WIDTH, PLAYFIELD_HEIGHT), pygame.SRCALPHA)
        self.flash_surf = pygame.Surface((PLAYFIELD_WIDTH, PLAYFIELD_HEIGHT), pygame.SRCALPHA)
        self.banner_surf = None
        self.banner_side = None

    def start_shake(self, intensity=5, duration=10):
        """Start screen shake effect."""
        self.shake_intensity = intensity
        self.shake_timer = duration

    def start_flash(self, color=(255, 255, 255), duration=8):
        """Start screen flash effect."""
        self.flash_color = color
        self.flash_alpha = 255
        self.flash_timer = duration
        self.flash_duration = duration

    def start_bomb_visual(self, x, y, duration=60):
        """Start bomb visual effect."""
        self.bomb_active = True
        self.bomb_timer = duration
        self.bomb_max_timer = duration
        self.bomb_x = x
        self.bomb_y = y

    def set_dim(self, target_alpha):
        """Set target dim level for background."""
        self.dim_target = target_alpha

    def start_cutin(self, character_id, spell_name):
        """Start spell card cut-in effect."""
        self.cutin_active = True
        self.cutin_duration = 60 # Reduced from 90 to reduce lag
        self.cutin_timer = self.cutin_duration
        self.cutin_text = spell_name
        self.cutin_side = "left" if character_id == "magical_girl" else "right"
        self._pre_render_banner()
        self.start_shake(4, 15)
        self.set_dim(180) # Deeper dim during cut-in

    def update(self):
        """Update all effects."""
        # Shake
        if self.shake_timer > 0:
            self.shake_timer -= 1
            intensity = self.shake_intensity * (self.shake_timer / max(1, self.shake_timer + 1))
            self.shake_x = random.uniform(-intensity, intensity)
            self.shake_y = random.uniform(-intensity, intensity)
        else:
            self.shake_x = 0
            self.shake_y = 0

        # Flash
        if self.flash_timer > 0:
            self.flash_timer -= 1
            t = self.flash_timer / max(1, self.flash_duration)
            self.flash_alpha = int(255 * t)
        else:
            self.flash_alpha = 0

        # Bomb
        if self.bomb_active:
            self.bomb_timer -= 1
            if self.bomb_timer <= 0:
                self.bomb_active = False

        # Dim interpolation
        dim_speed = 10 if self.cutin_active else 3
        if self.dim_alpha < self.dim_target:
            self.dim_alpha = min(self.dim_target, self.dim_alpha + dim_speed)
        elif self.dim_alpha > self.dim_target:
            self.dim_alpha = max(self.dim_target, self.dim_alpha - dim_speed)
            
        # Cut-in
        if self.cutin_active:
            self.cutin_timer -= 1
            if self.cutin_timer <= 0:
                self.cutin_active = False
                self.set_dim(0)

    def draw(self, surface, offset_x=0, offset_y=0):
        """Draw all active effects."""
        # Background dim
        if self.dim_alpha > 0:
            self.dim_surf.fill((0, 0, 20, int(self.dim_alpha)))
            surface.blit(self.dim_surf, (PLAYFIELD_X + offset_x, PLAYFIELD_Y + offset_y))

        # Bomb visual
        if self.bomb_active:
            self._draw_bomb(surface, offset_x, offset_y)

        # Flash
        if self.flash_alpha > 0:
            self.flash_surf.fill((*self.flash_color[:3], min(255, self.flash_alpha)))
            surface.blit(self.flash_surf, (PLAYFIELD_X + offset_x, PLAYFIELD_Y + offset_y))
            
        # Cut-in (Last to be on top of playfield but maybe under HUD)
        if self.cutin_active:
            self._draw_cutin(surface, offset_x, offset_y)

    def _pre_render_banner(self):
        """Pre-render the gradient banner for spell card cut-in."""
        banner_h = 100
        self.banner_surf = pygame.Surface((PLAYFIELD_WIDTH, banner_h), pygame.SRCALPHA)
        color_main = (60, 20, 100) if self.cutin_side == "left" else (100, 40, 20)
        
        for i in range(PLAYFIELD_WIDTH):
            grad_t = i / PLAYFIELD_WIDTH
            if self.cutin_side == "right": grad_t = 1.0 - grad_t
            
            # Non-linear gradient for more 'impact'
            curr_alpha = int(220 * (1.0 - grad_t**1.5))
            pygame.draw.line(self.banner_surf, (*color_main, curr_alpha), (i, 0), (i, banner_h))
            # Top/bottom lines
            if i % 2 == 0:
                pygame.draw.line(self.banner_surf, (255, 255, 255, curr_alpha // 2), (i, 0), (i, 2))
                pygame.draw.line(self.banner_surf, (255, 255, 255, curr_alpha // 2), (i, banner_h - 2), (i, banner_h))

    def _draw_cutin(self, surface, offset_x, offset_y):
        """Draw the spell card cut-in portrait and banner."""
        if not self.cutin_active or not self.banner_surf:
            return
            
        t = 1.0 - (self.cutin_timer / self.cutin_duration)
        
        # Timing phases
        slide_in_time = 0.15
        slide_out_time = 0.15
        
        alpha = 255
        move_t = 1.0
        
        if t < slide_in_time:
            progress = t / slide_in_time
            move_t = 1.0 - (1.0 - progress) ** 3 # Smoother cubic ease
            alpha = int(255 * progress)
        elif t > 1.0 - slide_out_time:
            progress = (1.0 - t) / slide_out_time
            move_t = 1.0 + (1.0 - progress) ** 2
            alpha = int(255 * progress)
        else:
            move_t = 1.0
            alpha = 255
            
        # Banner background
        banner_h = 100
        banner_y = PLAYFIELD_Y + (PLAYFIELD_HEIGHT // 2 - 50)
        
        self.banner_surf.set_alpha(alpha)
        surface.blit(self.banner_surf, (PLAYFIELD_X + offset_x, banner_y + offset_y))
        
        # Portrait removed as requested
            
        # Text Rendering
        font_large = pygame.font.Font(None, 72)
        font_small = pygame.font.Font(None, 32)
        
        label_surf = font_small.render("SPELL CARD", True, (255, 255, 255))
        name_surf = font_large.render(self.cutin_text, True, COLOR_TEXT_HIGHLIGHT)
        
        if self.cutin_side == "left":
            tx_start = PLAYFIELD_X - name_surf.get_width()
            tx_target = PLAYFIELD_X + (PLAYFIELD_WIDTH - name_surf.get_width()) // 2
            tx = tx_start + (tx_target - tx_start) * move_t
            if t > 0.85: tx += (t - 0.85) * 2000
        else:
            tx_start = PLAYFIELD_X + PLAYFIELD_WIDTH
            tx_target = PLAYFIELD_X + (PLAYFIELD_WIDTH - name_surf.get_width()) // 2
            tx = tx_start - (tx_start - tx_target) * move_t
            if t > 0.85: tx -= (t - 0.85) * 2000
            
        ty = banner_y + (banner_h - name_surf.get_height()) // 2 + 10 + offset_y
        tx += offset_x
        
        # Text alpha fade
        label_surf.set_alpha(alpha)
        name_surf.set_alpha(alpha)
        
        # Draw Glow
        glow_col = (255, 255, 255, int(100 * (alpha/255)))
        glow_surf = font_large.render(self.cutin_text, True, glow_col[:3])
        glow_surf.set_alpha(glow_col[3])
        for dx, dy in [(-2,0),(2,0),(0,-2),(0,2)]:
            surface.blit(glow_surf, (tx + dx, ty + dy))
            
        # surface.blit(label_surf, (tx, ty - 25)) # Removed label
        surface.blit(name_surf, (tx, ty))

    def _draw_bomb(self, surface, offset_x=0, offset_y=0):
        """Draw bomb/spell card visual effect with instant burst and shockwaves."""
        t = 1.0 - (self.bomb_timer / max(1, self.bomb_max_timer))
        max_radius = max(PLAYFIELD_WIDTH, PLAYFIELD_HEIGHT) * 1.5
        cx, cy = int(self.bomb_x) + offset_x, int(self.bomb_y) + offset_y

        # Instant Full-Screen Flash Burst
        if t < 0.15:
            burst_alpha = int(100 * (1.0 - t / 0.15))
            self.flash_surf.fill((255, 255, 255, burst_alpha))
            surface.blit(self.flash_surf, (PLAYFIELD_X + offset_x, PLAYFIELD_Y + offset_y))

        # High-speed shockwaves
        for i in range(5):
            # Faster expansion for 'instant' feel
            ring_t = max(0, t * 2.0 - i * 0.1)
            if ring_t <= 0 or ring_t >= 1.0: continue
            
            radius = int(ring_t * max_radius)
            alpha = int(220 * (1.0 - ring_t))
            color = [(255, 200, 255), (150, 255, 255), (255, 255, 255), (200, 150, 255)][i % 4]
            
            # Thick outer ring
            pygame.draw.circle(surface, (*color, alpha), (cx, cy), radius, 3)
            
            # Star trails on ring
            star_count = 8
            for s_i in range(star_count):
                angle = t * 10 + s_i * (math.pi * 2 / star_count)
                sx = cx + math.cos(angle) * radius
                sy = cy + math.sin(angle) * radius
                draw_star(surface, (*color, alpha), (int(sx), int(sy)), 12, 5, 5, angle * 3)

        # Impact Core
        if t < 0.5:
            core_alpha = int(255 * (1.0 - t * 2))
            pygame.draw.circle(surface, (255, 255, 255, core_alpha), (cx, cy), int(100 * (1.0 - t)))

    @property
    def offset(self):
        """Get shake offset as (x, y) tuple."""
        return (int(self.shake_x), int(self.shake_y))
