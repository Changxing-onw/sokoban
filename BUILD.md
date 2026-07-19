# 推箱子 Sokoban - 打包说明

纯 Python (Kivy) 离线推箱子游戏, 可打包为安卓 APK。

## 项目结构

```
sokoban/
├── main.py              # 游戏主程序 (Kivy)
├── test_game.py         # 逻辑测试 (不开窗口)
├── buildozer.spec       # buildozer 打包配置
├── .github/workflows/
│   └── build_apk.yml    # GitHub Actions 云端打包
├── .gitignore
└── BUILD.md             # 本文件
```

## 在 Windows 上运行 (开发/测试)

```bash
# venv 已建在 D:\python_envs\sokoban
D:\python_envs\sokoban\Scripts\python.exe main.py
```

操作: 方向键/WASD 移动, 触摸滑动, U=撤销, R=重置。

## 打包为安卓 APK

### 方式一: WSL + buildozer (本地)

> Windows 原生不支持 buildozer, 必须用 WSL (Ubuntu)。

```bash
# 1. 启用 WSL (管理员 PowerShell)
wsl --install -d Ubuntu

# 2. 进入 WSL, 装依赖
sudo apt update && sudo apt install -y python3 python3-pip openjdk-17-jdk autoconf automake libtool
pip3 install buildozer cython==0.29.36

# 3. 把项目拷进 WSL, 在项目目录执行
cd /mnt/e/workbuddyfile/2026-07-19-22-47-53/sokoban
buildozer -v android debug
# 首次构建约 30-60 分钟 (下载 Android SDK/NDK)
# 产出: bin/sokoban-1.0-arm64-v8a_armeabi-v7a-debug.apk
```

### 方式二: GitHub Actions (云端, 推荐)

无需本地 WSL, 把项目推到 GitHub, 自动打包:

```bash
git init && git add . && git commit -m "sokoban"
git remote add origin https://github.com/<你的用户名>/sokoban.git
git push -u origin main
# 打 tag 触发构建, 或在 Actions 页面手动运行
git tag v1.0 && git push origin v1.0
```

构建完成后, 在仓库 Actions → 对应 run → Artifacts 下载 `sokoban-apk`。

## 安装到手机

将 APK 传到手机, 开启「允许安装未知来源应用」, 点击安装即可。
游戏完全离线, 无需任何权限。
