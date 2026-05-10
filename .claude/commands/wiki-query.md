Query the Novel World Wiki and synthesize canon-aware answers.

Usage: /wiki-query $ARGUMENTS

$ARGUMENTS is the question, for example:
- `What does Mira know by chapter 12?`
- `List timeline conflicts in arc two`

Workflow:
1. Read `wiki/index.md` and identify relevant pages
2. Prefer scoped retrieval across `chapters`, `arcs`, `timeline`, `characters`
3. Answer in markdown with `[[PageName]]` citations
4. Include `## Sources`
5. Ask whether to save as `wiki/syntheses/<slug>.md`
