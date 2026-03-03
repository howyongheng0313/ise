"""
Game Main Entrance - Santa Adventure
"""
import pygame
import sys
from src.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, GAME_TITLE,
    STATE_MENU, STATE_LEVEL1, STATE_LEVEL2, STATE_GAME_OVER, STATE_VICTORY
)
from src.menu import run_menu
from src.level1 import run_level1
from src.level2 import run_level2
from src.game_over import run_game_over


def main():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(GAME_TITLE)
    clock = pygame.time.Clock()

    state = STATE_MENU
    score = 0

    while True:
        if state == STATE_MENU:
            state = run_menu(screen, clock)
            score = 0

        elif state == STATE_LEVEL1:
            result = run_level1(screen, clock)
            state = result["next_state"]
            score = result.get("score", 0)

        elif state == STATE_LEVEL2:
            result = run_level2(screen, clock, score)
            state = result["next_state"]
            score = result.get("score", score)

        elif state in (STATE_GAME_OVER, STATE_VICTORY):
            state = run_game_over(screen, clock, score, victory=(state == STATE_VICTORY))
            score = 0

        else:
            break

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pygame.quit()
        sys.exit(0)
    except Exception as e:
        import traceback
        print(f"[ERROR] 游戏崩溃: {e}")
        traceback.print_exc()
        pygame.quit()
        sys.exit(1)
