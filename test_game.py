#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""推箱子逻辑测试: 不开窗口, 验证关卡解析/移动/撤销/胜利判定"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import Game, LEVELS


def test_parse():
    print("=== 关卡解析 ===")
    for i, lv in enumerate(LEVELS):
        g = Game(lv)
        assert len(g.boxes) == len(g.targets), \
            "Level %d: 箱子 %d != 目标 %d" % (i + 1, len(g.boxes), len(g.targets))
        assert not g.is_won(), "Level %d 初始就赢了?" % (i + 1)
        print("Level %d: OK  箱子=%d 目标=%d 玩家=%s 地板=%d" % (
            i + 1, len(g.boxes), len(g.targets), g.player, len(g.floors)))


def test_level1():
    print("\n=== Level 1 通关 ===")
    g = Game(LEVELS[0])
    # 关卡1: # @$. #  玩家(2,2) 箱子(3,2) 目标(4,2), 向右推
    g.move(1, 0)
    assert g.is_won(), "Level 1 推完后应胜利"
    print("Level 1 通关! moves=%d pushes=%d" % (g.moves, g.pushes))


def test_undo():
    print("\n=== 撤销测试 ===")
    g = Game(LEVELS[0])
    g.move(1, 0)
    assert g.is_won()
    g.undo()
    assert g.moves == 0, "undo 后 moves 应为 0, 实际 %d" % g.moves
    assert g.pushes == 0
    assert not g.is_won(), "undo 后不应胜利"
    print("撤销 OK")


def test_wall_block():
    print("\n=== 撞墙测试 ===")
    g = Game(LEVELS[0])
    p0 = g.player
    g.move(0, -1)  # 往上走, 上面是墙或地板
    # 至少不会穿墙
    px, py = g.player
    assert (px, py) not in g.walls, "玩家不能穿墙!"
    print("撞墙防护 OK")


def test_level2():
    print("\n=== Level 2 通关 ===")
    g = Game(LEVELS[1])
    # Level2: "# .$ $.#"  玩家(3,3)
    # 左箱(3,2)->目标(2,2): 向左推, 玩家需到(4,2)
    # 右箱(5,2)->目标(6,2): 向右推, 玩家在(4,2)
    g.move(1, 0)   # (3,3)->(4,3)
    g.move(0, -1)  # (4,3)->(4,2)
    g.move(-1, 0)  # 推左箱 (3,2)->(2,2), 玩家到(3,2)
    assert (2, 2) in g.boxes, "左箱应到目标 (2,2)"
    g.move(1, 0)   # (3,2)->(4,2)
    g.move(1, 0)   # 推右箱 (5,2)->(6,2), 玩家到(5,2)
    assert g.is_won(), "Level 2 应胜利"
    print("Level 2 通关! moves=%d pushes=%d" % (g.moves, g.pushes))


if __name__ == '__main__':
    test_parse()
    test_level1()
    test_undo()
    test_wall_block()
    test_level2()
    print("\n=== 全部测试通过 ===")
