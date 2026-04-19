"""
Enemy wave spawning system.
"""
import random
import math
from config.settings import (
    PLAYFIELD_X, PLAYFIELD_Y, PLAYFIELD_WIDTH, PLAYFIELD_HEIGHT,
    WAVE_INTERVAL, BOSS_TRIGGER_WAVE, DIFFICULTY_SCALE_RATE,
)
from entities.enemy import Fairy, Witch, Spirit
from entities.boss import Boss


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
        self.game_won = False

    @property
    def current_difficulty(self):
        """Get current difficulty multiplier (increases over time)."""
        return self.difficulty_mult * (1.0 + self.wave_count * DIFFICULTY_SCALE_RATE)

    def update(self):
        """Update spawner, spawn waves when ready."""
        if self.boss_active or self.game_won:
            return None

        self.wave_timer -= 1
        if self.wave_timer <= 0:
            self.wave_count += 1

            if self.wave_count >= BOSS_TRIGGER_WAVE and not self.boss_defeated:
                # Spawn boss
                return self._spawn_boss()
            else:
                self._spawn_wave()
                self.wave_timer = max(60, int(WAVE_INTERVAL - self.wave_count * 3))

        return None

    def _spawn_wave(self):
        """Spawn a wave of enemies."""
        diff = self.current_difficulty
        wave_type = random.choices(
            ["fairy_line", "fairy_v", "witch_pair", "spirit_rush", "mixed"],
            weights=[30, 20, 15, 10, 25],
            k=1
        )[0]

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

    def _spawn_boss(self):
        """Spawn the boss."""
        self.boss = Boss(self.current_difficulty)
        self.boss_active = True
        self.enemy_group.add(self.boss)
        return self.boss

    def on_boss_defeated(self):
        """Called when boss is defeated."""
        self.boss_active = False
        self.boss_defeated = True
        self.boss = None
        self.wave_count = 0
        self.wave_timer = 180
        # Game continues with harder waves or can end
        self.game_won = True
