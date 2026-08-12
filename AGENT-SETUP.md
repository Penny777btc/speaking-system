# AGENT-SETUP.md — 给本地 AI Agent 的自动安装手册

> **你是一个拥有本地 shell 权限的 AI agent**(Codex / Claude Code / Cursor Agent 等)。
> 你的任务:替用户完成「口语学习系统」Obsidian 侧的全部安装与验收。
> 照本文逐步执行,每步自检并向用户报告。全部完成后,用户只剩两个必须亲手做的动作(见第 6 步)。
> 本手册已由 Claude 和 Codex CLI 各完整跑通一次(全新 Obsidian 库,含界面级验收),Codex 无人值守耗时约 90 秒。
> 如果你没有本地 shell 权限(例如你是网页版聊天 AI),请直接告诉用户:"我无法操作你的电脑,请改用 docs/安装指南.md 手动安装",不要假装执行。

## 怎么把本手册交给你的 agent(用户看这段)
**通用(任何有本地权限的 agent,推荐)**——打开 Codex / Claude Code / Cursor 的对话框,粘贴:
```
读取 https://raw.githubusercontent.com/Penny777btc/speaking-system/main/AGENT-SETUP.md 并严格照做,帮我完成安装
```
agent 会向你确认仓库路径并在每个动作前请求批准。

**Codex CLI 无人值守版(实测 93 秒完成)**——装了 ChatGPT 桌面版就自带 CLI(不在 PATH 里,藏在应用包内):
```
/Applications/ChatGPT.app/Contents/Resources/codex exec -C "<你的仓库路径>" \
  --approve-for-me --skip-git-repo-check \
  -c 'sandbox_workspace_write.network_access=true' \
  "读取 https://raw.githubusercontent.com/Penny777btc/speaking-system/main/AGENT-SETUP.md 并严格照做,帮我完成安装。仓库路径就是当前工作目录;不安装 Spaced Repetition;不要向我提问,按手册默认执行。"
```
三个坑:①`--approve-for-me` 与 `-s/--sandbox` 互斥,别同时给;②目标目录不是 git 仓库时必须加 `--skip-git-repo-check`;③联网靠 `-c 'sandbox_workspace_write.network_access=true'`,漏了会下载失败。

## 安全守则(最高优先级)
1. **绝不覆盖用户已有内容**:目标位置已存在 `English-Speaking-System` 文件夹时,立即停止并询问用户。
2. **改 JSON 配置一律「读取→合并→写回」**,禁止整文件覆盖——用户的 Obsidian 可能已有别的插件和快捷键。
3. 全程只写用户目录,不需要也不允许 sudo。
4. 含中文、空格或括号的路径全部加引号。

## 第 0 步:问用户五个问题

1. **Obsidian 仓库(vault)的绝对路径**。用户不清楚时这样引导:打开 Obsidian → 左下角仓库名 → 鼠标悬停可见路径;或者由你为 TA 新建一个空文件夹当作新仓库(之后在 Obsidian 里 Open folder as vault)。
2. **想练哪些领域?**(3–4 个,用于每天生成文章的选题轮换)。举例:AI、商业模式、创业、个人成长 / 医学、科研、职场沟通 / 旅行、美食、影视。用户没想法就用默认值。
3. **当前英语水平?** 给 CEFR 等级(A2 / B1 / B1+ / B2 / B2+)。不确定就用 B1+,以后每季度自己升级。
4. 是否顺便安装**可选**的复习闪卡插件 Spaced Repetition(默认不装,核心流程不依赖它)。
5. **是否配置「每晚 AI 自动整理」**(见第 5 步)。问的时候要说清楚这是什么:
   > 「我可以再配一个定时任务:每晚自动把你当天练到的表达和错误归类进库、重建复习闪卡、跑一遍数据体检。
   > 它会**定期在后台调用 AI**(消耗你的额度),所以要你明确同意。不配也完全能用——只是这些整理要你每周花 5 分钟手动做。
   > 现在配 / 以后再说?」

   默认**不配**,用户明确说要才做。

