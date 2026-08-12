#!/bin/bash
# 打包一个「开箱即用」的离线包 —— 给访问不了 GitHub 的用户
#
# 包里什么都有:系统文件、两个插件、全部文档、单独的 ChatGPT 指令文本。
# 用户下载后解压即可安装,全程不需要访问 GitHub。
#
# 用法(需要你自己能上 GitHub,因为要下载插件):
#   bash scripts/make_offline_bundle.sh
# 产物:~/Desktop/口语系统-完整包.zip
set -eu

SRC="$(cd "$(dirname "$0")/.." && pwd)"
WORK="$(mktemp -d)"
OUT="$HOME/Desktop/口语系统-完整包.zip"
B="$WORK/口语系统-完整包"
mkdir -p "$B"

echo "① 复制系统文件..."
mkdir -p "$B/1-把这个文件夹拖进Obsidian"
cp -R "$SRC/English-Speaking-System" "$B/1-把这个文件夹拖进Obsidian/"

echo "② 下载 Obsidian 插件(这样用户不用自己装)..."
dl_plugin () {  # $1=插件目录名 $2=repo $3=显示名
  local dir="$B/2-插件-装不上时用/$1"; mkdir -p "$dir"
  local tag
  tag=$(curl -fsSL "https://api.github.com/repos/$2/releases/latest" | python3 -c "import json,sys;print(json.load(sys.stdin)['tag_name'])")
  for f in main.js manifest.json styles.css; do
    curl -fsSL -o "$dir/$f" "https://github.com/$2/releases/download/$tag/$f" 2>/dev/null || true
  done
  echo "   $3 $tag"
}
dl_plugin templater-obsidian SilentVoid13/Templater "Templater"
dl_plugin dataview blacksmithgu/obsidian-dataview "Dataview"

cat > "$B/2-插件-装不上时用/怎么用.md" <<'PLUG'
# 插件装不上时用这里的文件

**优先还是走 Obsidian 的插件市场**(设置 → 第三方插件 → 关闭安全模式 → 浏览 → 搜索安装)。
只有当插件市场连不上时,才用这个文件夹里的现成文件:

1. 打开你的 Obsidian 仓库文件夹(访达里按 `Cmd+Shift+G` 输入仓库路径)
2. 找到里面的 `.obsidian` 文件夹(隐藏文件夹,访达里按 `Cmd+Shift+.` 显示隐藏文件)
3. 如果没有 `plugins` 子文件夹就新建一个
4. 把本文件夹里的 `templater-obsidian` 和 `dataview` 两个文件夹整个拷进 `.obsidian/plugins/`
5. 重启 Obsidian → 设置 → 第三方插件 → 关闭安全模式 → 在已安装列表里**启用**这两个插件

装好后回到「👉从这里开始.md」继续配置。

---
插件来源与版权:
- Templater — MIT License,作者 SilentVoid13,https://github.com/SilentVoid13/Templater
- Dataview — MIT License,作者 blacksmithgu,https://github.com/blacksmithgu/obsidian-dataview

本包仅为方便分发而附带其官方发布文件,未做任何修改。
PLUG

echo "③ 提取 ChatGPT 指令为纯文本(方便直接复制)..."
python3 - "$SRC" "$B" <<'PY'
import sys
src, b = sys.argv[1], sys.argv[2]
block = open(f"{src}/English-Speaking-System/00-Prompts/4-项目指令.md").read().split("```")[1].strip()
head = """【使用说明】
下面整段就是要粘进 ChatGPT 项目的指令。

粘贴前先改三处(都在最开头两行):
  1. 兴趣领域 —— 把「AI、商业模式、创业、个人成长」换成你关心的 3-4 个领域
     (注意:这个领域在全文出现 3 次,建议用编辑器的「全部替换」)
  2. 水平参数 —— 把【当前水平参数:B1+】换成你的水平,不确定就保持 B1+
  3. 目标 —— 把「一年内从 B1 到 C1」换成你的目标

改完后,从下面这条分割线之后开始,全选复制。
具体贴到哪里、怎么建项目,看「说明文档/配置ChatGPT项目.md」。

================== 从下一行开始复制 ==================

"""
open(f"{b}/ChatGPT指令-改完直接复制.txt", "w").write(head + block + "\n")
print("   已生成 ChatGPT指令-改完直接复制.txt")
PY

