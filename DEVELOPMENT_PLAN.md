# 圣诞老人大冒险 — 详细开发计划

## 项目背景

基于 Pygame 的 2D 圣诞主题游戏，共 2 关。所有 Python 文件均已为空桩文件，素材（精灵表、背景、音频、UI）已就绪，需从头实现全部逻辑。

**已确认配置：**
- 分辨率：**1280×720**（16:9 高清）
- UI 语言：**中文 / 英文混用**
- 向右移动：**水平翻转向左移动的帧**

---

## 第一阶段：基础设施 — 配置 + 工具

### 1.1 `src/settings.py`

全局共享常量：
```
SCREEN_WIDTH = 1280, SCREEN_HEIGHT = 720, FPS = 60
SANTA_HP = 10
LEVEL1_DURATION = 120（秒）
LEVEL2_TIMER = 180（秒）
TIME_BONUS = 15（秒）
KILL_SCORE = 100
```
颜色常量、素材路径助手函数、精灵表参数字典。

### 1.2 `src/utils.py`

**`load_spritesheet(path, frame_count, scale=None)`** — 核心精灵切割函数：
- 自动计算 `frame_width = sheet_width // frame_count`
- 返回 `pygame.Surface` 帧列表
- 可选 `scale` 元组对每帧缩放

**已验证的精灵表参数（实际测量值）：**

| 文件 | 尺寸 | 帧数 | 单帧尺寸 |
|------|------|------|----------|
| `santa_fronts.png` | 896×256 | 3 | 298×256 |
| `santa_right.png` | 1172×213 | 5 | 234×213 |
| `santa_attack.png` | 896×256 | 3 | 298×256 |
| `santa_hurts.png` | 384×256 | 1 | 384×256（单帧）|
| `santa_dead.png` | 1015×246 | 3 | 338×246 |
| `santa_floating.png` | 256×256 | 1 | 256×256（单帧）|
| `wildman_run.png` | 1184×211 | 5 | 236×211 |
| `wildman_attack.png` | 896×256 | 3 | 298×256 |
| `wildman_dead.png` | 1060×235 | 4 | 265×235 |
| `hunter_walk.png` | 1060×235 | 4 | 265×235 |
| `hunter_attack.png` | 1000×250 | 3 | 333×250 |

**其他工具函数：**
- `load_image(path, scale=None)` — 加载单张图片，支持缩放
- `draw_text(surface, text, pos, size, color)` — 文字渲染助手

---

## 第二阶段：游戏入口 + 菜单

### 2.1 `main.py` — 入口点与状态机

- 初始化 Pygame，创建 1280×720 窗口，标题设为 "Santa Adventure"
- 状态机：`MENU → LEVEL1 → LEVEL2 → GAME_OVER / VICTORY`
- 主循环将每个状态分发到对应场景的 `run()` 函数
- 在各场景间传递 `screen`、`clock`、`score`

### 2.2 `src/menu.py` — 开始菜单

- 圣诞主题背景（使用 `forest_bg.png` 缩放，或纯色渐变 + 雪花）
- 标题："Santa Adventure"
- "开始游戏" 按钮（悬停高亮）
- 雪花粒子特效作为装饰
- 播放 `menu_bgm.mp3`
- 返回下一个状态给 `main.py`

---

## 第三阶段：第一关 — 穿越雪地大森林

### 3.1 `src/level1.py`

**场景管理：**
- `forest_bg.png`（2560×1229）纵向滚动，平铺填满 1280×720
- 关卡计时器（120 秒）— 时间耗尽后城门出现
- 难度递增：雪怪生成频率随时间增加

**圣诞老人类：**
- 状态：`idle`（fronts）、`move_left` / `move_right`（左帧 / 翻转）、`attack`、`hurt`、`dead`
- 操作：← → 水平移动，W 发射法球
- 生命值：10 颗心，被雪球击中 -1 HP
- 动画：各状态按可配置速度循环帧

**雪怪类：**
- 从屏幕左右边缘随机生成，跑向中央雪道
- 状态：`run` → `attack`（投掷雪球）→ 继续或 `dead`
- 被法球击中 → 播放死亡动画 → 移除 + 加分

**弹射物：**
- `MagicBall` — `santa_magic.png`（32×32），向上飞行
- `SnowBall` — `wildmen_snow.png`（32×32），飞向圣诞老人位置

**粒子系统（代码生成）：**
- 雪花飘落：随机白色圆点，带漂移 + 轻微横向摆动
- 雪球撞击：命中时白色爆裂粒子
- 法球轨迹：弹射物后方蓝色发光粒子

**屏幕特效：**
- 圣诞老人被击中时屏幕震动（短暂偏移渲染坐标）
- 雪球弹道轨迹（淡出圆点）

**HUD：**
- 左上角：HP 心形图标（`heart_full.png` / `heart_empty.png`，缩放至约 32×32）
- 右上角：击杀数（`kill_icon.png` + 数字）
- 计时器显示

**关卡结束：**
- 存活至计时结束 → `city_gate.png` 从顶部滚入 → 圣诞老人到达城门 → 返回 `LEVEL2`
- HP = 0 → 死亡动画 → 返回 `GAME_OVER` 附带分数

