#!/bin/bash
# 用法: install_plugins.sh <vault绝对路径>
# 从官方 GitHub Releases 安装 Templater + Dataview,写入启用列表与基础配置
set -e
V="$1"
[ -d "$V" ] || { echo "vault not found: $V"; exit 1; }
mkdir -p "$V/.obsidian/plugins/templater-obsidian" "$V/.obsidian/plugins/dataview"
DL() { curl -sL -o "$2" "$1"; }
TPL_TAG=$(curl -s https://api.github.com/repos/SilentVoid13/Templater/releases/latest | python3 -c "import json,sys;print(json.load(sys.stdin)['tag_name'])")
DVW_TAG=$(curl -s https://api.github.com/repos/blacksmithgu/obsidian-dataview/releases/latest | python3 -c "import json,sys;print(json.load(sys.stdin)['tag_name'])")
for f in main.js manifest.json styles.css; do
  DL "https://github.com/SilentVoid13/Templater/releases/download/$TPL_TAG/$f" "$V/.obsidian/plugins/templater-obsidian/$f"
  DL "https://github.com/blacksmithgu/obsidian-dataview/releases/download/$DVW_TAG/$f" "$V/.obsidian/plugins/dataview/$f"
done
printf '%s' '["templater-obsidian","dataview"]' > "$V/.obsidian/community-plugins.json"
cat > "$V/.obsidian/plugins/dataview/data.json" <<'JSON'
{"enableDataviewJs": true}
JSON
cat > "$V/.obsidian/plugins/templater-obsidian/data.json" <<'JSON'
{"templates_folder": "English-Speaking-System/01-Templates"}
JSON
cat > "$V/.obsidian/hotkeys.json" <<'JSON'
{"templater-obsidian:create-new-note-from-template": [{"modifiers": ["Mod","Shift"], "key": "E"}]}
JSON
echo "plugins installed (Templater $TPL_TAG, Dataview $DVW_TAG). 重启 Obsidian 生效。"
