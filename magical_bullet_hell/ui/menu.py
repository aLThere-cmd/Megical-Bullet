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
        self.font_small = None
        self.initialized = False

        self.menu_state = "title"

        self.selected = 0  # 0: Start, 1: Settings, 2: Quit
        self.main_options = ["Start Game", "Settings", "Quit"]
        self.difficulty_selected = 1  # Default to Normal
        self.options = list(DIFFICULTY.keys())
        from config.settings import CHARACTERS
        self.characters = CHARACTERS
        self.char_selected = 0
        self.anim_timer = 0
        self.char_images = {}
        
        from config.manager import settings_manager
        self.settings_menu = SettingsMenu(settings_manager)

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
        self.font_small = pygame.font.Font(None, 24)
        
        # Load images
        for char in self.characters:
            try:
                img = pygame.image.load(char["image_path"]).convert_alpha()
                # Center crop and scale
                w, h = img.get_size()
                aspect = w / h
                if aspect > 1: # Wide
                    new_h = 260
                    new_w = int(260 * aspect)
                    img = pygame.transform.smoothscale(img, (new_w, new_h))
                    crop_x = (new_w - 260) // 2
                    img = img.subsurface((crop_x, 0, 260, 260))
                else: # Tall
                    new_w = 260
                    new_h = int(260 / aspect)
                    img = pygame.transform.smoothscale(img, (new_w, new_h))
                    crop_y = (new_h - 260) // 2
                    img = img.subsurface((0, crop_y, 260, 260))
                
                self.char_images[char["id"]] = img
            except Exception:
                surf = pygame.Surface((260, 260), pygame.SRCALPHA)
                surf.fill((40, 30, 50, 200))
                # Draw a star instead of a rectangle
                draw_star(surf, char["color"], (130, 130), 40, 15, 5, 0)
                txt = self.font_small.render("IMAGE MISSING", True, (255, 255, 255))
                surf.blit(txt, txt.get_rect(center=(130, 190)))
                self.char_images[char["id"]] = surf
                
        self.initialized = True

    def handle_input(self, event):
        """Handle menu input. Returns (difficulty_name, character_id) if selected, None otherwise."""
        if self.menu_state == "settings":
            self.settings_menu.handle_input(event)
            if self.settings_menu.closed:
                self.menu_state = "title"
            return None

        if event.type == pygame.KEYDOWN:
            if self.menu_state == "title":
                if event.key == pygame.K_w or event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.main_options)
                elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.main_options)
                elif event.key == pygame.K_j or event.key == pygame.K_RETURN:
                    if self.selected == 0:
                        self.menu_state = "character"
                    elif self.selected == 1:
                        self.menu_state = "settings"
                        self.settings_menu.open()
                    elif self.selected == 2:
                        pygame.event.post(pygame.event.Event(pygame.QUIT))
            elif self.menu_state == "character":
                if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    self.char_selected = (self.char_selected - 1) % len(self.characters)
                elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    self.char_selected = (self.char_selected + 1) % len(self.characters)
                elif event.key == pygame.K_j or event.key == pygame.K_RETURN:
                    self.menu_state = "difficulty"
                elif event.key == pygame.K_ESCAPE:
                    self.menu_state = "title"
            elif self.menu_state == "difficulty":
                if event.key == pygame.K_w or event.key == pygame.K_UP:
                    self.difficulty_selected = (self.difficulty_selected - 1) % len(self.options)
                elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    self.difficulty_selected = (self.difficulty_selected + 1) % len(self.options)
                elif event.key == pygame.K_j or event.key == pygame.K_RETURN:
                    return (self.options[self.difficulty_selected], self.characters[self.char_selected]["id"])
                elif event.key == pygame.K_ESCAPE:
                    self.menu_state = "character"
        return None

    def update(self):
        self.anim_timer += 1
        for p in self.particles:
            p["y"] += p["speed"]
            if p["y"] > WINDOW_HEIGHT:
                p["y"] = 0
                p["x"] = random.uniform(0, WINDOW_WIDTH)
        
        if self.menu_state == "settings":
            self.settings_menu.update()

    def draw(self, surface):
        self.init_fonts()
        
        if self.menu_state == "settings":
            self.settings_menu.draw(surface)
            return
        
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
        title = self.font_title.render("* Magical Star Burst *", True, COLOR_TEXT_HIGHLIGHT)
        title_rect = title.get_rect(center=(cx, title_y))
        
        # Draw shadow
        shadow = self.font_title.render("* Magical Star Burst *", True, (40, 20, 60))
        surface.blit(shadow, (title_rect.x + 4, title_rect.y + 4))
        surface.blit(title, title_rect)

        # Subtitle
        subtitle = self.font_subtitle.render("~ A Bullet Hell Adventure ~", True, COLOR_TEXT_DIM)
        sub_rect = subtitle.get_rect(center=(cx, title_y + 60))
        surface.blit(subtitle, sub_rect)

        # Sub-menus
        menu_y = 380
        if self.menu_state == "title":
            for i, opt in enumerate(self.main_options):
                y = menu_y + 40 + i * 50
                is_selected = (i == self.selected)
                
                if is_selected:
                    text = self.font_option.render(opt, True, COLOR_TEXT_HIGHLIGHT)
                    # Selector stars
                    star_offset = 120 + math.sin(self.anim_timer * 0.15) * 5
                    draw_star(surface, COLOR_TEXT_HIGHLIGHT, (cx - star_offset, y), 5, 2, 5, self.anim_timer * 0.05)
                    draw_star(surface, COLOR_TEXT_HIGHLIGHT, (cx + star_offset, y), 5, 2, 5, self.anim_timer * 0.05)
                else:
                    text = self.font_option.render(opt, True, (180, 160, 200))
                
                surface.blit(text, text.get_rect(center=(cx, y)))

        elif self.menu_state == "character":
            char_data = self.characters[self.char_selected]
            
            # Main panel
            panel_w, panel_h = 800, 360
            panel_rect = pygame.Rect(cx - panel_w//2, menu_y - 40, panel_w, panel_h)
            
            panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            pygame.draw.rect(panel_surf, (20, 15, 40, 220), (0, 0, panel_w, panel_h), border_radius=15)
            pygame.draw.rect(panel_surf, char_data["color"], (0, 0, panel_w, panel_h), 2, border_radius=15)
            surface.blit(panel_surf, panel_rect)

            # Left side (Name + Picture)
            name_text = self.font_option.render(f"<  {char_data['name']}  >", True, char_data["color"])
            surface.blit(name_text, name_text.get_rect(center=(cx - 200, menu_y - 10)))
            
            img = self.char_images[char_data["id"]]
            img_rect = img.get_rect(center=(cx - 200, menu_y + 160))
            
            # Picture border
            pygame.draw.rect(surface, (255, 255, 255), img_rect.inflate(4, 4), 2)
            surface.blit(img, img_rect)

            # Right side (Info Box)
            info_w, info_h = 360, 300
            info_rect = pygame.Rect(cx + 20, menu_y - 10, info_w, info_h)
            pygame.draw.rect(surface, (30, 25, 50), info_rect, border_radius=10)
            pygame.draw.rect(surface, (100, 80, 120), info_rect, 2, border_radius=10)
            
            # Skills info
            skills = char_data.get("skills", {})
            sy = info_rect.y + 20
            for skill_name, skill_desc in skills.items():
                st_text = self.font_hint.render(f"[{skill_name}]", True, (255, 200, 100))
                surface.blit(st_text, (info_rect.x + 20, sy))
                sy += 25
                
                # Simple line wrapping
                words = skill_desc.split(' ')
                line = ""
                for word in words:
                    test_line = line + word + " "
                    if self.font_small.size(test_line)[0] < info_w - 40:
                        line = test_line
                    else:
                        desc_text = self.font_small.render(line, True, (220, 220, 240))
                        surface.blit(desc_text, (info_rect.x + 30, sy))
                        sy += 20
                        line = word + " "
                desc_text = self.font_small.render(line, True, (220, 220, 240))
                surface.blit(desc_text, (info_rect.x + 30, sy))
                sy += 35

            # Arrow indicators
            arrow_offset = 380 + math.sin(self.anim_timer * 0.2) * 5
            arrow_l = self.font_option.render("*", True, char_data["color"])
            arrow_r = self.font_option.render("*", True, char_data["color"])
            surface.blit(arrow_l, (cx - arrow_offset - 20, menu_y + 130))
            surface.blit(arrow_r, (cx + arrow_offset, menu_y + 130))

            # Hint
            pulse_alpha = int(150 + 105 * math.sin(self.anim_timer * 0.08))
            hint_text = "A/D: Switch · J: Select · ESC: Back"
            hint = self.font_hint.render(hint_text, True, (255, 255, 200))
            hint.set_alpha(pulse_alpha)
            surface.blit(hint, hint.get_rect(center=(cx, WINDOW_HEIGHT - 30)))

        elif self.menu_state == "difficulty":
            panel_w, panel_h = 400, 280
            panel_rect = pygame.Rect(cx - panel_w//2, menu_y, panel_w, panel_h)
            
            panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            pygame.draw.rect(panel_surf, (20, 15, 40, 200), (0, 0, panel_w, panel_h), border_radius=15)
            pygame.draw.rect(panel_surf, (255, 180, 255, 100), (0, 0, panel_w, panel_h), 2, border_radius=15)
            surface.blit(panel_surf, panel_rect)

            for i, opt in enumerate(self.options):
                y = menu_y + 40 + i * 60
                is_selected = (i == self.difficulty_selected)

                if is_selected:
                    sel_surf = pygame.Surface((340, 50), pygame.SRCALPHA)
                    sel_pulse = int(40 + 30 * math.sin(self.anim_timer * 0.1))
                    pygame.draw.rect(sel_surf, (255, 150, 255, sel_pulse), (0, 0, 340, 50), border_radius=10)
                    pygame.draw.rect(sel_surf, (255, 200, 255, 150), (0, 0, 340, 50), 2, border_radius=10)
                    surface.blit(sel_surf, (cx - 170, y - 25))

                    arrow_offset = 140 + math.sin(self.anim_timer * 0.2) * 5
                    arrow_l = self.font_option.render("*", True, COLOR_TEXT_HIGHLIGHT)
                    arrow_r = self.font_option.render("*", True, COLOR_TEXT_HIGHLIGHT)
                    surface.blit(arrow_l, (cx - arrow_offset - 20, y - 15))
                    surface.blit(arrow_r, (cx + arrow_offset, y - 15))

                color = (255, 255, 255) if is_selected else (150, 140, 180)
                text = self.font_option.render(opt, True, color)
                surface.blit(text, text.get_rect(center=(cx, y)))

            pulse_alpha = int(150 + 105 * math.sin(self.anim_timer * 0.08))
            hint_text = "W/S: Select · J: Start Game · ESC: Back"
            hint = self.font_hint.render(hint_text, True, (255, 255, 200))
            hint.set_alpha(pulse_alpha)
            surface.blit(hint, hint.get_rect(center=(cx, WINDOW_HEIGHT - 30)))


class SettingsMenu:
    """Settings menu for audio, keys, and resolution."""
    
    def __init__(self, manager):
        self.manager = manager
        self.closed = True
        self.closed_this_frame = False
        self.selected = 0
        self.anim_timer = 0
        
        self.categories = ["Audio", "Keybinds", "Resolution"]
        self.sub_selected = 0
        self.in_sub = False
        self.mapping_key = None # Which key we are currently remapping
        
        self.resolutions = [(960, 540), (1280, 720), (1600, 900), (1920, 1080)]
        self.res_idx = 0
        current_res = manager.get_resolution()
        for i, res in enumerate(self.resolutions):
            if res == current_res:
                self.res_idx = i
                break

    def open(self):
        self.closed = False
        self.selected = 0
        self.in_sub = False

    def handle_input(self, event):
        if self.mapping_key:
            if event.type == pygame.KEYDOWN:
                self.manager.set_key(self.mapping_key, event.key)
                self.mapping_key = None
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.in_sub:
                    self.in_sub = False
                else:
                    self.closed = True
                    self.closed_this_frame = True
            
            elif not self.in_sub:
                if event.key == pygame.K_w or event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.categories)
                elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.categories)
                elif event.key == pygame.K_j or event.key == pygame.K_RETURN:
                    self.in_sub = True
                    self.sub_selected = 0
            
            else: # In sub-menu
                if self.selected == 0: # Audio
                    if event.key == pygame.K_w or event.key == pygame.K_UP:
                        self.sub_selected = (self.sub_selected - 1) % 2
                    elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                        self.sub_selected = (self.sub_selected + 1) % 2
                    elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
                        key = "music_volume" if self.sub_selected == 0 else "sfx_volume"
                        val = max(0.0, self.manager.get_audio(key) - 0.1)
                        self.manager.set_audio(key, val)
                    elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                        key = "music_volume" if self.sub_selected == 0 else "sfx_volume"
                        val = min(1.0, self.manager.get_audio(key) + 0.1)
                        self.manager.set_audio(key, val)
                        
                elif self.selected == 1: # Keybinds
                    keys = list(self.manager.settings["keybinds"].keys())
                    if event.key == pygame.K_w or event.key == pygame.K_UP:
                        self.sub_selected = (self.sub_selected - 1) % len(keys)
                    elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                        self.sub_selected = (self.sub_selected + 1) % len(keys)
                    elif event.key == pygame.K_j or event.key == pygame.K_RETURN:
                        self.mapping_key = keys[self.sub_selected]
                        
                elif self.selected == 2: # Resolution
                    if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                        self.res_idx = (self.res_idx - 1) % len(self.resolutions)
                    elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                        self.res_idx = (self.res_idx + 1) % len(self.resolutions)
                    elif event.key == pygame.K_j or event.key == pygame.K_RETURN:
                        res = self.resolutions[self.res_idx]
                        self.manager.set_resolution(res[0], res[1])
                        # In a real game, we'd trigger a window resize here or warn the user

    def update(self):
        self.anim_timer += 1

    def draw(self, surface):
        cx, cy = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
        
        # Overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 5, 20, 230))
        surface.blit(overlay, (0, 0))
        
        # Title
        font_title = pygame.font.Font(None, 64)
        title = font_title.render("S E T T I N G S", True, COLOR_TEXT_HIGHLIGHT)
        surface.blit(title, title.get_rect(center=(cx, 80)))
        
        # Categories (Left side)
        font_cat = pygame.font.Font(None, 36)
        for i, cat in enumerate(self.categories):
            is_sel = (i == self.selected)
            color = COLOR_TEXT_HIGHLIGHT if is_sel else (150, 130, 180)
            if is_sel and not self.in_sub:
                color = (255, 255, 255)
                pygame.draw.rect(surface, (255, 150, 255, 40), (cx - 450, 150 + i * 50, 200, 40), border_radius=5)
            
            txt = font_cat.render(cat, True, color)
            surface.blit(txt, (cx - 430, 160 + i * 50))
            
        # Divider
        pygame.draw.line(surface, (100, 80, 120), (cx - 230, 150), (cx - 230, 550), 2)
        
        # Content (Right side)
        if self.selected == 0: # Audio
            self._draw_audio(surface, cx, 160)
        elif self.selected == 1: # Keybinds
            self._draw_keys(surface, cx, 160)
        elif self.selected == 2: # Resolution
            self._draw_res(surface, cx, 160)
            
        # Hint
        font_hint = pygame.font.Font(None, 24)
        hint = font_hint.render("W/S: Navigate · A/D: Adjust · J: Select · ESC: Back", True, (150, 150, 180))
        surface.blit(hint, hint.get_rect(center=(cx, WINDOW_HEIGHT - 40)))

    def _draw_audio(self, surface, cx, start_y):
        font = pygame.font.Font(None, 32)
        options = ["Music Volume", "SFX Volume"]
        keys = ["music_volume", "sfx_volume"]
        
        for i, opt in enumerate(options):
            is_sel = (self.in_sub and self.sub_selected == i)
            color = (255, 255, 255) if is_sel else (180, 180, 220)
            
            txt = font.render(opt, True, color)
            surface.blit(txt, (cx - 180, start_y + i * 80))
            
            # Slider
            val = self.manager.get_audio(keys[i])
            bar_w = 200
            pygame.draw.rect(surface, (40, 30, 60), (cx + 50, start_y + i * 80 + 10, bar_w, 10))
            pygame.draw.rect(surface, COLOR_POWER, (cx + 50, start_y + i * 80 + 10, int(bar_w * val), 10))
            
            # Knob
            pygame.draw.circle(surface, (255, 255, 255), (cx + 50 + int(bar_w * val), start_y + i * 80 + 15), 8)
            
            # Percent
            pct = font.render(f"{int(val * 100)}%", True, color)
            surface.blit(pct, (cx + 270, start_y + i * 80))

    def _draw_keys(self, surface, cx, start_y):
        font = pygame.font.Font(None, 28)
        keys_dict = self.manager.settings["keybinds"]
        keys_list = list(keys_dict.items())
        
        visible_count = 10
        scroll_offset = max(0, self.sub_selected - 9) if self.in_sub else 0
        
        for i in range(min(visible_count, len(keys_list))):
            idx = i + scroll_offset
            if idx >= len(keys_list): break
            
            k_name, k_val = keys_list[idx]
            is_sel = (self.in_sub and self.sub_selected == idx)
            color = (255, 255, 255) if is_sel else (180, 180, 220)
            
            if self.mapping_key == k_name:
                color = COLOR_TEXT_HIGHLIGHT
                k_str = "Press any key..."
            else:
                k_str = pygame.key.name(k_val).upper()
            
            surface.blit(font.render(k_name.capitalize(), True, color), (cx - 180, start_y + i * 35))
            surface.blit(font.render(k_str, True, color), (cx + 100, start_y + i * 35))

    def _draw_res(self, surface, cx, start_y):
        font = pygame.font.Font(None, 36)
        res = self.resolutions[self.res_idx]
        is_sel = self.in_sub
        color = (255, 255, 255) if is_sel else (180, 180, 220)
        
        txt = font.render(f"<  {res[0]} x {res[1]}  >", True, color)
        rect = txt.get_rect(center=(cx + 100, start_y + 50))
        surface.blit(txt, rect)
        
        hint = pygame.font.Font(None, 24).render("Press J to Apply (Restart required)", True, (150, 130, 160))
        surface.blit(hint, hint.get_rect(center=(cx + 100, start_y + 100)))


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
            title_text = "* STAGE CLEAR! *"
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
        
        # Centered Graze info
        graze_txt = f"Graze Count: {player.graze_count}"
        graze = self.font_detail.render(graze_txt, True, COLOR_GRAZE)
        surface.blit(graze, graze.get_rect(center=(cx, detail_y)))

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
