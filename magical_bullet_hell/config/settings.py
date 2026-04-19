import pygame
from config.manager import settings_manager

# =============================================================================
# Window & Display
# =============================================================================
WINDOW_WIDTH, WINDOW_HEIGHT = settings_manager.get_resolution()
PLAYFIELD_WIDTH = 540
PLAYFIELD_HEIGHT = 680
PLAYFIELD_X = (WINDOW_WIDTH - PLAYFIELD_WIDTH) // 2 - 150
PLAYFIELD_Y = 20
SIDEBAR_X = PLAYFIELD_X + PLAYFIELD_WIDTH + 40
SIDEBAR_WIDTH = 320
FPS = 60
TITLE = "✦ Magical Star Burst ✦"

# =============================================================================
# Colors - Magical Girl Pastel Palette
# =============================================================================
# Backgrounds
COLOR_BG_DARK = (12, 8, 24)
COLOR_BG_PANEL = (20, 14, 40)
COLOR_PLAYFIELD_BG = (8, 6, 18)
COLOR_PLAYFIELD_BORDER = (140, 100, 200)

# Player colors
COLOR_PLAYER_BODY = (255, 170, 220)
COLOR_PLAYER_WING = (200, 140, 255)
COLOR_PLAYER_GLOW = (255, 200, 240)
COLOR_HITBOX = (255, 255, 255)
COLOR_HITBOX_RING = (255, 100, 200)

# Bullet colors
COLOR_BULLET_PLAYER = (120, 220, 255)
COLOR_BULLET_PLAYER_FOCUS = (255, 180, 255)

BULLET_COLORS = [
    (255, 100, 130),   # Red-pink
    (100, 180, 255),   # Blue
    (255, 200, 80),    # Yellow-gold
    (180, 100, 255),   # Purple
    (100, 255, 180),   # Green-cyan
    (255, 140, 200),   # Pink
    (255, 160, 80),    # Orange
    (140, 200, 255),   # Light blue
]

# Character 2: Muscular Man colors
COLOR_PLAYER2_BODY = (100, 60, 40)   # Dark skin
COLOR_PLAYER2_SHIRT = (255, 140, 0)  # Orange tank top
COLOR_PLAYER2_HEAD = (255, 240, 200) # Chicken head
COLOR_PLAYER2_COMB = (255, 50, 50)   # Chicken comb (red)
COLOR_FIREBALL = (255, 100, 50)
COLOR_BLUE_FLAME = (100, 180, 255)


# Enemy colors
COLOR_FAIRY = (180, 220, 255)
COLOR_WITCH = (220, 160, 255)
COLOR_SPIRIT = (160, 255, 220)

# UI colors
COLOR_TEXT = (255, 240, 255)
COLOR_TEXT_DIM = (140, 120, 160)
COLOR_TEXT_HIGHLIGHT = (255, 200, 100)
COLOR_SCORE = (255, 220, 100)
COLOR_POWER = (255, 120, 180)
COLOR_GRAZE = (150, 200, 255)
COLOR_HEALTH_BG = (40, 20, 60)
COLOR_HEALTH_FILL = (255, 100, 150)
COLOR_HEALTH_FILL2 = (255, 180, 200)

# Particle colors
COLOR_PARTICLE_STAR = (255, 255, 200)
COLOR_PARTICLE_SPARKLE = (255, 200, 255)

# =============================================================================
# Characters
# =============================================================================
CHARACTERS = [
    {
        "id": "magical_girl",
        "name": "Magical Girl",
        "color": COLOR_PLAYER_BODY,
        "image_path": "assets/magical_girl.png",
        "skills": {
            "Passive": "Standard (Start with 3 Lives)",
            "Normal": "Homing sine wave projectiles",
            "Focus": "High-damage concentrated laser",
            "Bomb": "Flex! Clears projectiles & +30% Damage Buff"
        }
    },
    {
        "id": "muscular_man",
        "name": "Muscular Man",
        "color": COLOR_PLAYER2_SHIRT,
        "image_path": "assets/muscular_man.png",
        "skills": {
            "Passive": "Start with +2 Extra Lives",
            "Normal": "Fireball (Applies Burn 5% HP/sec)",
            "Focus": "Fire Breath (Applies Blue Flame 10% HP/sec)",
            "Bomb": "Phoenix Form (Invincible for 15s & +30% Damage)"
        }
    }
]

