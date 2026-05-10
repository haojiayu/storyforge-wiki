#!/usr/bin/env python3
"""Lint continuity and canon quality for Novel World Wiki."""

from __future__ import annotations

import argparse
import os
import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
WIKI_DIR = REPO_ROOT / "wiki"
LOG_FILE = WIKI_DIR / "log.md"


def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def all_pages() -> list[Path]:
    return [p for p in WIKI_DIR.rglob("*.md") if p.name not in {"index.md", "log.md", "lint-report.md"}]


def extract_wikilinks(content: str) -> list[str]:
    return re.findall(r"\[\[([^\]]+)\]\]", content)


def page_stems(pages: list[Path]) -> set[str]:
    return {p.stem.lower() for p in pages}


def find_orphans(pages: list[Path]) -> list[Path]:
    inbound = defaultdict(int)
    stem_to_path = {p.stem.lower(): p for p in pages}
    for p in pages:
        for link in extract_wikilinks(read_file(p)):
            target = stem_to_path.get(Path(link).stem.lower())
            if target:
                inbound[target] += 1
    return [p for p in pages if inbound[p] == 0 and p.name != "overview.md"]


def find_broken_links(pages: list[Path]) -> list[tuple[Path, str]]:
    stems = page_stems(pages)
    broken = []
    for p in pages:
        for link in extract_wikilinks(read_file(p)):
            if Path(link).stem.lower() not in stems:
                broken.append((p, link))
    return broken


def find_sparse_pages(pages: list[Path], min_outbound: int = 2) -> list[tuple[Path, int]]:
    sparse = []
    for p in pages:
        links = {Path(link).stem.lower() for link in extract_wikilinks(read_file(p))}
        if len(links) < min_outbound:
            sparse.append((p, len(links)))
    return sorted(sparse, key=lambda item: item[1])


def find_alias_collisions(pages: list[Path]) -> dict[str, list[str]]:
    collisions: dict[str, list[str]] = defaultdict(list)
    alias_pattern = re.compile(r"^aliases:\s*\[(.*?)\]\s*$", re.MULTILINE)
    for p in pages:
        content = read_file(p)
        match = alias_pattern.search(content)
        if not match:
            continue
        raw = match.group(1).strip()
        if not raw:
            continue
        for part in raw.split(","):
            alias = part.strip().strip('"\'').lower()
            if alias:
                collisions[alias].append(str(p.relative_to(REPO_ROOT)))
    return {alias: refs for alias, refs in collisions.items() if len(refs) > 1}


def find_contested_without_rationale(pages: list[Path]) -> list[Path]:
    bad = []
    for p in pages:
        content = read_file(p)
        if "canon_status: contested" in content and "## Canon Conflicts" not in content:
            bad.append(p)
    return bad


def find_unresolved_threads_without_backlinks(pages: list[Path]) -> list[Path]:
    issues = []
    for p in pages:
        content = read_file(p)
        if "## Unresolved Threads" in content:
            section = content.split("## Unresolved Threads", 1)[1]
            if len(extract_wikilinks(section)) == 0:
                issues.append(p)
    return issues


def call_llm(prompt: str) -> str:
    try:
        from litellm import completion
    except ImportError:
        return (
            "## Timeline Contradictions\n- Semantic pass skipped (`litellm` not installed).\n\n"
            "## Character Continuity\n- Semantic pass skipped.\n\n"
            "## Setup and Payoff Gaps\n- Semantic pass skipped.\n\n"
            "## Retcon Risk\n- Semantic pass skipped."
        )

    model = os.getenv("LLM_MODEL", "anthropic/claude-3-5-sonnet-latest")
    try:
        response = completion(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2200,
        )
        return response.choices[0].message.content
    except Exception:
        return (
            "## Timeline Contradictions\n- Semantic pass skipped (LLM provider not configured).\n\n"
            "## Character Continuity\n- Semantic pass skipped.\n\n"
            "## Setup and Payoff Gaps\n- Semantic pass skipped.\n\n"
            "## Retcon Risk\n- Semantic pass skipped."
        )


def semantic_continuity_pass(pages: list[Path]) -> str:
    sample = pages[:20]
    context = ""
    for p in sample:
        context += f"\n\n### {p.relative_to(REPO_ROOT)}\n{read_file(p)[:1600]}"
    prompt = f"""You are linting a novel canon wiki. Identify:
1) timeline contradictions
2) character continuity breaks
3) setup/payoff mismatches
4) retcon risk areas
Keep output concise markdown with sections:
## Timeline Contradictions
## Character Continuity
## Setup and Payoff Gaps
## Retcon Risk
Context:
{context}
"""
    return call_llm(prompt)


def append_log(entry: str) -> None:
    existing = read_file(LOG_FILE)
    LOG_FILE.write_text(entry.strip() + "\n\n" + existing, encoding="utf-8")


def run_lint() -> str:
    pages = all_pages()
    if not pages:
        return "Wiki is empty."

    orphans = find_orphans(pages)
    broken = find_broken_links(pages)
    sparse = find_sparse_pages(pages)
    alias_collisions = find_alias_collisions(pages)
    contested = find_contested_without_rationale(pages)
    unresolved = find_unresolved_threads_without_backlinks(pages)
    semantic = semantic_continuity_pass(pages)

    lines = [
        f"# Novel Wiki Lint Report — {date.today().isoformat()}",
        "",
        "## Structural",
        f"- Orphans: {len(orphans)}",
        f"- Broken links: {len(broken)}",
        f"- Sparse pages: {len(sparse)}",
        "",
    ]
    if broken:
        lines.append("### Broken Links")
        lines.extend(f"- `{p.relative_to(REPO_ROOT)}` -> `[[{link}]]`" for p, link in broken[:40])
        lines.append("")
    if alias_collisions:
        lines.append("### Alias Collisions")
        for alias, refs in alias_collisions.items():
            lines.append(f"- `{alias}` appears in: {', '.join(refs)}")
        lines.append("")
    if contested:
        lines.append("### Contested Canon Without Rationale")
        lines.extend(f"- `{p.relative_to(REPO_ROOT)}`" for p in contested)
        lines.append("")
    if unresolved:
        lines.append("### Unresolved Threads Missing Wikilinks")
        lines.extend(f"- `{p.relative_to(REPO_ROOT)}`" for p in unresolved)
        lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(semantic)

    report = "\n".join(lines)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lint Novel World Wiki")
    parser.add_argument("--save", action="store_true")
    args = parser.parse_args()

    report = run_lint()
    print(report)
    if args.save:
        out = WIKI_DIR / "lint-report.md"
        out.write_text(report, encoding="utf-8")
        print(f"\nSaved: {out.relative_to(REPO_ROOT)}")
    append_log(f"## [{date.today().isoformat()}] lint | Continuity lint\n\nRan fiction continuity lint.")
