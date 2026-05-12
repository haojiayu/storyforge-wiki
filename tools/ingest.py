#!/usr/bin/env python3
"""Ingest manuscript/lore source files into the Novel World Wiki."""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

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
MAX_SOURCE_CHARS = 120_000
CHUNK_SIZE_CHARS = 45_000
CHUNK_OVERLAP_CHARS = 4_000
CHUNKING_THRESHOLD_CHARS = 90_000
MIN_RESPONSE_KEYS = {"title", "slug", "source_page", "index_entries", "domain_pages", "log_entry"}


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
        temperature=0,
    )
    return response.choices[0].message.content


def parse_json(text: str) -> dict:
    text = re.sub(r"^```(?:json)?\s*", "", text.strip())
    text = re.sub(r"\s*```$", "", text.strip())
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise ValueError("No JSON found in response")
    return json.loads(match.group(0))


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "untitled-source"


def truncate_for_prompt(content: str, max_chars: int = MAX_SOURCE_CHARS) -> tuple[str, bool]:
    if len(content) <= max_chars:
        return content, False
    keep_head = max_chars // 2
    keep_tail = max_chars - keep_head
    trimmed = (
        content[:keep_head]
        + "\n\n[... CONTENT TRUNCATED FOR INGEST PROMPT ...]\n\n"
        + content[-keep_tail:]
    )
    return trimmed, True