# =============================================================================
# Player Settings
# =============================================================================
PLAYER_SPEED = 5.0
PLAYER_FOCUS_SPEED = 2.0
PLAYER_HITBOX_RADIUS = 3
PLAYER_GRAZE_RADIUS = 24
PLAYER_COLLECT_RADIUS = 30
PLAYER_START_LIVES = 3
PLAYER_START_BOMBS = 1
PLAYER_START_POWER = 1.0
PLAYER_MAX_POWER = 4.0
PLAYER_SHOOT_DELAY = 4        # frames between shots
PLAYER_FOCUS_SHOOT_DELAY = 5
PLAYER_INVINCIBLE_TIME = 180  # frames (3 seconds)
PLAYER_BOMB_DURATION = 300     # 5 seconds
PLAYER_BOMB_INVINCIBLE = 150  # frames
PLAYER_RESPAWN_Y_OFFSET = 100

# =============================================================================
# Bullet Settings
# =============================================================================
PLAYER_BULLET_SPEED = 12.0
PLAYER_BULLET_DAMAGE = 10
PLAYER_FOCUS_BULLET_SPEED = 14.0
PLAYER_FOCUS_BULLET_DAMAGE = 15

ENEMY_BULLET_SPEED_SLOW = 2.0
ENEMY_BULLET_SPEED_MEDIUM = 3.5
ENEMY_BULLET_SPEED_FAST = 5.0

BULLET_OFFSCREEN_MARGIN = 40

# =============================================================================
# Status Effect Settings
# =============================================================================
BURN_DAMAGE_PERCENT = 0.06
BLUE_FLAME_DAMAGE_PERCENT = 0.12
BOSS_STATUS_DAMAGE_MULT = 0.4  # Reduction factor for bosses (40% of original dmg)
STATUS_TICK_RATE = 0.5         # seconds between ticks

# =============================================================================
# Enemy Settings
# =============================================================================
ENEMY_FAIRY_HP = 30
ENEMY_FAIRY_SCORE = 100
ENEMY_FAIRY_SHOOT_DELAY = 60

ENEMY_WITCH_HP = 80
ENEMY_WITCH_SCORE = 300
ENEMY_WITCH_SHOOT_DELAY = 45

ENEMY_SPIRIT_HP = 50
ENEMY_SPIRIT_SCORE = 200
ENEMY_SPIRIT_SHOOT_DELAY = 50

# =============================================================================
# Boss Settings
# =============================================================================
BOSS_PHASE_HP = [600, 800, 1200]
BOSS_PHASE_TIME = [30 * FPS, 35 * FPS, 45 * FPS]  # time limit per phase
BOSS_MOVE_SPEED = 1.5
BOSS_SCORE = 5000

# =============================================================================
# Item Settings
# =============================================================================
ITEM_FALL_SPEED = 2.0
ITEM_AUTOCOLLECT_Y = 120  # auto-collect when player above this Y
ITEM_POWER_VALUE = 0.05
ITEM_SCORE_VALUE = 100
ITEM_BIG_POWER_VALUE = 0.5
ITEM_LIFE_PIECE_VALUE = 1
ITEM_BOMB_PIECE_VALUE = 1

# =============================================================================
# Spawn / Wave Settings
# =============================================================================
WAVE_INTERVAL = 180          # frames between waves
BOSS_TRIGGER_WAVE = 12       # boss appears after this many waves
DIFFICULTY_SCALE_RATE = 0.02 # difficulty increase per wave

# =============================================================================
# Graze
# =============================================================================
GRAZE_SCORE = 10
GRAZE_POWER = 0.01

# =============================================================================
# Difficulty Multipliers
# =============================================================================
DIFFICULTY = {
    "Easy":    {"speed_mult": 0.7, "density_mult": 0.6, "hp_mult": 0.7, "score_mult": 0.5},
    "Normal":  {"speed_mult": 1.0, "density_mult": 1.0, "hp_mult": 1.0, "score_mult": 1.0},
    "Hard":    {"speed_mult": 1.15, "density_mult": 1.4, "hp_mult": 1.5, "score_mult": 2.0},
    "Chaotic": {"speed_mult": 1.5, "density_mult": 3.5, "hp_mult": 4.5, "score_mult": 5.0},
}

# =============================================================================
# Key Bindings
# =============================================================================
KEY_UP = settings_manager.get_key("up")
KEY_DOWN = settings_manager.get_key("down")
KEY_LEFT = settings_manager.get_key("left")
KEY_RIGHT = settings_manager.get_key("right")
KEY_SHOOT = settings_manager.get_key("shoot")
KEY_BOMB = settings_manager.get_key("bomb")
KEY_FOCUS = settings_manager.get_key("focus")
KEY_PAUSE = settings_manager.get_key("pause")
KEY_FULLSCREEN = pygame.K_F11

