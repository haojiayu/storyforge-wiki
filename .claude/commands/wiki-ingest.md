Ingest a manuscript, chapter, or lore source into the Novel World Wiki.

Usage: /wiki-ingest $ARGUMENTS

$ARGUMENTS should be a file path such as:
- `raw/novel/chapter-01.md`
- `raw/world/lore-notes.md`

Workflow:
1. Read source + `wiki/index.md` + `wiki/overview.md`
2. Write `wiki/sources/<slug>.md` with narrative beats and canon deltas
3. Update relevant domain pages (`characters`, `locations`, `factions`, `systems`, `events`, `timeline`, `arcs`, `chapters`)
4. Update `wiki/index.md` and `wiki/overview.md`
5. Append `wiki/log.md` entry for ingest
6. Report canon conflicts, if any
