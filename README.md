# Novel World Wiki Agent

Agent-first tooling for building a **story bible + worldbuilding wiki** from manuscript files.

## What It Does

- Ingest chapter drafts, lore docs, and notes from `raw/`
- Materialize/update canon pages for characters, locations, factions, artifacts, systems, events, arcs, chapters, and timeline
- Run continuity linting and structural health checks
- Build a typed narrative graph and interactive HTML view

## Wiki Layout

```text
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
```

## Core Commands

```bash
python tools/ingest.py raw/novel/chapter-01.md
python tools/query.py "What does Kira know by chapter 8?"
python tools/lint.py --save
python tools/health.py --save
python tools/build_graph.py --report --save
python tools/migrate_legacy_to_novel.py
```

## Canon Model

All pages use frontmatter fields such as:
- `type`
- `canon_status`
- `spoiler_level`
- `era`
- `aliases`
- `relationships`
- `first_appearance`
- `last_updated`

## Migration

Legacy generic folders (`wiki/entities`, `wiki/concepts`) are migrated into fiction taxonomy via:

```bash
python tools/migrate_legacy_to_novel.py
```

## Quartz Publishing

Use Quartz to publish the generated wiki as a beautiful website:

```bash
python tools/sync_to_quartz.py "../my-world-wiki" --clean
```

Full setup guide:
- `docs/quartz-worldbuilding-guide.md`
- Theme presets:
  - `docs/quartz-theme-presets.md`
