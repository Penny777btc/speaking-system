# 🎙️ Speaking System — 口语学习系统

一套「ChatGPT + Obsidian」双端闭环的语言口语训练系统,封装为 Claude skill,可一键部署、参数化配置(语言/水平/兴趣领域)。

**每日闭环**:每日输入(领域文章+地道表达)→ Live 口语练习(旧错重测热身)→ 模板复盘(全量错误清单)→ 一键归档 Obsidian → 仪表盘可视化(打卡/评分曲线/错误类型趋势)→ 定时任务每晚自动归集表达库与错误库。

灵感来自 [Gloria 的 X 帖](https://x.com/changloria0816/status/2080893224181547481):「光练不记,等于白练」。在其基础上扩展了:B1→C1 季度爬坡路线、错误重测闭环、全语音流程、全自动归档与统计。

## 安装

### 有 Claude(推荐,全自动)
1. 下载 [Releases](../../releases) 里的 `speaking-system.skill`,导入 Claude(或把本仓库克隆到 `~/.claude/skills/speaking-system`)
2. 对 Claude 说:**「帮我部署口语学习系统」**,回答 4 个问题即完成全部配置

### 没有 Claude(手动,约 15 分钟)
照着 [`references/manual-setup-guide.md`](references/manual-setup-guide.md) 一步步做:拖文件夹 → 装 2 个插件 → 贴一段指令进 ChatGPT 项目。

## 仓库结构

| 路径 | 内容 |
|---|---|
| `SKILL.md` | Claude 的操作手册(部署/参数变更/排障/体检) |
| `assets/vault-template/` | 完整 Obsidian 系统模板(归档模板、仪表盘、话题库、路线图) |
| `references/manual-setup-guide.md` | 人类可读的手动安装指南 |
| `references/project-instruction-template.md` | 参数化的 ChatGPT 项目指令模板 |
| `references/gotchas.md` | 19 条实战踩坑知识库(语音模式偏置、解析契约等) |
| `scripts/install_plugins.sh` | Templater/Dataview 一键安装脚本 |

## 系统要求

Obsidian(免费)+ ChatGPT 账号(免费版可用)。macOS 上体验最完整;核心流程跨平台。
