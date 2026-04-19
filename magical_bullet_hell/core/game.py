"""
Main game loop, state machine, and rendering orchestration.
"""
import pygame
import math
import random
from config.settings import (
    WINDOW_WIDTH, WINDOW_HEIGHT, PLAYFIELD_X, PLAYFIELD_Y,
    PLAYFIELD_WIDTH, PLAYFIELD_HEIGHT, FPS, TITLE,
    COLOR_BG_DARK, COLOR_PLAYFIELD_BG, COLOR_PLAYFIELD_BORDER,
    ITEM_AUTOCOLLECT_Y, DIFFICULTY,
    KEY_PAUSE, KEY_SHOOT, KEY_BOMB, KEY_FULLSCREEN
)
from entities.player import Player
from entities.boss import Boss
from systems.spawner import Spawner
from systems.particle import ParticleSystem
from systems.collision import (
    check_player_enemy_bullet_collision,
    check_graze,
    check_player_bullet_enemy_collision,
    check_item_collection,
)
from systems.bullet_patterns import spawn_bullets
from systems.item import spawn_enemy_drops, Item
from ui.hud import HUD
from ui.menu import TitleScreen, PauseOverlay, GameOverScreen
from ui.effects import ScreenEffects


# Game states
STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_PAUSED = "paused"
STATE_GAME_OVER = "game_over"
STATE_VICTORY = "victory"


