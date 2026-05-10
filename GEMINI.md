# Novel World Wiki Agent — Schema & Workflow Instructions

This wiki is maintained by Gemini CLI as a novel and worldbuilding knowledge system.

## Triggers

- `ingest <file>`
- `query: <question>`
- `health`
- `lint`
- `build graph`

## Wiki Structure

`wiki/` contains:
- `index.md`, `log.md`, `overview.md`
- `sources/`
- `characters/`, `locations/`, `factions/`, `cultures/`, `artifacts/`, `systems/`
- `events/`, `timeline/`, `arcs/`, `chapters/`
- `syntheses/`

## Frontmatter

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

## Workflow Summary

- Ingest creates source/chapter records and updates domain canon pages.
- Query answers continuity and lore questions with citations.
- Lint checks continuity and canon quality issues.
- Health checks structural integrity only.
- Graph builds typed narrative relationships.
