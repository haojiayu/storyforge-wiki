# Novel World Wiki Agent — Schema & Workflow Instructions

This repository is now a hybrid novel and worldbuilding wiki system.

## Commands

- `ingest <file>`: ingest chapter notes, manuscript slices, lore docs
- `query: <question>`: ask continuity, canon, timeline, and lore questions
- `health`: structural deterministic checks
- `lint`: continuity and canon quality checks
- `build graph`: build typed narrative relationship graph

## Directory Layout

```text
raw/
wiki/
  index.md
  log.md
  overview.md
  sources/
  characters/
  locations/
  factions/
  cultures/
  artifacts/
  systems/
  events/
  timeline/
  arcs/
  chapters/
  syntheses/
graph/
tools/
```

## Canon Frontmatter

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

1. Read source file and current wiki context (`wiki/index.md`, `wiki/overview.md`)
2. Write `wiki/sources/<slug>.md`
3. Update/create domain pages in:
   - `wiki/characters/`
   - `wiki/locations/`
   - `wiki/factions/`
   - `wiki/cultures/`
   - `wiki/artifacts/`
   - `wiki/systems/`
   - `wiki/events/`
   - `wiki/timeline/`
   - `wiki/arcs/`
   - `wiki/chapters/`
4. Capture canonical deltas:
   - narrative beats
   - character state changes
   - world facts and system rules
   - timeline events
   - unresolved threads and foreshadowing
   - retcons and canon conflicts
5. Update `wiki/index.md` and `wiki/overview.md`
6. Append `wiki/log.md`: `## [YYYY-MM-DD] ingest | <Title>`
7. Validate links and index coverage

### Source Template

```markdown
## Narrative Beats
- ...

## Character State Changes
- [[CharacterName]]: from ... to ...

## World Facts Introduced
- ...

## Timeline Events
- [[EventName]] ...

## Unresolved Threads
- ...

## Canon Conflicts
- ...
```

## Query Workflow

1. Read `wiki/index.md` to locate relevant pages
2. Prefer chapter/arc/timeline scoping when explicitly requested
3. Synthesize canon-first answer with `[[PageName]]` citations
4. Include `## Sources`
5. Offer save as `wiki/syntheses/<slug>.md`

## Lint Workflow

Check for:
- orphans and broken links
- timeline contradictions
- character continuity breaks
- unresolved setup/payoff threads
- canon drift and missing rationale for contested entries
- alias collisions and near-duplicate entities
- sparse pages with low outbound link density

## Health Workflow

Run `python tools/health.py` to check:
- empty/stub pages
- index sync
- log coverage (source/chapter ingest traceability)

## Graph Workflow

Build graph with typed edges:
- deterministic `EXTRACTED` (wikilinks)
- typed inferred edges (`ALLY_OF`, `CONFLICTS_WITH`, `LOCATED_IN`, `CAUSES`, `LEARNS`, `BETRAYS`, `OWNS`, `MEMBER_OF`)
- optional confidence and community grouping

## Naming

- source pages: `kebab-case.md`
- domain pages: `TitleCase.md`
- chapter pages: `chapter-XX-title.md`
- timeline pages: `YYYY-MM-DD-EventName.md` or `Era-EventName.md`
