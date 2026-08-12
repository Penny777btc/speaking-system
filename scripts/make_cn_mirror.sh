#!/bin/bash
# 生成「国内镜像版」——把所有 GitHub 链接换成 Gitee 链接
#
# 用法:
#   1. 先在 Gitee 上导入本仓库(见 docs/分享给大陆用户.md)
#   2. 在本仓库根目录运行:
#        bash scripts/make_cn_mirror.sh <你的Gitee用户名> [仓库名]
#   3. 它会在 ../speaking-system-cn/ 生成一份改好链接的副本
#   4. 把那份副本推到你的 Gitee 仓库
#
# 为什么需要:即使文件镜像到了 Gitee,文档里写死的 raw.githubusercontent.com
# 链接(agent 抓取安装手册用)在大陆依然打不开,必须一并替换。
set -eu

USER="${1:?用法: bash scripts/make_cn_mirror.sh <Gitee用户名> [仓库名]}"
REPO="${2:-speaking-system}"
SRC="$(cd "$(dirname "$0")/.." && pwd)"
DST="$(dirname "$SRC")/speaking-system-cn"

echo "源: $SRC"
echo "目标: $DST"
rm -rf "$DST"
# 用 git archive 避免复制 .git
mkdir -p "$DST"
(cd "$SRC" && git archive HEAD) | tar -x -C "$DST"

python3 - "$DST" "$USER" "$REPO" <<'PY'
import os, sys
dst, user, repo = sys.argv[1], sys.argv[2], sys.argv[3]
GH_RAW  = "https://raw.githubusercontent.com/Penny777btc/speaking-system/main"
GH_BLOB = "https://github.com/Penny777btc/speaking-system/blob/main"
GH_ZIP  = "https://github.com/Penny777btc/speaking-system/archive/refs/heads/main.zip"
GT_RAW  = f"https://gitee.com/{user}/{repo}/raw/main"
GT_BLOB = f"https://gitee.com/{user}/{repo}/blob/main"
GT_ZIP  = f"https://gitee.com/{user}/{repo}/repository/archive/main.zip"
pairs = [(GH_ZIP, GT_ZIP), (GH_RAW, GT_RAW), (GH_BLOB, GT_BLOB),
         ("https://github.com/Penny777btc/speaking-system", f"https://gitee.com/{user}/{repo}")]
n = 0
for root, dirs, files in os.walk(dst):
    if ".git" in root: continue
    for f in files:
        if not f.endswith((".md", ".sh", ".py")): continue
        p = os.path.join(root, f)
        s = open(p, errors="ignore").read(); o = s
        for a, b in pairs: s = s.replace(a, b)
        if s != o:
            open(p, "w").write(s); n += 1
print(f"已替换 {n} 个文件里的链接")

# 在 README 顶部加国内版说明
p = os.path.join(dst, "README.md")
s = open(p).read()
s = s.replace("# 🎙️ Speaking System", """> 🇨🇳 **这是国内镜像版**,链接已指向 Gitee。原版在 GitHub(内容相同)。
> ⚠️ **大陆用户请优先走「手动安装」**——自动安装需要从 GitHub 下载 Obsidian 插件,可能连不上。
> 手动安装走 Obsidian 自带的插件市场,通常不受影响。

# 🎙️ Speaking System""", 1)
open(p, "w").write(s)
print("已在 README 顶部加国内版提示")
PY

echo ""
echo "✅ 完成。下一步:"
echo "   cd \"$DST\""
echo "   git init && git add -A && git commit -m 'CN mirror'"
echo "   git remote add origin https://gitee.com/$USER/$REPO.git"
echo "   git push -u origin main --force"
