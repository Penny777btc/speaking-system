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

## 第 0 步:问用户两个问题
1. **Obsidian 仓库(vault)的绝对路径**。用户不清楚时这样引导:打开 Obsidian → 左下角仓库名 → 鼠标悬停可见路径;或者由你为 TA 新建一个空文件夹当作新仓库(之后在 Obsidian 里 Open folder as vault)。
2. 是否顺便安装**可选**的复习闪卡插件 Spaced Repetition(默认不装,核心流程不依赖它)。

以下用 `$VAULT` 指代用户给出的仓库路径。

## 第 1 步:下载系统文件
```bash
curl -fsSL -o /tmp/sps.zip https://github.com/Penny777btc/speaking-system/archive/refs/heads/main.zip
rm -rf /tmp/sps && mkdir -p /tmp/sps
# ⚠️ 不要用 macOS 自带 unzip:它解不了 zip 里的 UTF-8 中文文件名(Illegal byte sequence)
ditto -x -k /tmp/sps.zip /tmp/sps 2>/dev/null || python3 -m zipfile -e /tmp/sps.zip /tmp/sps
# 存在性护栏
[ -e "$VAULT/English-Speaking-System" ] && echo "已存在,停止并询问用户" || cp -R /tmp/sps/speaking-system-main/English-Speaking-System "$VAULT/"
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

## 第 5 步:验收(文件级由你做,界面级引导用户做)
你自己验证:
- `$VAULT/English-Speaking-System/01-Templates/English Study 剪贴板归档.md` 存在
- community-plugins.json 含两个插件 id;两个 data.json 键正确
引导用户验证(逐条发给用户):
1. 按 `Cmd+Shift+E`(Windows `Ctrl+Shift+E`):应弹出模板选择框,里面有「English Study 剪贴板归档」→ 按 Esc 关闭
2. 打开 `05-Dashboard/进度仪表盘.md`:应渲染出表格而非代码块(说明 Dataview 已生效)

## 第 6 步:交接(把这段话连同指令一起交给用户)
先尽量把项目指令放进用户剪贴板(macOS):
```bash
python3 -c "
import sys
s = open(sys.argv[1]).read()
print(s.split('\`\`\`')[1].strip())
" "$VAULT/English-Speaking-System/00-Prompts/4-项目指令.md" | pbcopy && echo "指令已复制到剪贴板"
```
(pbcopy 失败就打印文件路径让用户自己复制代码块。)

再顺手把浏览器打开到 ChatGPT 的项目页,省掉用户找路的时间(失败就跳过,不要报错中断):
```bash
open "https://chatgpt.com/projects" 2>/dev/null \
  || xdg-open "https://chatgpt.com/projects" 2>/dev/null \
  || echo "请手动打开 https://chatgpt.com/projects"
```
> 注意:你**只能把页面打开给用户**。创建项目、粘贴指令、保存这三步必须由用户亲手完成——ChatGPT 的项目是云端功能,没有公开 API,而用浏览器自动化去点它既需要接管登录态、又会因 UI 改版随时失效。不要尝试。

然后**原样输出**给用户:

> 安装完成 ✅。插件、配置、快捷键我都写好了,**剩下三件我做不了的事**(约 3 分钟):
>
> **1️⃣ 打开自动整理开关(1 分钟)** — 这是唯一一个我无法替你写的设置:Templater 把「自动执行模板」这类危险开关存在**设备本地**,不在配置文件里(这是它的安全设计,防止恶意模板通过文件自动执行代码)。
> Obsidian 设置 → Templater → 滚到 **Startup templates** 区 → 打开 **Enable startup templates**(弹出风险框,勾选「I understand the risks」→ Enable)→ 下面的列表点 ➕ 填 `English-Speaking-System/01-Templates/自动整理.md` → 重启 Obsidian。
> 开了之后:每次打开 Obsidian 会自动整理表达/错误库、重建复习闪卡。不开也能用,但这些要你手动做。
>
> **2️⃣ 配置 ChatGPT(2 分钟)** — 我已经帮你打开项目页了(没打开就去 chatgpt.com/projects)→ 新建项目(起名如「英语口语 B1→C1」)→ 项目页右上 ⋯ → **编辑指令** → 粘贴(指令已在你的剪贴板里;粘贴前把开头的兴趣领域和水平参数改成你自己的)→ 保存。
>
> **3️⃣ 开练** — 在项目里说 **「每日输入」**。遇到问题看 docs/常见问题.md。
>
> 补充:我不需要你关闭 Obsidian 的「安全模式」——插件是我直接装进 `.obsidian/plugins/` 的,不走插件市场。手动安装的人才需要关。

## 执行时的已知坑(来自 docs/维护知识库.md 的实战记录)
- 外部改插件配置后必须重启 Obsidian;且要防它退出时用内存旧配置回写(第 4 步已含)。
- Templater 的 Enable startup templates / Trigger on file creation 总闸存在设备 localStorage,**写配置文件永远打不开**,只能用户在界面点(所以放在第 6 步交接)。
- Spaced Repetition v1.15+ 的配置嵌套在 data.json 的 `settings` 键下,顶层同名键会被静默忽略;卡组标签默认是复数 `#flashcards`,顺着默认走,别改。
- GitHub API 匿名限流 60 次/小时;失败时等待或提示用户稍后再试,不要重试轰炸。
- 文件名含括号/空格/中文,所有路径必须加引号。
- **解压必须用 ditto(macOS)或 python3 -m zipfile,绝不能用 unzip**——BSD unzip 遇到 UTF-8 中文文件名会 Illegal byte sequence,核心文件全部解压失败。
