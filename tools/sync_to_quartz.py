#!/usr/bin/env python3
"""Sync wiki output into a Quartz content directory."""

from __future__ import annotations

import argparse
import shutil
import re
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
WIKI_DIR = REPO_ROOT / "wiki"


def _with_category_footer(content: str) -> str:
    """Append a Fandom-like category footer derived from frontmatter."""
    if not content.startswith("---\n"):
        return content
    fm_end = content.find("\n---", 4)
    if fm_end == -1:
        return content

    frontmatter = content[: fm_end + 4]
    body = content[fm_end + 4 :].rstrip()
    if "<!-- wiki-category-footer -->" in body:
        return content

    page_type = None
    type_match = re.search(r"^type:\s*([^\n]+)$", frontmatter, re.MULTILINE)
    if type_match:
        page_type = type_match.group(1).strip().strip('"\'')

    tags: list[str] = []
    tags_match = re.search(r"^tags:\s*\[(.*?)\]\s*$", frontmatter, re.MULTILINE)
    if tags_match:
        raw = tags_match.group(1).strip()
        if raw:
            tags = [x.strip().strip('"\'') for x in raw.split(",") if x.strip()]

    categories: list[str] = []
    if page_type:
        categories.append(page_type.title())
    categories.extend(tags)
    deduped: list[str] = []
    seen = set()
    for cat in categories:
        key = cat.lower()
        if key not in seen:
            deduped.append(cat)
            seen.add(key)
    if not deduped:
        return content

    chips = " ".join(f"<span class=\"wiki-category-chip\">{cat}</span>" for cat in deduped)
    footer = (
        "\n\n<!-- wiki-category-footer -->\n"
        "<div class=\"wiki-categories\">"
        "<span class=\"wiki-categories-label\">Categories:</span> "
        f"{chips}</div>\n"
    )
    return frontmatter + body + footer


def _with_redirect_aliases(content: str, rel: Path) -> str:
    """Ensure Quartz can resolve short wikilink slugs without 404s.

    Adds canonical alias variants based on title and filename stem:
    - Title (e.g. "Lawrence")
    - Title with spaces converted to hyphens (e.g. "Yozaki-Van-Krill")
    - TitleCase stem with hyphens (e.g. "Master-Timeline")
    """
    if not content.startswith("---\n"):
        return content
    fm_end = content.find("\n---", 4)
    if fm_end == -1:
        return content

    frontmatter = content[: fm_end + 4]
    body = content[fm_end + 4 :]

    title_match = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', frontmatter, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else rel.stem

    candidates = set()
    if title:
        candidates.add(title)
        candidates.add(title.replace(" ", "-"))
        candidates.add(title.lower().replace(" ", "-"))

    stem_parts = [p for p in rel.stem.split("-") if p]
    if stem_parts:
        candidates.add("-".join(part[:1].upper() + part[1:] for part in stem_parts))
    candidates.add(rel.stem)

    aliases_match = re.search(r"^aliases:\s*\[(.*?)\]\s*$", frontmatter, re.MULTILINE)
    existing: list[str] = []
    if aliases_match:
        raw = aliases_match.group(1).strip()
        if raw:
            existing = [x.strip().strip('"\'') for x in raw.split(",") if x.strip()]

    merged = []
    seen = set()
    for value in existing + sorted(candidates):
        if value and value not in seen:
            merged.append(value)
            seen.add(value)

    aliases_line = "aliases: [" + ", ".join(f'"{a}"' for a in merged) + "]"
    if aliases_match:
        frontmatter = re.sub(r"^aliases:\s*\[.*?\]\s*$", aliases_line, frontmatter, flags=re.MULTILINE)
    else:
        # Insert aliases near other canonical metadata if possible.
        if "relationships:" in frontmatter:
            frontmatter = frontmatter.replace("relationships: []", f"{aliases_line}\nrelationships: []")
        else:
            frontmatter = frontmatter.rstrip("\n") + "\n" + aliases_line + "\n"

    return frontmatter + body


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
    source_index_text = None
    source_overview_text = None
    for src in WIKI_DIR.rglob("*.md"):
        rel = src.relative_to(WIKI_DIR)
        if rel.as_posix() == "index.md":
            source_index_text = src.read_text(encoding="utf-8")
        if rel.as_posix() == "overview.md":
            source_overview_text = src.read_text(encoding="utf-8")
        dst = content_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        transformed = _with_redirect_aliases(src.read_text(encoding="utf-8"), rel)
        transformed = _with_category_footer(transformed)
        dst.write_text(transformed, encoding="utf-8")
        copied += 1

    # Quartz homepage should default to overview content, not index catalog.
    if source_overview_text is not None:
        (content_dir / "index.md").write_text(source_overview_text, encoding="utf-8")
    # Preserve original wiki index as a browseable page.
    if source_index_text is not None:
        (content_dir / "wiki-index.md").write_text(source_index_text, encoding="utf-8")

    print(f"Synced {copied} markdown files to {content_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync wiki to Quartz content/")
    parser.add_argument("quartz_root", help="Path to Quartz repository root")
    parser.add_argument("--clean", action="store_true", help="Clean content/ before copying")
    args = parser.parse_args()
    sync_to_quartz(Path(args.quartz_root), clean=args.clean)
