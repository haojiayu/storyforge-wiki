#!/usr/bin/env python3
"""One-time migration from legacy entities/concepts folders to novel taxonomy."""

from __future__ import annotations

import shutil
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
WIKI_DIR = REPO_ROOT / "wiki"
LOG_FILE = WIKI_DIR / "log.md"

MAP = {
    "entities": "characters",
    "concepts": "systems",
}


def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def migrate() -> None:
    moved = 0
    for src_dir_name, dst_dir_name in MAP.items():
        src_dir = WIKI_DIR / src_dir_name
        dst_dir = WIKI_DIR / dst_dir_name
        if not src_dir.exists():
            continue
        dst_dir.mkdir(parents=True, exist_ok=True)
        for page in src_dir.glob("*.md"):
            target = dst_dir / page.name
            if target.exists():
                target = dst_dir / f"{page.stem}-legacy.md"
            shutil.copy2(page, target)
            moved += 1
            print(f"migrated: {page.relative_to(REPO_ROOT)} -> {target.relative_to(REPO_ROOT)}")

    log_entry = (
        f"## [{date.today().isoformat()}] migrate | Legacy taxonomy migration\n\n"
        f"Migrated {moved} legacy pages into novel taxonomy folders."
    )
    LOG_FILE.write_text(log_entry + "\n\n" + read_file(LOG_FILE), encoding="utf-8")
    print(f"done: migrated {moved} files")


if __name__ == "__main__":
    migrate()
