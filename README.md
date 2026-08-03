# 🎙️ Speaking System — 口语学习系统

一套「ChatGPT + Obsidian」双端闭环的语言口语训练系统。核心是一个可独立发送给 ChatGPT 或 Codex 的自包含 Skill;插件只是可选安装外壳。

**每日闭环**:每日输入(领域文章+地道表达)→ Live 口语练习(旧错重测热身)→ 模板复盘(全量错误清单)→ 一键归档 Obsidian → 仪表盘可视化(打卡/评分曲线/错误类型趋势)→ 定时任务每晚自动归集表达库与错误库。

灵感来自 [Gloria 的 X 帖](https://x.com/changloria0816/status/2080893224181547481):「光练不记,等于白练」。在其基础上扩展了:B1→C1 季度爬坡路线、错误重测闭环、全语音流程、全自动归档与统计。

## 直接发送给 ChatGPT / Codex

下载 Release 中的 `speaking-system.zip`,作为附件发给 ChatGPT 或 Codex,然后发送:

> 请完整读取压缩包中 `speaking-system/SKILL.md`,按照它的流程帮我部署。我要通用配置 / Penny 同款。

Skill 会生成两项交付物:

1. 可放进 Obsidian 的完整配置 ZIP
2. 可复制进 ChatGPT 项目 Instructions 的个性化指令

“Penny 同款”复制公开的系统参数、话题库、训练节奏和路线图,不包含私人对话历史。用户另行提供表达库和错误库时,Skill 也能把学习状态迁入新配置。

## 可选:安装到 ChatGPT Work / Codex

长期跨对话使用时,可以把同一个 Skill 作为插件安装。插件可用于 **ChatGPT Work(Web/桌面端)** 和 **Codex(桌面端/CLI)**。

### GitHub 预览版(审核发布前)

先在终端注册这个 GitHub 插件市场,再安装插件:

```bash
codex plugin marketplace add Penny777btc/speaking-system
codex plugin add speaking-system@speaking-system
```

安装后新开一个 ChatGPT Work 或 Codex 对话,输入 **「帮我一键配置口语学习系统」**。回答目标语言、水平、目标和兴趣领域后,插件会生成一个可直接导入 Obsidian 的 zip 和 ChatGPT 项目指令。

已经注册过市场时,可直接点 [安装 Speaking System](codex://plugins/install/?marketplace=speaking-system)。

> 真正面向所有 ChatGPT 用户的单击安装,需要把本仓库提交并审核进入 ChatGPT/Codex 共用的通用插件目录。本仓库现已具备提交所需的插件结构;GitHub 命令是审核前的测试安装路径。

## 手动安装(约 15 分钟)

照着 [`skills/speaking-system/references/manual-setup-guide.md`](skills/speaking-system/references/manual-setup-guide.md) 操作:拖文件夹 → 装 2 个插件 → 把指令贴进 ChatGPT 项目。

## 仓库结构

| 路径 | 内容 |
|---|---|
| `.codex-plugin/plugin.json` | ChatGPT/Codex 插件清单与安装页元数据 |
| `.agents/plugins/marketplace.json` | GitHub 预览版插件市场入口 |
| `skills/speaking-system/` | 可独立发送、安装和运行的完整 Skill |
| `skills/speaking-system/SKILL.md` | ChatGPT/Codex 使用的部署、维护与排障工作流 |
| `skills/speaking-system/assets/` | Obsidian 模板、通用配置与 Penny 同款配置 |
| `skills/speaking-system/references/` | 项目指令模板、踩坑库、手动指南和可移植性边界 |
| `skills/speaking-system/scripts/` | 配置包生成、状态导入和 Obsidian 插件配置脚本 |

## 系统要求

Obsidian(免费)+ ChatGPT 账号(免费版可用)。macOS 上体验最完整;核心流程跨平台。