**使用素材：**
- `assets/sprites/santa/*`（全部 6 个文件）
- `assets/sprites/wildman/*`（全部 3 个文件）
- `assets/items/santa_magic.png`、`wildmen_snow.png`
- `assets/backgrounds/forest_bg.png`、`city_gate.png`
- `assets/ui/heart_full.png`、`heart_empty.png`、`kill_icon.png`
- `assets/audio/bgm/level1_bgm.mp3`
- `assets/audio/sfx/magic_shoot.wav`、`santa_hurt.wav`、`game_over.wav`

---

## 第四阶段：第二关 — 迷宫大逃亡

### 4.1 `src/level2.py`

> **说明：** 无房屋选择界面。第一关结束后直接进入迷宫。
> 迷宫背景图将由用户后续提供。

**迷宫系统：**
- 单一预设迷宫布局（较低难度）
- 二维数组网格：0 = 通道，1 = 墙壁
- 用代码绘制瓦片渲染墙壁/地板（用户后续提供迷宫背景图）
- 摄像机跟随圣诞老人（迷宫尺寸大于屏幕）

**圣诞老人（迷宫版）：**
- 四方向移动（↑ ↓ ← →）
- 墙壁碰撞检测
- 使用 `santa_fronts.png`（下）、`santa_right.png`（左）、水平翻转（右）、`santa_hurts.png`（上/背面视角）

**猎人类：**
- 在迷宫随机位置生成（远离圣诞老人）
- AI 寻路：BFS 向圣诞老人追踪，定期更新
- 接触圣诞老人 → 立即 Game Over
- 状态：`walk`、`attack`

**道具：**
- 时间沙漏（`santa_hourglass.png`）：随机出现在迷宫中，拾取 = +15 秒
- 视觉效果：脉冲发光 / 上下浮动动画

**圣诞树终点：**
- `christmass_tree.png` 位于迷宫终点
- 到达后 → 胜利庆祝粒子效果（烟花、星星）

**倒计时：**
- 180 秒，HUD 中用沙漏图标显示
- 时间耗尽 → Game Over

**使用素材：**
- `assets/sprites/santa/santa_fronts.png`、`santa_right.png`、`santa_hurts.png`
- `assets/sprites/hunter/*`（全部 2 个文件）
- `assets/items/santa_hourglass.png`、`christmass_tree.png`
- `assets/audio/bgm/level1_bgm.mp3`（临时使用，level2_bgm 缺失）
- `assets/audio/sfx/item_pickup.wav`、`level_clear.wav`

---

## 第五阶段：结束界面

### 5.1 `src/game_over.py`

- 两种模式：**Game Over**（失败）/ **Victory**（通关）
- 显示总分
- 按钮："重新开始"（从第一关重新开始）/ "退出"
- 通关：庆祝粒子效果（烟花、星星），播放 `level_clear.wav`
- 失败：播放 `game_over.wav`

---

## 开发顺序

| 步骤 | 任务 | 文件 |
|------|------|------|
| 1 | 全局常量与素材路径配置 | `src/settings.py` |
| 2 | 精灵表切割与工具函数 | `src/utils.py` |
| 3 | 游戏入口与状态机 | `main.py` |
| 4 | 开始菜单（雪花粒子 + BGM）| `src/menu.py` |
| 5 | 第一关：背景滚动 + 圣诞老人移动 | `src/level1.py` |
| 6 | 第一关：雪怪生成 + 弹射物 + 碰撞 | `src/level1.py` |
| 7 | 第一关：粒子、HUD、屏幕震动、音频 | `src/level1.py`、`src/utils.py` |
| 8 | 第一关：城门 + 关卡完成逻辑 | `src/level1.py` |
| 9 | 第二关：迷宫渲染 + 圣诞老人迷宫移动 | `src/level2.py` |
| 10 | 第二关：猎人 AI 寻路 | `src/level2.py` |
| 11 | 第二关：道具、倒计时、胜利条件 | `src/level2.py` |
| 12 | Game Over / 胜利界面 | `src/game_over.py` |
| 13 | 全流程游戏测试 + 参数调优 + 打磨 | 所有文件 |

---

## 缺失素材处理方案

| 缺失内容 | 解决方案 |
|----------|----------|
| 迷宫背景图 | 暂用代码绘制瓦片；用户后续提供图片 |
| `level2_bgm` | 暂时复用 `level1_bgm.mp3` |

---

## 验证计划

- **步骤 2 完成后**：运行测试脚本，在屏幕上显示所有切割帧 → 确认切割正确
- **步骤 4 完成后**：运行游戏 → 菜单显示、按钮可用、BGM 播放、雪花飘落
- **步骤 8 完成后**：完整第一关流程：移动、射击、敌人、受伤、城门过关
- **步骤 11 完成后**：完整第二关流程：迷宫、猎人、道具、圣诞树终点
- **步骤 12 完成后**：完整游戏循环：菜单 → 第一关 → 第二关 → 胜利/失败 → 重新开始
- **步骤 13 完成后**：端到端游戏测试，调整难度数值
