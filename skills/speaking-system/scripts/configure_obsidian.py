#!/usr/bin/env python3
"""Merge Speaking System settings into an existing Obsidian vault."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise SystemExit(f"Cannot safely update invalid JSON file {path}: {exc}")


def save_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("vault", type=Path)
    parser.add_argument("system_folder", nargs="?", default="Speaking-System")
    args = parser.parse_args()
    vault = args.vault.expanduser().resolve()
    if not vault.is_dir():
        raise SystemExit(f"vault not found: {vault}")

    obsidian = vault / ".obsidian"
    community_path = obsidian / "community-plugins.json"
    community = load_json(community_path, [])
    if not isinstance(community, list):
        raise SystemExit(f"Expected a JSON list in {community_path}")
    for plugin in ("templater-obsidian", "dataview"):
        if plugin not in community:
            community.append(plugin)
    save_json(community_path, community)

    dataview_path = obsidian / "plugins" / "dataview" / "data.json"
    dataview = load_json(dataview_path, {})
    if not isinstance(dataview, dict):
        raise SystemExit(f"Expected a JSON object in {dataview_path}")
    dataview["enableDataviewJs"] = True
    save_json(dataview_path, dataview)

    templater_path = obsidian / "plugins" / "templater-obsidian" / "data.json"
    templater = load_json(templater_path, {})
    if not isinstance(templater, dict):
        raise SystemExit(f"Expected a JSON object in {templater_path}")
    templater["templates_folder"] = f"{args.system_folder}/01-Templates"
    save_json(templater_path, templater)

    hotkeys_path = obsidian / "hotkeys.json"
    hotkeys = load_json(hotkeys_path, {})
    if not isinstance(hotkeys, dict):
        raise SystemExit(f"Expected a JSON object in {hotkeys_path}")
    hotkeys["templater-obsidian:create-new-note-from-template"] = [
        {"modifiers": ["Mod", "Shift"], "key": "E"}
    ]
    save_json(hotkeys_path, hotkeys)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
