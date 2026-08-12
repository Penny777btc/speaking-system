#!/bin/bash
# 把本工作区的改动并回 main 并推到 GitHub。
# 用法:  bash 并回主干.sh "这次改了什么"
set -e
MSG="${1:-更新}"
HERE="$(cd "$(dirname "$0")" && pwd)"
BR="$(git -C "$HERE" branch --show-current)"
MAIN="$(dirname "$HERE")/speaking-system"

cd "$HERE"
if [ -n "$(git status --porcelain)" ]; then
  git add -A
  git -c user.name="Penny777btc" -c user.email="elune.wen@gmail.com" commit -qm "$MSG"
  echo "✓ 已提交:$MSG"
else
  echo "· 没有新改动"
fi

git fetch -q origin
# 先把主干的新内容取过来,避免并回时冲突
if ! git rebase -q origin/main; then
  echo ""
  echo "⚠️  和主干有冲突,自动合并停下了。"
  echo "   让 AI 帮你解决:把冲突文件给它看,或直接说「解决 rebase 冲突」。"
  echo "   想放弃这次合并:git rebase --abort"
  exit 1
fi

git -C "$MAIN" fetch -q origin && git -C "$MAIN" merge -q --ff-only origin/main 2>/dev/null || true
git -C "$MAIN" merge -q "$BR" --no-edit
git -C "$MAIN" push -q
git push -qf origin "$BR"
echo "✓ 已并回主干并推送到 GitHub"
echo "  https://github.com/Penny777btc/speaking-system"