echo "④ 复制说明文档..."
mkdir -p "$B/说明文档"
for f in 手动安装 配置ChatGPT项目 安装验收 日常流程 常见问题 进阶 AI每晚自动整理; do
  cp "$SRC/docs/$f.md" "$B/说明文档/" 2>/dev/null || true
done
cp -R "$SRC/scripts" "$B/说明文档/脚本-可选" 2>/dev/null || true

echo "⑤ 生成入口文档..."
cat > "$B/👉从这里开始.md" <<'START'
# 👉 从这里开始

> 这是一套用 **ChatGPT 语音 + Obsidian** 练英语口语的系统。
> 每天说三句触发词练 40 分钟,系统自动帮你记录错误、评分、安排复习。
> **这个包里什么都有,不需要联网下载任何东西**(除了 ChatGPT 本身)。

---

## 你需要先准备

1. **Obsidian** —— 免费笔记软件,官网 obsidian.md 下载(电脑版)
2. **ChatGPT 账号** —— 免费版就能用,Plus 的语音体验更好

---

## 三步装好(约 15 分钟)

### 第 1 步:把系统放进 Obsidian

1. 打开 Obsidian,新建一个仓库(或用你已有的)
2. 打开文件夹 **`1-把这个文件夹拖进Obsidian`**
3. 把里面的 **`English-Speaking-System`** 整个文件夹,拖进你的 Obsidian 仓库文件夹
4. 回到 Obsidian,左边应该能看到它

### 第 2 步:装两个插件

Obsidian 设置 → 第三方插件 → 关闭「安全模式」→ 点「浏览」→ 搜索安装并启用:

- **Templater**(一键归档要用)
- **Dataview**(进度仪表盘要用)

> 🇨🇳 **如果插件市场连不上**,用本包的 `2-插件-装不上时用` 文件夹,里面有现成文件和图文说明。

装好后还要配三件事(详见 `说明文档/手动安装.md` 第 2 步):
- Dataview 设置里打开 **Enable JavaScript Queries**
- Templater 的模板目录填 `English-Speaking-System/01-Templates`
- 给「Templater: Create new note from template」绑快捷键 `Cmd+Shift+E`

### 第 3 步:配置 ChatGPT

1. 打开 **`ChatGPT指令-改完直接复制.txt`**,按说明改三处,复制整段
2. 在 ChatGPT 里**新建一个项目**(不是普通对话!),把指令粘进项目的「编辑指令」保存
3. ⚠️ 保存后**新开一个对话**才会生效

> 详细图文步骤看 `说明文档/配置ChatGPT项目.md`,里面讲了为什么必须建「项目」——贴错地方会失效且不报错。

---

## 装完了?跑一遍验收

打开 `说明文档/安装验收.md`,3 分钟用测试数据确认整条链路通了。**别跳过**,不然可能第一次真实练完才发现存不进去。

---

## 然后怎么用

每天在 ChatGPT 项目里说三句话:

1. **「每日输入」** —— 它给你一篇短文并朗读,教 5 个地道表达,逐个陪你操练
2. **「开始口语练习」** —— 先重测你之前的错误,再给你当天的输出任务
3. **「按模板复盘」** —— 输出完整记录(退出语音、用打字发)

然后点**复制** → 切到 Obsidian → 按 `Cmd+Shift+E` → 回车,当天的记录就自动存好了。

完整说明看 `说明文档/日常流程.md`。

---

## 遇到问题

- 装的时候卡住 → `说明文档/手动安装.md` 末尾的故障表
- 用的时候有疑问 → `说明文档/常见问题.md`
- 想要复习闪卡、发音朗读等额外功能 → `说明文档/进阶.md`

---

## 这套系统的来历

灵感来自 Gloria 在 X 上分享的方法:「光练不记,等于白练」。
在其基础上加了:B1→C1 的季度爬坡路线、错误重测闭环、表达毕业机制、证据锚定的评分体系。
经过真实用户连续多日的高强度使用打磨。

祝你练得开心 🎙️
START

echo "⑥ 打包..."
rm -f "$OUT"
(cd "$WORK" && zip -qr "$OUT" "口语系统-完整包" -x "*.DS_Store")
rm -rf "$WORK"
echo ""
echo "✅ 完成:$OUT"
echo "   大小:$(du -h "$OUT" | cut -f1)"
echo "   可以直接发微信 / 传网盘了"
