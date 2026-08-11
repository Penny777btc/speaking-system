<%*
/* 自动整理(无 AI 版,beta)
   作用:每次打开 Obsidian 时,把「上次整理之后」的新日志里的表达和错误,
   搬进表达库/错误库的「📥 待归类」区(带日期、去重;已存在的自动跳过)。
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
      const stateContent = `---\nlastRun: ${today}\n---\n\n# 整理状态\n\n最近一次自动整理:${today},处理日志 ${logs.length} 篇,新表达 ${newExpr.length},新错误 ${newErr.length},再犯 ${repeats.length}。`;
      if (stateFile) await v.modify(stateFile, stateContent);
      else await v.create(STATE, stateContent);
      new tp.obsidian.Notice(`自动整理:表达 +${newExpr.length},错误 +${newErr.length},再犯 ${repeats.length}`, 8000);
    }
  }
} catch (e) { console.error("自动整理失败:", e); }
-%>