def _ensure_list_of_str(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    return []


def _stable_key(value: Any) -> str:
    if isinstance(value, dict):
        return json.dumps(value, sort_keys=True, ensure_ascii=True)
    return str(value)


def _dedupe_list(values: list[Any]) -> list[Any]:
    deduped: list[Any] = []
    seen = set()
    for value in values:
        key = _stable_key(value)
        if key not in seen:
            deduped.append(value)
            seen.add(key)
    return deduped


def split_text_into_chunks(content: str, chunk_size: int = CHUNK_SIZE_CHARS, overlap: int = CHUNK_OVERLAP_CHARS) -> list[str]:
    if len(content) <= chunk_size:
        return [content]
    if overlap >= chunk_size:
        overlap = max(0, chunk_size // 10)
    chunks: list[str] = []
    start = 0
    content_len = len(content)
    while start < content_len:
        end = min(content_len, start + chunk_size)
        chunk = content[start:end]
        if chunk.strip():
            chunks.append(chunk)
        if end == content_len:
            break
        start = max(0, end - overlap)
    return chunks


def normalize_frontmatter(content: str, page_type: str, today: str, fallback_title: str, source_slug: str) -> str:
    if content.startswith("---\n"):
        fm_end = content.find("\n---", 4)
        if fm_end != -1:
            fm = content[: fm_end + 4]
            body = content[fm_end + 4 :].lstrip("\n")
            if not re.search(r'^last_updated:\s*', fm, re.MULTILINE):
                fm = fm.rstrip("\n") + f"\nlast_updated: {today}\n---"
            return fm + "\n\n" + body

    return (
        "---\n"
        f"title: \"{fallback_title}\"\n"
        f"type: {page_type}\n"
        "tags: []\n"
        f"sources: [\"{source_slug}\"]\n"
        "canon_status: draft\n"
        "spoiler_level: medium\n"
        "era: \"\"\n"
        "aliases: []\n"
        "relationships: []\n"
        "first_appearance: \"\"\n"
        f"last_updated: {today}\n"
        "---\n\n"
        + content.strip()
        + "\n"
    )


def normalize_ingest_payload(data: dict, source: Path, today: str) -> dict:
    missing = [k for k in MIN_RESPONSE_KEYS if k not in data]
    if missing:
        raise ValueError(f"Missing required keys in ingest response: {', '.join(missing)}")

    title = str(data.get("title", "")).strip() or source.stem.replace("-", " ").title()
    slug = slugify(str(data.get("slug", "")).strip() or title or source.stem)
    source_page = str(data.get("source_page", "")).strip()
    if not source_page:
        raise ValueError("source_page is empty")
    source_page = normalize_frontmatter(source_page, "source", today, title, slug)

    index_entries_raw = data.get("index_entries", {})
    if not isinstance(index_entries_raw, dict):
        index_entries_raw = {}
    index_entries: dict[str, list[str]] = {}
    for section in INDEX_SECTIONS:
        deduped: list[str] = []
        seen = set()
        for line in _ensure_list_of_str(index_entries_raw.get(section, [])):
            if line not in seen:
                deduped.append(line)
                seen.add(line)
        index_entries[section] = deduped
    if not index_entries["Sources"]:
        index_entries["Sources"].append(f"- [{title}](sources/{slug}.md) — ingested")

    domain_pages_raw = data.get("domain_pages", [])
    domain_pages: list[dict[str, str]] = []
    if isinstance(domain_pages_raw, list):
        for item in domain_pages_raw:
            if not isinstance(item, dict):
                continue
            rel_path = str(item.get("path", "")).strip().replace("\\", "/")
            content = str(item.get("content", "")).strip()
            if not rel_path or not content:
                continue
            folder = rel_path.split("/", 1)[0]
            if folder not in DOMAIN_DIRS:
                continue
            page_title = Path(rel_path).stem.replace("-", " ").title()
            page_type = folder[:-1] if folder.endswith("s") else folder
            normalized = normalize_frontmatter(content, page_type, today, page_title, slug)
            domain_pages.append({"path": rel_path, "content": normalized})

    log_entry = str(data.get("log_entry", "")).strip()
    if not log_entry:
        log_entry = f"## [{today}] ingest | {title}\n\nAdded canon updates and narrative deltas."

    return {
        "title": title,
        "slug": slug,
        "source_page": source_page,
        "overview_update": data.get("overview_update"),
        "index_entries": index_entries,
        "domain_pages": domain_pages,
        "contradictions": _ensure_list_of_str(data.get("contradictions", [])),
        "log_entry": log_entry,
    }


def call_llm_with_repair(prompt: str, max_tokens: int = 8192, retries: int = 2) -> dict:
    raw = call_llm(prompt, max_tokens=max_tokens)
    try:
        return parse_json(raw)
    except Exception:
        last_error = None
        last_raw = raw
        for _ in range(retries):
            repair_prompt = (
                "Fix the following output so it is valid JSON only and matches the requested schema exactly.\n\n"
                f"OUTPUT:\n{last_raw}\n"
            )
            try:
                last_raw = call_llm(repair_prompt, max_tokens=max_tokens)
                return parse_json(last_raw)
            except Exception as err:
                last_error = err
        raise ValueError(f"Could not parse valid JSON from LLM response: {last_error}")


def extract_ingest_facts(
    schema: str,
    templates: str,
    rel_source: str,
    source_for_prompt: str,
    chunk_info: str | None = None,
) -> dict:
    """Stage 1: Extract structured facts from source text."""
    chunk_prefix = f"Chunk context: {chunk_info}\n\n" if chunk_info else ""
    prompt = f"""You are a fiction wiki extraction engine.
Extract facts only. Do not author final pages yet.

Schema:
{schema}

Templates:
{templates}

{chunk_prefix}Source file: {rel_source}
=== SOURCE START ===
{source_for_prompt}
=== SOURCE END ===

Return valid JSON only:
{{
  "source_title_guess": "string",
  "story_scope": "one short paragraph",
  "entities": [
    {{
      "name": "string",
      "type": "character|location|faction|culture|artifact|system|event|arc|chapter|timeline",
      "aliases": [],
      "facts": [],
      "relationships": [
        {{"target": "Name", "type": "ALLY_OF|CONFLICTS_WITH|LOCATED_IN|CAUSES|LEARNS|BETRAYS|OWNS|MEMBER_OF", "evidence": "quote or summary"}}
      ]
    }}
  ],
  "timeline_events": [
    {{"label": "string", "date_or_era": "string", "summary": "string"}}
  ],
  "character_state_changes": [
    {{"character": "string", "from": "string", "to": "string", "evidence": "string"}}
  ],
  "world_facts": [],
  "unresolved_threads": [],
  "contradictions": []
}}
"""
    return call_llm_with_repair(prompt, max_tokens=8192)


def merge_extracted_facts(parts: list[dict]) -> dict:
    if not parts:
        return {
            "source_title_guess": "",
            "story_scope": "",
            "entities": [],
            "timeline_events": [],
            "character_state_changes": [],
            "world_facts": [],
            "unresolved_threads": [],
            "contradictions": [],
        }

    source_title_guess = ""
    scopes: list[str] = []
    entities: list[Any] = []
    timeline_events: list[Any] = []
    character_state_changes: list[Any] = []
    world_facts: list[Any] = []
    unresolved_threads: list[Any] = []
    contradictions: list[Any] = []

    for part in parts:
        if not source_title_guess:
            source_title_guess = str(part.get("source_title_guess", "")).strip()
        scope = str(part.get("story_scope", "")).strip()
        if scope:
            scopes.append(scope)
        if isinstance(part.get("entities"), list):
            entities.extend(part["entities"])
        if isinstance(part.get("timeline_events"), list):
            timeline_events.extend(part["timeline_events"])
        if isinstance(part.get("character_state_changes"), list):
            character_state_changes.extend(part["character_state_changes"])
        if isinstance(part.get("world_facts"), list):
            world_facts.extend(part["world_facts"])
        if isinstance(part.get("unresolved_threads"), list):
            unresolved_threads.extend(part["unresolved_threads"])
        if isinstance(part.get("contradictions"), list):
            contradictions.extend(part["contradictions"])

    return {
        "source_title_guess": source_title_guess,
        "story_scope": " ".join(scopes[:3]).strip(),
        "entities": _dedupe_list(entities),
        "timeline_events": _dedupe_list(timeline_events),
        "character_state_changes": _dedupe_list(character_state_changes),
        "world_facts": _dedupe_list(world_facts),
        "unresolved_threads": _dedupe_list(unresolved_threads),
        "contradictions": _dedupe_list(contradictions),
    }


def extract_ingest_facts_mapreduce(schema: str, templates: str, rel_source: str, source_content: str) -> dict:
    if len(source_content) < CHUNKING_THRESHOLD_CHARS:
        return extract_ingest_facts(schema, templates, rel_source, source_content)

    chunks = split_text_into_chunks(source_content)
    print(f"  chunking large source: {len(source_content)} chars into {len(chunks)} chunks")
    chunk_results: list[dict] = []
    for idx, chunk in enumerate(chunks, start=1):
        chunk_info = f"{idx}/{len(chunks)} (chars={len(chunk)})"
        print(f"  extracting chunk {chunk_info}")
        chunk_result = extract_ingest_facts(
            schema=schema,
            templates=templates,
            rel_source=rel_source,
            source_for_prompt=chunk,
            chunk_info=chunk_info,
        )
        chunk_results.append(chunk_result)
    merged = merge_extracted_facts(chunk_results)
    print(
        "  merged extracted facts: "
        f"{len(merged.get('entities', []))} entities, "
        f"{len(merged.get('timeline_events', []))} timeline events"
    )
    return merged


def synthesize_ingest_pages(
    schema: str,
    templates: str,
    index_content: str,
    overview_content: str,
    rel_source: str,
    extracted_facts: dict,
    today: str,
) -> dict:
    """Stage 2: Build final wiki pages from extracted facts."""
    prompt = f"""You are maintaining a novel/worldbuilding wiki.
Use the extracted facts as your primary grounding.

Schema:
{schema}

Section templates (must follow when writing pages):
{templates}

Current index:
{index_content}

Current overview:
{overview_content}

Source file: {rel_source}

Extracted facts JSON:
{json.dumps(extracted_facts, ensure_ascii=True)}

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
    return call_llm_with_repair(prompt, max_tokens=8192)


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
        section_match = re.search(rf"(## {re.escape(section)}\n)([\s\S]*?)(?=\n## |\Z)", content)
        existing_items: list[str] = []
        if section_match:
            existing_items = [
                line.strip()
                for line in section_match.group(2).splitlines()
                if line.strip().startswith("- ")
            ]
        merged = []
        seen = set()
        for line in existing_items + [line.strip() for line in items if line.strip()]:
            if line not in seen:
                merged.append(line)
                seen.add(line)
        replacement = header + "\n" + ("\n".join(merged) + "\n" if merged else "")
        if section_match:
            content = content[: section_match.start()] + replacement + content[section_match.end() :]
        else:
            content = content.rstrip() + "\n\n" + replacement
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
    _, was_truncated = truncate_for_prompt(source_content)
    schema = read_file(SCHEMA_FILE)
    templates = read_file(TEMPLATES_FILE)
    index_content = read_file(INDEX_FILE)
    overview_content = read_file(OVERVIEW_FILE)
    today = date.today().isoformat()

    rel_source = source.relative_to(REPO_ROOT) if source.is_relative_to(REPO_ROOT) else source.name

    try:
        extracted = extract_ingest_facts_mapreduce(schema, templates, str(rel_source), source_content)
        raw_data = synthesize_ingest_pages(
            schema=schema,
            templates=templates,
            index_content=index_content,
            overview_content=overview_content,
            rel_source=str(rel_source),
            extracted_facts=extracted,
            today=today,
        )
        data = normalize_ingest_payload(raw_data, source=source, today=today)
    except Exception:
        print("  warning: LLM call failed, using deterministic fallback ingest")
        data = local_fallback_ingest(source, source_content, today)
    if was_truncated:
        print(f"  note: source prompt truncated to {MAX_SOURCE_CHARS} chars for stable ingestion")

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