第 2、3 项你会在第 6 步用来**替用户把指令填好**——不要让用户自己去改一段 6000 字的文本。

以下用 `$VAULT` 指代用户给出的仓库路径。

## 第 1 步:下载系统文件
```bash
curl -fsSL -o /tmp/sps.zip https://github.com/Penny777btc/speaking-system/archive/refs/heads/main.zip
rm -rf /tmp/sps && mkdir -p /tmp/sps
# ⚠️ 不要用 macOS 自带 unzip:它解不了 zip 里的 UTF-8 中文文件名(Illegal byte sequence)
ditto -x -k /tmp/sps.zip /tmp/sps 2>/dev/null || python3 -m zipfile -e /tmp/sps.zip /tmp/sps
# 存在性护栏
[ -e "$VAULT/English-Speaking-System" ] && echo "已存在,停止并询问用户" || cp -R /tmp/sps/speaking-system-main/English-Speaking-System "$VAULT/"
# 顺便把仓库本体留一份在用户目录:闪卡脚本和(可选的)夜间任务都要用它,/tmp 会被系统清理
rm -rf "$HOME/speaking-system" && cp -R /tmp/sps/speaking-system-main "$HOME/speaking-system" && echo "仓库副本: $HOME/speaking-system"
```
✅ 自检:`ls "$VAULT/English-Speaking-System"` 应包含 00-Prompts、01-Templates、02-Daily-Logs、03-Expression-Bank、04-Error-Patterns、05-Dashboard、06-Roadmap、07-Review、README.md。

## 第 2 步:安装插件(Templater + Dataview,从各自官方 GitHub Releases)
```bash
install_plugin () {  # $1=插件目录名 $2=github repo
  local dir="$VAULT/.obsidian/plugins/$1"; mkdir -p "$dir"
  local tag=$(curl -fsSL "https://api.github.com/repos/$2/releases/latest" | python3 -c "import json,sys;print(json.load(sys.stdin)['tag_name'])")
  for f in main.js manifest.json styles.css; do
    curl -fsSL -o "$dir/$f" "https://github.com/$2/releases/download/$tag/$f" || true
  done
  echo "$1 -> $tag"
}
install_plugin templater-obsidian SilentVoid13/Templater
install_plugin dataview blacksmithgu/obsidian-dataview
# 可选:用户第 0 步同意才装
# install_plugin obsidian-spaced-repetition st3v3nmw/obsidian-spaced-repetition
```
✅ 自检:两个插件目录里的 `manifest.json` 都能读到 `"id"` 字段。

## 第 3 步:写配置(合并式,禁止覆盖)
```bash
python3 - "$VAULT" <<'PY'
import json, os, sys
V = sys.argv[1]; ob = os.path.join(V, ".obsidian")
os.makedirs(ob, exist_ok=True)
def merge(path, patch, must_take=()):
    # must_take 里的键:原值为空/缺失时才写(用户已有非空的自定义值时停下来问,不要静默跳过)
    data = {}
    if os.path.exists(path):
        try: data = json.load(open(path))
        except Exception: data = {}
    for k, v in patch.items():
        cur = data.get(k)
        if k in must_take:
            if cur in (None, "", [], {}):
                data[k] = v
            elif cur != v:
                print(f"⚠️ {path} 的 {k} 已是 {cur!r},与要写入的 {v!r} 冲突——请询问用户后再决定")
        else:
            data.setdefault(k, v)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(data, open(path, "w"), ensure_ascii=False, indent=2)
    print("merged:", path)
# 1) 启用插件(数组合并)
p = os.path.join(ob, "community-plugins.json")
cur = json.load(open(p)) if os.path.exists(p) else []
for x in ["templater-obsidian", "dataview"]:
    if x not in cur: cur.append(x)
json.dump(cur, open(p, "w"), ensure_ascii=False, indent=2); print("merged:", p)
# 2) Templater 模板目录
merge(os.path.join(ob, "plugins/templater-obsidian/data.json"),
      {"templates_folder": "English-Speaking-System/01-Templates"},
      must_take=("templates_folder",))  # Templater 装过就会有这个键(默认空串),setdefault 会静默失效
# 3) Dataview 开 JS
merge(os.path.join(ob, "plugins/dataview/data.json"), {"enableDataviewJs": True})
# 4) 一键归档快捷键(用户已占用该命令的绑定则保留原样)
merge(os.path.join(ob, "hotkeys.json"),
      {"templater-obsidian:create-new-note-from-template": [{"modifiers": ["Mod","Shift"], "key": "E"}]})
PY
```
✅ 自检:重新读取上述 4 个文件,确认 ①`community-plugins.json` 含两个插件 id ②`templates_folder` 的值**确实等于** `English-Speaking-System/01-Templates`(不是空串)③`enableDataviewJs` 为 true ④快捷键已写入 ⑤用户原有条目一个没丢。

