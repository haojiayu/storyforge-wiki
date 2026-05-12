#!/usr/bin/env python3
"""Ensure required section headings and infoboxes exist for wiki domain pages."""

from __future__ import annotations

from pathlib import Path
import re

REPO_ROOT = Path(__file__).parent.parent
WIKI_DIR = REPO_ROOT / "wiki"

REQUIRED_HEADINGS: dict[str, list[str]] = {
    "characters": [
        "## Overview",
        "## Biography",
        "## Personality and Traits",
        "## Abilities and Equipment",
        "## Relationships",
        "## Appearances and Arc Role",
        "## Trivia",
    ],
    "arcs": [
        "## Synopsis",
        "## Plot",
        "## Major Events",
        "## Characters Involved",
        "## Continuity Notes",
    ],
    "locations": [
        "## Overview",
        "## Geography",
        "## History",
        "## Politics and Society",
        "## Notable Events",
    ],
    "factions": [
        "## Overview",
        "## History",
        "## Organization",
        "## Goals and Methods",
        "## Relationships",
    ],
    "systems": [
        "## Overview",
        "## Mechanics",
        "## Limitations and Costs",
        "## Known Users or Practitioners",
        "## Canon Clarifications",
    ],
    "events": [
        "## Summary",
        "## Prelude",
        "## Event Breakdown",
        "## Aftermath",
        "## Related Pages",
    ],
    "timeline": [
        "## Timeline Overview",
        "## Chronology",
        "## Uncertain Dates",
    ],
    "sources": [
        "## Source Overview",
        "## Plot and Lore Extracts",
        "## Character Updates",
        "## Timeline Additions",
        "## Open Questions",
        "## Contradictions and Retcons",
    ],
}

INFOBOXES: dict[str, str] = {
    "characters": (
        "<table class=\"infobox\">\n"
        "  <tr><th colspan=\"2\">Character Information</th></tr>\n"
        "  <tr><td>Full Name</td><td>TBD</td></tr>\n"
        "  <tr><td>Aliases</td><td>TBD</td></tr>\n"
        "  <tr><td>Species</td><td>TBD</td></tr>\n"
        "  <tr><td>Affiliation</td><td>TBD</td></tr>\n"
        "  <tr><td>Status</td><td>TBD</td></tr>\n"
        "  <tr><td>First Appearance</td><td>TBD</td></tr>\n"
        "</table>"
    ),
    "arcs": (
        "<table class=\"infobox\">\n"
        "  <tr><th colspan=\"2\">Arc Information</th></tr>\n"
        "  <tr><td>Name</td><td>TBD</td></tr>\n"
        "  <tr><td>Timeline</td><td>TBD</td></tr>\n"
        "  <tr><td>Main Conflict</td><td>TBD</td></tr>\n"
        "  <tr><td>Primary Cast</td><td>TBD</td></tr>\n"
        "  <tr><td>Status</td><td>TBD</td></tr>\n"
        "</table>"
    ),
    "locations": (
        "<table class=\"infobox\">\n"
        "  <tr><th colspan=\"2\">Location Information</th></tr>\n"
        "  <tr><td>Region</td><td>TBD</td></tr>\n"
        "  <tr><td>Type</td><td>TBD</td></tr>\n"
        "  <tr><td>Ruling Power</td><td>TBD</td></tr>\n"
        "  <tr><td>Population</td><td>TBD</td></tr>\n"
        "  <tr><td>First Appearance</td><td>TBD</td></tr>\n"
        "</table>"
    ),
    "factions": (
        "<table class=\"infobox\">\n"
        "  <tr><th colspan=\"2\">Faction Information</th></tr>\n"
        "  <tr><td>Type</td><td>TBD</td></tr>\n"
        "  <tr><td>Leader</td><td>TBD</td></tr>\n"
        "  <tr><td>Base of Operations</td><td>TBD</td></tr>\n"
        "  <tr><td>Alignment</td><td>TBD</td></tr>\n"
        "  <tr><td>Status</td><td>TBD</td></tr>\n"
        "</table>"
    ),
    "systems": (
        "<table class=\"infobox\">\n"
        "  <tr><th colspan=\"2\">System Information</th></tr>\n"
        "  <tr><td>Category</td><td>TBD</td></tr>\n"
        "  <tr><td>Source</td><td>TBD</td></tr>\n"
        "  <tr><td>Users</td><td>TBD</td></tr>\n"
        "  <tr><td>Limitations</td><td>TBD</td></tr>\n"
        "  <tr><td>Risk level</td><td>TBD</td></tr>\n"
        "</table>"
    ),
    "events": (
        "<table class=\"infobox\">\n"
        "  <tr><th colspan=\"2\">Event Information</th></tr>\n"
        "  <tr><td>Date/Era</td><td>TBD</td></tr>\n"
        "  <tr><td>Location</td><td>TBD</td></tr>\n"
        "  <tr><td>Participants</td><td>TBD</td></tr>\n"
        "  <tr><td>Outcome</td><td>TBD</td></tr>\n"
        "  <tr><td>Significance</td><td>TBD</td></tr>\n"
        "</table>"
    ),
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def split_frontmatter(content: str) -> tuple[str, str]:
    if not content.startswith("---\n"):
        return "", content
    parts = content.split("---\n", 2)
    if len(parts) < 3:
        return "", content
    return f"---\n{parts[1]}---\n", parts[2].lstrip("\n")


def ensure_headings(path: Path, headings: list[str], infobox: str | None) -> bool:
    content = read(path)
    if not content.strip():
        return False

    changed = False
    frontmatter, body = split_frontmatter(content)

    if infobox:
        infobox_pattern = re.compile(
            r"<table class=\"infobox\">[\s\S]*?</table>\s*",
            re.MULTILINE,
        )
        if "class=\"infobox\"" in body:
            updated_body, replacements = infobox_pattern.subn(infobox + "\n\n", body, count=1)
            if replacements > 0 and updated_body != body:
                body = updated_body
                changed = True
        else:
            body = infobox + "\n\n" + body
            changed = True

    for heading in headings:
        if heading not in body:
            body = body.rstrip() + f"\n\n{heading}\n- TBD\n"
            changed = True

    if changed:
        final_content = ((frontmatter + "\n") if frontmatter else "") + body.rstrip() + "\n"
        write(path, final_content)
    return changed


def main() -> None:
    updated = 0
    scanned = 0
    for folder, headings in REQUIRED_HEADINGS.items():
        base = WIKI_DIR / folder
        if not base.exists():
            continue
        for page in base.glob("*.md"):
            scanned += 1
            infobox = INFOBOXES.get(folder)
            if ensure_headings(page, headings, infobox):
                updated += 1
                print(f"updated: {page.relative_to(REPO_ROOT)}")
    print(f"scanned: {scanned}, updated: {updated}")


if __name__ == "__main__":
    main()
