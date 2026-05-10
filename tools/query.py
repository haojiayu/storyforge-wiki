#!/usr/bin/env python3
"""Query the Novel World Wiki with timeline/arc-aware retrieval."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
WIKI_DIR = REPO_ROOT / "wiki"
INDEX_FILE = WIKI_DIR / "index.md"
LOG_FILE = WIKI_DIR / "log.md"
SCHEMA_FILE = REPO_ROOT / "CLAUDE.md"

PRIORITY_DIRS = ["chapters", "arcs", "timeline", "characters", "events", "systems"]


def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  saved: {path.relative_to(REPO_ROOT)}")


def call_llm(prompt: str, model_env: str, default_model: str, max_tokens: int = 4096) -> str:
    from litellm import completion

    model = os.getenv(model_env, default_model)
    response = completion(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content


def score_page(question: str, path: Path, content: str) -> int:
    q = question.lower()
    score = 0
    for token in re.findall(r"[a-zA-Z0-9_-]{3,}", q):
        if token in path.stem.lower() or token in content.lower():
            score += 2
    if any(word in q for word in ["chapter", "timeline", "arc", "canon", "continuity", "know by"]):
        if path.parts[-2] in PRIORITY_DIRS:
            score += 5
    if "spoiler" in q and "spoiler_level" in content:
        score += 3
    return score


def find_relevant_pages(question: str, cap: int = 18) -> list[Path]:
    pages = [p for p in WIKI_DIR.rglob("*.md") if p.name not in {"index.md", "log.md", "lint-report.md", "health-report.md"}]
    ranked: list[tuple[int, Path]] = []
    for p in pages:
        content = read_file(p)
        ranked.append((score_page(question, p, content), p))
    ranked.sort(key=lambda item: item[0], reverse=True)
    selected = [p for score, p in ranked if score > 0][:cap]
    overview = WIKI_DIR / "overview.md"
    if overview.exists() and overview not in selected:
        selected.insert(0, overview)
    return selected


def append_log(entry: str) -> None:
    existing = read_file(LOG_FILE)
    LOG_FILE.write_text(entry.strip() + "\n\n" + existing, encoding="utf-8")


def synthesize(question: str, pages: list[Path]) -> str:
    pages_context = ""
    for p in pages:
        pages_context += f"\n\n### {p.relative_to(REPO_ROOT)}\n{read_file(p)[:6000]}"
    schema = read_file(SCHEMA_FILE)
    prompt = f"""You are answering a novel/worldbuilding wiki query.
Schema:
{schema}

Question:
{question}

Wiki context:
{pages_context}

Write a markdown answer optimized for canon and continuity use:
- Explicitly state uncertainty for contested canon.
- Use timeline/chapter ordering when relevant.
- Cite supporting pages as [[PageName]].
- End with:
## Sources
- ...
"""
    try:
        return call_llm(prompt, "LLM_MODEL", "anthropic/claude-3-5-sonnet-latest", max_tokens=4096)
    except Exception:
        sources = "\n".join(f"- [[{p.stem}]]" for p in pages[:12])
        return (
            "## Fallback Answer\n"
            "LLM provider is not configured, so this is a retrieval-only fallback.\n\n"
            f"Question: {question}\n\n"
            "Use these pages as starting points:\n"
            f"{sources}\n\n"
            "## Sources\n"
            f"{sources}"
        )


def save_synthesis(question: str, answer: str, save_path: str) -> None:
    today = date.today().isoformat()
    full = WIKI_DIR / save_path
    frontmatter = (
        "---\n"
        f"title: \"{question[:80]}\"\n"
        "type: synthesis\n"
        "tags: []\n"
        "sources: []\n"
        "canon_status: canon\n"
        "spoiler_level: medium\n"
        "era: \"\"\n"
        "aliases: []\n"
        "relationships: []\n"
        "first_appearance: \"\"\n"
        f"last_updated: {today}\n"
        "---\n\n"
    )
    write_file(full, frontmatter + answer)


def query(question: str, save_path: str | None) -> None:
    if not read_file(INDEX_FILE):
        print("Wiki index missing/empty. Ingest first.")
        sys.exit(1)

    pages = find_relevant_pages(question)
    if not pages:
        pages = [INDEX_FILE]
    print(f"  querying with {len(pages)} pages")
    answer = synthesize(question, pages)
    print("\n" + "=" * 60)
    print(answer)
    print("=" * 60)

    actual_save = save_path
    if save_path is not None:
        if save_path == "":
            slug = re.sub(r"[^a-z0-9]+", "-", question.lower()).strip("-")[:60] or "synthesis"
            actual_save = f"syntheses/{slug}.md"
        save_synthesis(question, answer, actual_save)

    append_log(
        f"## [{date.today().isoformat()}] query | {question[:80]}\n\n"
        f"Synthesized from {len(pages)} pages."
        + (f" Saved to {actual_save}." if actual_save else "")
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query the Novel World Wiki")
    parser.add_argument("question")
    parser.add_argument("--save", nargs="?", const="", default=None)
    args = parser.parse_args()
    query(args.question, args.save)
