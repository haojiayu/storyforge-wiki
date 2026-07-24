# Upstream Maintenance

## Sources

- Storyforge novel upstream: `https://github.com/abrahamp47/storyforge-wiki`
- Generic engine upstream: `https://github.com/SamurAIGPT/llm-wiki-agent`
- Initial common ancestor: `82b80782f6b0eed5dd28196d4074174d465a6795`
- Preserved Storyforge head: `e05622343ee2999cef2d547465a28a92f9c673f6`
- Last integrated llm-upstream SHA: `d499867afd933cebe3d351596f9a1c43a73e4261`

## Ownership Rules

Storyforge owns the novel schema, templates, domain directories, chunked MapReduce ingest,
query/lint behavior, graph behavior, and Quartz publishing. The generic upstream supplies
security fixes and reusable engine improvements. Generic changes never auto-merge.

## Manual Check

```bash
git fetch llm-upstream main
git switch -C sync/llm-wiki-agent main
git merge --no-ff llm-upstream/main
python -m compileall -q tools
python tools/health.py
python tools/ingest.py --validate-only
```

If the merge conflicts, abort it with `git merge --abort`, resolve on a separate branch,
and submit a pull request. Update the recorded SHA only inside the reviewed sync PR.
