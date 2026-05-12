#!/usr/bin/env python3
"""Ingest manuscript/lore source files into the Novel World Wiki."""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
WIKI_DIR = REPO_ROOT / "wiki"
INDEX_FILE = WIKI_DIR / "index.md"
OVERVIEW_FILE = WIKI_DIR / "overview.md"
LOG_FILE = WIKI_DIR / "log.md"
SCHEMA_FILE = REPO_ROOT / "CLAUDE.md"
TEMPLATES_FILE = REPO_ROOT / "templates" / "wiki-section-templates.md"

DOMAIN_DIRS = [
    "sources", "characters", "locations", "factions", "cultures", "artifacts",
    "systems", "events", "timeline", "arcs", "chapters", "syntheses",
]
INDEX_SECTIONS = [
    "Sources", "Characters", "Locations", "Factions", "Cultures",
    "Artifacts", "Systems", "Events", "Timeline", "Arcs", "Chapters", "Syntheses",
]
CONVERTIBLE_EXTENSIONS = {
    ".pdf", ".docx", ".pptx", ".xlsx", ".xls", ".html", ".htm", ".txt",
    ".csv", ".json", ".xml", ".rst", ".rtf", ".epub", ".ipynb",
    ".yaml", ".yml", ".tsv", ".wav", ".mp3",
}
ALL_SUPPORTED_EXTENSIONS = {".md"} | CONVERTIBLE_EXTENSIONS


def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  wrote: {path.relative_to(REPO_ROOT)}")


