<%*
// 一键归档:读取剪贴板里 GPT 的复盘输出,自动解析评分进 frontmatter,建好今日笔记
const logsFolder = "English-Speaking-System/02-Daily-Logs";
let clip = "";
try { clip = await tp.system.clipboard(); } catch (e) {}
clip = (clip || "").trim();
const looksLike = /English Study|Key Corrections|Overall Evaluation/.test(clip);
// 日期以复盘里写的「练习日期」为准,按快捷键的时间只是回退方案。
// 直接用 tp.date.now() 会让「晚上练、隔天归档」和「补档」全部盖成归档那天,
// 打卡天数、趋势图、以及按 date 找日志的定时整理都会跟着错。
const today = tp.date.now("YYYY-MM-DD");
const tomorrow = tp.date.now("YYYY-MM-DD", 1);
const clipDate = (clip.match(/(20\d{2}-\d{2}-\d{2})\s*English Study/i) || [])[1] || "";
const dateStr = (looksLike && clipDate && clipDate <= tomorrow) ? clipDate : today;
const num = (re) => { const m = clip.match(re); return m ? m[1] : ""; };
// [^\d\n]* 兼容标准表格「| Fluency | 4/5 |」和手机复制出的纯文本「Fluency	4.5/5」
const fluency = looksLike ? num(/Fluency[^\d\n]*([\d.]+)\s*\/\s*5/i) : "";
const grammar = looksLike ? num(/Grammar[^\d\n]*([\d.]+)\s*\/\s*5/i) : "";
const vocabulary = looksLike ? num(/Vocabulary[^\d\n]*([\d.]+)\s*\/\s*5/i) : "";
const communication = looksLike ? num(/Communication[^\d\n]*([\d.]+)\s*\/\s*5/i) : "";
const overall = looksLike ? num(/Overall[^\d\n]*([\d.]+)\s*\/\s*10/i) : "";
const speakingTime = looksLike ? num(/Your speaking time:\D*?(\d+(?:\.\d+)?)/i) : "";
// 评分口径字段:搭配操练不计入评分,所以「用于评分的时长/词数」和总时长是两回事
const scoredTime = looksLike ? num(/Scored speaking time:\D*?(\d+(?:\.\d+)?)/i) : "";
const wordCount = looksLike ? num(/Scored word count:\D*?([\d,]+)/i).replace(/,/g, "") : "";
const errorRate = looksLike ? num(/Errors per 100 words:\D*?([\d.]+)/i) : "";
let body;
if (looksLike) {
  body = clip.replace(/^#[^\n]*English Study[^\n]*$/m, "# " + dateStr + " English Study");
  // 手机复制会丢失 # 标题:把开头的纯文本标题行换成正式标题,并给已知小节补 ##
  if (!/^# /m.test(body)) {
    body = body.replace(/^[^\n]*English Study[^\n]*\n?/, "");
    const secs = ["Speaking Time","Main Topics","Strengths","Key Corrections","Error Log","New Words & Phrases","Expressions Used","明日重测清单","Model Sentence","Tomorrow's Suggestion & Topic","Tomorrow’s Suggestion & Topic","Overall Evaluation","Today's Input"];
    for (const h of secs) body = body.replace(new RegExp("^" + h.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + "$", "m"), "## " + h);
    body = "# " + dateStr + " English Study\n\n" + body;
  }
} else {
  body = "# " + dateStr + " English Study\n\n> ⚠️ 剪贴板中未检测到复盘内容。请在 ChatGPT 里点复制「按模板复盘」的输出后再运行一次,或直接把内容手动粘贴到下面。\n\n## Speaking Time\n- Total session:\n- Your speaking time:\n- Scored speaking time:\n- Scored word count:\n- Errors per 100 words:\n\n## Main Topics\n-\n\n## Strengths\n-\n\n## Key Corrections\n\n### 1. [Category]\n❌\n✅\n\n### 2. [Category]\n❌\n✅\n\n### 3. [Category]\n❌\n✅\n\n## Error Log\n- [类型] ❌ → ✅\n\n## New Words & Phrases\n- expression — 中文意思\n\n## Expressions Used\n- 自发用出:\n- 任务卡:/3\n- 本次毕业:\n\n## 明日重测清单\n- 表达重测(5):\n- 任务卡(3):\n- 错误重测(2):\n\n## Model Sentence\n>\n\n## Tomorrow's Suggestion & Topic\n**Speaking Goal**\n-\n\n**Tomorrow's Topic**\n-\n\n**引导问题**\n1.\n2.\n3.\n\n## Overall Evaluation\n| 维度 | 评分 | 说明 |\n|------|------|------|\n| Fluency | /5 | |\n| Grammar | /5 | |\n| Vocabulary | /5 | |\n| Communication | /5 | |\n| **Overall** | /10 | |";
}
let name = dateStr + " English Study";
if (await tp.file.exists(logsFolder + "/" + name + ".md")) {
  name = name + " " + tp.date.now("HHmm");
}
await tp.file.move(logsFolder + "/" + name);
-%>
---
date: <% dateStr %>
tags:
  - english-study
  - speaking
speaking_time: <% speakingTime %>
scored_time: <% scoredTime %>
word_count: <% wordCount %>
error_rate: <% errorRate %>
fluency: <% fluency %>
grammar: <% grammar %>
vocabulary: <% vocabulary %>
communication: <% communication %>
overall_score: <% overall %>
---

<% body %>
