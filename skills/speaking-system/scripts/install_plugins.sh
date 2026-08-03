#!/bin/bash
# 用法: install_plugins.sh <vault绝对路径> [系统文件夹名]
# 从官方 GitHub Releases 安装 Templater + Dataview,并安全合并基础配置
set -eu
[ "$#" -ge 1 ] || { echo "usage: install_plugins.sh <vault绝对路径> [系统文件夹名]"; exit 2; }
V="$1"
SYSTEM_FOLDER="${2:-Speaking-System}"
[ -d "$V" ] || { echo "vault not found: $V"; exit 1; }
mkdir -p "$V/.obsidian/plugins/templater-obsidian" "$V/.obsidian/plugins/dataview"
DL() { curl -fsSL -o "$2" "$1"; }
TPL_TAG=$(curl -fsSL https://api.github.com/repos/SilentVoid13/Templater/releases/latest | python3 -c "import json,sys;print(json.load(sys.stdin)['tag_name'])")
DVW_TAG=$(curl -fsSL https://api.github.com/repos/blacksmithgu/obsidian-dataview/releases/latest | python3 -c "import json,sys;print(json.load(sys.stdin)['tag_name'])")
for f in main.js manifest.json styles.css; do
  DL "https://github.com/SilentVoid13/Templater/releases/download/$TPL_TAG/$f" "$V/.obsidian/plugins/templater-obsidian/$f"
  DL "https://github.com/blacksmithgu/obsidian-dataview/releases/download/$DVW_TAG/$f" "$V/.obsidian/plugins/dataview/$f"
done
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
python3 "$SCRIPT_DIR/configure_obsidian.py" "$V" "$SYSTEM_FOLDER"
echo "plugins installed (Templater $TPL_TAG, Dataview $DVW_TAG). 重启 Obsidian 生效。"
