"""
Game Over / Victory Screen
"""
import pygame
import os
import random
import math
from src.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    WHITE, RED,
    BGM_DIR, SFX_DIR,
    STATE_MENU
)
from src.utils import draw_text, ParticleEmitter, SnowfallSystem


def run_game_over(screen, clock, score, victory=False):
    """
    Display Game Over or Victory screen.

    Args:
        screen: Pygame display surface
        clock: Pygame clock
        score: Final score to display
        victory: True = victory screen, False = game over screen

    Returns:
        Next game state string
    """
    # Particles
    particles = ParticleEmitter()
    snowfall = SnowfallSystem(count=60)
    firework_timer = 0

    # Buttons
    button_width = 200
    button_height = 50
    button_gap = 30
    total_width = button_width * 2 + button_gap
    start_x = SCREEN_WIDTH // 2 - total_width // 2

    retry_rect = pygame.Rect(start_x, SCREEN_HEIGHT // 2 + 100, button_width, button_height)
    quit_rect = pygame.Rect(start_x + button_width + button_gap,
                            SCREEN_HEIGHT // 2 + 100, button_width, button_height)

    button_color_normal = (180, 30, 30)
    button_color_hover = (220, 50, 50)
    quit_color_normal = (80, 80, 80)
    quit_color_hover = (120, 120, 120)
    border_color = (255, 215, 0)

    # Audio
    if victory:
        sfx_path = os.path.join(SFX_DIR, "level_clear.wav")
    else:
        sfx_path = os.path.join(SFX_DIR, "game_over.wav")

    pygame.mixer.music.stop()
    if os.path.exists(sfx_path):
        sfx = pygame.mixer.Sound(sfx_path)
        sfx.set_volume(0.5)
        sfx.play()

    while True:
        dt = clock.tick(FPS) / 1000.0
        mouse_pos = pygame.mouse.get_pos()
        retry_hover = retry_rect.collidepoint(mouse_pos)
        quit_hover = quit_rect.collidepoint(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return STATE_MENU
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    raise SystemExit
            if event.type == pygame.MOUSEBUTTONDOWN:
                if retry_hover:
                    return STATE_MENU
                if quit_hover:
                    pygame.quit()
                    raise SystemExit

        # Update
        snowfall.update(dt)
        particles.update(dt)

        # Victory fireworks
        if victory:
            firework_timer += dt
            if firework_timer >= 0.4:
                firework_timer = 0
                fx = random.randint(100, SCREEN_WIDTH - 100)
                fy = random.randint(80, SCREEN_HEIGHT // 2)
                color = random.choice([
                    (255, 50, 50), (50, 255, 50), (255, 215, 0),
                    (50, 150, 255), (255, 100, 200), (255, 165, 0)
                ])
                particles.emit(fx, fy, 25, color=color,
                                speed_range=(60, 180), lifetime_range=(0.5, 1.2), size_range=(2, 5))

        # Draw
        screen.fill((10, 10, 30))
        snowfall.draw(screen)
        particles.draw(screen)

        if victory:
            # Victory text
            draw_text(screen, "VICTORY!", (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 - 30),
                      size=72, color=(255, 215, 0), center=True)
            draw_text(screen, "Merry Christmas!", (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + 50),
                      size=32, color=(200, 230, 255), center=True)
        else:
            # Game Over text
            draw_text(screen, "GAME OVER", (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 - 30),
                      size=72, color=RED, center=True)
            draw_text(screen, "Better luck next time!", (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + 50),
                      size=28, color=(180, 180, 180), center=True)

        # Score
        draw_text(screen, f"Total Score: {score}", (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30),
                  size=40, color=WHITE, center=True)

        # Retry button
        color = button_color_hover if retry_hover else button_color_normal
        pygame.draw.rect(screen, color, retry_rect, border_radius=8)
        pygame.draw.rect(screen, border_color, retry_rect, 2, border_radius=8)
        draw_text(screen, "Retry", retry_rect.center, size=28, color=WHITE, center=True)

        # Quit button
        color = quit_color_hover if quit_hover else quit_color_normal
        pygame.draw.rect(screen, color, quit_rect, border_radius=8)
        pygame.draw.rect(screen, border_color, quit_rect, 2, border_radius=8)
        draw_text(screen, "Quit", quit_rect.center, size=28, color=WHITE, center=True)

        # Hint
        draw_text(screen, "Press ENTER to retry or ESC to quit",
                  (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40),
                  size=16, color=(120, 120, 120), center=True)

        pygame.display.flip()
