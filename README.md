# Storyforge Wiki

Storyforge Wiki is a Claude Code-first tool for turning your manuscript and lore files into a structured **story bible + worldbuilding wiki**.

## Use with Claude Code

From repo root:

```bash
claude
```

Then use slash commands:

- `/wiki-ingest raw/novel/` - ingest a file or whole folder
- `/wiki-query What does Mira know by chapter 12?`
- `/wiki-health`
- `/wiki-lint`
- `/wiki-graph`

You can also use plain prompts in Claude:

- `ingest raw/`
- `query: list timeline contradictions in arc two`

## Recommended Claude Workflow

1. Drop docs into `raw/`
2. Run `/wiki-ingest raw/`
3. Run `/wiki-lint` for continuity/canon issues
4. Ask questions with `/wiki-query ...`
5. Run `/wiki-graph` to regenerate narrative relationships

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

## Optional Python Entrypoints

If you want direct script usage:

```bash
python tools/ingest.py raw/novel/chapter-01.md
python tools/query.py "What changed for Kira in arc one?"
python tools/health.py --save
python tools/lint.py --save
python tools/build_graph.py --report --save
```

## Quartz Publishing

```bash
python tools/sync_to_quartz.py "../my-world-wiki" --clean
```

Guides:
- `docs/quartz-worldbuilding-guide.md`
- `docs/quartz-theme-presets.md`
