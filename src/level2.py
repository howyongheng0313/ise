"""
Level 2: Present Delivery Mission — Maze Escape
"""
import pygame
import random
import math
import os
from collections import deque

from src.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    SPRITES_DIR, ITEMS_DIR, BACKGROUNDS_DIR, UI_DIR, BGM_DIR, SFX_DIR,
    STATE_GAME_OVER, STATE_VICTORY,
    LEVEL2_TIMER, TIME_BONUS, HUNTER_PATHFIND_INTERVAL, ANIMATION_SPEED,
    MAZE_GRID, MAZE_COLS, MAZE_ROWS, MAZE_TILE_SIZE,
    SPRITESHEET_CONFIG,
    SANTA_MAZE_SPEED, HUNTER_SPEED_PPS,
    SANTA_DISPLAY, HUNTER_DISPLAY, TREE_DISPLAY, HOURGLASS_DISPLAY,
    SANTA_HITBOX, HUNTER_COUNT, HUNTER_ATTACK_RANGE, HOURGLASS_COUNT,
    HUNTER_KILL_SCORE, ATTACK_RANGE, ATTACK_COOLDOWN,
)
from src.utils import load_spritesheet, load_image, draw_text, Animator, ParticleEmitter

TILE = MAZE_TILE_SIZE

_SAFE_CELLS = None


def _compute_safe_cells():
    """Compute safe cells lazily on first call."""
    global _SAFE_CELLS
    if _SAFE_CELLS is not None:
        return
    _SAFE_CELLS = set()
    for r in range(MAZE_ROWS):
        for c in range(MAZE_COLS):
            if all(
                0 <= c + dc < MAZE_COLS and 0 <= r + dr < MAZE_ROWS
                and MAZE_GRID[r + dr][c + dc] == 0
                for dc in (-1, 0, 1) for dr in (-1, 0, 1)
            ):
                _SAFE_CELLS.add((c, r))


# ========== Grid Helpers ==========

def is_wall(col, row):
    if col < 0 or col >= MAZE_COLS or row < 0 or row >= MAZE_ROWS:
        return True
    return MAZE_GRID[row][col] == 1


def pixel_to_cell(px, py):
    return int(px) // TILE, int(py) // TILE


def cell_center(col, row):
    return col * TILE + TILE // 2, row * TILE + TILE // 2


def all_path_cells():
    """Return safe cells (enough clearance for entity hitboxes)."""
    _compute_safe_cells()
    return sorted(_SAFE_CELLS)


# ========== BFS Pathfinding ==========

def _simplify_path(path):
    """Collapse straight-line runs into just the turning points + destination.

    Keeps movement axis-aligned so the hitbox never clips walls diagonally.
    """
    if len(path) <= 2:
        return path
    result = [path[0]]
    for i in range(1, len(path) - 1):
        d1 = (path[i][0] - path[i - 1][0], path[i][1] - path[i - 1][1])
        d2 = (path[i + 1][0] - path[i][0], path[i + 1][1] - path[i][1])
        if d1 != d2:
            result.append(path[i])
    result.append(path[-1])
    return result


def bfs(sc, sr, gc, gr):
    """BFS shortest path using parent tracking (memory-efficient).

    Returns simplified list of (col, row) waypoints excluding start.
    """
    if sc == gc and sr == gr:
        return []
    parent = {(sc, sr): None}
    queue = deque([(sc, sr)])
    while queue:
        col, row = queue.popleft()
        for dc, dr in ((0, -1), (0, 1), (-1, 0), (1, 0)):
            nc, nr = col + dc, row + dr
            if (nc, nr) not in parent and (nc, nr) in _SAFE_CELLS:
                parent[(nc, nr)] = (col, row)
                if nc == gc and nr == gr:
                    path = []
                    cur = (gc, gr)
                    while cur != (sc, sr):
                        path.append(cur)
                        cur = parent[cur]
                    path.reverse()
                    return _simplify_path(path)
                queue.append((nc, nr))
    return []


# ========== Santa ==========