## 第 4 步:重启 Obsidian(仅 macOS;其他系统请用户手动重启)
配置是外部写入的,Obsidian 必须重启才会读取(运行中的 Obsidian 退出时可能用内存里的旧配置回写覆盖你刚写的文件——所以先退出、确认配置仍在、再启动):
```bash
pgrep -x Obsidian >/dev/null && { osascript -e 'tell application "Obsidian" to quit'; sleep 3; }
# 重新校验第 3 步的 4 个文件仍然正确,若被回写覆盖则重写一次
open -a Obsidian
```
征得用户同意后再重启;用户正在编辑时先提醒保存。

## 第 5 步:配置每晚自动整理(**仅当用户在第 0 步明确同意**)

用户说不要就跳过这一步,直接进第 6 步。

### 先取任务提示词

从 `https://raw.githubusercontent.com/Penny777btc/speaking-system/main/docs/AI每晚自动整理.md` 抓取,取「任务提示词」代码块里的全文,把 `{{VAULT}}` 换成用户的仓库路径、`{{REPO}}` 换成你解压系统文件的目录(`/tmp/sps/speaking-system-main`,建议先把它拷到用户目录下持久保存,比如 `~/speaking-system`,否则 /tmp 会被清理)。

### 再按你自己的类型选调度方式

**如果你是 Claude Code**(或任何自带定时任务能力的 agent):用你自己的调度机制创建任务,时间设 22:15,内容就是上面那段提示词。

**如果你是 Codex / Cursor 等无调度器的 CLI agent**:用 macOS 的 launchd(比 cron 可靠,不需要额外的磁盘访问授权)。

```bash
mkdir -p "$HOME/speaking-system"   # 提示词和脚本的持久位置
cat > "$HOME/speaking-system/nightly-prompt.txt" <<'PROMPT'
<把替换好占位符的任务提示词整段写在这里>
PROMPT

CODEX=/Applications/ChatGPT.app/Contents/Resources/codex   # 按实际路径调整
cat > "$HOME/speaking-system/nightly.sh" <<EOF
#!/bin/bash
"$CODEX" exec --approve-for-me --skip-git-repo-check \
  -c 'sandbox_workspace_write.network_access=true' \
  "\$(cat "$HOME/speaking-system/nightly-prompt.txt")" \
  >> "$HOME/speaking-system/nightly.log" 2>&1
EOF
chmod +x "$HOME/speaking-system/nightly.sh"

cat > "$HOME/Library/LaunchAgents/com.speakingsystem.nightly.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.speakingsystem.nightly</string>
  <key>ProgramArguments</key>
  <array><string>/bin/bash</string><string>$HOME/speaking-system/nightly.sh</string></array>
  <key>StartCalendarInterval</key>
  <dict><key>Hour</key><integer>22</integer><key>Minute</key><integer>15</integer></dict>
  <key>RunAtLoad</key><false/>
</dict></plist>
EOF
launchctl unload "$HOME/Library/LaunchAgents/com.speakingsystem.nightly.plist" 2>/dev/null
launchctl load "$HOME/Library/LaunchAgents/com.speakingsystem.nightly.plist" && echo "定时任务已装载"
```

