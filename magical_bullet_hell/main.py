"""
✦ Magical Star Burst ✦
A Touhou-style Bullet Hell game with Magical Girl theme.

Controls:
  WASD  - Move
  J     - Shoot
  K     - Spell Card (Bomb)
  Shift - Focus mode
  Esc   - Pause
"""
import sys
import os

# Add project root to path and set CWD
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
os.chdir(project_root)

from core.game import Game


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