class Santa:
    def __init__(self, x, y, sprites):
        self.x = float(x)
        self.y = float(y)
        self.sprites = sprites  # {'down': Animator, 'right': Animator, 'up': Animator}
        self.direction = 'down'
        self.last_horizontal = 'right'
        self.charges = 0            # gift charges collected from hourglasses
        self.attack_cooldown = 0.0  # seconds until next attack allowed

    @property
    def rect(self):
        h = SANTA_HITBOX
        return pygame.Rect(int(self.x) - h, int(self.y) - h, h * 2, h * 2)

    def _passable(self, nx, ny):
        h = SANTA_HITBOX - 1
        for px, py in ((nx - h, ny - h), (nx + h, ny - h),
                       (nx - h, ny + h), (nx + h, ny + h)):
            if is_wall(int(px) // TILE, int(py) // TILE):
                return False
        return True

    def update(self, dt, keys):
        dx = dy = 0
        if keys[pygame.K_LEFT]:
            dx = -SANTA_MAZE_SPEED
            self.direction = 'left'
            self.last_horizontal = 'left'
        elif keys[pygame.K_RIGHT]:
            dx = SANTA_MAZE_SPEED
            self.direction = 'right'
            self.last_horizontal = 'right'
        elif keys[pygame.K_UP]:
            dy = -SANTA_MAZE_SPEED
            self.direction = 'up'
        elif keys[pygame.K_DOWN]:
            dy = SANTA_MAZE_SPEED
            self.direction = 'down'

        moving = bool(dx or dy)
        self.attack_cooldown = max(0.0, self.attack_cooldown - dt)

        if dx:
            nx = self.x + dx * dt
            if self._passable(nx, self.y):
                self.x = nx
        if dy:
            ny = self.y + dy * dt
            if self._passable(self.x, ny):
                self.y = ny

        anim_key = 'right' if self.direction in ('left', 'right') else self.direction
        if moving:
            self.sprites[anim_key].update(dt)
        else:
            # Freeze on frame 0 when standing still
            self.sprites[anim_key].index = 0
            self.sprites[anim_key].timer = 0

    def draw(self, surface):
        anim_key = 'right' if self.direction in ('left', 'right') else self.direction
        frame = self.sprites[anim_key].get_frame()
        if self.direction == 'left':
            frame = pygame.transform.flip(frame, True, False)
        elif self.direction in ('up', 'down') and self.last_horizontal == 'left':
            frame = pygame.transform.flip(frame, True, False)
        surface.blit(frame, frame.get_rect(center=(int(self.x), int(self.y))))


# ========== Hunter ==========

class Hunter:
    def __init__(self, x, y, walk_frames, attack_frames):
        self.x = float(x)
        self.y = float(y)
        self.walk_anim = Animator(walk_frames, ANIMATION_SPEED)
        self.attack_anim = Animator(attack_frames, ANIMATION_SPEED)
        self.attacking = False
        self.path = []
        self.path_timer = 0.0
        self.facing_left = False

    @property
    def rect(self):
        h = SANTA_HITBOX  # same hitbox size as santa for fair collision
        return pygame.Rect(int(self.x) - h, int(self.y) - h, h * 2, h * 2)

    @staticmethod
    def _passable(nx, ny):
        h = SANTA_HITBOX - 1
        for px, py in ((nx - h, ny - h), (nx + h, ny - h),
                       (nx - h, ny + h), (nx + h, ny + h)):
            if is_wall(int(px) // TILE, int(py) // TILE):
                return False
        return True

    def update(self, dt, santa_x, santa_y):
        self.path_timer -= dt
        if self.path_timer <= 0:
            sc, sr = pixel_to_cell(santa_x, santa_y)
            hc, hr = pixel_to_cell(self.x, self.y)
            new_path = bfs(hc, hr, sc, sr)
            # Skip leading waypoints that are behind / very close to us
            while new_path:
                wc, wr = new_path[0]
                wx, wy = cell_center(wc, wr)
                if math.hypot(wx - self.x, wy - self.y) < TILE * 0.5:
                    new_path.pop(0)
                else:
                    break
            if new_path:
                self.path = new_path
            self.path_timer = HUNTER_PATHFIND_INTERVAL

        if self.path:
            tc, tr = self.path[0]
            tx, ty = cell_center(tc, tr)
            dx, dy = tx - self.x, ty - self.y
            dist = math.hypot(dx, dy)
            step = HUNTER_SPEED_PPS * dt
            if dist <= step:
                if self._passable(tx, ty):
                    self.x, self.y = float(tx), float(ty)
                    if abs(dx) > abs(dy):
                        self.facing_left = dx < 0
                self.path.pop(0)
            else:
                nx = self.x + dx / dist * step
                ny = self.y + dy / dist * step
                if self._passable(nx, ny):
                    self.x = nx
                    self.y = ny
                elif self._passable(nx, self.y):
                    self.x = nx
                elif self._passable(self.x, ny):
                    self.y = ny
                else:
                    self.path = []
                    self.path_timer = 0.0
                if abs(dx) > abs(dy):
                    self.facing_left = dx < 0

        self.attacking = math.hypot(santa_x - self.x, santa_y - self.y) < HUNTER_ATTACK_RANGE
        if self.attacking:
            self.attack_anim.update(dt)
        else:
            self.attack_anim.reset()
            self.walk_anim.update(dt)

    def draw(self, surface):
        frame = self.attack_anim.get_frame() if self.attacking else self.walk_anim.get_frame()
        if self.facing_left:
            frame = pygame.transform.flip(frame, True, False)
        surface.blit(frame, frame.get_rect(center=(int(self.x), int(self.y))))


# ========== Hourglass ==========

class Hourglass:
    def __init__(self, x, y, image):
        self.x = float(x)
        self.base_y = float(y)
        self.y = float(y)
        self.image = image
        self.phase = random.uniform(0, math.pi * 2)
        self.collected = False

    @property
    def rect(self):
        hw, hh = HOURGLASS_DISPLAY[0] // 2, HOURGLASS_DISPLAY[1] // 2
        return pygame.Rect(self.x - hw, self.y - hh, HOURGLASS_DISPLAY[0], HOURGLASS_DISPLAY[1])

    def update(self, dt):
        self.phase += dt * 3.0
        self.y = self.base_y + math.sin(self.phase) * 3

    def draw(self, surface):
        # Glow
        glow_r = int(HOURGLASS_DISPLAY[0] + math.sin(self.phase) * 2)
        glow = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 220, 80, 55), (glow_r, glow_r), glow_r)
        surface.blit(glow, (int(self.x) - glow_r, int(self.y) - glow_r))
        # Sprite
        surface.blit(self.image, self.image.get_rect(center=(int(self.x), int(self.y))))