**其他系统**:用 cron 或任务计划程序,原理相同——定时把提示词喂给 agent。

### ✅ 自检并告诉用户怎么退出

- 确认 `launchctl list | grep speakingsystem` 有输出(或你自己的任务列表里能看到)
- **必须告诉用户卸载方法**(写进第 7 步交接里):
  `launchctl unload ~/Library/LaunchAgents/com.speakingsystem.nightly.plist && rm ~/Library/LaunchAgents/com.speakingsystem.nightly.plist`
- 提醒用户:今晚第一次运行时,你的 agent 可能会请求权限;第一次通过后就静默了

### ⚠️ 配了这个就不要再让用户开启动脚本

两者互斥:启动脚本会先把新表达搬进「📥 待归类」区,AI 晚上读日志时发现"已存在"就跳过了,结果表达永远卡在待归类、拿不到智能分类和使用统计。第 7 步交接话术里**不要再提「打开 Enable startup templates」**。

## 第 6 步:验收(文件级由你做,界面级引导用户做)
你自己验证:
- `$VAULT/English-Speaking-System/01-Templates/English Study 剪贴板归档.md` 存在
- community-plugins.json 含两个插件 id;两个 data.json 键正确
引导用户验证(逐条发给用户):
1. 按 `Cmd+Shift+E`(Windows `Ctrl+Shift+E`):应弹出模板选择框,里面有「English Study 剪贴板归档」→ 按 Esc 关闭
2. 打开 `05-Dashboard/进度仪表盘.md`:应渲染出表格而非代码块(说明 Dataview 已生效)

## 第 7 步:交接(把这段话连同指令一起交给用户)
**先按第 0 步收集的参数把指令个性化**,再放进剪贴板。把下面的 `DOMAINS`(顿号分隔)、`DOMAINS_SLASH`(斜杠分隔)、`LEVEL` 换成用户的答案:

```bash
python3 - "$VAULT/English-Speaking-System/00-Prompts/4-项目指令.md" <<'PY'
import sys, subprocess
DOMAINS = "AI、商业模式、创业、个人成长"      # ← 换成用户的领域(顿号分隔)
DOMAINS_SLASH = "AI/商业模式/创业/个人成长"    # ← 同上(斜杠分隔)
LEVEL = "B1+"                                  # ← 换成用户的水平

p = sys.argv[1]
full = open(p).read()
for a, b in [("兴趣领域:AI、商业模式、创业、个人成长。", f"兴趣领域:{DOMAINS}。"),
             ("从 AI/商业模式/创业/个人成长中轮换", f"从 {DOMAINS_SLASH} 中轮换"),
             ("话题从 AI/商业模式/创业/个人成长中选", f"话题从 {DOMAINS_SLASH} 中选"),
             ("【当前水平参数:B1+】", f"【当前水平参数:{LEVEL}】")]:
    full = full.replace(a, b)
open(p, "w").write(full)                       # 顺便把 vault 里的备份也个性化
block = full.split("```")[1].strip()
try:
    subprocess.run(["pbcopy"], input=block, text=True, check=True)
    print(f"✅ 指令已个性化({DOMAINS} / {LEVEL})并复制到剪贴板,共 {len(block)} 字")
except Exception:
    print(f"⚠️ 剪贴板不可用,请让用户手动复制:{p} 里的代码块")
PY
```

这样用户粘贴的就是**已经填好自己参数**的指令,不需要在一段 6000 字的文本里找地方改。

再顺手把浏览器打开到 ChatGPT 的项目页,省掉用户找路的时间(失败就跳过,不要报错中断):
```bash
open "https://chatgpt.com/projects" 2>/dev/null \
  || xdg-open "https://chatgpt.com/projects" 2>/dev/null \
  || echo "请手动打开 https://chatgpt.com/projects"
