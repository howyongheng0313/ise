# Santa Adventure — Detailed Development Plan

## Context

A Pygame 2D Christmas-themed game with 2 levels. All Python files are currently empty stubs. Assets (sprite sheets, backgrounds, audio, UI) are ready. We need to implement everything from scratch.

**Settings confirmed:**
- Resolution: **1280×720** (16:9 HD)
- UI Language: **English**
- Right-movement: **Flip left-movement frames horizontally**

---

## Phase 1: Infrastructure — Settings + Utils

### 1.1 `src/settings.py`

All shared constants:
```
SCREEN_WIDTH = 1280, SCREEN_HEIGHT = 720, FPS = 60
SANTA_HP = 10
LEVEL1_DURATION = 120 (sec)
LEVEL2_TIMER = 180 (sec)
TIME_BONUS = 15 (sec)
KILL_SCORE = 100
```
Color constants, asset path helpers, sprite sheet config dictionary.

### 1.2 `src/utils.py`

**`load_spritesheet(path, frame_count, scale=None)`** — Core sprite cutting function:
- Auto-calculates `frame_width = sheet_width // frame_count`
- Returns list of `pygame.Surface` frames
- Optional `scale` tuple to resize each frame

**Verified sprite sheet parameters (actual measured):**

| File | Size | Frames | Frame Size |
|------|------|--------|------------|
| `santa_fronts.png` | 896×256 | 3 | 298×256 |
| `santa_right.png` | 1172×213 | 5 | 234×213 |
| `santa_attack.png` | 896×256 | 3 | 298×256 |
| `santa_hurts.png` | 384×256 | 1 | 384×256 (single) |
| `santa_dead.png` | 1015×246 | 3 | 338×246 |
| `santa_floating.png` | 256×256 | 1 | 256×256 (single) |
| `wildman_run.png` | 1184×211 | 5 | 236×211 |
| `wildman_attack.png` | 896×256 | 3 | 298×256 |
| `wildman_dead.png` | 1060×235 | 4 | 265×235 |
| `hunter_walk.png` | 1060×235 | 4 | 265×235 |
| `hunter_attack.png` | 1000×250 | 3 | 333×250 |

**Other utils:**
- `load_image(path, scale=None)` — Load single image with optional scaling
- `draw_text(surface, text, pos, size, color)` — Text rendering helper

---

## Phase 2: Game Entry + Menu

### 2.1 `main.py` — Entry point & state machine

- Init Pygame, create 1280×720 window, set title "Santa Adventure"
- State machine: `MENU → LEVEL1 → LEVEL2 → GAME_OVER / VICTORY`
- Main loop dispatches to each scene's `run()` function
- Pass `screen`, `clock`, and `score` between scenes

### 2.2 `src/menu.py` — Start menu

- Christmas-themed background (use `forest_bg.png` scaled, or solid gradient + snow)
- Title: "Santa Adventure"
- "Start Game" button (hover highlight)
- Snowfall particle effect as decoration
- Play `menu_bgm.mp3`
- Returns next state to `main.py`

---

## Phase 3: Level 1 — The Frosty Forest Run

### 3.1 `src/level1.py`

**Scene management:**
- `forest_bg.png` (2560×1229) vertically scrolling, tiled to fill 1280×720
- Level timer (120s) — when time expires, city gate appears
- Difficulty ramp: wildman spawn rate increases over time

**Santa class:**
- States: `idle` (fronts), `move_left`/`move_right` (left frames / flipped), `attack`, `hurt`, `dead`
- Controls: ← → move horizontally, W fires magic ball
- HP: 10 hearts, snowball hit = -1 HP
- Animation: frame cycling per state at configurable speed

**Wildman class:**
- Spawn randomly from left/right screen edges, run toward center road
- States: `run` → `attack` (throw snowball) → continue or `dead`
- Hit by magic ball → play death anim → remove + add score

**Projectiles:**
- `MagicBall` — `santa_magic.png` (32×32), flies upward
- `SnowBall` — `wildmen_snow.png` (32×32), flies toward Santa's position

**Particle system (code-generated):**
- Snowfall: random white dots with drift + gentle horizontal sway
- Snowball impact: white burst particles on hit
- Magic ball trail: blue glowing particles behind projectile

**Screen effects:**
- Screen shake on Santa hit (short offset to render coords)
- Snowball trajectory trail (fading dots)

**HUD:**
- Top-left: HP hearts (`heart_full.png` / `heart_empty.png`, scaled to ~32×32)
- Top-right: Kill count (`kill_icon.png` + number)
- Timer display

