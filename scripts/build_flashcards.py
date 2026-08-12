#!/usr/bin/env python3
"""Generate a Spaced-Repetition deck from the Expression Bank.

The deck is a supplement for ad-hoc self-review in Obsidian. Production practice
with real feedback stays in the ChatGPT loop -- a plugin can only self-grade
recognition, it cannot judge whether a sentence you produced is correct.

Card fronts are built from whatever cue the bank entry already carries, in
priority order: Chinese gloss > example sentence with the expression blanked.
Entries with no usable cue are listed at the bottom as a plain read-through
list rather than being turned into a card with a meaningless front.

Usage: build_flashcards.py <vault-root-English-Speaking-System>
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(sys.argv[1])
BANK = ROOT / "03-Expression-Bank" / "Expression Bank.md"
OUT = ROOT / "07-Review" / "表达闪卡.md"
AUDIO_DIR = ROOT / "07-Review" / "audio"
VOICE = "Samantha"  # 唯一像样的 en_US 系统音色;装了 Premium 音色后可换

# The plugin writes scheduling as <!--SR:!date,interval,ease--> on the line AFTER
# the card (cardCommentOnSameLine=false). Regenerating the deck blindly would
# wipe every card's review history, so harvest and re-attach it.
SR_RE = re.compile(r"^\s*<!--SR:.*-->\s*$")


def slugify(s):
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s[:60] or "card"


def speakable(expr):
    """Text to synthesise: first alternative only, no brackets/markup."""
    t = expr.split(" / ")[0]
    t = re.sub(r"[()\[\]*`]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def harvest_schedules(path):
    """Map card-key -> SR comment line, from the previous deck."""
    keep = {}
    if not path.exists():
        return keep
    lines = path.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines):
        if "#flashcards" not in line or "::" not in line:
            continue
        if i + 1 < len(lines) and SR_RE.match(lines[i + 1]):
            front, back = line.split("::", 1)
            back = re.sub(r"!\[\[[^\]]*\]\]", "", back)
            back = back.replace("#flashcards", "")
            keep[(front.strip(), back.strip())] = lines[i + 1].rstrip()
    return keep


def make_audio(expr):
    """Return the embed filename, generating the clip if missing."""
    text = speakable(expr)
    if not text:
        return None
    name = slugify(text) + ".m4a"
    dest = AUDIO_DIR / name
    if dest.exists() and dest.stat().st_size > 0:
        return name
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(
        ["say", "-v", VOICE, "-o", str(dest), "--data-format=aac", text],
        capture_output=True,
    )
    if r.returncode != 0 or not dest.exists():
        print(f"  [warn] TTS failed for {text!r}", file=sys.stderr)
        return None
    return name

HEADER = """---
tags:
  - english-study
  - flashcards
---

# 🔁 表达闪卡(自助复习)

> 由 [[Expression Bank]] 自动生成,**不要手动编辑**——改动会在下次生成时被覆盖。
> 想复习时:命令面板搜 `flashcards` → 「Spaced Repetition: Review flashcards from all notes」。
> 这里是「偶尔想起来练一下」的补充。真正的产出式练习和反馈在每天的 ChatGPT 热身里——
> 插件只能自评「记得/不记得」,判断不了你造的句子对不对。

"""

EMPTY_HINT = """
## 现在还是空的,这是正常的

闪卡来自 `03-Expression-Bank/Expression Bank.md`(表达库)。练几天、让表达库攒下
**带中文释义**的条目之后,这里就会自动长出卡片。

条目格式:`- expression *(YYYY-MM-DD,中文意思)*` —— 没有中文释义的条目做不成卡片,
因为卡片正面就是那个中文提示。

