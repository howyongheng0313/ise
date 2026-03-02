# PROJECT_STRUCTURE.md — 项目文件结构与命名规范

## 目录结构

```
SantaAdventure/
├── CLAUDE.md                    # 全局游戏规则与机制
├── PROJECT_STRUCTURE.md         # 本文件：文件结构与命名规范
├── main.py                      # 游戏入口（启动菜单 → 关卡调度）
│
├── src/                         # 源代码
│   ├── menu.py                  # 开始菜单界面
│   ├── level1.py                # 第一关：穿越雪地大森林
│   ├── level2.py                # 第二关：迷宫大逃亡
│   ├── game_over.py             # 游戏失败 / 通关界面
│   ├── settings.py              # 全局常量（屏幕尺寸、颜色、帧率、TODO数值）
│   └── utils.py                 # 公共工具（精灵表切割、碰撞检测、粒子系统等）
│
├── assets/                      # 所有游戏资产
│   ├── sprites/                 # 精灵图
│   │   ├── santa/               # 圣诞老人
│   │   │   ├── santa_fronts.png         # 正面行走 (896×256, 3帧 ≈ 299×256/帧)
│   │   │   ├── santa_left.png           # 左移行走 (1408×256, 5帧 ≈ 282×256/帧)
│   │   │   ├── santa_attack.png         # 攻击动画 (896×256, 3帧)
│   │   │   ├── santa_hurts.png          # 受伤动画 (384×256, 1-2帧)
│   │   │   ├── santa_dead.png           # 死亡动画 (1056×256, 3-4帧)
│   │   │   └── santa_floating.png       # 浮空/待机 (256×256, 单帧)
│   │   │
│   │   ├── wildman/             # 雪怪（第一关敌人）
│   │   │   ├── wildman_run.png          # 跑动动画 (1436×256, 5帧)
│   │   │   ├── wildman_attack.png       # 攻击动画 (896×256, 3帧)
│   │   │   └── wildman_dead.png         # 死亡动画 (1152×256, 4帧)
│   │   │
│   │   └── hunter/              # 猎人（第二关敌人）
│   │       ├── hunter_walk.png          # 行走动画 (2000×434, 4帧 ≈ 500×434/帧)
│   │       └── hunter_attack.png        # 攻击动画 (1024×256, 3帧)
│   │
│   ├── items/                   # 道具与物品
│   │   ├── santa_magic.png              # 法球弹射物 (32×32)
│   │   ├── wildmen_snow.png             # 雪球弹射物 (32×32)
│   │   ├── santa_hourglass.png          # 时间延长道具 (64×64)，同时用作计时器UI图标
│   │   └── christmass_tree.png          # 圣诞树 (626×626)
│   │
│   ├── backgrounds/             # 背景图
│   │   ├── forest_bg.png               # 第一关森林背景（待制作）
│   │   ├── city_gate.png               # 城门过渡画面（待制作）
│   │   ├── house_select.png            # 第二关房屋选择界面（待制作）
│   │   └── maze_floor.png              # 迷宫地板纹理（待制作）
│   │
│   ├── ui/                      # UI 元素
│   │   ├── heart_full.png              # 实心 
│   │   ├── heart_empty.png             # 空心（当被雪球击中）
│   │   └── kill_icon.png               # 击杀图标（使用pygame显示分数）
│   │
│   └── audio/                   # 音频资产
│       ├── bgm/                        # 背景音乐
│       │   ├── menu_bgm.ogg            # 菜单音乐
│       │   ├── level1_bgm.ogg          # 第一关音乐
│       │   └── level2_bgm.ogg          # 第二关音乐（待添加）
│       │
│       └── sfx/                         # 音效
│           ├── magic_shoot.ogg          # 法球发射
│           ├── santa_hurt.ogg           # 圣诞老人受伤
│           ├── item_pickup.ogg          # 道具拾取
│           ├── level_clear.ogg          # 过关音效
│           └── game_over.ogg            # Game Over 音效
│
└── docs/                        # 文档（非游戏运行必需）
    └── storyboard.png                  # 故事板草图
```

---

## 命名规范

| 类别 | 规则 | 示例 |
|------|------|------|
| 精灵图 | `角色_动作.png` | `santa_attack.png`, `wildman_run.png` |
| 弹射物 | `角色_弹射物名.png` | `santa_magic.png`, `wildmen_snow.png` |
| 背景音乐 | `场景_bgm.ogg` | `level1_bgm.ogg` |
| 音效 | `动作描述.ogg` | `magic_shoot.ogg`, `santa_hurt.ogg` |
| 代码文件 | 小写 + 下划线 | `level1.py`, `game_over.py` |

---

## 精灵表 (Sprite Sheet) 切割规则

所有角色精灵图都是**横向排列的帧序列**，高度统一为单帧高度。切割方式：

```python
# 通用切割方法（放在 utils.py 中）
def load_spritesheet(path, frame_count, frame_size=None):
    """
    path: 精灵表文件路径
    frame_count: 帧数
    frame_size: (width, height) 每帧尺寸，None则自动计算
    """
    sheet = pygame.image.load(path).convert_alpha()
    if frame_size is None:
        fw = sheet.get_width() // frame_count
        fh = sheet.get_height()
        frame_size = (fw, fh)
    frames = []
    for i in range(frame_count):
        frame = sheet.subsurface((i * frame_size[0], 0, frame_size[0], frame_size[1]))
        frames.append(frame)
    return frames
```

### 各精灵表帧数参考

| 文件名 | 尺寸 | 推测帧数 | 每帧尺寸 |
|--------|------|---------|---------|
| `santa_fronts.png` | 896×256 | 3 | ~299×256 |
| `santa_left.png` | 1408×256 | 5 | ~282×256 |
| `santa_attack.png` | 896×256 | 3 | ~299×256 |
| `santa_hurts.png` | 384×256 | 1-2 | 需确认 |
| `santa_dead.png` | 1056×256 | 3-4 | 需确认 |
| `wildman_run.png` | 1436×256 | 5 | ~287×256 |
| `wildman_attack.png` | 896×256 | 3 | ~299×256 |
| `wildman_dead.png` | 1152×256 | 4 | ~288×256 |
| `hunter_walk.png` | 2000×434 | 4 | ~500×434 |
| `hunter_attack.png` | 1024×256 | 3 | ~341×256 |

> ⚠️ 帧数是根据图片尺寸推测的，实际开发时需要打开图片确认精确帧数和每帧宽度。

---

## 分工对照

| 模块 | 负责人 | 对应文件 |
|------|--------|---------|
| 开始菜单 | Zheng Yu + Yong Heng | `main.py`, `src/menu.py` |
| 第一关 | Zheng Yu + Yong Heng | `src/level1.py` |
| 第二关 | Michelle + Zhi Ruo | `src/level2.py` |
| 游戏失败/通关界面 | Michelle + Zhi Ruo | `src/game_over.py` |
| 公共模块 | 全员协商 | `src/settings.py`, `src/utils.py` |

> `settings.py` 和 `utils.py` 是两关共享的基础，建议开发初期由全员一起定好接口，之后各自调用。

---

## 音频格式建议

- 推荐使用 `.ogg` 格式（Pygame 对 `.ogg` 兼容性最好）。
- `.mp3` 在某些系统上 Pygame 解码会出问题，尽量避免。
- 背景音乐文件大小建议控制在 5MB 以内。
