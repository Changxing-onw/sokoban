#!/bin/bash
# ============================================================
# WSL Ubuntu 一键搭建 buildozer 环境并打包推箱子 APK
# 用法: 在 Ubuntu 终端里执行  bash wsl_setup.sh
# ============================================================
set -e

echo "============================================================"
echo "  推箱子 APK 打包脚本"
echo "============================================================"

# ---- [1/6] 安装系统依赖 ----
echo ""
echo ">>> [1/6] 安装系统依赖 (需要 sudo 密码)..."
sudo apt update
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf \
    libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev \
    libtinfo5 cmake libffi-dev libssl-dev build-essential ccache

# ---- [2/6] 安装 buildozer ----
echo ""
echo ">>> [2/6] 安装 buildozer (Python 包)..."
pip3 install --user --upgrade pip
pip3 install --user --upgrade buildozer cython virtualenv
export PATH="$HOME/.local/bin:$PATH"

# ---- [3/6] 复制项目到 WSL 本地文件系统 ----
# 在 /mnt/e 下跑 buildozer 会很慢 (NTFS 挂载), 必须复制到本地
echo ""
echo ">>> [3/6] 复制项目到 ~/sokoban (WSL 本地)..."
SRC="/mnt/e/workbuddyfile/2026-07-19-22-47-53/sokoban"
rm -rf ~/sokoban
mkdir -p ~/sokoban
cp -r "$SRC"/* ~/sokoban/
cp -r "$SRC"/.gitignore ~/sokoban/ 2>/dev/null || true
cp -r "$SRC"/.github ~/sokoban/ 2>/dev/null || true
cd ~/sokoban
echo "项目已复制到: $(pwd)"

# ---- [4/6] 清理旧构建 ----
echo ""
echo ">>> [4/6] 清理旧构建缓存..."
rm -rf .buildozer bin

# ---- [5/6] 打包 APK ----
echo ""
echo ">>> [5/6] 开始打包 APK..."
echo "    首次构建会下载 Android SDK/NDK (约 2-3 GB)"
echo "    预计耗时 30-60 分钟, 请耐心等待..."
echo ""
buildozer android debug 2>&1 | tee build.log

# ---- [6/6] 输出结果 ----
echo ""
echo ">>> [6/6] 打包结果:"
if ls bin/*.apk 1>/dev/null 2>&1; then
    echo "============================================================"
    echo "  ✓ 打包成功!"
    echo "============================================================"
    ls -lh bin/*.apk
    echo ""
    echo "APK 文件路径 (WSL): ~/sokoban/bin/"
    echo "APK 文件路径 (Windows): E:\\workbuddyfile\\2026-07-19-22-47-53\\sokoban\\bin\\"
    echo ""
    echo "把 APK 传到手机安装即可。"
else
    echo "============================================================"
    echo "  ✗ 打包失败, 请查看 build.log"
    echo "============================================================"
    echo "常见问题:"
    echo "  - 内存不足: 关掉其他程序重试"
    echo "  - 网络中断: 重新跑 buildozer android debug (会断点续传)"
    echo "  - SDK 下载失败: 删掉 .buildozer 目录重试"
    exit 1
fi
