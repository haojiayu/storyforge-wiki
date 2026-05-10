# Storyforge Wiki

Storyforge Wiki is a Claude Code-first system for turning scattered manuscript files into a structured, queryable **story bible + worldbuilding wiki**.

It is optimized for novels and long-form fiction with continuity pressure: characters, factions, locations, arcs, timeline events, systems, and canon conflicts.

## Why Use It

- Builds a persistent wiki from your source docs in `raw/`
- Maintains linked domain pages in `wiki/`
- Supports continuity-focused querying
- Runs structural and canon lint checks
- Builds a narrative relationship graph
- Publishes cleanly to Quartz + GitHub Pages

## Best Way to Use It (Claude Code)

From repo root:

```bash
claude
```

Use slash commands:

- `/wiki-health`
- `/wiki-ingest raw/`
- `/wiki-lint`
- `/wiki-query What does <character> know by chapter 12?`
- `/wiki-graph`

You can also use plain prompts:

- `ingest raw/`
- `query: list canon conflicts in arc two`

## 10-Minute Quickstart

1. Put your files in `raw/` (folders are fine)
2. Run `/wiki-health`
3. Run `/wiki-ingest raw/`
4. Run `/wiki-lint`
5. Ask 2-3 key questions with `/wiki-query ...`
6. Run `/wiki-graph` and inspect relationship quality

## Recommended Production Workflow

### 1) Ingestion cadence

- Ingest in batches (per chapter drop or per writing session)
- Keep `raw/` organized by project/book/arc
- Add one `PURPOSE.md` in `raw/` to steer extraction quality

### 2) Quality loop

- `health` every session
- `lint` after meaningful ingest batches
- resolve high-impact continuity warnings first:
  - timeline contradictions
  - character state mismatches
  - unresolved setup/payoff

### 3) Query loop

Ask operational writing questions:

- "What changed for <character> between chapter 5 and 9?"
- "Where does canon conflict on <artifact/system>?"
- "What timeline gaps still exist before arc finale?"

Save useful answers to `wiki/syntheses/`.

### 4) Graph loop

Run `/wiki-graph` after large ingests to:

- spot disconnected lore clusters
- identify over-centralized hubs
- verify relation quality across arcs/factions/locations

## Folder Model

```text
raw/                       # your source docs (ignored in git by default)
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
  graph.json
  graph.html
```

## Command Reference

### Claude commands

- `/wiki-health` - deterministic structural checks
- `/wiki-ingest <path>` - ingest file/folder
- `/wiki-lint` - continuity + canon lint
- `/wiki-query <question>` - narrative Q&A with citations
- `/wiki-graph` - rebuild typed relationship graph

### Python entrypoints (optional)

```bash
python tools/health.py --save
python tools/ingest.py raw/novel/
python tools/query.py "What changed for Kira in arc one?" --save
python tools/lint.py --save
python tools/build_graph.py --report --save
python tools/migrate_legacy_to_novel.py
```

## Quartz Publishing

Sync generated wiki into a Quartz repo:

```bash
python tools/sync_to_quartz.py "../my-world-wiki" --clean
```

Then in Quartz:

```bash
npx quartz build --serve
npx quartz sync
```

See:

- `docs/quartz-worldbuilding-guide.md`
- `docs/quartz-theme-presets.md`

## Practical Tips

- Keep source filenames stable; re-ingests are easier to reason about
- Use chapter-prefixed naming for better timeline retrieval
- Treat `wiki/overview.md` as your current canon lens
- Commit only tooling/docs; keep raw and generated content local unless intentional

## Troubleshooting

- Unknown slash command: restart `claude` in repo root and verify `.claude/commands/`
- Weak semantic output: confirm your Claude runtime/model context is available
- Graph looks sparse: run more ingests and then lint/fix links
- Too much noise: ingest in smaller thematic batches (arc-by-arc)
