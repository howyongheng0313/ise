"""
Public tools (Sprite sheet segmentation, collision detection, particles system)
"""
import pygame
import random
import math
from src.settings import SNOWFLAKE_COUNT, SCREEN_WIDTH, SCREEN_HEIGHT


# ========== Sprite Sheet Loading ==========

def load_spritesheet(path, frame_count, scale=None):
    """
    Load a horizontal sprite sheet and cut it into individual frames.

    Args:
        path: Full path to the sprite sheet image
        frame_count: Number of frames in the sheet
        scale: Optional (width, height) tuple to scale each frame

    Returns:
        List of pygame.Surface frames
    """
    sheet = pygame.image.load(path).convert_alpha()
    frame_width = sheet.get_width() // frame_count
    frame_height = sheet.get_height()

    frames = []
    for i in range(frame_count):
        frame = sheet.subsurface((i * frame_width, 0, frame_width, frame_height))
        if scale:
            frame = pygame.transform.scale(frame, scale)
        frames.append(frame)
    return frames


def load_image(path, scale=None):
    """
    Load a single image with optional scaling.

    Args:
        path: Full path to the image file
        scale: Optional (width, height) tuple to scale the image

    Returns:
        pygame.Surface
    """
    image = pygame.image.load(path).convert_alpha()
    if scale:
        image = pygame.transform.scale(image, scale)
    return image


# ========== Text Rendering ==========

def draw_text(surface, text, pos, size=32, color=(255, 255, 255), font_name=None, center=False):
    """
    Render text onto a surface.

    Args:
        surface: Target pygame.Surface
        text: String to render
        pos: (x, y) position
        size: Font size in pixels
        color: RGB tuple
        font_name: Font name (None = default)
        center: If True, pos is the center of the text
    """
    font = pygame.font.SysFont(font_name, size)
    text_surface = font.render(str(text), True, color)
    if center:
        rect = text_surface.get_rect(center=pos)
        surface.blit(text_surface, rect)
    else:
        surface.blit(text_surface, pos)


# ========== Animation Helper ==========

class Animator:
    """Handles frame-based animation cycling."""

    def __init__(self, frames, speed=0.15, loop=True):
        """
        Args:
            frames: List of pygame.Surface frames
            speed: Seconds per frame
            loop: Whether to loop the animation
        """
        self.frames = frames
        self.speed = speed
        self.loop = loop
        self.index = 0
        self.timer = 0
        self.finished = False

    def update(self, dt):
        """Advance animation by dt seconds."""
        if self.finished:
            return
        self.timer += dt
        if self.timer >= self.speed:
            self.timer -= self.speed
            self.index += 1
            if self.index >= len(self.frames):
                if self.loop:
                    self.index = 0
                else:
                    self.index = len(self.frames) - 1
                    self.finished = True

    def get_frame(self):
        """Return the current frame surface."""
        return self.frames[self.index]

    def reset(self):
        """Reset animation to the beginning."""
        self.index = 0
        self.timer = 0
        self.finished = False


# ========== Particle System ==========

class Particle:
    """A single particle with position, velocity, lifetime."""

    def __init__(self, x, y, vx, vy, lifetime, color, size):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.color = color
        self.size = size

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.lifetime -= dt

    def is_alive(self):
        return self.lifetime > 0

    def draw(self, surface, offset=(0, 0)):
        alpha = max(0, self.lifetime / self.max_lifetime)
        radius = max(1, int(self.size * alpha))
        pygame.draw.circle(surface, self.color,
                           (int(self.x + offset[0]), int(self.y + offset[1])), radius)


class ParticleEmitter:
    """Manages a collection of particles."""

    def __init__(self):
        self.particles = []

    def emit(self, x, y, count, color=(255, 255, 255),
             speed_range=(20, 80), lifetime_range=(0.3, 0.8), size_range=(2, 5)):
        """Emit particles in random directions."""
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(*speed_range)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            lifetime = random.uniform(*lifetime_range)
            size = random.uniform(*size_range)
            self.particles.append(Particle(x, y, vx, vy, lifetime, color, size))

    def update(self, dt):
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.is_alive()]

    def draw(self, surface, offset=(0, 0)):
        for p in self.particles:
            p.draw(surface, offset)


# ========== Snowfall System ==========

class Snowflake:
    """A single snowflake for the snowfall effect."""

    def __init__(self):
        self.reset(random_y=True)

    def reset(self, random_y=False):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(-SCREEN_HEIGHT, SCREEN_HEIGHT) if random_y else random.randint(-50, -10)
        self.size = random.uniform(1, 4)
        self.speed = random.uniform(30, 80)
        self.drift = random.uniform(-15, 15)
        self.sway_offset = random.uniform(0, math.pi * 2)
        self.sway_speed = random.uniform(0.5, 2.0)
        self.sway_amount = random.uniform(10, 30)

    def update(self, dt, time):
        self.y += self.speed * dt
        self.x += self.drift * dt + math.sin(time * self.sway_speed + self.sway_offset) * self.sway_amount * dt
        if self.y > SCREEN_HEIGHT + 10:
            self.reset()

    def draw(self, surface):
        alpha = min(255, int(200 + self.size * 15))
        pygame.draw.circle(surface, (alpha, alpha, alpha),
                           (int(self.x), int(self.y)), max(1, int(self.size)))


class SnowfallSystem:
    """Manages snowfall particle effect."""

    def __init__(self, count=None):
        self.count = count or SNOWFLAKE_COUNT
        self.snowflakes = [Snowflake() for _ in range(self.count)]
        self.time = 0

    def update(self, dt):
        self.time += dt
        for s in self.snowflakes:
            s.update(dt, self.time)

    def draw(self, surface):
        for s in self.snowflakes:
            s.draw(surface)


# ========== Screen Shake ==========

class ScreenShake:
    """Manages screen shake effect."""

    def __init__(self):
        self.duration = 0
        self.intensity = 0
        self.offset = (0, 0)

    def start(self, duration=0.3, intensity=8):
        self.duration = duration
        self.intensity = intensity

    def update(self, dt):
        if self.duration > 0:
            self.duration -= dt
            self.offset = (
                random.randint(-self.intensity, self.intensity),
                random.randint(-self.intensity, self.intensity)
            )
        else:
            self.offset = (0, 0)

    def get_offset(self):
        return self.offset
