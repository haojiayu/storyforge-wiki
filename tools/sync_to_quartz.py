#!/usr/bin/env python3
"""Sync wiki output into a Quartz content directory."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
WIKI_DIR = REPO_ROOT / "wiki"


def sync_to_quartz(quartz_root: Path, clean: bool = False) -> None:
    content_dir = quartz_root / "content"
    if not quartz_root.exists():
        raise FileNotFoundError(f"Quartz root not found: {quartz_root}")
    content_dir.mkdir(parents=True, exist_ok=True)

    if clean:
        for item in content_dir.iterdir():
            if item.name.startswith("."):
                continue
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()

    copied = 0
    for src in WIKI_DIR.rglob("*.md"):
        rel = src.relative_to(WIKI_DIR)
        dst = content_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        copied += 1

    print(f"Synced {copied} markdown files to {content_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync wiki to Quartz content/")
    parser.add_argument("quartz_root", help="Path to Quartz repository root")
    parser.add_argument("--clean", action="store_true", help="Clean content/ before copying")
    args = parser.parse_args()
    sync_to_quartz(Path(args.quartz_root), clean=args.clean)
