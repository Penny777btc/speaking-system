# 手动安装指南(无需 AI 帮助,约 15 分钟)

> 这份指南写给**人**看。如果你有 Claude,不用读这个——直接对它说「帮我部署口语学习系统」即可。
> 没有 Claude 的话,照下面一步步做,同样能把系统跑起来;只是「每晚自动整理」这类自动化没有,退回每周手动整理 5 分钟(系统文档里有写怎么做)。

## 你需要准备

- **Obsidian**(免费,obsidian.md 下载,电脑版)
- **ChatGPT 账号**(免费版可用;Plus 的语音体验更好)

## 第一步:装入 Obsidian(5 分钟)

1. 打开 Obsidian → 创建一个新仓库(或用你现有的仓库)
2. 把本 skill 包里 `assets/vault-template/` 下的 **English-Speaking-System 整个文件夹**,拖进你仓库的根目录(在访达/资源管理器里拖即可)
3. 回到 Obsidian,左侧应能看到 English-Speaking-System 及其子文件夹

## 第二步:装两个插件(5 分钟)

1. Obsidian 设置 → **第三方插件** → 关闭「安全模式/受限模式」
2. 点「浏览」社区插件市场,搜索并安装+启用:
   - **Templater**(一键归档靠它)
   - **Dataview**(仪表盘靠它;装好后进它的设置,打开 **Enable JavaScript Queries**)
3. 进 Templater 设置:
   - Template folder location 填:`English-Speaking-System/01-Templates`
4. 设置 → 快捷键 → 搜「Templater: Create new note from template」→ 绑定 `Cmd+Shift+E`(Windows 用 `Ctrl+Shift+E`)

✅ 自检:按一下快捷键,应弹出模板选择框,里面有「English Study 剪贴板归档」。

## 第三步:配置 ChatGPT(3 分钟)

1. 在 Obsidian 里打开 `00-Prompts/4-项目指令(完整版).md`
2. **先按你自己的情况改三处**:兴趣领域(默认 AI/商业模式/创业/个人成长)、水平参数(默认 B1+)、目标(默认一年 B1→C1)
3. 复制代码块里的整段指令
4. 打开 ChatGPT → 侧栏「项目」→ 新建项目(起名如「英语口语 B1→C1」)→ 项目页右上 ⋯ → **编辑指令** → 粘贴 → 保存

✅ 自检:在项目里发「每日输入」,它应生成一篇你领域的英文短文+5 个加粗表达+提问。

## 第四步:跑通第一个循环(当天练习时)

1. 在项目里开语音(或打字),说 **「每日输入」** → 读/听文章、回答问题
2. 说 **「开始口语练习」** → 自由对话
3. 练完说 **「按模板复盘」** → 点复盘消息的**复制**按钮
4. 回 Obsidian 按 `Cmd+Shift+E` → 回车 → 笔记自动建好,评分自动写进属性
5. 打开 `05-Dashboard/进度仪表盘.md` → 应看到你的第一条记录和评分

## 日常与每周

- **每天**:上面 4 步,全流程 20–40 分钟(详见系统内 README)
- **每周日 5 分钟**:把本周日志里的好表达抄进 `03-Expression-Bank`、犯过 2 次的错误抄进 `04-Error-Patterns`,然后**大声朗读一遍错误库**——这是整个系统防止重复犯错的核心动作
- **每月 1 号**:对项目说 **「月度模考」**
- **每季度**:模考通过后,把项目指令第一行的水平参数升一级(B1+ → B2 → B2+ → C1-approaching)

## 常见问题(踩坑速查)

| 现象 | 原因与解法 |
|---|---|
| 说触发词没反应 | 你不在项目里,或改完指令没**开新会话**(改指令必开新会话) |
| 语音朗读文章太短/中途停 | 对它说 "Too short, add two more paragraphs" / "Keep going" |
| 语音突然说中文 | 说一句 "English only, please" |
| 归档后评分是空的 | 复制时格式被拍平了,正常现象,手动把分数填进笔记属性即可 |
| 仪表盘显示的是代码不是图表 | Dataview 没装好,或没开 Enable JavaScript Queries |
| 手机也想用 | 把仓库放进 iCloud 的 Obsidian 文件夹,手机装 Obsidian 即可同步 |

更深的原理和维护知识见同目录 `gotchas.md`(写给 AI 维护者,但人也能读)。