```
> 注意:你**只能把页面打开给用户**。创建项目、粘贴指令、保存这三步必须由用户亲手完成——ChatGPT 的项目是云端功能,没有公开 API,而用浏览器自动化去点它既需要接管登录态、又会因 UI 改版随时失效。不要尝试。

然后**原样输出**给用户:

**⚠️ 分叉**:如果第 5 步已经配了每晚 AI 整理,**删掉下面的 1️⃣ 整段**(两者互斥),改成一句:
> **1️⃣ 每晚自动整理已配好** — 每晚 22:15 我会自动帮你归类表达、合并错误、重建闪卡、做数据体检,第二天早上给你简报。不想要了就跑:`launchctl unload ~/Library/LaunchAgents/com.speakingsystem.nightly.plist && rm ~/Library/LaunchAgents/com.speakingsystem.nightly.plist`

否则用下面这段原文:

> 安装完成 ✅。插件、配置、快捷键我都写好了,**剩下三件我做不了的事**(约 3 分钟):
>
> **1️⃣ 打开自动整理开关(1 分钟)** — 这是唯一一个我无法替你写的设置:Templater 把「自动执行模板」这类危险开关存在**设备本地**,不在配置文件里(这是它的安全设计,防止恶意模板通过文件自动执行代码)。
> Obsidian 设置 → Templater → 滚到 **Startup templates** 区 → 打开 **Enable startup templates**(弹出风险框,勾选「I understand the risks」→ Enable)→ 下面的列表点 ➕ 填 `English-Speaking-System/01-Templates/自动整理.md` → 重启 Obsidian。
> 开了之后:每次打开 Obsidian 会自动整理表达/错误库、重建复习闪卡。不开也能用,但这些要你手动做。
>
> **2️⃣ 配置 ChatGPT(2 分钟)** — 指令已经按你的领域和水平填好,就在你的剪贴板里,直接粘贴即可。
> 我已经帮你打开项目页了(没打开就去 chatgpt.com/projects)→ **新建项目**(起名如「英语口语 B1→C1」)→ 进入项目 → 右上角 `⋯` → **编辑指令** → 粘贴 → 保存。
>
> ⚠️ **必须建「项目」,不能贴进普通对话或账号的自定义指令**——原因有二:①项目里每个新对话都自动带着指令;②项目能引用同项目内的历史对话,而「昨天犯的错今天重测」正是靠这个。贴错地方的表现是:说触发词没反应,或者今天完全不知道昨天练过什么。
>
> **3️⃣ 验证并开练** — 在项目里新开对话,发 **「每日输入」**。
> 成功的样子:它给你一篇约 300 词的英文短文(你选的领域)+ 5 个**加粗**的表达和中文解释,然后开始让你用第一个表达造句。
> 如果它只是普通闲聊 → 检查三件事:你在项目**里面**吗?指令保存了吗?保存后**新开对话**了吗?
> 遇到其他问题看 docs/常见问题.md。
>
> 补充:我不需要你关闭 Obsidian 的「安全模式」——插件是我直接装进 `.obsidian/plugins/` 的,不走插件市场。手动安装的人才需要关。

## 执行时的已知坑(来自 docs/维护知识库.md 的实战记录)
- 外部改插件配置后必须重启 Obsidian;且要防它退出时用内存旧配置回写(第 4 步已含)。
- Templater 的 Enable startup templates / Trigger on file creation 总闸存在设备 localStorage,**写配置文件永远打不开**,只能用户在界面点(所以放在第 6 步交接)。
- Spaced Repetition v1.15+ 的配置嵌套在 data.json 的 `settings` 键下,顶层同名键会被静默忽略;卡组标签默认是复数 `#flashcards`,顺着默认走,别改。
- GitHub API 匿名限流 60 次/小时;失败时等待或提示用户稍后再试,不要重试轰炸。
- 文件名含括号/空格/中文,所有路径必须加引号。
- **解压必须用 ditto(macOS)或 python3 -m zipfile,绝不能用 unzip**——BSD unzip 遇到 UTF-8 中文文件名会 Illegal byte sequence,核心文件全部解压失败。
