#!/usr/bin/env python3
"""Create a personalized, import-ready Speaking System bundle."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VAULT_TEMPLATE = ROOT / "assets" / "vault-template"
INSTRUCTION_TEMPLATE = ROOT / "references" / "project-instruction-template.md"
PROFILE_DIR = ROOT / "assets" / "profiles"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a personalized ChatGPT + Obsidian speaking system."
    )
    parser.add_argument(
        "--profile",
        default="generic",
        help="Bundled profile name (generic or penny), or a profile JSON path.",
    )
    parser.add_argument("--target-language")
    parser.add_argument("--native-language")
    parser.add_argument("--level")
    parser.add_argument("--goal")
    parser.add_argument(
        "--domains",
        help="Interest domains separated by / or commas.",
    )
    parser.add_argument("--words", type=int, help="Article word minimum; inferred from level when omitted.")
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Parent directory that will receive the configured folder and zip archive.",
    )
    parser.add_argument("--folder-name")
    parser.add_argument("--expression-bank", type=Path, help="Optional existing Expression Bank Markdown file.")
    parser.add_argument("--error-bank", type=Path, help="Optional existing Error Patterns Markdown file.")
    parser.add_argument("--topic-bank", type=Path, help="Optional personalized quarterly topic bank Markdown file.")
    parser.add_argument("--force", action="store_true", help="Replace an existing generated folder/archive.")
    return parser.parse_args()


def infer_words(level: str) -> int:
    normalized = level.upper().replace(" ", "")
    return 250 if normalized.startswith(("A", "B1")) else 400


def load_profile(value: str) -> dict:
    bundled = PROFILE_DIR / f"{value}.json"
    path = bundled if bundled.is_file() else Path(value).expanduser().resolve()
    if not path.is_file():
        raise ValueError(f"profile not found: {value}")
    try:
        profile = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise ValueError(f"cannot read profile {path}: {exc}") from exc
    if not isinstance(profile, dict):
        raise ValueError(f"profile must be a JSON object: {path}")
    return profile


def validate_folder_name(value: str) -> str:
    if not value or value in {".", ".."} or "/" in value or "\\" in value:
        raise ValueError("--folder-name must be a single safe directory name")
    return value


def normalized_domains(value: str | list) -> str:
    if isinstance(value, list):
        value = "/".join(str(part) for part in value)
    parts = [part.strip() for part in re.split(r"[/,，、]+", value) if part.strip()]
    if not parts:
        raise ValueError("--domains must contain at least one domain")
    return "/".join(parts)


def render_instructions(config: dict, domains: str, words: int) -> str:
    template = INSTRUCTION_TEMPLATE.read_text(encoding="utf-8")
    fenced = re.search(r"```[^\n]*\n(.*?)\n```", template, flags=re.DOTALL)
    if not fenced:
        raise RuntimeError(f"Instruction template has no fenced prompt: {INSTRUCTION_TEMPLATE}")
    text = fenced.group(1)
    replacements = {
        "{{TARGET_LANG}}": config["target_language"],
        "{{NATIVE_LANG}}": config["native_language"],
        "{{LEVEL}}": config["level"],
        "{{GOAL}}": config["goal"],
        "{{DOMAINS}}": domains,
        "{{WORDS}}": str(words),
    }
    for marker, value in replacements.items():
        text = text.replace(marker, value)
    return (
        "# ChatGPT 项目指令(已配置)\n\n"
        "> 复制下面代码块中的全部内容,粘贴到 ChatGPT 项目的 Instructions。\n\n"
        "```\n"
        f"{text.rstrip()}\n"
        "```\n"
    )


def make_zip(source_dir: Path, archive: Path) -> None:
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for path in sorted(source_dir.rglob("*")):
            if path.is_file():
                bundle.write(path, path.relative_to(source_dir.parent))


def rewrite_system_folder(staged: Path, folder_name: str) -> None:
    """Keep Dataview, Templater, and documentation paths in sync."""
    for path in staged.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        updated = text.replace("English-Speaking-System", folder_name)
        if updated != text:
            path.write_text(updated, encoding="utf-8")


def import_state_file(source: Path | None, destination: Path) -> None:
    if source is None:
        return
    source = source.expanduser().resolve()
    if not source.is_file():
        raise ValueError(f"state file not found: {source}")
    shutil.copy2(source, destination)


def main() -> int:
    args = parse_args()
    try:
        profile = load_profile(args.profile)
        config = dict(profile)
        config.update({
            "target_language": args.target_language or profile.get("target_language", "英语"),
            "native_language": args.native_language or profile.get("native_language", "中文"),
            "level": args.level or profile.get("level", "B1+"),
            "goal": args.goal or profile.get("goal", "一年内从 B1 到 C1"),
        })
        domains = normalized_domains(args.domains or profile.get("domains", []))
        folder_name = validate_folder_name(
            args.folder_name or profile.get("folder_name", "Speaking-System")
        )
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    words = args.words if args.words is not None else profile.get("words")
    words = words or infer_words(config["level"])
    try:
        words = int(words)
    except (TypeError, ValueError):
        print("error: words must be an integer", file=sys.stderr)
        return 2
    if words < 100 or words > 2000:
        print("error: --words must be between 100 and 2000", file=sys.stderr)
        return 2

    output = args.output.expanduser().resolve()
    destination = output / folder_name
    archive = output / f"{folder_name}.zip"
    output.mkdir(parents=True, exist_ok=True)

    if (destination.exists() or archive.exists()) and not args.force:
        print("error: output already exists; choose another folder or pass --force", file=sys.stderr)
        return 2

    if args.force:
        if destination.is_dir():
            shutil.rmtree(destination)
        elif destination.exists():
            destination.unlink()
        if archive.exists():
            archive.unlink()

    with tempfile.TemporaryDirectory(prefix="speaking-system-") as temporary:
        staged = Path(temporary) / folder_name
        shutil.copytree(VAULT_TEMPLATE, staged)
        rewrite_system_folder(staged, folder_name)
        try:
            import_state_file(
                args.topic_bank,
                staged / "00-Prompts" / "3-话题库(按季度爬坡).md",
            )
            import_state_file(
                args.expression_bank,
                staged / "03-Expression-Bank" / "Expression Bank.md",
            )
            import_state_file(
                args.error_bank,
                staged / "04-Error-Patterns" / "Error Patterns.md",
            )
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        prompt_path = staged / "00-Prompts" / "4-项目指令(完整版).md"
        config.update({
            "target_language": config["target_language"],
            "native_language": config["native_language"],
            "level": config["level"],
            "goal": config["goal"],
            "domains": domains.split("/"),
            "words": words,
            "folder_name": folder_name,
            "imported_state": {
                "topic_bank": args.topic_bank is not None,
                "expression_bank": args.expression_bank is not None,
                "error_bank": args.error_bank is not None,
            },
        })
        prompt_path.write_text(render_instructions(config, domains, words), encoding="utf-8")
        (staged / "speaking-system.json").write_text(
            json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        shutil.copytree(staged, destination)
        make_zip(staged, archive)

    print(json.dumps({
        "folder": str(destination),
        "archive": str(archive),
        "chatgpt_instructions": str(destination / "00-Prompts" / "4-项目指令(完整版).md"),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