class Game:
    """Main game class managing the game loop and state."""

    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()
        
        # Initialize audio
        from systems.audio import audio
        audio.init()
        audio.play_music("menu")

        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = STATE_MENU
        self.frame_count = 0
        self.is_fullscreen = False

        # Background stars
        self.bg_stars = []
        for _ in range(60):
            self.bg_stars.append({
                "x": random.uniform(PLAYFIELD_X, PLAYFIELD_X + PLAYFIELD_WIDTH),
                "y": random.uniform(PLAYFIELD_Y, PLAYFIELD_Y + PLAYFIELD_HEIGHT),
                "speed": random.uniform(0.3, 1.2),
                "size": random.uniform(0.5, 2),
                "brightness": random.uniform(60, 200),
            })

        # UI components
        self.title_screen = TitleScreen()
        self.pause_overlay = PauseOverlay()
        self.game_over_screen = GameOverScreen()
        self.hud = HUD()
        self.effects = ScreenEffects()

        # Game objects (initialized on game start)
        self.player = None
        self.spawner = None
        self.particles = ParticleSystem()
        self.difficulty_name = "Normal"
        self.character_id = "magical_girl"

        # Sprite groups
        self.player_bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.items = pygame.sprite.Group()

    def start_game(self, difficulty_name, character_id="magical_girl"):
        """Initialize a new game with selected difficulty and character."""
        self.difficulty_name = difficulty_name
        self.character_id = character_id
        diff = DIFFICULTY[difficulty_name]

        # Clear everything
        self.player_bullets.empty()
        self.enemy_bullets.empty()
        self.enemies.empty()
        self.items.empty()
        self.particles.clear()
        self.effects = ScreenEffects()
        self.frame_count = 0

        # Create player
        self.player = Player(self.player_bullets, character_id=self.character_id)

        # Create spawner
        self.spawner = Spawner(self.enemies, diff)

        # Start stage 1 music
        from systems.audio import audio
        audio.play_music("stage1")

        self.state = STATE_PLAYING

    def run(self):
        """Main game loop."""
        while self.running:
            dt = self.clock.tick(FPS)
            self.frame_count += 1

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break
                self._handle_event(event)

            # Update
            self._update()

            # Draw
            self._draw()

            pygame.display.flip()

        pygame.quit()

    def toggle_fullscreen(self):
        """Toggle fullscreen mode."""
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    def resize_window(self, width, height):
        """Update window size from settings."""
        if not self.is_fullscreen:
            self.screen = pygame.display.set_mode((width, height))
            
    def _handle_event(self, event):
        """Handle a single event based on current state."""
        # Handle global events first
        if event.type == pygame.KEYDOWN and event.key == KEY_FULLSCREEN:
            self.toggle_fullscreen()
            return
            
        if self.state == STATE_MENU:
            result = self.title_screen.handle_input(event)
            if result:
                self.start_game(result[0], result[1])
            
            # Check for resolution/volume changes from settings
            if self.title_screen.menu_state == "title" and self.title_screen.settings_menu.closed_this_frame:
                from config.manager import settings_manager
                w, h = settings_manager.get_resolution()
                self.resize_window(w, h)
                from systems.audio import audio
                audio.update_volumes()
                self.title_screen.settings_menu.closed_this_frame = False

        elif self.state == STATE_PLAYING:
            if event.type == pygame.KEYDOWN:
                if event.key == KEY_PAUSE:
                    self.state = STATE_PAUSED

        elif self.state == STATE_PAUSED:
            if event.type == pygame.KEYDOWN:
                if event.key == KEY_PAUSE:
                    self.state = STATE_PLAYING

        elif self.state in (STATE_GAME_OVER, STATE_VICTORY):
            if event.type == pygame.KEYDOWN:
                if event.key == KEY_SHOOT or event.key == pygame.K_j:
                    # Restart with same difficulty and character
                    self.start_game(self.difficulty_name, self.character_id)
                elif event.key == KEY_PAUSE or event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                    # Return to menu
                    self.state = STATE_MENU
                    from systems.audio import audio
                    audio.play_music("menu")

    def _update(self):
        """Update game state."""
        if self.state == STATE_MENU:
            self.title_screen.update()

        elif self.state == STATE_PLAYING:
            self._update_gameplay()

        elif self.state in (STATE_GAME_OVER, STATE_VICTORY):
            self.game_over_screen.update()
            self.particles.update()

    def _update_gameplay(self):
        """Update all gameplay systems."""
        # Player input
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)

        # Update entities
        self.player.update()
        self.player_bullets.update(self.enemies)
        self.enemy_bullets.update()
        self.enemies.update()

        # Update items with player position
        for item in self.items:
            # Auto-collect when player is near top
            if self.player.y < PLAYFIELD_Y + ITEM_AUTOCOLLECT_Y:
                item.attracted = True
            item.update(self.player.x, self.player.y)

        # Spawner
        boss_result = self.spawner.update()
        from systems.audio import audio
        if boss_result:
            # Boss appeared
            self.effects.start_flash((255, 200, 255), 15)
            self.effects.start_shake(3, 20)
            audio.play_music("boss")
            
        # Check for stage transition music
        if not self.spawner.boss_active:
            if self.spawner.current_stage == 2 and self.frame_count % 60 == 0:
                # This is a bit hacky, but check if we should play stage2 music
                # Only if not already playing and boss is dead
                pass # Logic to handle this better in spawner would be better

        # Boss spell card dimming
        if self.spawner.boss_active and self.spawner.boss:
            if self.spawner.boss.is_spell_card:
                self.effects.set_dim(60)
            else:
                self.effects.set_dim(0)
        else:
            self.effects.set_dim(0)

        # Enemy shooting
        for enemy in self.enemies:
            if isinstance(enemy, Boss):
                if not enemy.entering:
                    params = enemy.get_bullet_params(self.player.x, self.player.y)
                    if params:
                        spawn_bullets(self.enemy_bullets, enemy.x, enemy.y, params)
            elif hasattr(enemy, 'can_shoot') and enemy.can_shoot():
                params = enemy.get_bullet_params(self.player.x, self.player.y)
                if params:
                    spawn_bullets(self.enemy_bullets, enemy.x, enemy.y, params)
                    enemy.reset_shoot_timer()

        # Collision detection
        if not self.player.dead:
            # Process status effects
            for enemy in list(self.enemies):
                if hasattr(enemy, 'process_status_effects'):
                    died = enemy.process_status_effects()
                    if died and not enemy.alive():
                        pass # already handled or should be handled. Actually we just let collision logic handle or add death handler
                    if died:
                        self._handle_enemy_death(enemy)
            
            # Player bullets vs enemies
            killed_enemies = check_player_bullet_enemy_collision(
                self.player_bullets, self.enemies, self.particles
            )
            for enemy in killed_enemies:
                self._handle_enemy_death(enemy)

            # Graze detection
            check_graze(self.player, self.enemy_bullets, self.particles)

            # Player hit detection
            was_hit = check_player_enemy_bullet_collision(
                self.player, self.enemy_bullets, self.particles
            )
            if was_hit:
                died = self.player.die()
                if died:
                    from systems.audio import audio
                    audio.play("death")
                    self.particles.emit_explosion(
                        self.player.x, self.player.y, (255, 200, 255), count=25
                    )
                    self.effects.start_flash((255, 100, 150), 10)
                    self.effects.start_shake(6, 15)

                    # Clear bullets on death
                    for bullet in self.enemy_bullets:
                        self.particles.emit_sparkle(bullet.x, bullet.y, (200, 200, 255))
                    self.enemy_bullets.empty()

                    if self.player.lives <= 0:
                        self.state = STATE_GAME_OVER

            # Item collection
            collected = check_item_collection(self.player, self.items)
            if collected:
                from systems.audio import audio
                audio.play("item")
            for item in collected:
                self.particles.emit_item_collect(item.x, item.y, item.color)
                item.collect(self.player)

        # Bomb effect
        if self.player.is_bombing:
            self._process_bomb()

        # Particles
        self.particles.update()
        self.effects.update()

        # Player trail particles
        if not self.player.dead and self.frame_count % 3 == 0:
            self.particles.emit_trail(
                self.player.x, self.player.y + 10,
                (255, 180, 220), size=2
            )

    def _handle_enemy_death(self, enemy):
        """Handle score, particles, drops, and state when enemy dies."""
        if not enemy.alive():
            return
            
        self.player.add_score(enemy.score_value)
        from systems.audio import audio
        audio.play("explosion")
        self.particles.emit_explosion(enemy.x, enemy.y, enemy.color)

        if isinstance(enemy, Boss):
            self.particles.emit_boss_defeat(enemy.x, enemy.y)
            self.effects.start_flash((255, 255, 255), 20)
            self.effects.start_shake(8, 30)
            spawn_enemy_drops(enemy.x, enemy.y, self.items, is_boss=True)
            self.spawner.on_boss_defeated()
            # If we just moved to stage 2, change music
            if self.spawner.current_stage == 2:
                audio.play_music("stage2")
            
            # Check victory
            if self.spawner.game_won:
                self.state = STATE_VICTORY
        else:
            spawn_enemy_drops(enemy.x, enemy.y, self.items, is_boss=False)
            self.effects.start_shake(2, 5)

        enemy.kill()

    def _process_bomb(self):
        """Process bomb: clear bullets and damage enemies."""
        # Expand clearing radius over time
        bomb_progress = 1.0 - (self.player.bomb_timer / 90.0)
        clear_radius = 300 * bomb_progress

        # Clear enemy bullets within radius (only for magical girl)
        if self.player.character_id == "magical_girl":
            for bullet in list(self.enemy_bullets):
                dx = bullet.x - self.player.x
                dy = bullet.y - self.player.y
                dist = math.sqrt(dx * dx + dy * dy)
                if dist < clear_radius:
                    self.particles.emit_sparkle(bullet.x, bullet.y)
                    self.player.add_score(10)
                    bullet.kill()

        # Magical Girl bomb: does NOT damage enemies
        # Muscular Man bomb: does NOT damage enemies, just self buff/phoenix form
        pass

        # Visual
        if self.player.bomb_timer > 60:
            self.effects.start_bomb_visual(self.player.x, self.player.y, 90)
            self.effects.start_flash((255, 200, 255), 5)

        self.particles.emit_bomb_effect(
            self.player.x, self.player.y,
            clear_radius * 0.3, (255, 200, 255)
        )

    def _draw(self):
        """Draw everything."""
        self.screen.fill(COLOR_BG_DARK)

        if self.state == STATE_MENU:
            self.title_screen.draw(self.screen)
            return

        # Apply shake offset
        ox, oy = self.effects.offset

        # Draw playfield background
        self._draw_playfield_bg(ox, oy)

        # Set playfield clipping rect to restrict drawing
        clip_rect = pygame.Rect(PLAYFIELD_X + ox, PLAYFIELD_Y + oy, PLAYFIELD_WIDTH, PLAYFIELD_HEIGHT)
        self.screen.set_clip(clip_rect)

        # Draw game elements directly on screen with shake offset
        # Items
        for item in self.items:
            self.screen.blit(item.image, (item.rect.x + ox, item.rect.y + oy))

        # Enemy bullets
        for bullet in self.enemy_bullets:
            self.screen.blit(bullet.image, (bullet.rect.x + ox, bullet.rect.y + oy))

        # Enemies
        for enemy in self.enemies:
            self.screen.blit(enemy.image, (enemy.rect.x + ox, enemy.rect.y + oy))

        # Player bullets
        for bullet in self.player_bullets:
            self.screen.blit(bullet.image, (bullet.rect.x + ox, bullet.rect.y + oy))

        # Player
        if not self.player.dead:
            self.screen.blit(self.player.image, (self.player.rect.x + ox, self.player.rect.y + oy))

        # Particles
        self.particles.draw(self.screen, ox, oy)

        # Effects on playfield
        self.effects.draw(self.screen, ox, oy)

        # Reset clipping rect
        self.screen.set_clip(None)

        # Playfield border
        border_rect = pygame.Rect(PLAYFIELD_X + ox - 2, PLAYFIELD_Y + oy - 2,
                                  PLAYFIELD_WIDTH + 4, PLAYFIELD_HEIGHT + 4)
        pygame.draw.rect(self.screen, COLOR_PLAYFIELD_BORDER, border_rect, 2, border_radius=2)

        # HUD
        self.hud.draw(self.screen, self.player, self.spawner, self.frame_count)

        # Overlays
        if self.state == STATE_PAUSED:
            self.pause_overlay.draw(self.screen)
        elif self.state == STATE_GAME_OVER:
            self.game_over_screen.draw(self.screen, self.player, victory=False)
        elif self.state == STATE_VICTORY:
            self.game_over_screen.draw(self.screen, self.player, victory=True)

    def _draw_playfield_bg(self, ox, oy):
        """Draw playfield background with scrolling stars."""
        # Dark background
        bg_rect = pygame.Rect(PLAYFIELD_X + ox, PLAYFIELD_Y + oy,
                              PLAYFIELD_WIDTH, PLAYFIELD_HEIGHT)
        pygame.draw.rect(self.screen, COLOR_PLAYFIELD_BG, bg_rect)

        # Scrolling stars
        for star in self.bg_stars:
            star["y"] += star["speed"]
            if star["y"] > PLAYFIELD_Y + PLAYFIELD_HEIGHT:
                star["y"] = PLAYFIELD_Y
                star["x"] = random.uniform(PLAYFIELD_X, PLAYFIELD_X + PLAYFIELD_WIDTH)

            sx = star["x"] + ox
            sy = star["y"] + oy

            # Only draw if in playfield
            if (PLAYFIELD_X <= sx <= PLAYFIELD_X + PLAYFIELD_WIDTH and
                PLAYFIELD_Y <= sy <= PLAYFIELD_Y + PLAYFIELD_HEIGHT):
                bright = star["brightness"]
                twinkle = 0.5 + 0.5 * math.sin(self.frame_count * 0.03 + star["x"])
                alpha = int(bright * twinkle)
                size = max(1, int(star["size"]))

                if size <= 1:
                    self.screen.set_at((int(sx), int(sy)),
                                       (alpha, alpha, int(alpha * 0.9)))
                else:
                    s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                    pygame.draw.circle(s, (alpha, alpha, int(alpha * 0.9), alpha),
                                       (size, size), size)
                    self.screen.blit(s, (int(sx) - size, int(sy) - size))