# ========== Main Level Runner ==========

def run_level2(screen, clock, score=0):

    # ---- Load sprites via SPRITESHEET_CONFIG ----
    cfg = SPRITESHEET_CONFIG
    santa_sprites = {
        'down':  Animator(load_spritesheet(os.path.join(SPRITES_DIR, cfg["santa_floating"][0]), cfg["santa_floating"][1], SANTA_DISPLAY), ANIMATION_SPEED),
        'right': Animator(load_spritesheet(os.path.join(SPRITES_DIR, cfg["santa_right"][0]),    cfg["santa_right"][1],    SANTA_DISPLAY), ANIMATION_SPEED),
        'up':    Animator(load_spritesheet(os.path.join(SPRITES_DIR, cfg["santa_floating"][0]), cfg["santa_floating"][1], SANTA_DISPLAY), ANIMATION_SPEED),
    }
    hunter_walk_frames = load_spritesheet(os.path.join(SPRITES_DIR, cfg["hunter_walk"][0]), cfg["hunter_walk"][1], HUNTER_DISPLAY)
    hunter_attack_frames = load_spritesheet(os.path.join(SPRITES_DIR, cfg["hunter_attack"][0]), cfg["hunter_attack"][1], HUNTER_DISPLAY)

    maze_bg   = load_image(os.path.join(BACKGROUNDS_DIR, 'maze_bg.png'))
    tree_img  = load_image(os.path.join(ITEMS_DIR, 'christmass_tree.png'), TREE_DISPLAY)
    hg_img    = load_image(os.path.join(ITEMS_DIR, 'santa_hourglass.png'), HOURGLASS_DISPLAY)
    kill_icon = load_image(os.path.join(UI_DIR, 'kill_icon.png'), (28, 28))

    # ---- Place entities on valid path cells ----
    paths = all_path_cells()

    # Santa start: top-left quadrant — paths already filtered to safe cells only
    start_cell = next(
        (c for c in paths
         if c[0] < MAZE_COLS // 4 and c[1] < MAZE_ROWS // 4),
        paths[0]  # fallback: first safe cell
    )
    sx, sy = cell_center(*start_cell)
    santa = Santa(sx, sy, santa_sprites)

    # Christmas tree: bottom-right quadrant — paths already filtered to safe cells
    end_candidates = [(c, r) for c, r in paths
                      if c > MAZE_COLS * 3 // 4 and r > MAZE_ROWS * 3 // 4]
    tree_cell = random.choice(end_candidates) if end_candidates else paths[-1]
    tree_x, tree_y = cell_center(*tree_cell)

    # Hunters: far from Santa start
    hunter_pool = [(c, r) for c, r in paths
                   if math.hypot(c * TILE - sx, r * TILE - sy) > 300]
    random.shuffle(hunter_pool)
    hunters = [
        Hunter(*cell_center(*hunter_pool[i]),
               [f.copy() for f in hunter_walk_frames],
               [f.copy() for f in hunter_attack_frames])
        for i in range(min(HUNTER_COUNT, len(hunter_pool)))
    ]

    # Hourglasses: mid-maze, away from start and tree
    hg_pool = [(c, r) for c, r in paths
               if math.hypot(c * TILE - sx, r * TILE - sy) > 120
               and math.hypot(c * TILE - tree_x, r * TILE - tree_y) > 80]
    random.shuffle(hg_pool)
    hourglasses = [Hourglass(*cell_center(*hg_pool[i]), hg_img)
                   for i in range(min(HOURGLASS_COUNT, len(hg_pool)))]

    # ---- State ----
    time_left = float(LEVEL2_TIMER)
    particles = ParticleEmitter()
    hunter_kills = 0            # how many hunters Santa has killed
    outcome = None      # None | 'victory' | 'game_over'
    end_msg = ''
    result_delay = 2.5  # seconds to show result before returning

    # ---- Audio ----
    # Try level2 BGM first (both formats), fall back to level1 BGM if missing
    bgm_candidates = [
        os.path.join(BGM_DIR, 'level2_bgm.ogg'),
        os.path.join(BGM_DIR, 'level2_bgm.mp3'),
        os.path.join(BGM_DIR, 'level1_bgm.ogg'),
        os.path.join(BGM_DIR, 'level1_bgm.mp3'),
    ]
    for bgm_path in bgm_candidates:
        if os.path.exists(bgm_path):
            try:
                pygame.mixer.music.load(bgm_path)
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play(-1)
            except Exception:
                pass
            break

    sfx = {}
    for name, filename in (('pickup',       'item_pickup.wav'),
                           ('clear',        'level_clear.wav'),
                           ('over',         'game_over.wav'),
                           ('attack',       'santa_attack.wav'),
                           ('hunter_die',   'hunter_die.wav')):
        path = os.path.join(SFX_DIR, filename)
        if os.path.exists(path):
            try:
                sfx[name] = pygame.mixer.Sound(path)
            except Exception:
                pass

    running = True
    while running:
        dt = min(clock.tick(FPS) / 1000.0, 0.05)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.music.stop()
                return {"next_state": STATE_GAME_OVER, "score": score}
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.mixer.music.stop()
                return {"next_state": STATE_GAME_OVER, "score": score}
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_w:
                # Gift attack — only if Santa has charges and cooldown is ready
                if outcome is None and santa.charges > 0 and santa.attack_cooldown <= 0:
                    # Find nearest hunter within ATTACK_RANGE
                    nearest = None
                    nearest_dist = ATTACK_RANGE
                    for h in hunters:
                        d = math.hypot(h.x - santa.x, h.y - santa.y)
                        if d <= nearest_dist:
                            nearest_dist = d
                            nearest = h
                    if nearest is not None:
                        hunters.remove(nearest)
                        score += HUNTER_KILL_SCORE
                        hunter_kills += 1
                        santa.charges -= 1
                        santa.attack_cooldown = ATTACK_COOLDOWN
                        # Death burst particles
                        particles.emit(nearest.x, nearest.y, 40,
                                       color=(255, 100, 50),
                                       speed_range=(60, 200),
                                       lifetime_range=(0.4, 1.0),
                                       size_range=(3, 7))
                        if 'hunter_die' in sfx:
                            sfx['hunter_die'].play()
                        if 'attack' in sfx:
                            sfx['attack'].play()
                    else:
                        # No hunter in range — still play attack sound, waste no charge
                        if 'attack' in sfx:
                            sfx['attack'].play()

        # ---- Update ----
        if outcome is None:
            keys = pygame.key.get_pressed()
            santa.update(dt, keys)

            for hunter in hunters:
                hunter.update(dt, santa.x, santa.y)

            for hg in hourglasses:
                hg.update(dt)

            time_left = max(0.0, time_left - dt)

            # Hunter catches Santa (checked first — instant death per spec)
            for hunter in hunters:
                if santa.rect.colliderect(hunter.rect):
                    outcome = 'game_over'
                    end_msg = 'Caught by Hunter!'
                    if 'over' in sfx:
                        sfx['over'].play()
                    break

            # Hourglass pickup
            for hg in hourglasses[:]:
                if santa.rect.colliderect(hg.rect):
                    hg.collected = True
                    time_left += TIME_BONUS
                    santa.charges += 1          # gain 1 gift attack charge
                    particles.emit(hg.x, hg.y, 25, color=(255, 220, 80),
                                   speed_range=(40, 120), lifetime_range=(0.3, 0.7))
                    if 'pickup' in sfx:
                        sfx['pickup'].play()
            hourglasses = [hg for hg in hourglasses if not hg.collected]

            # Reach Christmas tree
            tree_rect = tree_img.get_rect(center=(tree_x, tree_y))
            if outcome is None and santa.rect.colliderect(tree_rect):
                outcome = 'victory'
                end_msg = 'Gift Delivered!'
                score += int(time_left) * 10
                if 'clear' in sfx:
                    sfx['clear'].play()
                _spawn_fireworks(particles)

            # Time out
            if time_left <= 0 and outcome is None:
                outcome = 'game_over'
                end_msg = "Time's Up!"
                if 'over' in sfx:
                    sfx['over'].play()

        else:
            # Outcome shown — count down before transitioning
            result_delay -= dt
            if outcome == 'victory' and random.random() < 0.12:
                _spawn_fireworks(particles)
            if result_delay <= 0:
                pygame.mixer.music.stop()
                next_state = STATE_VICTORY if outcome == 'victory' else STATE_GAME_OVER
                return {"next_state": next_state, "score": score}

        particles.update(dt)

        # ---- Draw ----
        screen.blit(maze_bg, (0, 0))

        # Christmas tree
        screen.blit(tree_img, tree_img.get_rect(center=(tree_x, tree_y)))

        # Hourglasses
        for hg in hourglasses:
            hg.draw(screen)

        # Hunters
        for hunter in hunters:
            hunter.draw(screen)

        # Santa
        santa.draw(screen)

        # Particles
        particles.draw(screen)

        # HUD — timer bar background
        _draw_hud(screen, time_left, score, santa.charges, hunter_kills, kill_icon, hg_img)

        # Outcome overlay
        if outcome:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            screen.blit(overlay, (0, 0))

            color = (255, 220, 50) if outcome == 'victory' else (255, 80, 80)
            draw_text(screen, end_msg, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40),
                      size=68, color=color, center=True)
            if outcome == 'victory':
                bonus_pts = int(time_left) * 10
                draw_text(screen, f"Time Bonus: +{bonus_pts} pts",
                          (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30),
                          size=36, color=(255, 255, 180), center=True)
            draw_text(screen, f"Total Score: {score}",
                      (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80),
                      size=36, color=(255, 255, 255), center=True)

        pygame.display.flip()

    pygame.mixer.music.stop()
    return {"next_state": STATE_GAME_OVER, "score": score}


# ========== Helpers ==========

def _spawn_fireworks(particles):
    colors = [(255, 80, 80), (80, 255, 80), (80, 80, 255),
              (255, 255, 80), (255, 80, 255), (80, 255, 255)]
    for _ in range(5):
        cx = random.randint(80, SCREEN_WIDTH - 80)
        cy = random.randint(80, SCREEN_HEIGHT - 80)
        particles.emit(cx, cy, 30, color=random.choice(colors),
                       speed_range=(60, 220), lifetime_range=(0.5, 1.4), size_range=(2, 7))


def _draw_hud(surface, time_left, score, charges, hunter_kills, kill_icon, hg_img):
    # Semi-transparent HUD bar at top
    bar = pygame.Surface((SCREEN_WIDTH, 44), pygame.SRCALPHA)
    bar.fill((0, 0, 0, 150))
    surface.blit(bar, (0, 0))

    # Timer (centre)
    mins = int(time_left) // 60
    secs = int(time_left) % 60
    timer_color = (255, 80, 80) if time_left < 30 else (255, 255, 255)
    draw_text(surface, f"TIME  {mins:02d}:{secs:02d}",
              (SCREEN_WIDTH // 2, 6), size=36, color=timer_color, center=True)

    # Score (right side)
    font = pygame.font.SysFont(None, 32)
    score_surf = font.render(f"Score: {score}", True, (255, 255, 255))
    surface.blit(score_surf, (SCREEN_WIDTH - score_surf.get_width() - 12, 8))

    # Power charges
    charge_color = (255, 220, 80) if charges > 0 else (150, 150, 150)
    draw_text(surface, f"Power x{charges}", (8, 10), size=24, color=charge_color)

    # Hunter kill count
    surface.blit(kill_icon, (90, 8))
    draw_text(surface, f"x{hunter_kills}", (122, 10), size=28, color=(255, 180, 80))
