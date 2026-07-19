#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sokoban (推箱子) - Kivy edition
纯 Python 实现的推箱子益智游戏，离线运行，可打包为安卓 APK。

符号约定:
  #  墙壁      .  目标点      $  箱子
  @  玩家      *  箱子在目标上  +  玩家在目标上
     空格 = 地板/外部空地
"""

import os

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.anchorlayout import AnchorLayout
from kivy.graphics import Color, Rectangle, Line
from kivy.core.window import Window
from kivy.core.image import Image as CoreImage
from kivy.properties import NumericProperty


# ============================ 关卡数据 ============================
LEVELS = [
    # Level 1 - 入门: 向右推一格
    [
        "#######",
        "#     #",
        "# @$. #",
        "#     #",
        "#######",
    ],
    # Level 2 - 两个箱子
    [
        "########",
        "#      #",
        "# .$ $.#",
        "#  @   #",
        "#      #",
        "########",
    ],
    # Level 3 - 对称推开
    [
        "#########",
        "#       #",
        "# .   . #",
        "#  $ $  #",
        "#   @   #",
        "#       #",
        "#########",
    ],
    # Level 4 - 绕墙
    [
        "########",
        "#   #  #",
        "# .$   #",
        "# @ $ .#",
        "#      #",
        "########",
    ],
    # Level 5 - 四角
    [
        "##########",
        "#        #",
        "# .#  #. #",
        "#  $  $  #",
        "#   @    #",
        "#  $  $  #",
        "# .#  #. #",
        "#        #",
        "##########",
    ],
    # Level 6 - 十字阵
    [
        "  #####  ",
        "###   ###",
        "#  $.$  #",
        "#  .@.  #",
        "#  $.$  #",
        "###   ###",
        "  #####  ",
    ],
    # Level 7 - 长走廊单箱
    [
        "##########",
        "#        #",
        "#  $   . #",
        "#  @     #",
        "#        #",
        "##########",
    ],
    # Level 8 - 三箱齐推
    [
        "##########",
        "#        #",
        "# . . .  #",
        "# $ $ $  #",
        "#   @    #",
        "#        #",
        "##########",
    ],
    # Level 9 - 小房间三箱
    [
        "#########",
        "#       #",
        "# ##### #",
        "# #...# #",
        "# #$$$  #",
        "# # @   #",
        "# ##### #",
        "#       #",
        "#########",
    ],
    # Level 10 - 四箱双向
    [
        "##########",
        "#        #",
        "#  $  $  #",
        "#  .  .  #",
        "#   @    #",
        "#  .  .  #",
        "#  $  $  #",
        "#        #",
        "##########",
    ],
    # Level 11 - 四箱齐推
    [
        "###########",
        "#         #",
        "# . . . . #",
        "# $ $ $ $ #",
        "#    @    #",
        "#         #",
        "###########",
    ],
    # Level 12 - 四角大阵
    [
        "############",
        "#          #",
        "# .  ##  . #",
        "#  $    $  #",
        "#    @     #",
        "#  $    $  #",
        "# .  ##  . #",
        "#          #",
        "############",
    ],
]


# ============================ 配色（图片缺失时的 fallback） ============================
C_BG     = (0.09, 0.12, 0.18, 1)   # 深蓝背景，衬托亮地板
C_WALL   = (0.36, 0.39, 0.46, 1)
C_FLOOR  = (0.20, 0.22, 0.27, 1)
C_GRID   = (0.28, 0.30, 0.35, 1)
C_TARGET = (0.95, 0.55, 0.20, 1)
C_BOX    = (0.82, 0.56, 0.26, 1)
C_BOX_OK = (0.30, 0.78, 0.45, 1)
C_PLAYER = (0.25, 0.62, 0.95, 1)
C_TEXT   = (0.95, 0.95, 0.95, 1)


# ============================ 素材纹理加载（启动时一次缓存） ============================
ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
FONT = os.path.join(ASSETS, 'fonts', 'simhei.ttf')   # 中文字体，避免乱码
_TEX_CACHE = {}


def load_texture(name):
    path = os.path.join(ASSETS, name)
    if os.path.exists(path):
        return CoreImage(path).texture
    return None


def get_tex(name):
    if name not in _TEX_CACHE:
        _TEX_CACHE[name] = load_texture(name)
    return _TEX_CACHE[name]


def ensure_assets():
    """预加载所有素材，避免第一帧卡顿"""
    for name in [
        'floor.png', 'wall.png', 'target.png',
        'box.png', 'box_ok.png',
        'player_down.png', 'player_up.png',
        'player_left.png', 'player_right.png',
    ]:
        get_tex(name)


# ============================ 游戏逻辑 ============================
class Game:
    """推箱子核心逻辑: 解析关卡 / 移动 / 撤销 / 胜利判定"""

    def __init__(self, data):
        self.load(data)
        self.history = []
        self.moves = 0
        self.pushes = 0

    def load(self, data):
        self.data = data
        self.rows = len(data)
        self.cols = max(len(r) for r in data)
        self.walls = set()
        self.targets = set()
        self.boxes = set()
        self.player = (0, 0)
        for y, row in enumerate(data):
            for x, ch in enumerate(row):
                if ch == '#':
                    self.walls.add((x, y))
                elif ch == '.':
                    self.targets.add((x, y))
                elif ch == '$':
                    self.boxes.add((x, y))
                elif ch == '*':
                    self.boxes.add((x, y))
                    self.targets.add((x, y))
                elif ch == '@':
                    self.player = (x, y)
                elif ch == '+':
                    self.player = (x, y)
                    self.targets.add((x, y))
        self._compute_floor()

    def _compute_floor(self):
        """从玩家位置 floodfill, 标记关卡内部地板, 跳过外部空地"""
        self.floors = set()
        stack = [self.player]
        seen = set()
        while stack:
            x, y = stack.pop()
            if (x, y) in seen or (x, y) in self.walls:
                continue
            if not (0 <= x < self.cols and 0 <= y < self.rows):
                continue
            seen.add((x, y))
            self.floors.add((x, y))
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                stack.append((x + dx, y + dy))
        self.floors |= self.targets

    def move(self, dx, dy):
        """尝试朝 (dx,dy) 移动一步, 成功返回 True"""
        px, py = self.player
        nx, ny = px + dx, py + dy
        if (nx, ny) in self.walls:
            return False
        if (nx, ny) in self.boxes:
            bx, by = nx + dx, ny + dy
            if (bx, by) in self.walls or (bx, by) in self.boxes:
                return False
            self.history.append(('P', self.player, (nx, ny), (bx, by)))
            self.boxes.discard((nx, ny))
            self.boxes.add((bx, by))
            self.player = (nx, ny)
            self.moves += 1
            self.pushes += 1
            return True
        self.history.append(('M', self.player, (nx, ny)))
        self.player = (nx, ny)
        self.moves += 1
        return True

    def undo(self):
        if not self.history:
            return False
        a = self.history.pop()
        if a[0] == 'P':
            _, old_p, new_p, box_new = a
            self.boxes.discard(box_new)
            self.boxes.add(new_p)
            self.player = old_p
            self.pushes -= 1
        else:
            _, old_p, _ = a
            self.player = old_p
        self.moves -= 1
        return True

    def is_won(self):
        return self.boxes <= self.targets


# ============================ 游戏画面 ============================
class GameWidget(Widget):
    """负责绘制网格 + 处理触摸滑动"""

    game_width = NumericProperty(0)   # 游戏区实际像素宽度，供按钮区对齐

    def __init__(self, **kw):
        super().__init__(**kw)
        self.game = None
        self.level_idx = 0
        self.cell = 40
        self.player_dir = 'down'
        self.on_info = None
        self.on_win = None
        self._touch_start = None
        self.bind(size=self._draw, pos=self._draw)

    def load_level(self, idx):
        self.level_idx = idx
        self.game = Game(LEVELS[idx])
        self.player_dir = 'down'
        self._draw()
        if self.on_info:
            self.on_info()

    def do_move(self, dx, dy):
        if not self.game:
            return
        # 先转身（即使走不动也允许朝向改变）
        if dx == 1:
            self.player_dir = 'right'
        elif dx == -1:
            self.player_dir = 'left'
        elif dy == -1:
            self.player_dir = 'up'
        elif dy == 1:
            self.player_dir = 'down'

        if self.game.move(dx, dy):
            self._draw()
            if self.on_info:
                self.on_info()
            if self.game.is_won() and self.on_win:
                self.on_win()
        else:
            self._draw()

    def undo(self):
        if self.game and self.game.undo():
            self._draw()
            if self.on_info:
                self.on_info()

    def reset(self):
        self.load_level(self.level_idx)

    def next_level(self):
        if self.level_idx < len(LEVELS) - 1:
            self.load_level(self.level_idx + 1)

    def prev_level(self):
        if self.level_idx > 0:
            self.load_level(self.level_idx - 1)

    def _draw(self, *a):
        if not self.game:
            return
        g = self.game
        self.canvas.clear()
        cell = min(self.width // max(g.cols, 1),
                   self.height // max(g.rows, 1))
        cell = max(18, min(cell, 64))
        self.cell = cell
        self.game_width = g.cols * cell
        ox = self.x + (self.width - g.cols * cell) / 2
        oy = self.y + (self.height - g.rows * cell) / 2

        def sx(x):
            return ox + x * cell

        def sy(y):
            return oy + (g.rows - 1 - y) * cell

        tex_floor = get_tex('floor.png')
        tex_wall = get_tex('wall.png')
        tex_target = get_tex('target.png')
        tex_box = get_tex('box.png')
        tex_box_ok = get_tex('box_ok.png')
        tex_player = get_tex('player_%s.png' % self.player_dir)

        with self.canvas:
            # 背景
            Color(*C_BG)
            Rectangle(pos=self.pos, size=self.size)
            # 重置为白色——纹理必须以原色显示，否则会被前面的 Color 着色变灰
            Color(1, 1, 1, 1)

            # 地板 + 目标点
            for (x, y) in g.floors:
                if tex_floor:
                    Rectangle(pos=(sx(x), sy(y)), size=(cell, cell),
                              texture=tex_floor)
                else:
                    Color(*C_FLOOR)
                    Rectangle(pos=(sx(x), sy(y)), size=(cell, cell))
                    Color(1, 1, 1, 1)

                # 网格线
                Color(*C_GRID)
                Line(rectangle=(sx(x), sy(y), cell, cell), width=0.6)
                Color(1, 1, 1, 1)

                if (x, y) in g.targets:
                    if tex_target:
                        Rectangle(pos=(sx(x), sy(y)), size=(cell, cell),
                                  texture=tex_target)
                    else:
                        Color(*C_TARGET)
                        Ellipse(pos=(sx(x) + cell * 0.32, sy(y) + cell * 0.32),
                                size=(cell * 0.36, cell * 0.36))
                        Color(1, 1, 1, 1)

            # 墙
            for (x, y) in g.walls:
                if tex_wall:
                    Rectangle(pos=(sx(x), sy(y)), size=(cell, cell),
                              texture=tex_wall)
                else:
                    Color(*C_WALL)
                    Rectangle(pos=(sx(x), sy(y)), size=(cell, cell))
                    Color(1, 1, 1, 1)

            # 箱子
            for (x, y) in g.boxes:
                tex = tex_box_ok if (x, y) in g.targets else tex_box
                if tex:
                    Rectangle(pos=(sx(x) + cell * 0.05, sy(y) + cell * 0.05),
                              size=(cell * 0.9, cell * 0.9),
                              texture=tex)
                else:
                    Color(*C_BOX_OK if (x, y) in g.targets else C_BOX)
                    Rectangle(pos=(sx(x) + cell * 0.08, sy(y) + cell * 0.08),
                              size=(cell * 0.84, cell * 0.84))
                    Color(1, 1, 1, 1)

            # 玩家
            px, py = g.player
            if tex_player:
                Rectangle(pos=(sx(px) + cell * 0.05, sy(py) + cell * 0.05),
                          size=(cell * 0.9, cell * 0.9),
                          texture=tex_player)
            else:
                Color(*C_PLAYER)
                Ellipse(pos=(sx(px) + cell * 0.14, sy(py) + cell * 0.14),
                        size=(cell * 0.72, cell * 0.72))

    # ---- 触摸滑动 (安卓主要操作方式) ----
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self._touch_start = touch.pos
            return True
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if self._touch_start:
            sx, sy = touch.x - self._touch_start[0], touch.y - self._touch_start[1]
            t = 28
            if abs(sx) > t or abs(sy) > t:
                if abs(sx) > abs(sy):
                    self.do_move(1 if sx > 0 else -1, 0)
                else:
                    self.do_move(0, -1 if sy > 0 else 1)
            self._touch_start = None
            return True
        return super().on_touch_up(touch)


# ============================ 应用主体 ============================
class SokobanApp(App):
    def build(self):
        ensure_assets()  # 预加载所有图片
        Window.clearcolor = C_BG
        self.gw = GameWidget()
        self.gw.on_info = self._upd_info
        self.gw.on_win = self._on_win

        root = BoxLayout(orientation='vertical', padding=8, spacing=6)

        self.info = Label(text='', size_hint=(1, None), height=30,
                          font_size='16sp', color=C_TEXT, bold=True,
                          font_name=FONT)
        root.add_widget(self.info)

        root.add_widget(self.gw)

        # 按钮区：用 AnchorLayout 居中，bar 宽度绑定游戏区宽度，和游戏边框等宽对齐
        bar_wrap = AnchorLayout(anchor_x='center', anchor_y='center',
                                size_hint=(1, None), height=116)
        bar = BoxLayout(orientation='horizontal', size_hint=(None, 1),
                        width=300, spacing=4)
        self.gw.bind(game_width=lambda *_: setattr(bar, 'width', self.gw.game_width))

        dpad = GridLayout(cols=3, size_hint=(0.45, 1), spacing=4)
        dpad.add_widget(Label())
        dpad.add_widget(self._btn('^', lambda *_: self.gw.do_move(0, -1)))
        dpad.add_widget(Label())
        dpad.add_widget(self._btn('<', lambda *_: self.gw.do_move(-1, 0)))
        dpad.add_widget(self._btn('v', lambda *_: self.gw.do_move(0, 1)))
        dpad.add_widget(self._btn('>', lambda *_: self.gw.do_move(1, 0)))
        bar.add_widget(dpad)

        funcs = BoxLayout(orientation='vertical', size_hint=(0.55, 1), spacing=4)
        top = BoxLayout(orientation='horizontal', spacing=4)
        top.add_widget(self._btn('撤销', lambda *_: self.gw.undo()))
        top.add_widget(self._btn('重置', lambda *_: self.gw.reset()))
        funcs.add_widget(top)
        bot = BoxLayout(orientation='horizontal', spacing=4)
        bot.add_widget(self._btn('上一关', lambda *_: self.gw.prev_level()))
        bot.add_widget(self._btn('下一关', lambda *_: self.gw.next_level()))
        funcs.add_widget(bot)
        bar.add_widget(funcs)
        bar_wrap.add_widget(bar)
        root.add_widget(bar_wrap)

        self.gw.load_level(0)
        Window.bind(on_key_down=self._on_key)
        return root

    def _btn(self, text, cb):
        b = Button(text=text, font_size='17sp', padding=(6, 4),
                   color=(0.97, 0.97, 0.97, 1), font_name=FONT)
        b.background_color = (0.22, 0.30, 0.44, 1)
        b.bind(on_press=cb)
        return b

    def _on_key(self, win, key, *args):
        m = {
            273: (0, -1), 274: (0, 1), 275: (1, 0), 276: (-1, 0),
            ord('w'): (0, -1), ord('s'): (0, 1),
            ord('d'): (1, 0), ord('a'): (-1, 0),
        }
        if key in m:
            self.gw.do_move(*m[key])
            return True
        if key in (ord('z'), ord('u')):
            self.gw.undo()
        if key == ord('r'):
            self.gw.reset()
        return False

    def _upd_info(self):
        g = self.gw.game
        if g:
            self.info.text = '第 %d/%d 关    步数: %d    推动: %d' % (
                self.gw.level_idx + 1, len(LEVELS), g.moves, g.pushes)

    def _on_win(self):
        if self.gw.level_idx == len(LEVELS) - 1:
            self.info.text = '*** 全部 %d 关通关！  总步数: %d ***' % (
                len(LEVELS), self.gw.game.moves)
        else:
            self.info.text = '第 %d 关过关！  步数: %d   >> 点「下一关」' % (
                self.gw.level_idx + 1, self.gw.game.moves)


if __name__ == '__main__':
    SokobanApp().run()
