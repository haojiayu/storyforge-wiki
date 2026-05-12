# Storyforge Wiki — Schema & Workflow Instructions

This wiki is maintained by Claude Code as a hybrid story bible and worldbuilding system.

## Slash Commands

- `/wiki-ingest`
- `/wiki-query`
- `/wiki-health`
- `/wiki-lint`
- `/wiki-graph`

## Domain Model

Primary page types:
- `source`
- `character`
- `location`
- `faction`
- `culture`
- `artifact`
- `system`
- `event`
- `timeline`
- `arc`
- `chapter`
- `synthesis`

Canonical folders under `wiki/`:
- `sources`, `characters`, `locations`, `factions`, `cultures`, `artifacts`, `systems`, `events`, `timeline`, `arcs`, `chapters`, `syntheses`

Section templates are defined in:
- `templates/wiki-section-templates.md`
- Always follow these heading structures when creating/updating pages.

## Frontmatter Contract

```yaml
---
title: "Page Title"
type: source | character | location | faction | culture | artifact | system | event | timeline | arc | chapter | synthesis
tags: []
sources: []
canon_status: canon | contested | apocrypha | draft
spoiler_level: none | low | medium | high
era: ""
aliases: []
relationships: []
first_appearance: ""
last_updated: YYYY-MM-DD
---
```

## Ingest Workflow

1. Read source file fully (auto-convert non-md with markitdown if needed)
2. Read `wiki/index.md` and `wiki/overview.md`
3. Write `wiki/sources/<slug>.md` with:
   - narrative beats
   - character state changes
   - world facts introduced
   - timeline events
   - unresolved threads
   - canon conflicts
4. Update or create domain pages across the fiction folders
   - Domain pages must follow the corresponding section template headings.
5. Update `wiki/index.md`
6. Update `wiki/overview.md`
7. Append `wiki/log.md` with `## [YYYY-MM-DD] ingest | <title>`
8. Validate links and index registration

## Query Workflow

1. Read `wiki/index.md`
2. Read relevant pages, prioritizing `chapters`, `arcs`, `timeline` for scoped questions
3. Answer with markdown + `[[PageName]]` citations
4. Add `## Sources`
5. Ask whether to save as `wiki/syntheses/<slug>.md`

## Lint Workflow

Run checks for:
- broken/orphan wikilinks
- timeline contradictions
- character continuity errors
- unresolved setup/payoff
- alias collisions
- canon drift (`canon_status: contested` with no explanation)
- sparse pages with low link density

## Health Workflow

Run `python tools/health.py` for deterministic checks:
- stubs
- index sync
- log coverage

## Graph Workflow

Generate graph with:
- `EXTRACTED` edges from wikilinks
- typed inferred narrative edges (`ALLY_OF`, `CONFLICTS_WITH`, `LOCATED_IN`, `CAUSES`, `LEARNS`, `BETRAYS`, `OWNS`, `MEMBER_OF`)
- optional confidence and community detection
