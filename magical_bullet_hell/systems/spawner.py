"""
Enemy wave spawning system.
"""
import random
import math
from config.settings import (
    PLAYFIELD_X, PLAYFIELD_Y, PLAYFIELD_WIDTH, PLAYFIELD_HEIGHT,
    WAVE_INTERVAL, BOSS_TRIGGER_WAVE, DIFFICULTY_SCALE_RATE,
)
from entities.enemy import Fairy, Witch, Spirit, Slime, AquaSpirit
from entities.boss import Boss
from entities.boss_water import WaterBoss


class Spawner:
    """Manages enemy wave spawning and difficulty scaling."""

    def __init__(self, enemy_group, difficulty_settings):
        self.enemy_group = enemy_group
        self.difficulty_settings = difficulty_settings

        self.wave_timer = 120  # Initial delay before first wave
        self.wave_count = 0
        self.difficulty_mult = difficulty_settings["hp_mult"]
        self.speed_mult = difficulty_settings["speed_mult"]
        self.density_mult = difficulty_settings["density_mult"]

        self.boss = None
        self.boss_active = False
        self.boss_defeated = False
        self.current_stage = 1
        self.game_won = False

    @property
    def current_difficulty(self):
        """Get current difficulty multiplier (increases over time)."""
        stage_mult = 1.0 + (self.current_stage - 1) * 0.5
        return self.difficulty_mult * (1.0 + self.wave_count * DIFFICULTY_SCALE_RATE) * stage_mult

    def update(self):
        """Update spawner, spawn waves when ready."""
        if self.boss_active or self.game_won:
            return None

        self.wave_timer -= 1
        if self.wave_timer <= 0:
            self.wave_count += 1

            if self.wave_count >= BOSS_TRIGGER_WAVE:
                # Spawn boss for current stage
                return self._spawn_boss()
            else:
                self._spawn_wave()
                self.wave_timer = max(60, int(WAVE_INTERVAL - self.wave_count * 3))

        return None

    def _spawn_wave(self):
        """Spawn a wave of enemies based on current stage."""
        diff = self.current_difficulty
        
        if self.current_stage == 1:
            wave_types = ["fairy_line", "fairy_v", "witch_pair", "spirit_rush", "mixed"]
            weights = [30, 20, 15, 10, 25]
        else: # Stage 2
            wave_types = ["slime_bounce", "aqua_rush", "mixed_water", "spirit_rush"]
            weights = [35, 30, 25, 10]
            
        wave_type = random.choices(wave_types, weights=weights, k=1)[0]

        if wave_type == "fairy_line":
            self._spawn_fairy_line(diff)
        elif wave_type == "fairy_v":
            self._spawn_fairy_v(diff)
        elif wave_type == "witch_pair":
            self._spawn_witch_pair(diff)
        elif wave_type == "spirit_rush":
            self._spawn_spirit_rush(diff)
        elif wave_type == "mixed":
            self._spawn_mixed(diff)
        elif wave_type == "slime_bounce":
            self._spawn_slime_bounce(diff)
        elif wave_type == "aqua_rush":
            self._spawn_aqua_rush(diff)
        elif wave_type == "mixed_water":
            self._spawn_mixed_water(diff)

    def _spawn_fairy_line(self, diff):
        """Line of fairies from one side."""
        count = int((4 + random.randint(0, 2)) * self.density_mult)
        from_left = random.choice([True, False])
        base_y = random.uniform(PLAYFIELD_Y + 60, PLAYFIELD_Y + 200)

        for i in range(count):
            if from_left:
                sx = PLAYFIELD_X - 20
                tx = PLAYFIELD_X + 40 + i * 50
            else:
                sx = PLAYFIELD_X + PLAYFIELD_WIDTH + 20
                tx = PLAYFIELD_X + PLAYFIELD_WIDTH - 40 - i * 50

            sy = PLAYFIELD_Y - 20
            ty = base_y + random.uniform(-20, 20)

            fairy = Fairy(sx, sy, tx, ty, diff)
            self.enemy_group.add(fairy)

    def _spawn_fairy_v(self, diff):
        """V-formation of fairies."""
        count = int(5 * self.density_mult)
        center_x = PLAYFIELD_X + PLAYFIELD_WIDTH // 2 + random.randint(-80, 80)

        for i in range(count):
            offset = (i - count // 2) * 40
            sx = center_x + offset
            sy = PLAYFIELD_Y - 20 - abs(offset) * 0.5
            tx = center_x + offset * 0.6
            ty = PLAYFIELD_Y + 80 + abs(offset) * 0.3

            fairy = Fairy(sx, sy, tx, ty, diff)
            self.enemy_group.add(fairy)

    def _spawn_witch_pair(self, diff):
        """Pair of witches."""
        count = max(1, int(2 * self.density_mult))
        for i in range(count):
            sx = PLAYFIELD_X + random.randint(60, PLAYFIELD_WIDTH - 60)
            sy = PLAYFIELD_Y - 30
            tx = PLAYFIELD_X + random.randint(80, PLAYFIELD_WIDTH - 80)
            ty = PLAYFIELD_Y + random.randint(60, 160)

            witch = Witch(sx, sy, tx, ty, diff)
            self.enemy_group.add(witch)

    def _spawn_spirit_rush(self, diff):
        """Quick spirits that rush through."""
        count = max(2, int(3 * self.density_mult))
        for i in range(count):
            side = random.choice([-1, 1])
            if side == -1:
                sx = PLAYFIELD_X - 20
            else:
                sx = PLAYFIELD_X + PLAYFIELD_WIDTH + 20

            sy = PLAYFIELD_Y + random.randint(30, 150)
            tx = PLAYFIELD_X + PLAYFIELD_WIDTH // 2 + random.randint(-100, 100)
            ty = PLAYFIELD_Y + random.randint(60, 200)

            spirit = Spirit(sx, sy, tx, ty, diff)
            self.enemy_group.add(spirit)

    def _spawn_mixed(self, diff):
        """Mixed wave of different enemy types."""
        self._spawn_fairy_line(diff * 0.8)
        if random.random() < 0.5:
            self._spawn_witch_pair(diff * 0.9)
        else:
            self._spawn_spirit_rush(diff * 0.9)

    def _spawn_slime_bounce(self, diff):
        """Group of slimes."""
        count = int(3 * self.density_mult)
        for i in range(count):
            sx = PLAYFIELD_X + (i + 1) * (PLAYFIELD_WIDTH / (count + 1))
            sy = PLAYFIELD_Y - 30
            tx = sx
            ty = PLAYFIELD_Y + 120
            self.enemy_group.add(Slime(sx, sy, tx, ty, diff))

    def _spawn_aqua_rush(self, diff):
        """Rapid aqua spirits."""
        count = int(4 * self.density_mult)
        for i in range(count):
            sx = PLAYFIELD_X + random.randint(0, PLAYFIELD_WIDTH)
            sy = PLAYFIELD_Y - 20
            tx = sx + random.randint(-50, 50)
            ty = PLAYFIELD_Y + 100 + i * 30
            self.enemy_group.add(AquaSpirit(sx, sy, tx, ty, diff))

    def _spawn_mixed_water(self, diff):
        self._spawn_slime_bounce(diff * 0.8)
        self._spawn_aqua_rush(diff * 0.8)

    def _spawn_boss(self):
        """Spawn the boss for current stage."""
        if self.current_stage == 1:
            self.boss = Boss(self.current_difficulty)
        else:
            self.boss = WaterBoss(self.current_difficulty)
            
        self.boss_active = True
        self.enemy_group.add(self.boss)
        return self.boss

    def on_boss_defeated(self):
        """Called when boss is defeated. Advance stage or win."""
        self.boss_active = False
        self.boss = None
        
        if self.current_stage == 1:
            self.current_stage = 2
            self.wave_count = 0
            self.wave_timer = 240 # Longer break between stages
        else:
            self.boss_defeated = True
            self.game_won = True
