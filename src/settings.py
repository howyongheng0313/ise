"""
Global Variables (Screen Size, color, frame, TODO value)
"""
import os

# ========== Screen =========
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
GAME_TITLE = "Santa Adventure"

# ========== Colors ==========
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
DARK_BLUE = (10, 10, 40)
SNOW_WHITE = (240, 248, 255)

# ========== Paths ==========
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
SPRITES_DIR = os.path.join(ASSETS_DIR, "sprites")
ITEMS_DIR = os.path.join(ASSETS_DIR, "items")
BACKGROUNDS_DIR = os.path.join(ASSETS_DIR, "backgrounds")
UI_DIR = os.path.join(ASSETS_DIR, "ui")
BGM_DIR = os.path.join(ASSETS_DIR, "audio", "bgm")
SFX_DIR = os.path.join(ASSETS_DIR, "audio", "sfx")

# ========== Game States ==========
STATE_MENU = "menu"
STATE_LEVEL1 = "level1"
STATE_LEVEL2 = "level2"
STATE_GAME_OVER = "game_over"
STATE_VICTORY = "victory"

# ========== Level 1 Settings ==========
SANTA_HP = 10
LEVEL1_DURATION = 120           # seconds
KILL_SCORE = 1                  # points per wildman kill
SANTA_SPEED = 5                 # pixels per frame
MAGIC_BALL_SPEED = 8            # pixels per frame (upward)
SNOWBALL_SPEED = 4              # pixels per frame (toward santa)
BG_SCROLL_SPEED = 2             # background scroll pixels per frame
WILDMAN_SPEED = 3               # pixels per frame
WILDMAN_SPAWN_INTERVAL = 2.0    # seconds (initial)
WILDMAN_SPAWN_MIN = 0.5         # seconds (minimum after ramp)
WILDMAN_ATTACK_RANGE = 250      # pixels, distance to throw snowball
ROAD_LEFT = 430                 # left boundary of snow road (screen coords)
ROAD_RIGHT = 850                # right boundary of snow road (screen coords)

# ========== Level 2 Settings ==========
LEVEL2_TIMER = 180              # seconds
TIME_BONUS = 15                 # seconds added per hourglass pickup
MAZE_TILE_SIZE = 64             # pixels per maze cell
SANTA_MAZE_SPEED = 4            # pixels per frame in maze
HUNTER_SPEED = 2                # pixels per frame
HUNTER_PATHFIND_INTERVAL = 0.5  # seconds between path recalculations

# ========== Sprite Sheet Config ==========
# { key: (relative_path_from_SPRITES_DIR, frame_count) }
SPRITESHEET_CONFIG = {
    "santa_fronts":    ("santa/santa_fronts.png", 3),
    "santa_right":     ("santa/santa_right.png", 5),
    "santa_attack":    ("santa/santa_attack.png", 3),
    "santa_hurts":     ("santa/santa_hurts.png", 1),
    "santa_dead":      ("santa/santa_dead.png", 3),
    "santa_floating":  ("santa/santa_floating.png", 1),
    "wildman_run":     ("wildman/wildman_run.png", 5),
    "wildman_attack":  ("wildman/wildman_attack.png", 3),
    "wildman_dead":    ("wildman/wildman_dead.png", 4),
    "hunter_walk":     ("hunter/hunter_walk.png", 4),
    "hunter_attack":   ("hunter/hunter_attack.png", 3),
}

# ========== Animation ==========
ANIMATION_SPEED = 0.15  # seconds per frame (default)

# ========== Particles ==========
SNOWFLAKE_COUNT = 80    # number of snowflakes on screen
SCREEN_SHAKE_DURATION = 0.3  # seconds
SCREEN_SHAKE_INTENSITY = 8   # max pixel offset