> 复习方法:装 Spaced Repetition 插件 → 命令面板搜 `flashcards`。
> 注意它只能自评「记得/不记得」;真正的产出式练习在每天 ChatGPT 热身的「表达重测」里。
"""

entry_re = re.compile(r"^- (?P<body>.+)$")
# trailing *(YYYY-MM-DD,中文说明)* or *(YYYY-MM-DD)*
# 不要求 meta 在行尾:条目末尾可能被追加使用记录(· 用过 ×2 · 上次 08-10 🎓),
# 锚定行尾会让这些「真正用出来过的表达」反而进不了闪卡。
meta_re = re.compile(r"\*\((?P<date>\d{4}-\d{2}-\d{2})(?P<extra>[^)]*)\)\*")
example_re = re.compile(r"—\s*\*(?P<ex>[^*]+)\*")


def clean(s):
    return re.sub(r"\s+", " ", s.replace("**", "").strip(" *—-·")).strip()


def main():
    if not BANK.exists():
        print(f"missing: {BANK}", file=sys.stderr)
        return 1
    text = BANK.read_text(encoding="utf-8")

    cards, no_cue, section = [], [], ""
    seen = set()
    for line in text.splitlines():
        if line.startswith("###"):
            section = clean(line.lstrip("#"))
            continue
        if line.startswith("## "):
            # stop before the model-sentence section; those are quotes, not chunks
            if "金句" in line:
                break
            continue
        m = entry_re.match(line)
        if not m:
            continue
        body = m.group("body")
        meta = meta_re.search(body)
        if not meta:
            continue
        gloss = meta.group("extra").lstrip("，,").strip()
        head = body[: meta.start()]

        ex = example_re.search(head)
        example = clean(ex.group("ex")) if ex else ""
        expr = clean(head.split("—")[0])
        if not expr or expr.lower() in seen:
            continue
        seen.add(expr.lower())

        # primary cue: the Chinese gloss the bank already carries.
        # Skip provenance tags ("每日输入") and editorial notes about the edit
        # itself -- those make fronts that cue nothing, or leak the answer.
        gloss = re.sub(r"^(当天批改|按当天批改)[：:]\s*", "", gloss)
        gloss = re.split(r"[；;·]", gloss)[0].strip()
        if re.fullmatch(r"(每日输入|原句.*|.*已按.*改为.*)", gloss or ""):
            gloss = ""

        # a gloss that spells out the answer is worse than no card
        if gloss and expr.split("(")[0].strip().lower() in gloss.lower():
            gloss = ""

        front = ""
        if gloss and re.search(r"[一-鿿]", gloss):
            front = gloss
        elif example:
            # blank the expression out of its own example
            core = expr.split("(")[0].strip()
            blanked = re.sub(re.escape(core), "____", example, flags=re.I)
            if blanked != example:
                front = blanked

        if front:
            cards.append((section, front, expr))
        else:
            no_cue.append((section, expr))

    kept = harvest_schedules(OUT)
    if not cards and not no_cue:
        # 表达库还是空的(新用户第一天):写引导文案而不是一个空文件,
        # 否则用户会以为脚本坏了。
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(HEADER + EMPTY_HINT, encoding="utf-8")
        print(f"cards=0(表达库还没有带中文释义的条目,已写入引导说明)-> {OUT}")
        return 0
    lines = [HEADER, f"共 {len(cards)} 张卡片。\n"]
    cur = None
    audio_n = restored = 0
    for sec, front, back in cards:
        if sec != cur:
            lines.append(f"\n## {sec}\n")
            cur = sec
        clip = make_audio(back)
        if clip:
            audio_n += 1
        embed = f" ![[{clip}]]" if clip else ""
        lines.append(f"{front}::{back}{embed} #flashcards")
        sched = kept.get((front.strip(), back.strip()))
        if sched:
            lines.append(sched)
            restored += 1

    if no_cue:
        lines.append("\n## 📖 只读清单(没有可用提示,不做成卡片)\n")
        lines.append("> 这些条目本身就是提示语,做成卡片正反面会一样。当词表朗读即可。\n")
        cur = None
        for sec, expr in no_cue:
            if sec != cur:
                lines.append(f"\n**{sec}**\n")
                cur = sec
            lines.append(f"- {expr}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(
        f"cards={len(cards)} audio={audio_n} schedules-kept={restored}/{len(kept)} "
        f"read-only={len(no_cue)} -> {OUT}"
    )
    if kept and restored < len(kept):
        print(
            f"  [note] {len(kept) - restored} 条旧调度未能匹配(对应表达已从表达库消失或改写),"
            "其复习进度归零",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