def call_llm(prompt: str, max_tokens: int = 8192) -> str:
    from litellm import completion

    model = os.getenv("LLM_MODEL", "anthropic/claude-3-5-sonnet-latest")
    response = completion(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content


def parse_json(text: str) -> dict:
    text = re.sub(r"^```(?:json)?\s*", "", text.strip())
    text = re.sub(r"\s*```$", "", text.strip())
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise ValueError("No JSON found in response")
    return json.loads(match.group(0))


def local_fallback_ingest(source: Path, source_content: str, today: str) -> dict:
    slug = source.stem.lower()
    title = source.stem.replace("-", " ").title()
    source_page = (
        "---\n"
        f"title: \"{title}\"\n"
        "type: source\n"
        "tags: []\n"
        f"sources: [\"{slug}\"]\n"
        "canon_status: draft\n"
        "spoiler_level: medium\n"
        "era: \"\"\n"
        "aliases: []\n"
        "relationships: []\n"
        "first_appearance: \"\"\n"
        f"last_updated: {today}\n"
        "---\n\n"
        "## Narrative Beats\n"
        f"- Imported from `{source.name}` without LLM enrichment.\n\n"
        "## Character State Changes\n- TBD\n\n"
        "## World Facts Introduced\n- TBD\n\n"
        "## Timeline Events\n- TBD\n\n"
        "## Unresolved Threads\n- TBD\n\n"
        "## Canon Conflicts\n- None detected in fallback mode.\n\n"
        "## Raw Extract\n"
        + source_content[:2500]
        + "\n"
    )
    return {
        "title": title,
        "slug": slug,
        "source_page": source_page,
        "overview_update": None,
        "index_entries": {"Sources": [f"- [{title}](sources/{slug}.md) — fallback ingest"]},
        "domain_pages": [],
        "contradictions": [],
        "log_entry": f"## [{today}] ingest | {title}\n\nFallback ingest (no LLM provider configured).",
    }


def ensure_wiki_scaffold() -> None:
    for dirname in DOMAIN_DIRS:
        (WIKI_DIR / dirname).mkdir(parents=True, exist_ok=True)
    if not INDEX_FILE.exists():
        lines = ["# Wiki Index", "", "## Overview", "- [Overview](overview.md) — living synthesis", ""]
        for section in INDEX_SECTIONS:
            lines.extend([f"## {section}", ""])
        write_file(INDEX_FILE, "\n".join(lines).strip() + "\n")
    if not OVERVIEW_FILE.exists():
        write_file(
            OVERVIEW_FILE,
            "---\n"
            "title: \"Overview\"\n"
            "type: synthesis\n"
            "tags: []\n"
            "sources: []\n"
            "canon_status: canon\n"
            "spoiler_level: low\n"
            "era: \"\"\n"
            "aliases: []\n"
            "relationships: []\n"
            "first_appearance: \"\"\n"
            f"last_updated: {date.today().isoformat()}\n"
            "---\n\n"
            "# Overview\n\nNo sources ingested yet.\n",
        )


def update_index(entries: dict[str, list[str]]) -> None:
    content = read_file(INDEX_FILE)
    for section, items in entries.items():
        header = f"## {section}"
        if header not in content:
            content += f"\n{header}\n"
        insertion = "".join(f"{line}\n" for line in items if line.strip())
        content = content.replace(header + "\n", header + "\n" + insertion)
    write_file(INDEX_FILE, content)


def append_log(entry: str) -> None:
    existing = read_file(LOG_FILE)
    write_file(LOG_FILE, entry.strip() + "\n\n" + existing)


def extract_wikilinks(content: str) -> list[str]:
    return re.findall(r"\[\[([^\]]+)\]\]", content)


def validate_pages(changed_pages: list[Path]) -> None:
    page_stems = {p.stem.lower() for p in WIKI_DIR.rglob("*.md")}
    broken = []
    for page in changed_pages:
        if not page.exists():
            continue
        for link in extract_wikilinks(read_file(page)):
            if Path(link).stem.lower() not in page_stems:
                broken.append((page.relative_to(WIKI_DIR), link))
    if broken:
        print("  warning: broken wikilinks found")
        for rel, link in broken[:10]:
            print(f"    wiki/{rel} -> [[{link}]]")
    else:
        print("  validation: no broken wikilinks in changed pages")


def convert_to_md(source: Path) -> Path:
    from markitdown import MarkItDown

    md = MarkItDown(enable_plugins=False)
    result = md.convert(str(source))
    output = source.with_suffix(".md")
    output.write_text(result.text_content, encoding="utf-8")
    print(f"  converted: {source.name} -> {output.name}")
    return output


def ingest(source_path: str, auto_convert: bool = True) -> None:
    ensure_wiki_scaffold()
    source = Path(source_path)
    if not source.exists():
        print(f"Error: file not found: {source_path}")
        sys.exit(1)

    if source.suffix.lower() != ".md":
        if not auto_convert:
            print(f"  skipping non-md with --no-convert: {source.name}")
            return
        if source.suffix.lower() not in CONVERTIBLE_EXTENSIONS:
            print(f"  unsupported format: {source.suffix}")
            return
        source = convert_to_md(source)

    source_content = source.read_text(encoding="utf-8")
    schema = read_file(SCHEMA_FILE)
    templates = read_file(TEMPLATES_FILE)
    index_content = read_file(INDEX_FILE)
    overview_content = read_file(OVERVIEW_FILE)
    today = date.today().isoformat()

    rel_source = source.relative_to(REPO_ROOT) if source.is_relative_to(REPO_ROOT) else source.name

    prompt = f"""You are maintaining a novel/worldbuilding wiki.
Schema:
{schema}

Section templates (must follow when writing pages):
{templates}

Current index:
{index_content}

Current overview:
{overview_content}

New source file: {rel_source}
=== SOURCE START ===
{source_content}
=== SOURCE END ===

Return only valid JSON:
{{
  "title": "Source title",
  "slug": "kebab-case-source-slug",
  "source_page": "full markdown page for wiki/sources/<slug>.md",
  "overview_update": "full markdown for wiki/overview.md or null",
  "index_entries": {{
    "Sources": ["- [Title](sources/slug.md) — one line"],
    "Characters": [],
    "Locations": [],
    "Factions": [],
    "Cultures": [],
    "Artifacts": [],
    "Systems": [],
    "Events": [],
    "Timeline": [],
    "Arcs": [],
    "Chapters": []
  }},
  "domain_pages": [
    {{"path": "characters/CharacterName.md", "content": "full markdown following Character template"}},
    {{"path": "timeline/Era-EventName.md", "content": "full markdown following Timeline template"}}
  ],
  "contradictions": ["..."],
  "log_entry": "## [{today}] ingest | <title>\\n\\nAdded canon updates and narrative deltas."
}}
"""

    try:
        raw = call_llm(prompt)
        data = parse_json(raw)
    except Exception:
        print("  warning: LLM call failed, using deterministic fallback ingest")
        data = local_fallback_ingest(source, source_content, today)

    changed = []
    slug = data["slug"]
    source_page = WIKI_DIR / "sources" / f"{slug}.md"
    write_file(source_page, data["source_page"])
    changed.append(source_page)

    for page in data.get("domain_pages", []):
        target = WIKI_DIR / page["path"]
        write_file(target, page["content"])
        changed.append(target)

    if data.get("overview_update"):
        write_file(OVERVIEW_FILE, data["overview_update"])
        changed.append(OVERVIEW_FILE)

    update_index(data.get("index_entries", {}))
    append_log(data["log_entry"])

    contradictions = data.get("contradictions", [])
    if contradictions:
        print("  contradictions:")
        for item in contradictions:
            print(f"    - {item}")

    validate_pages(changed)
    print(f"  done ingest: {data['title']}")


def main() -> None:
    no_convert = "--no-convert" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]

    if not args:
        print("Usage: python tools/ingest.py <file-or-dir> [more files] [--no-convert]")
        sys.exit(1)

    paths: list[Path] = []
    for arg in args:
        p = Path(arg)
        if p.is_file() and p.suffix.lower() in ALL_SUPPORTED_EXTENSIONS:
            paths.append(p)
        elif p.is_dir():
            for candidate in p.rglob("*"):
                if candidate.is_file() and candidate.suffix.lower() in ALL_SUPPORTED_EXTENSIONS:
                    paths.append(candidate)

    if not paths:
        print("No supported files found.")
        sys.exit(1)

    seen = set()
    unique_paths = []
    for path in paths:
        resolved = path.resolve()
        if resolved not in seen:
            seen.add(resolved)
            unique_paths.append(path)

    for path in unique_paths:
        ingest(str(path), auto_convert=not no_convert)


if __name__ == "__main__":
    main()