**Level end:**
- Survive to timer end → `city_gate.png` scrolls in from top → Santa reaches gate → return `LEVEL2`
- HP = 0 → death animation → return `GAME_OVER` with score

**Assets used:**
- `assets/sprites/santa/*` (all 6 files)
- `assets/sprites/wildman/*` (all 3 files)
- `assets/items/santa_magic.png`, `wildmen_snow.png`
- `assets/backgrounds/forest_bg.png`, `city_gate.png`
- `assets/ui/heart_full.png`, `heart_empty.png`, `kill_icon.png`
- `assets/audio/bgm/level1_bgm.mp3`
- `assets/audio/sfx/magic_shoot.wav`, `santa_hurt.wav`, `game_over.wav`

---

## Phase 4: Level 2 — Present Delivery Mission (Simplified)

### 4.1 `src/level2.py`

> **Change:** No house selection screen. After Level 1, player enters the maze directly.
> Maze background image will be provided by user later.

**Maze system:**
- Single pre-designed maze layout (easier difficulty)
- 2D array grid: 0 = path, 1 = wall
- Render walls/floor with code-drawn tiles (user will provide maze background image later)
- Camera follows Santa (maze larger than screen)

**Santa (maze version):**
- 4-direction movement (↑↓←→)
- Wall collision detection
- Uses `santa_fronts.png` (down), `santa_right.png` (left), flipped left (right), `santa_hurts.png` (up/back view)

**Hunter class:**
- Spawns at random maze positions (away from Santa)
- AI pathfinding: BFS toward Santa, updates periodically
- Touch Santa → instant Game Over
- States: `walk`, `attack`

**Items:**
- Time hourglass (`santa_hourglass.png`): random maze positions, pickup = +15s
- Visual effect: pulsing glow / bobbing animation

**Christmas tree goal:**
- `christmass_tree.png` at maze end
- Reach it → victory celebration particles (fireworks, stars)

**Countdown:**
- 180 seconds, displayed with hourglass icon in HUD
- Time up → Game Over

**Assets used:**
- `assets/sprites/santa/santa_fronts.png`, `santa_right.png`, `santa_hurts.png`
- `assets/sprites/hunter/*` (both files)
- `assets/items/santa_hourglass.png`, `christmass_tree.png`
- `assets/audio/bgm/level1_bgm.mp3` (temp, level2_bgm missing)
- `assets/audio/sfx/item_pickup.wav`, `level_clear.wav`

---

## Phase 5: End Screens

### 5.1 `src/game_over.py`

- Two modes: **Game Over** (failure) / **Victory** (cleared)
- Display Total Score
- Buttons: "Retry" (restart from Level 1) / "Quit"
- Victory: celebration particles (fireworks, stars), play `level_clear.wav`
- Game Over: play `game_over.wav`

---

## Development Order

| Step | Task | File(s) |
|------|------|---------|
| 1 | Global constants & asset path config | `src/settings.py` |
| 2 | Sprite sheet cutter & utility functions | `src/utils.py` |
| 3 | Game entry point & state machine | `main.py` |
| 4 | Start menu with snow particles & BGM | `src/menu.py` |
| 5 | L1: Background scrolling + Santa movement | `src/level1.py` |
| 6 | L1: Wildman spawning + projectiles + collision | `src/level1.py` |
| 7 | L1: Particles, HUD, screen shake, audio | `src/level1.py`, `src/utils.py` |
| 8 | L1: City gate + level completion logic | `src/level1.py` |
| 9 | L2: Maze rendering + Santa maze movement | `src/level2.py` |
| 10 | L2: Hunter AI pathfinding | `src/level2.py` |
| 11 | L2: Items, countdown, victory condition | `src/level2.py` |
| 12 | Game Over / Victory screens | `src/game_over.py` |
| 13 | Full playtest + parameter tuning + polish | All files |

---

## Missing Assets — Workarounds

| Missing | Solution |
|---------|----------|
| Maze background image | Code-drawn tiles for now; user will provide image later |
| `level2_bgm` | Reuse `level1_bgm.mp3` temporarily |

---

## Verification Plan

- **After Step 2**: Run a test script to display all cut frames on screen → confirm correct cutting
- **After Step 4**: Run game → menu displays, button works, BGM plays, snow falls
- **After Step 8**: Full Level 1 playthrough: move, shoot, enemies, damage, gate transition
- **After Step 11**: Full Level 2 playthrough: maze, hunter, items, tree goal
- **After Step 12**: Complete game loop: menu → L1 → L2 → victory/game over → retry
- **After Step 13**: End-to-end playtest, tweak difficulty values
