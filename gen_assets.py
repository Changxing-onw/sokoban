#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成推箱子游戏素材 PNG，输出到 assets/ 目录。

素材清单 (均 128x128, RGBA):
  floor.png / wall.png / target.png
  box.png / box_ok.png
  player_down.png / player_up.png / player_left.png / player_right.png
"""

import os
import random
from PIL import Image, ImageDraw

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
os.makedirs(OUT, exist_ok=True)

SZ = 128


def canvas():
    img = Image.new('RGBA', (SZ, SZ), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)


def save(img, name):
    img.save(os.path.join(OUT, name))
    print('  saved', name)


# ---------------- 地板（亮浅灰蓝石板） ----------------
def make_floor():
    img, d = canvas()
    # 明显提亮：接近浅白偏冷调，告别灰蒙蒙
    base = (198, 204, 216)
    img.paste(base + (255,), (0, 0, SZ, SZ))
    # 石板纹理：随机明暗斑点
    rnd = random.Random(42)
    for _ in range(90):
        x, y = rnd.randint(2, SZ - 3), rnd.randint(2, SZ - 3)
        delta = rnd.randint(-14, 12)
        c0 = max(0, min(255, base[0] + delta))
        c1 = max(0, min(255, base[1] + delta))
        c2 = max(0, min(255, base[2] + delta))
        img.putpixel((x, y), (c0, c1, c2, 255))
    # 顶部高光（立体感）
    d.line([(2, 2), (SZ - 3, 2)], fill=(228, 234, 244, 255), width=2)
    d.line([(2, 2), (2, SZ - 3)], fill=(218, 224, 236, 255), width=1)
    # 底部暗边
    d.line([(2, SZ - 3), (SZ - 3, SZ - 3)], fill=(158, 166, 180, 255), width=2)
    d.line([(SZ - 3, 2), (SZ - 3, SZ - 3)], fill=(158, 166, 180, 255), width=1)
    # 内框描边
    d.rectangle([0, 0, SZ - 1, SZ - 1], outline=(150, 158, 172, 255), width=1)
    # 四角小钉（石板拼接感）
    for cx, cy in [(8, 8), (SZ - 9, 8), (8, SZ - 9), (SZ - 9, SZ - 9)]:
        d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2],
                  fill=(138, 146, 160, 255))
    return img


# ---------------- 砖墙（深棕灰，和亮地板形成对比） ----------------
def make_wall():
    img, d = canvas()
    img.paste((78, 72, 68, 255), (0, 0, SZ, SZ))
    bh = SZ // 4       # 4 行砖
    bw = SZ // 2       # 砖宽
    for row in range(4):
        y0 = row * bh
        offset = (bw // 2) if row % 2 else 0
        for col in range(-1, 3):
            x0 = col * bw + offset
            x1 = x0 + bw
            shade = (row * 7 + col * 13) % 22 - 11
            base = (78 + shade, 72 + shade, 68 + shade, 255)
            d.rectangle([x0 + 1, y0 + 1, x1 - 1, y0 + bh - 1], fill=base)
        # 横向灰浆线
        d.line([(0, y0), (SZ, y0)], fill=(44, 40, 36, 255), width=2)
    # 砖缝竖线
    for row in range(4):
        y0 = row * bh
        offset = (bw // 2) if row % 2 else 0
        for col in range(-1, 3):
            x = col * bw + offset
            d.line([(x, y0), (x, y0 + bh)], fill=(44, 40, 36, 255), width=2)
    # 顶部高光
    d.line([(1, 1), (SZ - 2, 1)], fill=(104, 96, 90, 255), width=1)
    d.rectangle([0, 0, SZ - 1, SZ - 1], outline=(36, 32, 28, 255), width=2)
    return img


# ---------------- 目标点 ----------------
def make_target():
    img, d = canvas()
    cx = cy = SZ // 2
    # 发光晕
    for r, a in [(46, 25), (38, 45), (30, 75)]:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 150, 50, a))
    # 圆环
    d.ellipse([cx - 24, cy - 24, cx + 24, cy + 24],
              outline=(255, 160, 60, 255), width=4)
    # 中心十字
    d.line([(cx - 9, cy), (cx + 9, cy)], fill=(255, 210, 110, 255), width=3)
    d.line([(cx, cy - 9), (cx, cy + 9)], fill=(255, 210, 110, 255), width=3)
    return img


# ---------------- 木箱 ----------------
def make_box():
    img, d = canvas()
    m = 10
    # 主体
    d.rounded_rectangle([m, m, SZ - m, SZ - m], radius=8,
                        fill=(196, 140, 58, 255))
    # 木纹横线
    for y in [30, 64, 98]:
        d.line([(m + 6, y), (SZ - m - 6, y)], fill=(150, 100, 40, 255), width=2)
    # 顶部高光
    d.line([(m + 4, m + 4), (SZ - m - 4, m + 4)],
           fill=(232, 184, 105, 255), width=2)
    # 左侧高光
    d.line([(m + 4, m + 4), (m + 4, SZ - m - 4)],
           fill=(216, 168, 90, 255), width=2)
    # 4 角金属包角
    cs = 16
    for cx, cy in [(m, m), (SZ - m - cs, m),
                   (m, SZ - m - cs), (SZ - m - cs, SZ - m - cs)]:
        d.rectangle([cx, cy, cx + cs, cy + cs], fill=(90, 92, 102, 255))
        d.rectangle([cx, cy, cx + cs, cy + cs],
                    outline=(55, 57, 67, 255), width=1)
        # 包角小钉
        d.ellipse([cx + cs // 2 - 2, cy + cs // 2 - 2,
                   cx + cs // 2 + 2, cy + cs // 2 + 2],
                  fill=(160, 162, 172, 255))
    # 外边框
    d.rounded_rectangle([m, m, SZ - m, SZ - m], radius=8,
                        outline=(120, 80, 30, 255), width=2)
    return img


# ---------------- 箱子到位 ----------------
def make_box_ok():
    img, d = canvas()
    m = 10
    # 外发光
    d.rounded_rectangle([m - 3, m - 3, SZ - m + 3, SZ - m + 3],
                        radius=11, fill=(60, 180, 100, 90))
    # 主体
    d.rounded_rectangle([m, m, SZ - m, SZ - m], radius=8,
                        fill=(77, 200, 120, 255))
    # 顶部高光
    d.line([(m + 4, m + 4), (SZ - m - 4, m + 4)],
           fill=(170, 245, 195, 255), width=2)
    # 白色对勾
    cx = cy = SZ // 2
    d.line([(cx - 20, cy + 4), (cx - 6, cy + 18)],
           fill=(255, 255, 255, 255), width=7)
    d.line([(cx - 6, cy + 18), (cx + 24, cy - 16)],
           fill=(255, 255, 255, 255), width=7)
    # 外边框
    d.rounded_rectangle([m, m, SZ - m, SZ - m], radius=8,
                        outline=(40, 150, 80, 255), width=2)
    return img


# ---------------- 玩家工具函数 ----------------
def draw_body(d, cx):
    """蓝色身体 + 高光"""
    d.rounded_rectangle([cx - 26, 62, cx + 26, 110], radius=10,
                        fill=(60, 140, 230, 255))
    d.line([(cx - 20, 66), (cx - 20, 100)], fill=(120, 185, 250, 255), width=3)


def draw_limbs(d, cx):
    """手脚"""
    # 手
    d.ellipse([cx - 34, 70, cx - 22, 84], fill=(255, 220, 180, 255))
    d.ellipse([cx + 22, 70, cx + 34, 84], fill=(255, 220, 180, 255))
    # 脚
    d.rounded_rectangle([cx - 22, 108, cx - 6, 120], radius=4,
                        fill=(40, 40, 50, 255))
    d.rounded_rectangle([cx + 6, 108, cx + 22, 120], radius=4,
                        fill=(40, 40, 50, 255))


# ---------------- 玩家朝下 (正面) ----------------
def make_player_down():
    img, d = canvas()
    cx = SZ // 2
    draw_body(d, cx)
    # 头
    d.ellipse([cx - 22, 16, cx + 22, 60], fill=(255, 220, 180, 255))
    # 头发顶
    d.chord([cx - 22, 12, cx + 22, 50], 180, 360, fill=(70, 50, 35, 255))
    # 眼睛
    d.ellipse([cx - 13, 35, cx - 5, 43], fill=(30, 30, 40, 255))
    d.ellipse([cx + 5, 35, cx + 13, 43], fill=(30, 30, 40, 255))
    # 嘴
    d.arc([cx - 7, 46, cx + 7, 56], 0, 180, fill=(180, 100, 80, 255), width=2)
    draw_limbs(d, cx)
    return img


# ---------------- 玩家朝上 (背面) ----------------
def make_player_up():
    img, d = canvas()
    cx = SZ // 2
    draw_body(d, cx)
    # 头 (整圆头发色)
    d.ellipse([cx - 22, 16, cx + 22, 60], fill=(70, 50, 35, 255))
    # 后脑勺发丝纹理
    d.arc([cx - 14, 24, cx + 14, 56], 200, 340, fill=(48, 33, 23, 255), width=2)
    d.arc([cx - 18, 22, cx + 18, 58], 200, 340, fill=(48, 33, 23, 255), width=1)
    draw_limbs(d, cx)
    return img


# ---------------- 玩家朝左 (侧面) ----------------
def make_player_left():
    img, d = canvas()
    cx = SZ // 2
    draw_body(d, cx)
    # 头
    d.ellipse([cx - 22, 16, cx + 22, 60], fill=(255, 220, 180, 255))
    # 头发 (右后侧 + 顶部)
    d.chord([cx - 22, 12, cx + 22, 52], 250, 360 + 90, fill=(70, 50, 35, 255))
    # 一只眼在左侧
    d.ellipse([cx - 15, 35, cx - 7, 43], fill=(30, 30, 40, 255))
    # 鼻子小提示
    d.ellipse([cx - 20, 42, cx - 16, 47], fill=(240, 195, 160, 255))
    # 手 (左手前伸)
    d.ellipse([cx - 38, 72, cx - 24, 86], fill=(255, 220, 180, 255))
    d.ellipse([cx + 22, 70, cx + 34, 84], fill=(255, 220, 180, 255))
    # 脚
    d.rounded_rectangle([cx - 20, 108, cx - 4, 120], radius=4,
                        fill=(40, 40, 50, 255))
    d.rounded_rectangle([cx + 4, 108, cx + 20, 120], radius=4,
                        fill=(40, 40, 50, 255))
    return img


# ---------------- 玩家朝右 (镜像) ----------------
def make_player_right():
    return make_player_left().transpose(Image.FLIP_LEFT_RIGHT)


def main():
    print('Generating assets to:', OUT)
    save(make_floor(), 'floor.png')
    save(make_wall(), 'wall.png')
    save(make_target(), 'target.png')
    save(make_box(), 'box.png')
    save(make_box_ok(), 'box_ok.png')
    save(make_player_down(), 'player_down.png')
    save(make_player_up(), 'player_up.png')
    save(make_player_left(), 'player_left.png')
    save(make_player_right(), 'player_right.png')
    print('Done. %d files.' % 9)


if __name__ == '__main__':
    main()
