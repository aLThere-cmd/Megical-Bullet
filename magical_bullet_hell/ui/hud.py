"""
In-game HUD: score, lives, bombs, power gauge, graze counter, boss health bar.
"""
import pygame
import math
from config.settings import (
    SIDEBAR_X, SIDEBAR_WIDTH, PLAYFIELD_X, PLAYFIELD_Y, PLAYFIELD_WIDTH,
    WINDOW_HEIGHT, PLAYER_MAX_POWER,
    COLOR_TEXT, COLOR_TEXT_DIM, COLOR_TEXT_HIGHLIGHT,
    COLOR_SCORE, COLOR_POWER, COLOR_GRAZE,
    COLOR_HEALTH_BG, COLOR_HEALTH_FILL, COLOR_HEALTH_FILL2,
    COLOR_BG_PANEL, COLOR_PLAYFIELD_BORDER,
)
from utils.renderer import draw_star


class HUD:
    """Renders the in-game heads-up display."""

    def __init__(self):
        self.font_large = None
        self.font_medium = None
        self.font_small = None
        self.initialized = False

    def init_fonts(self):
        """Initialize fonts (must be called after pygame.init)."""
        if self.initialized:
            return
        self.font_large = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 22)
        self.initialized = True

    def draw(self, surface, player, spawner, frame_count):
        """Draw the complete HUD."""
        self.init_fonts()

        # Draw sidebar background
        sidebar_rect = pygame.Rect(SIDEBAR_X - 10, 10,
                                   SIDEBAR_WIDTH + 20, WINDOW_HEIGHT - 20)
        pygame.draw.rect(surface, COLOR_BG_PANEL, sidebar_rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_PLAYFIELD_BORDER, sidebar_rect, 1, border_radius=8)

        x = SIDEBAR_X
        y = 30

        # Title
        title = self.font_large.render("✦ Magical Star Burst ✦", True, COLOR_TEXT_HIGHLIGHT)
        surface.blit(title, (x, y))
        y += 40

        # Separator
        pygame.draw.line(surface, (*COLOR_PLAYFIELD_BORDER, 100),
                         (x, y), (x + SIDEBAR_WIDTH, y))
        y += 15

        # High Score label
        label = self.font_small.render("HiScore", True, COLOR_TEXT_DIM)
        surface.blit(label, (x, y))
        y += 18

        # Score
        score_text = f"{player.score:>12,}"
        score_surf = self.font_large.render(score_text, True, COLOR_SCORE)
        surface.blit(score_surf, (x, y))
        y += 35

        # Separator
        pygame.draw.line(surface, (*COLOR_PLAYFIELD_BORDER, 60),
                         (x, y), (x + SIDEBAR_WIDTH, y))
        y += 15

        # Lives
        label = self.font_medium.render("Life", True, COLOR_TEXT)
        surface.blit(label, (x, y))
        y += 25
        for i in range(player.lives):
            star_x = x + 15 + i * 22
            star_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
            draw_star(star_surf, (255, 150, 200), (10, 10), 8, 4, 5, 0)
            surface.blit(star_surf, (star_x, y))
        y += 28

        # Bombs
        label = self.font_medium.render("Spell", True, COLOR_TEXT)
        surface.blit(label, (x, y))
        y += 25
        for i in range(player.bombs):
            star_x = x + 15 + i * 22
            star_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
            draw_star(star_surf, (150, 255, 150), (10, 10), 8, 4, 4, 0)
            surface.blit(star_surf, (star_x, y))
        y += 28

        # Separator
        pygame.draw.line(surface, (*COLOR_PLAYFIELD_BORDER, 60),
                         (x, y), (x + SIDEBAR_WIDTH, y))
        y += 15

        # Power gauge
        label = self.font_medium.render("Power", True, COLOR_TEXT)
        surface.blit(label, (x, y))
        power_text = f"{player.power:.2f} / {PLAYER_MAX_POWER:.2f}"
        power_surf = self.font_medium.render(power_text, True, COLOR_POWER)
        surface.blit(power_surf, (x + 70, y))
        y += 25

        # Power bar
        bar_w = SIDEBAR_WIDTH - 10
        bar_h = 10
        pygame.draw.rect(surface, COLOR_HEALTH_BG,
                         (x, y, bar_w, bar_h), border_radius=5)
        fill_w = int(bar_w * (player.power / PLAYER_MAX_POWER))
        if fill_w > 0:
            for px_i in range(fill_w):
                t = px_i / max(1, bar_w)
                r = int(255 * (1 - t * 0.3))
                g = int(100 + 80 * t)
                b = int(180 + 75 * t)
                pygame.draw.line(surface, (r, g, b), (x + px_i, y), (x + px_i, y + bar_h - 1))
            pygame.draw.rect(surface, COLOR_POWER, (x, y, fill_w, bar_h), 1, border_radius=5)
        y += 20

        # Graze
        label = self.font_medium.render("Graze", True, COLOR_TEXT)
        surface.blit(label, (x, y))
        graze_surf = self.font_medium.render(str(player.graze_count), True, COLOR_GRAZE)
        surface.blit(graze_surf, (x + 70, y))
        y += 30

        # Separator
        pygame.draw.line(surface, (*COLOR_PLAYFIELD_BORDER, 60),
                         (x, y), (x + SIDEBAR_WIDTH, y))
        y += 15

        # Wave info
        wave_text = f"Wave {spawner.wave_count}"
        wave_surf = self.font_medium.render(wave_text, True, COLOR_TEXT_DIM)
        surface.blit(wave_surf, (x, y))
        y += 25

        # Difficulty
        diff_text = f"Difficulty: x{spawner.current_difficulty:.2f}"
        diff_surf = self.font_small.render(diff_text, True, COLOR_TEXT_DIM)
        surface.blit(diff_surf, (x, y))
        y += 30

        # Controls help
        pygame.draw.line(surface, (*COLOR_PLAYFIELD_BORDER, 60),
                         (x, y), (x + SIDEBAR_WIDTH, y))
        y += 15
        controls = [
            "WASD  - Move",
            "J     - Shoot",
            "K     - Spell Card",
            "Shift - Focus",
            "Esc   - Pause",
        ]
        for ctrl in controls:
            ctrl_surf = self.font_small.render(ctrl, True, COLOR_TEXT_DIM)
            surface.blit(ctrl_surf, (x, y))
            y += 18

        # Boss health bar (at top of playfield)
        if spawner.boss_active and spawner.boss:
            self._draw_boss_health(surface, spawner.boss, frame_count)

    def _draw_boss_health(self, surface, boss, frame_count):
        """Draw boss health bar at top of playfield."""
        bar_x = PLAYFIELD_X + 10
        bar_y = PLAYFIELD_Y + 8
        bar_w = PLAYFIELD_WIDTH - 20
        bar_h = 8

        # Background
        pygame.draw.rect(surface, COLOR_HEALTH_BG,
                         (bar_x, bar_y, bar_w, bar_h), border_radius=4)

        # Fill
        fill_w = int(bar_w * boss.hp_ratio)
        if fill_w > 0:
            # Gradient fill
            for px_i in range(fill_w):
                t = px_i / max(1, bar_w)
                pulse = 0.8 + 0.2 * math.sin(frame_count * 0.1 + t * 6)
                r = int(COLOR_HEALTH_FILL[0] * pulse)
                g = int(COLOR_HEALTH_FILL[1] * pulse)
                b = int(COLOR_HEALTH_FILL[2] * pulse)
                r = min(255, r)
                g = min(255, g)
                b = min(255, b)
                pygame.draw.line(surface, (r, g, b),
                                 (bar_x + px_i, bar_y),
                                 (bar_x + px_i, bar_y + bar_h - 1))

        pygame.draw.rect(surface, COLOR_HEALTH_FILL2, (bar_x, bar_y, bar_w, bar_h), 1,
                         border_radius=4)

        # Phase name
        if not self.initialized:
            self.init_fonts()
        name_surf = self.font_small.render(boss.phase_name, True, COLOR_TEXT)
        surface.blit(name_surf, (bar_x, bar_y + bar_h + 2))

        # Phase timer
        time_left = boss.phase_timer // 60
        timer_surf = self.font_medium.render(f"{time_left}s", True,
                                              (255, 100, 100) if time_left < 10 else COLOR_TEXT)
        surface.blit(timer_surf, (bar_x + bar_w - 30, bar_y + bar_h + 1))
