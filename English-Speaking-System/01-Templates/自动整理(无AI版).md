<%*

/* ---------- 闪卡重建(纯 JS,无需 Python / 定时器) ---------- */
async function rebuildFlashcards(v, get, SYS) {
  const bankFile = get(SYS + "/03-Expression-Bank/Expression Bank.md");
  if (!bankFile) return null;
  const outPath = SYS + "/07-Review/表达闪卡.md";
  const text = await v.read(bankFile);
  const clean = (s) => s.replace(/\*\*/g, "").replace(/\s+/g, " ")
    .replace(/^[\s*—\-·]+|[\s*—\-·]+$/g, "").trim();
  const esc = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

  // 1) 收割旧文件里的复习进度和音频引用(Python 版生成过音频时保留)
  const outFile = get(outPath);
  const kept = new Map();
  if (outFile) {
    const old = (await v.read(outFile)).split("\n");
    for (let i = 0; i < old.length; i++) {
      const m = old[i].match(/^(.+?)::(.+?)\s*#flashcards\s*$/);
      if (!m) continue;
      const audio = (m[2].match(/!\[\[[^\]]*\]\]/) || [""])[0];
      const back = m[2].replace(/!\[\[[^\]]*\]\]/g, "").trim();
      const sr = (old[i + 1] || "").match(/^\s*<!--SR:.*-->\s*$/) ? old[i + 1] : "";
      kept.set(m[1].trim() + "||" + back, { sr, audio });
    }
  }

  // 2) 解析表达库
  const cards = [], noCue = [], seen = new Set();
  let section = "";
  for (const line of text.split("\n")) {
    if (line.startsWith("###")) { section = clean(line.replace(/^#+/, "")); continue; }
    if (line.startsWith("## ")) { if (line.includes("金句")) break; continue; }
    const em = line.match(/^- (.+)$/);
    if (!em) continue;
    const body = em[1];
    const meta = body.match(/\*\((\d{4}-\d{2}-\d{2})([^)]*)\)\*/);
    if (!meta) continue;
    let gloss = (meta[2] || "").replace(/^[，,]/, "").trim();
    const head = body.slice(0, meta.index);
    const ex = head.match(/—\s*\*([^*]+)\*/);
    const example = ex ? clean(ex[1]) : "";
    const expr = clean(head.split("—")[0]);
    if (!expr || seen.has(expr.toLowerCase())) continue;
    seen.add(expr.toLowerCase());
    gloss = gloss.replace(/^(当天批改|按当天批改)[：:]\s*/, "").split(/[；;·]/)[0].trim();
    if (/^(每日输入|原句.*|.*已按.*改为.*|用过.*)$/.test(gloss)) gloss = "";
    const core = expr.split("(")[0].trim();
    if (gloss && gloss.toLowerCase().includes(core.toLowerCase())) gloss = "";
    let front = "";
    if (gloss && /[一-鿿]/.test(gloss)) front = gloss;
    else if (example) {
      const blanked = example.replace(new RegExp(esc(core), "i"), "____");
      if (blanked !== example) front = blanked;
    }
    if (front) cards.push([section, front, expr]); else noCue.push([section, expr]);
  }

  // 3) 组装(保留分类、进度、音频)
  const out = ["---", "tags:", "  - english-study", "  - flashcards", "---", "",
    "# 🔁 表达闪卡(自助复习)", "",
    "> 打开 Obsidian 时由「自动整理」脚本重建,**不要手动编辑**——改动会被覆盖。",
    "> 复习:命令面板搜 `flashcards` → 「Spaced Repetition: Review flashcards from all notes」。",
    "> 插件只能自评「记得/不记得」;真正的产出式练习在每天 ChatGPT 热身的「表达重测」里。", "",
    `共 ${cards.length} 张卡片。`];
  let cur = null, restored = 0;
  for (const [sec, front, back] of cards) {
    if (sec !== cur) { out.push("", "## " + sec, ""); cur = sec; }
    const hit = kept.get(front.trim() + "||" + back.trim());
    out.push(`${front}::${back}${hit && hit.audio ? " " + hit.audio : ""} #flashcards`);
    if (hit && hit.sr) { out.push(hit.sr); restored++; }
  }
  if (noCue.length) {
    out.push("", "## 📖 只读清单(没有可用提示,不做成卡片)", "",
      "> 这些条目本身就是提示语,做成卡片正反面会一样。当词表朗读即可。", "");
    cur = null;
    for (const [sec, expr] of noCue) {
      if (sec !== cur) { out.push("", "**" + sec + "**", ""); cur = sec; }
      out.push("- " + expr);
    }
  }
  const content = out.join("\n") + "\n";
  const f = get(outPath);
  if (f) await v.modify(f, content); else await v.create(outPath, content);
  return { cards: cards.length, restored, kept: kept.size, readonly: noCue.length };
}

/* 自动整理(无 AI 版)
   作用:每次打开 Obsidian 时自动做两件事——
   ①把新日志里的表达和错误搬进表达库/错误库的「📥 待归类」区(带日期、去重);
   ②按表达库重建复习闪卡(保留 Spaced Repetition 的复习进度和已有音频引用)。
   纯 JS,不需要 Python、不需要定时任务、跨平台。
   领域归类与相似错误合并留给你人工 1 分钟——顺手就完成了一次复习。
   启用方法:Templater 设置 → Startup templates → 添加本文件。
   注意:若你使用 AI 助手的每晚自动整理,请勿同时启用本模板,两者会互相干扰。 */
try {
  const SYS = "English-Speaking-System";
  const v = app.vault;
  const get = (p) => v.getAbstractFileByPath(p);
  const STATE = SYS + "/07-Review/整理状态.md";

  const today = tp.date.now("YYYY-MM-DD");
  let lastRun = "1970-01-01";
  const stateFile = get(STATE);
  if (stateFile) {
    const m = (await v.read(stateFile)).match(/lastRun: *(\d{4}-\d{2}-\d{2})/);
    if (m) lastRun = m[1];
  }
  const folder = get(SYS + "/02-Daily-Logs");
  const bankFile = get(SYS + "/03-Expression-Bank/Expression Bank.md");
  const errFile = get(SYS + "/04-Error-Patterns/Error Patterns.md");
  if (folder && bankFile && errFile) {
    const logs = (folder.children || []).filter(f => f.extension === "md")
      .filter(f => { const d = (f.name.match(/^(\d{4}-\d{2}-\d{2})/) || [])[1]; return d && d > lastRun && d <= today; })
      .sort((a, b) => a.name.localeCompare(b.name));
    if (logs.length > 0) {
      let bank = await v.read(bankFile);
      let errs = await v.read(errFile);
      const section = (c, name) => (c.split(new RegExp("##\\s*" + name))[1] || "").split(/\n##\s/)[0];
      let newExpr = [], newErr = [], repeats = [];
      for (const f of logs) {
        const c = await v.read(f);
        const d = f.name.slice(0, 10);
        // 表达:- expr — 中文
        for (const line of section(c, "New Words & Phrases").split("\n")) {
          const m = line.match(/^[-*]\s+(.+?)\s+—\s+(.+)$/);
          if (!m) continue;
          const expr = m[1].replace(/\*/g, "").trim();
          if (expr && !bank.toLowerCase().includes(expr.toLowerCase()) && !newExpr.some(e => e.includes(expr)))
            newExpr.push(`- ${expr} *(${d},${m[2].trim()})*`);
        }
        // 错误:单行式(Error Log)+ 块式(Key Corrections)
        const errLines = [];
        for (const line of section(c, "Error Log").split("\n")) {
          if (line.includes("❌") && line.includes("→")) errLines.push(line.replace(/^[-*]\s*/, ""));
        }
        const kc = section(c, "Key Corrections");
        const blocks = [...kc.matchAll(/[\[【]([^\]】\n]{1,16})[\]】][^\n]*\n+[^❌\n]*❌\s*([^\n]+)\n+[^✅\n]*✅\s*([^\n]+)/g)];
        for (const b of blocks) errLines.push(`[${b[1]}] ❌ ${b[2].trim()} → ✅ ${b[3].trim()}`);
        for (const line of errLines) {
          const wrong = ((line.match(/❌\s*([^→]+)/) || [])[1] || "").trim().slice(0, 25);
          if (!wrong) continue;
          if (errs.includes(wrong) || newErr.some(e => e.includes(wrong))) {
            if (!repeats.some(r => r.includes(wrong))) repeats.push(`- 🔥 再犯(${d}):${line}`);
          } else newErr.push(`- ${line} *(${d})*`);
        }
      }
      const addUnder = (text, header, lines) => {
        if (lines.length === 0) return text;
        if (!text.includes(header)) text = text.trimEnd() + "\n\n" + header + "\n";
        return text.replace(header, header + "\n" + lines.join("\n"));
      };
      bank = addUnder(bank, "## 📥 待归类(自动搬入,请移到对应领域)", newExpr);
      errs = addUnder(errs, "## 📥 待归类(自动搬入,请移到对应类型)", newErr.concat(repeats));
      if (newExpr.length || newErr.length || repeats.length) {
        await v.modify(bankFile, bank);
        await v.modify(errFile, errs);
      }
      let deck = null;
      try { deck = await rebuildFlashcards(v, get, SYS); } catch (e) { console.error("闪卡重建失败:", e); }
      const deckMsg = deck ? `;闪卡 ${deck.cards} 张(进度保留 ${deck.restored}/${deck.kept})` : "";
      const stateContent = `---\nlastRun: ${today}\n---\n\n# 整理状态\n\n最近一次自动整理:${today},处理日志 ${logs.length} 篇,新表达 ${newExpr.length},新错误 ${newErr.length},再犯 ${repeats.length}${deckMsg}。`;
      if (stateFile) await v.modify(stateFile, stateContent);
      else await v.create(STATE, stateContent);
      new tp.obsidian.Notice(`自动整理:表达 +${newExpr.length},错误 +${newErr.length},再犯 ${repeats.length}${deckMsg}`, 8000);
    }
  }
} catch (e) { console.error("自动整理失败:", e); }
-%>
