[app]

# 应用名称 (显示在手机上)
title = Sokoban

# 包名 / 域名 (反向域名, 决定 APK 的 package id)
package.name = sokoban
package.domain = org.game

# 源码目录与入口 (buildozer 默认找 main.py)
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,ttf,otf

# 版本号 (也可用 git rev-parse --short HEAD)
version = 1.0

# Python 依赖: 仅需 kivy, 纯离线游戏无其他依赖
requirements = python3,kivy

# 竖屏, 适合手机单手操作
orientation = portrait

# 不全屏 (保留状态栏, 兼容性好)
fullscreen = 0

# Android SDK 配置
android.api = 31
android.minapi = 21
android.arch = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True

# 无任何权限 (离线游戏, 不联网/不读存储/不定位)
android.permissions =

# 启动画面背景色 (深灰, 与游戏背景一致)
presplash.color = #1F232B

# 日志过滤
android.logcat_filters = *:S python:D

# 构建后自动清理临时文件
buildozer_cmd = buildozer

[buildozer]
log_level = 2
warn_on_root = 1
