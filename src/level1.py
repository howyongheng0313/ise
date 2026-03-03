"""
Level 1: Cross Snow Forest - The Frosty Forest Run
"""
import pygame
import os
import random
import math
from src.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, WHITE, RED,
    SPRITES_DIR, ITEMS_DIR, BACKGROUNDS_DIR, UI_DIR, BGM_DIR, SFX_DIR,
    SANTA_HP, LEVEL1_DURATION, KILL_SCORE,
    SANTA_SPEED, MAGIC_BALL_SPEED, SNOWBALL_SPEED,
    BG_SCROLL_SPEED, WILDMAN_SPEED,
    WILDMAN_SPAWN_INTERVAL, WILDMAN_SPAWN_MIN,
    ROAD_LEFT, ROAD_RIGHT,
    ANIMATION_SPEED, SCREEN_SHAKE_DURATION, SCREEN_SHAKE_INTENSITY,
    SPRITESHEET_CONFIG,
    STATE_LEVEL2, STATE_GAME_OVER
)
from src.utils import (
    load_spritesheet, load_image, draw_text,
    Animator, ParticleEmitter, SnowfallSystem, ScreenShake
)


# ========== Santa Level 1 ==========

class Santa(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Load sprite sheets
        self.sprites = {}
        self._load_sprites()

        self.state = "idle"
        self.animator = Animator(self.sprites["fronts"], speed=ANIMATION_SPEED)
        self.image = self.animator.get_frame()
        self.rect = self.image.get_rect(center=(x, y))
        self.hp = SANTA_HP
        self.speed = SANTA_SPEED
        self.invincible_timer = 0
        self.attack_cooldown = 0
        self.is_dead = False
        self.death_finished = False

    def _load_sprites(self):
        scale = (80, 80)
        cfg = SPRITESHEET_CONFIG
        self.sprites["fronts"] = load_spritesheet(
            os.path.join(SPRITES_DIR, cfg["santa_fronts"][0]), cfg["santa_fronts"][1], scale)
        right_frames = load_spritesheet(
            os.path.join(SPRITES_DIR, cfg["santa_right"][0]), cfg["santa_right"][1], scale)
        self.sprites["right"] = right_frames
        self.sprites["left"] = [pygame.transform.flip(f, True, False) for f in right_frames]
        self.sprites["attack"] = load_spritesheet(
            os.path.join(SPRITES_DIR, cfg["santa_attack"][0]), cfg["santa_attack"][1], scale)
        self.sprites["hurt"] = load_spritesheet(
            os.path.join(SPRITES_DIR, cfg["santa_hurts"][0]), cfg["santa_hurts"][1], scale)
        self.sprites["dead"] = load_spritesheet(
            os.path.join(SPRITES_DIR, cfg["santa_dead"][0]), cfg["santa_dead"][1], (100, 80))

    def set_state(self, state):
        if state != self.state and not self.is_dead:
            self.state = state
            if state == "move_left":
                self.animator = Animator(self.sprites["left"], speed=ANIMATION_SPEED)
            elif state == "move_right":
                self.animator = Animator(self.sprites["right"], speed=ANIMATION_SPEED)
            elif state == "attack":
                self.animator = Animator(self.sprites["attack"], speed=0.1, loop=False)
            elif state == "hurt":
                self.animator = Animator(self.sprites["hurt"], speed=0.1, loop=False)
            elif state == "dead":
                self.animator = Animator(self.sprites["dead"], speed=0.2, loop=False)
                self.is_dead = True
            else:
                self.animator = Animator(self.sprites["fronts"], speed=ANIMATION_SPEED)

    def take_damage(self):
        if self.invincible_timer <= 0 and not self.is_dead:
            self.hp -= 1
            self.invincible_timer = 1.0
            if self.hp <= 0:
                self.set_state("dead")
            else:
                self.set_state("hurt")
            return True
        return False

    def update(self, dt, keys):
        if self.is_dead:
            self.animator.update(dt)
            self.image = self.animator.get_frame()
            if self.animator.finished:
                self.death_finished = True
            return

        self.invincible_timer = max(0, self.invincible_timer - dt)
        self.attack_cooldown = max(0, self.attack_cooldown - dt)

        # Movement
        moving = False
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
            if self.state not in ("attack", "hurt"):
                self.set_state("move_left")
            moving = True
        elif keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
            if self.state not in ("attack", "hurt"):
                self.set_state("move_right")
            moving = True

        if not moving and self.state not in ("attack", "hurt", "dead"):
            self.set_state("idle")

        # Clamp position to snow road
        self.rect.clamp_ip(pygame.Rect(ROAD_LEFT, 0, ROAD_RIGHT - ROAD_LEFT, SCREEN_HEIGHT))

        # Non-looping animations finished -> back to idle
        if self.state in ("attack", "hurt") and self.animator.finished:
            self.set_state("idle")

        self.animator.update(dt)
        self.image = self.animator.get_frame()

    def draw(self, surface, offset=(0, 0)):
        # Blink when invincible
        if self.invincible_timer > 0 and int(self.invincible_timer * 10) % 2 == 0:
            return
        pos = (self.rect.x + offset[0], self.rect.y + offset[1])
        surface.blit(self.image, pos)


# ========== Magic Ball (Santa's Projectile) ==========

class MagicBall(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = load_image(os.path.join(ITEMS_DIR, "santa_magic.png"), scale=(24, 24))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = MAGIC_BALL_SPEED

    def update(self, dt):
        self.rect.y -= self.speed

    def draw(self, surface, offset=(0, 0)):
        surface.blit(self.image, (self.rect.x + offset[0], self.rect.y + offset[1]))


# ========== Snowball (Wildman's Projectile) ==========

class SnowBall(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y):
        super().__init__()
        self.image = load_image(os.path.join(ITEMS_DIR, "wildmen_snow.png"), scale=(20, 20))
        self.rect = self.image.get_rect(center=(x, y))
        self.x = float(x)
        self.y = float(y)
        # Calculate direction toward target
        dx = target_x - x
        dy = target_y - y
        dist = max(1, math.sqrt(dx * dx + dy * dy))
        self.vx = (dx / dist) * SNOWBALL_SPEED
        self.vy = (dy / dist) * SNOWBALL_SPEED

    def update(self, dt):
        self.x += self.vx
        self.y += self.vy
        self.rect.center = (int(self.x), int(self.y))

    def draw(self, surface, offset=(0, 0)):
        surface.blit(self.image, (self.rect.x + offset[0], self.rect.y + offset[1]))


# ========== Wildman (Level 1 Enemy) ==========

class Wildman(pygame.sprite.Sprite):
    SAFE_ZONE_Y = 150  # wildmen won't spawn within this distance of Santa's Y

    def __init__(self, side, santa_y):
        """side: 'left' or 'right' - which side of screen to spawn from."""
        super().__init__()
        self._load_sprites()

        self.side = side

        # Right-side wildmen: flip all sprite frames horizontally
        if side == "right":
            for key in self.sprites:
                self.sprites[key] = [pygame.transform.flip(f, True, False) for f in self.sprites[key]]

        self.state = "run"
        self.animator = Animator(self.sprites["run"], speed=ANIMATION_SPEED)
        self.image = self.animator.get_frame()

        # Spawn position: off-screen on the chosen side
        if side == "left":
            start_x = -50
        else:
            start_x = SCREEN_WIDTH + 50

        # Target: left-side wildmen stay in left half, right-side in right half
        road_mid = (ROAD_LEFT + ROAD_RIGHT) // 2
        if side == "left":
            self.target_x = random.randint(ROAD_LEFT + 20, road_mid)
        else:
            self.target_x = random.randint(road_mid, ROAD_RIGHT - 20)

        # Spawn Y: avoid Santa's Y ± SAFE_ZONE_Y
        min_y, max_y = 80, SCREEN_HEIGHT * 2 // 3
        safe_lo = santa_y - self.SAFE_ZONE_Y
        safe_hi = santa_y + self.SAFE_ZONE_Y
        # Build list of valid ranges
        valid_ranges = []
        if min_y < safe_lo:
            valid_ranges.append((min_y, int(safe_lo)))
        if safe_hi < max_y:
            valid_ranges.append((int(safe_hi), max_y))
        if valid_ranges:
            chosen = random.choice(valid_ranges)
            start_y = random.randint(chosen[0], chosen[1])
        else:
            start_y = min_y  # fallback: spawn at top

        self.rect = self.image.get_rect(center=(start_x, start_y))
        self.x = float(self.rect.centerx)
        self.y = float(self.rect.centery)
        self.speed = WILDMAN_SPEED
        self.is_dead = False
        self.death_finished = False

        # State timers
        self.idle_timer = 0
        self.throw_count = 0
        self.max_throws = random.randint(3, 5)  # Remove after several throws
        self.lifetime = 0

    def _load_sprites(self):
        scale = (70, 70)
        cfg = SPRITESHEET_CONFIG
        self.sprites = {}
        self.sprites["run"] = load_spritesheet(
            os.path.join(SPRITES_DIR, cfg["wildman_run"][0]), cfg["wildman_run"][1], scale)
        self.sprites["attack"] = load_spritesheet(
            os.path.join(SPRITES_DIR, cfg["wildman_attack"][0]), cfg["wildman_attack"][1], scale)
        self.sprites["dead"] = load_spritesheet(
            os.path.join(SPRITES_DIR, cfg["wildman_dead"][0]), cfg["wildman_dead"][1], scale)

    def set_state(self, new_state):
        if new_state != self.state:
            self.state = new_state
            if new_state == "run":
                self.animator = Animator(self.sprites["run"], speed=ANIMATION_SPEED)
            elif new_state == "idle":
                # Use first frame of run as idle (standing still, facing forward)
                self.animator = Animator(self.sprites["run"][:1], speed=1.0)
            elif new_state == "attack":
                self.animator = Animator(self.sprites["attack"], speed=0.15, loop=False)
            elif new_state == "dead":
                self.animator = Animator(self.sprites["dead"], speed=0.15, loop=False)
                self.is_dead = True

    def die(self):
        self.set_state("dead")

    def update(self, dt, santa_rect):
        self.animator.update(dt)
        self.image = self.animator.get_frame()
        self.lifetime += dt

        if self.is_dead:
            # Dead wildmen also drift downward with background
            self.y += BG_SCROLL_SPEED
            self.rect.center = (int(self.x), int(self.y))
            if self.animator.finished:
                self.death_finished = True
            return None

        if self.state == "run":
            # Move horizontally toward target_x (no vertical drift)
            dx = self.target_x - self.x
            if abs(dx) > 5:
                self.x += self.speed if dx > 0 else -self.speed
                self.rect.center = (int(self.x), int(self.y))
            else:
                # Reached target — stop and enter idle
                self.x = self.target_x
                self.rect.center = (int(self.x), int(self.y))
                self.set_state("idle")
                self.idle_timer = random.uniform(0.3, 0.8)  # Brief pause before first attack

        elif self.state == "idle":
            # Drift downward with background scroll
            self.y += BG_SCROLL_SPEED
            self.rect.center = (int(self.x), int(self.y))
            self.idle_timer -= dt
            # Only attack if outside Santa's Y safe zone
            in_safe_zone = abs(self.y - santa_rect.centery) < self.SAFE_ZONE_Y
            if self.idle_timer <= 0 and not in_safe_zone:
                # Start attack
                self.set_state("attack")
                return "throw"  # Signal to create snowball

        elif self.state == "attack":
            # Drift downward with background scroll
            self.y += BG_SCROLL_SPEED
            self.rect.center = (int(self.x), int(self.y))
            if self.animator.finished:
                self.throw_count += 1
                if self.throw_count >= self.max_throws:
                    # Done throwing — remove this wildman
                    self.death_finished = True
                    return None
                # Only continue attacking if outside safe zone
                if abs(self.y - santa_rect.centery) < self.SAFE_ZONE_Y:
                    self.death_finished = True
                    return None
                # Enter cooldown idle before next throw
                self.set_state("idle")
                self.idle_timer = random.uniform(1.5, 3.0)

        # Safety removal: if alive too long
        if self.lifetime > 20:
            self.death_finished = True

        return None

    def draw(self, surface, offset=(0, 0)):
        surface.blit(self.image, (self.rect.x + offset[0], self.rect.y + offset[1]))


# ========== HUD ==========

class HUD:
    def __init__(self):
        self.heart_full = load_image(os.path.join(UI_DIR, "heart_full.png"), scale=(32, 32))
        self.heart_empty = load_image(os.path.join(UI_DIR, "heart_empty.png"), scale=(32, 32))
        self.kill_icon = load_image(os.path.join(UI_DIR, "kill_icon.png"), scale=(32, 32))

    def draw(self, surface, hp, max_hp, kills, time_left):
        # HP hearts
        for i in range(max_hp):
            x = 10 + i * 36
            y = 10
            if i < hp:
                surface.blit(self.heart_full, (x, y))
            else:
                surface.blit(self.heart_empty, (x, y))

        # Kill count
        surface.blit(self.kill_icon, (SCREEN_WIDTH - 120, 10))
        draw_text(surface, str(kills), (SCREEN_WIDTH - 82, 12), size=28, color=WHITE)

        # Timer
        minutes = int(time_left) // 60
        seconds = int(time_left) % 60
        draw_text(surface, f"{minutes}:{seconds:02d}",
                  (SCREEN_WIDTH // 2, 12), size=28, color=WHITE, center=True)


# ========== Level 1 Main Loop ==========

def run_level1(screen, clock):
    """
    Run Level 1: The Frosty Forest Run.

    Returns:
        dict with 'next_state' and 'score'
    """
    # Load background (already 1280x720)
    bg = load_image(os.path.join(BACKGROUNDS_DIR, "forest_bg.png"))
    bg_height = bg.get_height()
    bg_y = 0.0

    # Load city gate (already 1280x720)
    city_gate = load_image(os.path.join(BACKGROUNDS_DIR, "city_gate.png"))

    # Create Santa
    santa = Santa((ROAD_LEFT + ROAD_RIGHT) // 2, SCREEN_HEIGHT - 100)

    # Systems
    snowfall = SnowfallSystem(count=80)
    particle_emitter = ParticleEmitter()
    screen_shake = ScreenShake()
    hud = HUD()

    # Sprite groups
    wildmen = []
    magic_balls = []
    snowballs = []

    # Game state
    score = 0
    kills = 0
    time_elapsed = 0
    spawn_timer = 0
    current_spawn_interval = WILDMAN_SPAWN_INTERVAL
    level_complete = False
    game_over = False
    game_over_delay = 2.0

    # Background scroll phases: "scrolling" -> "gate_entering" -> "gate_reached"
    bg_phase = "scrolling"
    gate_scroll = 0.0  # how far the gate has scrolled in from top (0 to SCREEN_HEIGHT)
    GATE_STOP_Y = int(SCREEN_HEIGHT * 0.35)  # y position where Santa stops at gate

    # Audio
    bgm_path = os.path.join(BGM_DIR, "level1_bgm.mp3")
    if os.path.exists(bgm_path):
        pygame.mixer.music.load(bgm_path)
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play(-1)

    # Sound effects
    sfx = {}
    shoot_path = os.path.join(SFX_DIR, "magic_shoot.wav")
    hurt_path = os.path.join(SFX_DIR, "santa_hurt.wav")
    if os.path.exists(shoot_path):
        sfx["shoot"] = pygame.mixer.Sound(shoot_path)
        sfx["shoot"].set_volume(0.3)
    if os.path.exists(hurt_path):
        sfx["hurt"] = pygame.mixer.Sound(hurt_path)
        sfx["hurt"].set_volume(0.4)

    class _EmptyKeys:
        """Proxy that returns 0 for any key index, compatible with pygame key constants."""
        def __getitem__(self, key): return 0
    _empty_keys = _EmptyKeys()

    while True:
        dt = clock.tick(FPS) / 1000.0
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.mixer.music.fadeout(500)
                    return {"next_state": STATE_GAME_OVER, "score": score}
                if event.key == pygame.K_w and not santa.is_dead and santa.attack_cooldown <= 0 and bg_phase not in ("gate_entering", "gate_reached"):
                    # Fire magic ball
                    santa.set_state("attack")
                    santa.attack_cooldown = 0.3
                    ball = MagicBall(santa.rect.centerx, santa.rect.top)
                    magic_balls.append(ball)
                    if "shoot" in sfx:
                        sfx["shoot"].play()

        if game_over or level_complete:
            game_over_delay -= dt
            if game_over_delay <= 0:
                pygame.mixer.music.fadeout(500)
                if level_complete:
                    return {"next_state": STATE_LEVEL2, "score": score}
                else:
                    return {"next_state": STATE_GAME_OVER, "score": score}

        # Update time
        time_elapsed += dt
        time_left = max(0, LEVEL1_DURATION - time_elapsed)

        # Difficulty ramp
        progress = time_elapsed / LEVEL1_DURATION
        current_spawn_interval = max(WILDMAN_SPAWN_MIN,
                                     WILDMAN_SPAWN_INTERVAL - progress * (WILDMAN_SPAWN_INTERVAL - WILDMAN_SPAWN_MIN))

        # Spawn wildmen (only during normal scrolling phase)
        if bg_phase == "scrolling" and not santa.is_dead:
            spawn_timer += dt
            if spawn_timer >= current_spawn_interval:
                spawn_timer = 0
                side = random.choice(["left", "right"])
                wildmen.append(Wildman(side, santa.rect.centery))

        # --- Background phase transitions ---
        if bg_phase == "scrolling":
            # Normal looping scroll
            bg_y += BG_SCROLL_SPEED
            if bg_y >= bg_height * 2:
                bg_y -= bg_height * 2
            # Transition to gate_entering when time runs out
            if time_left <= 0 and not santa.is_dead:
                bg_phase = "gate_entering"
                gate_scroll = 0.0

        elif bg_phase == "gate_entering":
            # Both forest and gate scroll; gate slides in from top
            bg_y += BG_SCROLL_SPEED
            gate_scroll += BG_SCROLL_SPEED
            # Once gate fully covers the screen, stop scrolling
            if gate_scroll >= SCREEN_HEIGHT:
                gate_scroll = SCREEN_HEIGHT
                bg_phase = "gate_reached"

        elif bg_phase == "gate_reached":
            # Background is static (city_gate only), Santa walks to gate
            if not santa.is_dead and not level_complete:
                santa.rect.y -= santa.speed * 0.5
                santa.rect.clamp_ip(pygame.Rect(ROAD_LEFT, 0, ROAD_RIGHT - ROAD_LEFT, SCREEN_HEIGHT))
                if santa.rect.centery <= GATE_STOP_Y:
                    santa.rect.centery = GATE_STOP_Y
                    level_complete = True

        # Update santa (disable player input during gate_reached phase)
        if bg_phase == "gate_reached":
            santa.update(dt, _empty_keys)
        else:
            santa.update(dt, keys)
        if santa.death_finished and not game_over:
            game_over = True

        # Update magic balls
        for ball in magic_balls[:]:
            ball.update(dt)
            if ball.rect.bottom < 0:
                magic_balls.remove(ball)

        # Update snowballs
        for sb in snowballs[:]:
            sb.update(dt)
            if (sb.rect.top > SCREEN_HEIGHT or sb.rect.bottom < 0 or
                    sb.rect.left > SCREEN_WIDTH or sb.rect.right < 0):
                snowballs.remove(sb)

        # Update wildmen
        for wm in wildmen[:]:
            result = wm.update(dt, santa.rect)
            if result == "throw":
                sb = SnowBall(wm.rect.centerx, wm.rect.centery,
                              santa.rect.centerx, santa.rect.centery)
                snowballs.append(sb)
            if wm.death_finished:
                wildmen.remove(wm)
            elif wm.rect.top > SCREEN_HEIGHT + 100:
                wildmen.remove(wm)

        # Collision: magic balls vs wildmen
        for ball in magic_balls[:]:
            for wm in wildmen[:]:
                if not wm.is_dead and ball.rect.colliderect(wm.rect):
                    wm.die()
                    magic_balls.remove(ball)
                    kills += 1
                    score += KILL_SCORE
                    particle_emitter.emit(wm.rect.centerx, wm.rect.centery, 12,
                                          color=(200, 200, 255), speed_range=(30, 100))
                    break

        # Collision: snowballs vs santa
        if not santa.is_dead:
            for sb in snowballs[:]:
                if sb.rect.colliderect(santa.rect):
                    if santa.take_damage():
                        snowballs.remove(sb)
                        screen_shake.start(SCREEN_SHAKE_DURATION, SCREEN_SHAKE_INTENSITY)
                        particle_emitter.emit(santa.rect.centerx, santa.rect.centery, 8,
                                              color=(255, 255, 255), speed_range=(40, 120))
                        if "hurt" in sfx:
                            sfx["hurt"].play()
                    break

        # Update effects
        snowfall.update(dt)
        particle_emitter.update(dt)
        screen_shake.update(dt)
        shake_offset = screen_shake.get_offset()

        # ===== Draw =====
        # Background
        if bg_phase == "scrolling":
            # Normal tiling forest loop
            scroll_offset = int(bg_y) % bg_height
            start_y = scroll_offset - bg_height
            for i in range(3):
                y = start_y + i * bg_height
                screen.blit(bg, (shake_offset[0], y + shake_offset[1]))

        elif bg_phase == "gate_entering":
            # Forest scrolls down, city_gate slides in from top
            # Draw forest (still scrolling)
            scroll_offset = int(bg_y) % bg_height
            start_y = scroll_offset - bg_height
            for i in range(3):
                y = start_y + i * bg_height
                screen.blit(bg, (shake_offset[0], y + shake_offset[1]))
            # Draw city_gate sliding in from top
            gate_draw_y = (gate_scroll) - SCREEN_HEIGHT
            screen.blit(city_gate, (shake_offset[0], gate_draw_y + shake_offset[1]))

        elif bg_phase == "gate_reached":
            # Only city_gate, static
            screen.blit(city_gate, (shake_offset[0], shake_offset[1]))

        # Wildmen
        for wm in wildmen:
            wm.draw(screen, shake_offset)

        # Santa
        santa.draw(screen, shake_offset)

        # Magic balls
        for ball in magic_balls:
            ball.draw(screen, shake_offset)

        # Snowballs (with trail effect)
        for sb in snowballs:
            # Trail dots
            for i in range(3):
                trail_x = int(sb.x - sb.vx * i * 3 + shake_offset[0])
                trail_y = int(sb.y - sb.vy * i * 3 + shake_offset[1])
                radius = max(1, 4 - i)
                pygame.draw.circle(screen, (200, 200, 220), (trail_x, trail_y), radius)
            sb.draw(screen, shake_offset)

        # Snowfall (always on top of game objects, below HUD)
        snowfall.draw(screen)

        # Particles
        particle_emitter.draw(screen, shake_offset)

        # HUD (no shake offset - stays stable)
        hud.draw(screen, santa.hp, SANTA_HP, kills, time_left)

        # Score
        draw_text(screen, f"Score: {score}", (SCREEN_WIDTH // 2, 45),
                  size=22, color=(255, 215, 0), center=True)

        # Game over / level complete overlay
        if game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))
            screen.blit(overlay, (0, 0))
            draw_text(screen, "GAME OVER", (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
                      size=64, color=RED, center=True)
        elif level_complete:
            draw_text(screen, "LEVEL COMPLETE!", (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
                      size=64, color=(255, 215, 0), center=True)

        pygame.display.flip()
