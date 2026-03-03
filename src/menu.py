"""
Game Start Page - Santa Adventure Menu
"""
import pygame
import os
from src.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    WHITE, SNOW_WHITE,
    BACKGROUNDS_DIR, BGM_DIR,
    STATE_LEVEL1
)
from src.utils import draw_text, load_image, SnowfallSystem


def run_menu(screen, clock):
    """
    Display the start menu screen.
    Returns next game state string.
    """
    # Load background
    bg_path = os.path.join(BACKGROUNDS_DIR, "forest_bg.png")
    bg = load_image(bg_path, scale=(SCREEN_WIDTH, SCREEN_HEIGHT))

    # Dark overlay for readability
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120))

    # Snowfall effect
    snowfall = SnowfallSystem(count=100)

    # Button setup
    button_width = 280
    button_height = 60
    button_x = SCREEN_WIDTH // 2 - button_width // 2
    button_y = SCREEN_HEIGHT // 2 + 60
    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    button_color_normal = (180, 30, 30)
    button_color_hover = (220, 50, 50)
    button_border_color = (255, 215, 0)

    # Play BGM
    bgm_path = os.path.join(BGM_DIR, "menu_bgm.mp3")
    if os.path.exists(bgm_path):
        pygame.mixer.music.load(bgm_path)
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

    # Flush any events queued during startup (e.g. Enter key from terminal)
    pygame.event.clear()

    while True:
        dt = clock.tick(FPS) / 1000.0
        mouse_pos = pygame.mouse.get_pos()
        hover = button_rect.collidepoint(mouse_pos)

        for event in pygame.event.get():
            print(f"[DEBUG] Menu event: {event}")  # temporary debug
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    pygame.mixer.music.fadeout(500)
                    return STATE_LEVEL1
            if event.type == pygame.MOUSEBUTTONDOWN:
                if hover:
                    pygame.mixer.music.fadeout(500)
                    return STATE_LEVEL1

        # Update
        snowfall.update(dt)

        # Draw
        screen.blit(bg, (0, 0))
        screen.blit(overlay, (0, 0))
        snowfall.draw(screen)

        # Title
        draw_text(screen, "Santa Adventure", (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3),
                  size=72, color=(255, 215, 0), center=True)
        draw_text(screen, "The Frosty Forest Run", (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + 70),
                  size=28, color=SNOW_WHITE, center=True)

        # Button
        color = button_color_hover if hover else button_color_normal
        pygame.draw.rect(screen, color, button_rect, border_radius=10)
        pygame.draw.rect(screen, button_border_color, button_rect, 3, border_radius=10)
        draw_text(screen, "Start Game", button_rect.center, size=32, color=WHITE, center=True)

        # Hint
        draw_text(screen, "Press ENTER or click to start",
                  (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60),
                  size=18, color=(180, 180, 180), center=True)

        pygame.display.flip()
