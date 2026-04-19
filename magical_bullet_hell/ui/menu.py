"""
Menu screens: title screen, difficulty select, pause, and game over.
"""
import pygame
import math
import random
from config.settings import (
    WINDOW_WIDTH, WINDOW_HEIGHT, DIFFICULTY,
    COLOR_BG_DARK, COLOR_TEXT, COLOR_TEXT_HIGHLIGHT, COLOR_TEXT_DIM,
    COLOR_PLAYFIELD_BORDER, COLOR_POWER, COLOR_SCORE, COLOR_GRAZE
)
from utils.renderer import draw_star, draw_glow_circle


class TitleScreen:
    """Animated title screen with difficulty selection and magical aesthetics."""

    def __init__(self):
        self.font_title = None
        self.font_subtitle = None
        self.font_option = None
        self.font_hint = None
        self.initialized = False

        self.selected = 1  # Default to Normal
        self.options = list(DIFFICULTY.keys())
        self.anim_timer = 0

        # Background particles
        self.particles = []
        for _ in range(120):
            self.particles.append({
                "x": random.uniform(0, WINDOW_WIDTH),
                "y": random.uniform(0, WINDOW_HEIGHT),
                "speed": random.uniform(0.1, 0.8),
                "size": random.uniform(1, 4),
                "brightness": random.uniform(50, 200),
                "twinkle_speed": random.uniform(0.01, 0.05),
                "color": random.choice([
                    (255, 200, 255), (200, 255, 255), (255, 255, 200), (255, 255, 255)
                ])
            })

    def init_fonts(self):
        if self.initialized:
            return
        self.font_title = pygame.font.Font(None, 84)
        self.font_subtitle = pygame.font.Font(None, 36)
        self.font_option = pygame.font.Font(None, 42)
        self.font_hint = pygame.font.Font(None, 28)
        self.initialized = True

    def handle_input(self, event):
        """Handle menu input. Returns difficulty name if selected, None otherwise."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w or event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key == pygame.K_j or event.key == pygame.K_RETURN:
                return self.options[self.selected]
        return None

    def update(self):
        self.anim_timer += 1
        for p in self.particles:
            p["y"] += p["speed"]
            if p["y"] > WINDOW_HEIGHT:
                p["y"] = 0
                p["x"] = random.uniform(0, WINDOW_WIDTH)

    def draw(self, surface):
        self.init_fonts()
        
        # Draw background gradient
        for y in range(WINDOW_HEIGHT):
            t = y / WINDOW_HEIGHT
            r = int(12 + 20 * t)
            g = int(8 + 10 * t)
            b = int(24 + 40 * t)
            pygame.draw.line(surface, (r, g, b), (0, y), (WINDOW_WIDTH, y))

        # Draw particles
        for p in self.particles:
            bright = p["brightness"]
            twinkle = 0.5 + 0.5 * math.sin(self.anim_timer * p["twinkle_speed"])
            alpha = int(bright * twinkle)
            size = int(p["size"])
            if alpha > 0:
                s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(s, (*p["color"], alpha), (size, size), size)
                surface.blit(s, (int(p["x"]) - size, int(p["y"]) - size))

        cx = WINDOW_WIDTH // 2

        # Rotating magical circles behind title
        circle_y = 180
        for i in range(2):
            radius = 250 - i * 50
            angle_offset = self.anim_timer * (0.005 if i == 0 else -0.008)
            points = []
            num_points = 6 if i == 0 else 8
            for j in range(num_points):
                a = angle_offset + (2 * math.pi * j / num_points)
                px = cx + math.cos(a) * radius
                py = circle_y + math.sin(a) * radius
                points.append((px, py))
            
            # Draw connecting lines for magical circle
            for j in range(num_points):
                p1 = points[j]
                p2 = points[(j + 2) % num_points]
                color = (255, 180, 255, 30) if i == 0 else (180, 255, 255, 30)
                pygame.draw.line(surface, color, p1, p2, 2)
            
            pygame.draw.circle(surface, (255, 200, 255, 20), (cx, circle_y), radius, 2)

        # Title text with floating animation
        title_y = circle_y - 30 + math.sin(self.anim_timer * 0.05) * 10
        
        # Title Glow
        glow_surf = pygame.Surface((600, 150), pygame.SRCALPHA)
        pulse = 0.7 + 0.3 * math.sin(self.anim_timer * 0.04)
        draw_glow_circle(glow_surf, (255, 150, 200), (300, 75), 100, 0.4 * pulse)
        surface.blit(glow_surf, (cx - 300, title_y - 75))

        # Title string
        title = self.font_title.render("✦ Magical Star Burst ✦", True, COLOR_TEXT_HIGHLIGHT)
        title_rect = title.get_rect(center=(cx, title_y))
        
        # Draw shadow
        shadow = self.font_title.render("✦ Magical Star Burst ✦", True, (40, 20, 60))
        surface.blit(shadow, (title_rect.x + 4, title_rect.y + 4))
        surface.blit(title, title_rect)

        # Subtitle
        subtitle = self.font_subtitle.render("~ A Bullet Hell Adventure ~", True, COLOR_TEXT_DIM)
        sub_rect = subtitle.get_rect(center=(cx, title_y + 60))
        surface.blit(subtitle, sub_rect)

        # Difficulty Menu Panel
        menu_y = 380
        panel_w, panel_h = 400, 280
        panel_rect = pygame.Rect(cx - panel_w//2, menu_y, panel_w, panel_h)
        
        # Panel Background
        panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        pygame.draw.rect(panel_surf, (20, 15, 40, 200), (0, 0, panel_w, panel_h), border_radius=15)
        pygame.draw.rect(panel_surf, (255, 180, 255, 100), (0, 0, panel_w, panel_h), 2, border_radius=15)
        surface.blit(panel_surf, panel_rect)

        # Menu options
        for i, opt in enumerate(self.options):
            y = menu_y + 40 + i * 60
            is_selected = (i == self.selected)

            if is_selected:
                # Highlight background
                sel_surf = pygame.Surface((340, 50), pygame.SRCALPHA)
                sel_pulse = int(40 + 30 * math.sin(self.anim_timer * 0.1))
                pygame.draw.rect(sel_surf, (255, 150, 255, sel_pulse), (0, 0, 340, 50), border_radius=10)
                pygame.draw.rect(sel_surf, (255, 200, 255, 150), (0, 0, 340, 50), 2, border_radius=10)
                surface.blit(sel_surf, (cx - 170, y - 25))

                # Arrow indicators
                arrow_offset = 140 + math.sin(self.anim_timer * 0.2) * 5
                arrow_l = self.font_option.render("✦", True, COLOR_TEXT_HIGHLIGHT)
                arrow_r = self.font_option.render("✦", True, COLOR_TEXT_HIGHLIGHT)
                surface.blit(arrow_l, (cx - arrow_offset - 20, y - 15))
                surface.blit(arrow_r, (cx + arrow_offset, y - 15))

            color = (255, 255, 255) if is_selected else (150, 140, 180)
            text = self.font_option.render(opt, True, color)
            text_rect = text.get_rect(center=(cx, y))
            surface.blit(text, text_rect)

        # Start Hint
        pulse_alpha = int(150 + 105 * math.sin(self.anim_timer * 0.08))
        hint_text = "W/S to select · J to Start"
        hint = self.font_hint.render(hint_text, True, (255, 255, 200))
        hint.set_alpha(pulse_alpha)
        hint_rect = hint.get_rect(center=(cx, WINDOW_HEIGHT - 40))
        surface.blit(hint, hint_rect)


class PauseOverlay:
    """Pause screen overlay."""

    def __init__(self):
        self.font_title = None
        self.font_hint = None
        self.initialized = False

    def init_fonts(self):
        if self.initialized:
            return
        self.font_title = pygame.font.Font(None, 72)
        self.font_hint = pygame.font.Font(None, 32)
        self.initialized = True

    def draw(self, surface):
        self.init_fonts()

        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        cx = WINDOW_WIDTH // 2
        cy = WINDOW_HEIGHT // 2

        # Panel
        panel_w, panel_h = 400, 200
        panel_rect = pygame.Rect(cx - panel_w//2, cy - panel_h//2, panel_w, panel_h)
        pygame.draw.rect(surface, (30, 20, 50), panel_rect, border_radius=10)
        pygame.draw.rect(surface, (200, 150, 255), panel_rect, 2, border_radius=10)

        # Pause text
        text = self.font_title.render("P A U S E D", True, COLOR_TEXT)
        rect = text.get_rect(center=(cx, cy - 20))
        surface.blit(text, rect)

        hint = self.font_hint.render("Press ESC to resume", True, COLOR_TEXT_DIM)
        hint_rect = hint.get_rect(center=(cx, cy + 40))
        surface.blit(hint, hint_rect)


class GameOverScreen:
    """Beautiful Game Over screen with score display."""

    def __init__(self):
        self.font_title = None
        self.font_score = None
        self.font_detail = None
        self.font_hint = None
        self.initialized = False
        self.anim_timer = 0
        self.fade_alpha = 0

    def init_fonts(self):
        if self.initialized:
            return
        self.font_title = pygame.font.Font(None, 84)
        self.font_score = pygame.font.Font(None, 56)
        self.font_detail = pygame.font.Font(None, 36)
        self.font_hint = pygame.font.Font(None, 32)
        self.initialized = True

    def update(self):
        self.anim_timer += 1
        if self.fade_alpha < 200:
            self.fade_alpha += 4

    def draw(self, surface, player, victory=False):
        self.init_fonts()

        # Fade Overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        bg_color = (20, 10, 40, self.fade_alpha) if victory else (40, 10, 20, self.fade_alpha)
        overlay.fill(bg_color)
        surface.blit(overlay, (0, 0))

        cx = WINDOW_WIDTH // 2
        y = 120

        # Title
        if victory:
            title_text = "✦ STAGE CLEAR! ✦"
            title_color = (255, 230, 120)
            shadow_color = (80, 60, 20)
        else:
            title_text = "G A M E  O V E R"
            title_color = (255, 120, 150)
            shadow_color = (80, 20, 30)

        title_y = y + math.sin(self.anim_timer * 0.05) * 10
        title = self.font_title.render(title_text, True, title_color)
        title_rect = title.get_rect(center=(cx, title_y))
        
        shadow = self.font_title.render(title_text, True, shadow_color)
        surface.blit(shadow, (title_rect.x + 4, title_rect.y + 4))
        surface.blit(title, title_rect)
        
        y += 120

        # Results Panel
        panel_w, panel_h = 500, 280
        panel_rect = pygame.Rect(cx - panel_w//2, y, panel_w, panel_h)
        
        panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        pygame.draw.rect(panel_surf, (20, 15, 30, 220), (0, 0, panel_w, panel_h), border_radius=15)
        
        border_color = (255, 200, 100) if victory else (255, 100, 150)
        pygame.draw.rect(panel_surf, (*border_color, 150), (0, 0, panel_w, panel_h), 2, border_radius=15)
        surface.blit(panel_surf, panel_rect)

        # Score Display inside panel
        py = y + 50
        score_label = self.font_detail.render("Final Score", True, COLOR_TEXT_DIM)
        surface.blit(score_label, score_label.get_rect(center=(cx, py)))
        py += 45
        
        score_text = f"{player.score:,}"
        score = self.font_score.render(score_text, True, COLOR_SCORE)
        surface.blit(score, score.get_rect(center=(cx, py)))
        py += 60

        # Details row
        detail_y = py
        
        graze_lbl = self.font_hint.render("Graze:", True, COLOR_TEXT_DIM)
        graze_val = self.font_detail.render(f"{player.graze_count}", True, COLOR_GRAZE)
        surface.blit(graze_lbl, (cx - 150, detail_y))
        surface.blit(graze_val, (cx - 150 + 80, detail_y - 2))

        power_lbl = self.font_hint.render("Power:", True, COLOR_TEXT_DIM)
        power_val = self.font_detail.render(f"{player.power:.2f}", True, COLOR_POWER)
        surface.blit(power_lbl, (cx + 30, detail_y))
        surface.blit(power_val, (cx + 30 + 80, detail_y - 2))

        # Action Hints
        y = panel_rect.bottom + 60
        pulse = 0.5 + 0.5 * math.sin(self.anim_timer * 0.08)
        alpha = int(150 + 105 * pulse)
        
        hint_text = "Press [J] to Play Again   ·   Press [ESC] for Menu"
        hint = self.font_hint.render(hint_text, True, (255, 255, 255))
        hint.set_alpha(alpha)
        hint_rect = hint.get_rect(center=(cx, y))
        
        # Hint background
        bg_rect = hint_rect.inflate(40, 20)
        pygame.draw.rect(surface, (0, 0, 0, 150), bg_rect, border_radius=10)
        surface.blit(hint, hint_rect)
