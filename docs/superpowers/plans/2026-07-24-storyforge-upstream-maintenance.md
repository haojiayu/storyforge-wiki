# Storyforge Upstream Maintenance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create `haojiayu/storyforge-wiki`, rebuild its `main` on the latest `SamurAIGPT/llm-wiki-agent` baseline while preserving Storyforge's novel-analysis features, and add a weekly upstream-check workflow that opens reviewable PRs or conflict Issues.

**Architecture:** The personal repository remains a GitHub Fork of `abrahamp47/storyforge-wiki`, with `storyforge-original` preserving the original fork head. Its maintained `main` is rebuilt once by replaying the seven Storyforge commits onto the audited `llm-wiki-agent` head; future generic-upstream updates arrive through non-auto-merging PRs created by a scheduled workflow. The local clone has `origin`, `storyforge`, and `llm-upstream` remotes.

**Tech Stack:** Git/GitHub CLI, GitHub Actions, Python 3.10–3.13, unittest, Storyforge Python tools, LiteLLM, NetworkX, Markdown/Quartz.

## Global Constraints

- Do not read, move, modify, copy, commit, upload, or analyze `/Users/haojiayu/Documents/qltx/权力的体香@sosdbot.txt`.
- Do not initialize `/Users/haojiayu/Documents/qltx` as a Git repository.
- Do not store model API keys in files, commits, Actions secrets, logs, or tool output.
- The maintained repository path is `/Users/haojiayu/Documents/qltx/storyforge`.
- The GitHub Fork is public and named `haojiayu/storyforge-wiki`.
- `main` must preserve Storyforge's novel-specific schema, long-source chunking, MapReduce extraction, graph, lint, query, and Quartz publishing.
- `storyforge-original` must remain fixed at `e05622343ee2999cef2d547465a28a92f9c673f6`.
- The initial generic baseline is `d499867afd933cebe3d351596f9a1c43a73e4261` from `SamurAIGPT/llm-wiki-agent`.
- Scheduled upstream checks run Mondays at 09:00 Asia/Shanghai (`0 1 * * 1` UTC), may create PRs or Issues, and never auto-merge.
- Generated `raw/` and `wiki/` content remains local/ignored unless the user explicitly publishes it later.

---

### Task 1: Create the Personal Fork and Recovery Branch

**Files:**
- Create remotely: `haojiayu/storyforge-wiki`
- Create locally: `/Users/haojiayu/Documents/qltx/storyforge/`
- Copy later: `docs/superpowers/specs/2026-07-24-storyforge-upstream-maintenance-design.md`
- Copy later: `docs/superpowers/plans/2026-07-24-storyforge-upstream-maintenance.md`

**Interfaces:**
- Consumes: authenticated GitHub account `haojiayu`; original repository `abrahamp47/storyforge-wiki`.
- Produces: local clone with three named remotes and immutable recovery branch `storyforge-original`.

- [ ] **Step 1: Verify the target repository does not already exist**

Run:

```bash
gh repo view haojiayu/storyforge-wiki
```

Expected: non-zero exit with “Could not resolve to a Repository”. If the repository exists, stop and inspect it instead of overwriting it.

- [ ] **Step 2: Create the GitHub Fork without cloning**

Run:

```bash
gh repo fork abrahamp47/storyforge-wiki --clone=false --remote=false
```

Expected: GitHub reports `haojiayu/storyforge-wiki` created or already forked.

- [ ] **Step 3: Clone the personal Fork into the approved path**

Run:

```bash
git clone https://github.com/haojiayu/storyforge-wiki.git /Users/haojiayu/Documents/qltx/storyforge
```

Expected: clone completes and `git -C /Users/haojiayu/Documents/qltx/storyforge remote get-url origin` prints the personal Fork URL.

- [ ] **Step 4: Configure both source remotes**

Run:

```bash
git -C /Users/haojiayu/Documents/qltx/storyforge remote add storyforge https://github.com/abrahamp47/storyforge-wiki.git
git -C /Users/haojiayu/Documents/qltx/storyforge remote add llm-upstream https://github.com/SamurAIGPT/llm-wiki-agent.git
git -C /Users/haojiayu/Documents/qltx/storyforge fetch --all --prune
```

Expected: `git remote -v` shows `origin`, `storyforge`, and `llm-upstream`.

- [ ] **Step 5: Create and push the immutable recovery branch**

Run:

```bash
git -C /Users/haojiayu/Documents/qltx/storyforge branch storyforge-original e05622343ee2999cef2d547465a28a92f9c673f6
git -C /Users/haojiayu/Documents/qltx/storyforge push origin storyforge-original
```

Expected: remote branch `origin/storyforge-original` resolves to `e05622343ee2999cef2d547465a28a92f9c673f6`.

---

### Task 2: Replay Storyforge on the Current Generic Baseline

**Files:**
- Resolve: `README.md`
- Resolve: `tools/build_graph.py`
- Resolve: `tools/health.py`
- Resolve: `tools/ingest.py`
- Resolve: `tools/lint.py`
- Resolve: `tools/query.py`
- Preserve from generic baseline: `tools/_utils.py`
- Preserve from generic baseline: `.github/workflows/star-history.yml`
- Preserve from Storyforge: `templates/wiki-section-templates.md`
- Preserve from Storyforge: `tools/apply_templates.py`
- Preserve from Storyforge: `tools/sync_to_quartz.py`
- Preserve from Storyforge: `wiki/{arcs,artifacts,chapters,characters,cultures,events,factions,locations,sources,syntheses,systems,timeline}/.gitkeep`

**Interfaces:**
- Consumes: `storyforge-original`, `llm-upstream/main`, common ancestor `82b80782f6b0eed5dd28196d4074174d465a6795`.
- Produces: local `main` whose base is `d499867...` and whose top contains the seven Storyforge commits in their original order.

- [ ] **Step 1: Create the integration branch at the audited generic baseline**

Run:

```bash
git -C /Users/haojiayu/Documents/qltx/storyforge switch --create integration/storyforge-on-llm-upstream d499867afd933cebe3d351596f9a1c43a73e4261
```

Expected: `HEAD` equals `d499867afd933cebe3d351596f9a1c43a73e4261`.

- [ ] **Step 2: Replay the seven novel commits in order**

Run each command separately:

```bash
git cherry-pick 9f80d92
git cherry-pick 504ea89
git cherry-pick f2aa4b5
git cherry-pick a0503ef
git cherry-pick 8fb1355
git cherry-pick d2cd221
git cherry-pick e056223
```

Expected: conflicts occur only while replaying files changed by both lines of development. Resolve one commit before starting the next.

- [ ] **Step 3: Resolve conflicts according to the approved ownership rules**

For each stopped cherry-pick:

```bash
git status --short
```

Resolution rules:

- Use the Storyforge version for `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `README.md`, `.claude/commands/*`, `tools/ingest.py`, `tools/lint.py`, `tools/query.py`, `tools/health.py`, and `tools/build_graph.py` because these files define the novel workflow.
- Keep upstream-only `tools/_utils.py`, `assets/`, and `.github/workflows/star-history.yml` present.
- Keep Storyforge deletions of `tools/heal.py`, `tools/refresh.py`, `docs/automated-sync.md`, the generic CJK demo, and the generic starter `wiki/index.md`, `wiki/log.md`, and `wiki/overview.md`.
- Keep all Storyforge novel templates, domain directories, migration helper, and Quartz files.

For a conflicted file owned by Storyforge during a cherry-pick, run:

```bash
git checkout --theirs -- <path>
git add <path>
```

For an upstream-only file that must remain, run:

```bash
git checkout --ours -- <path>
git add <path>
```

For a modify/delete conflict where Storyforge intentionally deleted the file, run:

```bash
git rm <path>
```

Continue each replayed commit with:

```bash
git cherry-pick --continue
```

Expected: all seven commits complete and `git status --short` is empty.

- [ ] **Step 4: Verify the resulting ancestry and feature files**

Run:

```bash
git merge-base --is-ancestor d499867afd933cebe3d351596f9a1c43a73e4261 HEAD
test -f templates/wiki-section-templates.md
test -f tools/sync_to_quartz.py
test -f tools/_utils.py
test -f wiki/characters/.gitkeep
rg "extract_ingest_facts_mapreduce|split_text_into_chunks" tools/ingest.py
```

Expected: all commands exit 0; the `rg` output lists both long-source functions.

---

### Task 3: Add Testable Upstream-Sync Metadata Utilities

**Files:**
- Create: `tools/upstream_sync.py`
- Create: `tests/test_upstream_sync.py`
- Create: `UPSTREAMS.md`
- Create: `docs/superpowers/specs/2026-07-24-storyforge-upstream-maintenance-design.md`
- Create: `docs/superpowers/plans/2026-07-24-storyforge-upstream-maintenance.md`

**Interfaces:**
- Consumes: exact 40-character Git SHAs and `UPSTREAMS.md` text.
- Produces: `read_integrated_sha(text) -> str`, `replace_integrated_sha(text, new_sha) -> str`, and `build_conflict_body(old_sha, new_sha, files) -> str`; CLI subcommands `current`, `update`, and `conflict-body`.

- [ ] **Step 1: Write failing unittest coverage**

Create `tests/test_upstream_sync.py` with:

```python
import unittest

from tools.upstream_sync import (
    build_conflict_body,
    read_integrated_sha,
    replace_integrated_sha,
)


OLD_SHA = "d499867afd933cebe3d351596f9a1c43a73e4261"
NEW_SHA = "0123456789abcdef0123456789abcdef01234567"


class UpstreamSyncTests(unittest.TestCase):
    def setUp(self):
        self.text = (
            "# Upstreams\n\n"
            f"- Last integrated llm-upstream SHA: `{OLD_SHA}`\n"
        )

    def test_read_integrated_sha(self):
        self.assertEqual(read_integrated_sha(self.text), OLD_SHA)

    def test_replace_integrated_sha(self):
        updated = replace_integrated_sha(self.text, NEW_SHA)
        self.assertEqual(read_integrated_sha(updated), NEW_SHA)
        self.assertNotIn(OLD_SHA, updated)

    def test_rejects_non_sha(self):
        with self.assertRaises(ValueError):
            replace_integrated_sha(self.text, "main")

    def test_conflict_body_is_deterministic(self):
        body = build_conflict_body(OLD_SHA, NEW_SHA, ["tools/ingest.py", "README.md"])
        self.assertIn(OLD_SHA, body)
        self.assertIn(NEW_SHA, body)
        self.assertLess(body.index("README.md"), body.index("tools/ingest.py"))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests and confirm the missing-module failure**

Run:

```bash
python -m unittest tests/test_upstream_sync.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'tools.upstream_sync'`.

- [ ] **Step 3: Implement the metadata utility and CLI**

Create `tools/upstream_sync.py` with:

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path


SHA_RE = re.compile(r"^[0-9a-f]{40}$")
RECORD_RE = re.compile(
    r"^- Last integrated llm-upstream SHA: `(?P<sha>[0-9a-f]{40})`$",
    re.MULTILINE,
)


def read_integrated_sha(text: str) -> str:
    match = RECORD_RE.search(text)
    if not match:
        raise ValueError("UPSTREAMS.md has no valid llm-upstream SHA record")
    return match.group("sha")


def replace_integrated_sha(text: str, new_sha: str) -> str:
    if not SHA_RE.fullmatch(new_sha):
        raise ValueError("new SHA must be 40 lowercase hexadecimal characters")
    if not RECORD_RE.search(text):
        raise ValueError("UPSTREAMS.md has no valid llm-upstream SHA record")
    return RECORD_RE.sub(
        f"- Last integrated llm-upstream SHA: `{new_sha}`",
        text,
        count=1,
    )


def build_conflict_body(old_sha: str, new_sha: str, files: list[str]) -> str:
    for value in (old_sha, new_sha):
        if not SHA_RE.fullmatch(value):
            raise ValueError("conflict SHAs must be 40 lowercase hexadecimal characters")
    conflict_lines = "\n".join(f"- `{name}`" for name in sorted(set(files)))
    return (
        "## Automated upstream check found merge conflicts\n\n"
        f"- Last integrated SHA: `{old_sha}`\n"
        f"- Latest upstream SHA: `{new_sha}`\n\n"
        "### Conflicting files\n\n"
        f"{conflict_lines or '- No filenames reported'}\n\n"
        "`main` was not changed. Resolve these conflicts on a dedicated branch and "
        "submit a reviewed pull request.\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    current = subparsers.add_parser("current")
    current.add_argument("--file", type=Path, required=True)

    update = subparsers.add_parser("update")
    update.add_argument("--file", type=Path, required=True)
    update.add_argument("--sha", required=True)

    conflict = subparsers.add_parser("conflict-body")
    conflict.add_argument("--old-sha", required=True)
    conflict.add_argument("--new-sha", required=True)
    conflict.add_argument("--files-file", type=Path, required=True)
    conflict.add_argument("--output", type=Path, required=True)

    args = parser.parse_args()
    if args.command == "current":
        print(read_integrated_sha(args.file.read_text(encoding="utf-8")))
    elif args.command == "update":
        text = args.file.read_text(encoding="utf-8")
        args.file.write_text(replace_integrated_sha(text, args.sha), encoding="utf-8")
    else:
        files = args.files_file.read_text(encoding="utf-8").splitlines()
        args.output.write_text(
            build_conflict_body(args.old_sha, args.new_sha, files),
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Create the authoritative upstream record**

Create `UPSTREAMS.md` with:

```markdown
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
```

- [ ] **Step 5: Copy the approved design and plan into the maintained repository**

Run:

```bash
mkdir -p docs/superpowers/specs docs/superpowers/plans
cp /Users/haojiayu/Documents/qltx/docs/superpowers/specs/2026-07-24-storyforge-upstream-maintenance-design.md docs/superpowers/specs/
cp /Users/haojiayu/Documents/qltx/docs/superpowers/plans/2026-07-24-storyforge-upstream-maintenance.md docs/superpowers/plans/
```

Expected: both documents exist inside the Storyforge clone.

- [ ] **Step 6: Run the tests and commit the maintenance foundation**

Run:

```bash
python -m unittest tests/test_upstream_sync.py -v
git add tools/upstream_sync.py tests/test_upstream_sync.py UPSTREAMS.md docs/superpowers
git commit -m "chore: document dual-upstream maintenance"
```

Expected: 4 tests pass and the commit completes.

---

### Task 4: Add the Weekly Upstream PR/Issue Workflow

**Files:**
- Create: `.github/workflows/check-llm-upstream.yml`
- Test: `tests/test_upstream_sync.py`

**Interfaces:**
- Consumes: `UPSTREAMS.md`, `tools/upstream_sync.py`, public upstream branch `SamurAIGPT/llm-wiki-agent/main`, and repository `GITHUB_TOKEN`.
- Produces: branch `sync/llm-wiki-agent` plus a review PR on clean merges, or a fixed-title Issue on conflicts; never mutates `main` directly.

- [ ] **Step 1: Create the scheduled workflow**

Create `.github/workflows/check-llm-upstream.yml` with:

```yaml
name: Check llm-wiki-agent upstream

on:
  schedule:
    - cron: "0 1 * * 1"
  workflow_dispatch:

permissions:
  contents: write
  pull-requests: write
  issues: write

concurrency:
  group: llm-upstream-sync
  cancel-in-progress: false

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Configure Git
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"

      - name: Fetch upstream
        run: git fetch https://github.com/SamurAIGPT/llm-wiki-agent.git main:refs/remotes/llm-upstream/main

      - name: Compare and attempt merge
        id: merge
        shell: bash
        run: |
          set -euo pipefail
          old_sha="$(python tools/upstream_sync.py current --file UPSTREAMS.md)"
          new_sha="$(git rev-parse llm-upstream/main)"
          echo "old_sha=$old_sha" >> "$GITHUB_OUTPUT"
          echo "new_sha=$new_sha" >> "$GITHUB_OUTPUT"
          if [[ "$old_sha" == "$new_sha" ]]; then
            echo "state=unchanged" >> "$GITHUB_OUTPUT"
            exit 0
          fi
          git switch -C sync/llm-wiki-agent origin/main
          if git merge --no-ff --no-edit llm-upstream/main; then
            python tools/upstream_sync.py update --file UPSTREAMS.md --sha "$new_sha"
            git add UPSTREAMS.md
            git commit -m "chore: record llm-wiki-agent upstream $new_sha"
            echo "state=clean" >> "$GITHUB_OUTPUT"
          else
            git diff --name-only --diff-filter=U | sort -u > /tmp/conflict-files.txt
            git merge --abort
            python tools/upstream_sync.py conflict-body \
              --old-sha "$old_sha" \
              --new-sha "$new_sha" \
              --files-file /tmp/conflict-files.txt \
              --output /tmp/conflict-body.md
            echo "state=conflict" >> "$GITHUB_OUTPUT"
          fi

      - name: Verify clean merge
        if: steps.merge.outputs.state == 'clean'
        run: |
          python -m unittest tests/test_upstream_sync.py -v
          python -m compileall -q tools
          python tools/health.py
          python tools/ingest.py --validate-only
          test -f templates/wiki-section-templates.md
          test -f tools/sync_to_quartz.py
          rg "extract_ingest_facts_mapreduce|split_text_into_chunks" tools/ingest.py

      - name: Push sync branch
        if: steps.merge.outputs.state == 'clean'
        run: git push --force-with-lease origin sync/llm-wiki-agent

      - name: Create or update pull request
        if: steps.merge.outputs.state == 'clean'
        env:
          GH_TOKEN: ${{ github.token }}
          NEW_SHA: ${{ steps.merge.outputs.new_sha }}
        run: |
          pr_number="$(gh pr list --head sync/llm-wiki-agent --state open --json number --jq '.[0].number // empty')"
          body="Automated, non-merging sync proposal for llm-wiki-agent upstream at \`$NEW_SHA\`. Review novel-specific ingest, schema, lint, graph, and query behavior before merging."
          if [[ -n "$pr_number" ]]; then
            gh pr edit "$pr_number" --title "chore: sync llm-wiki-agent upstream" --body "$body"
          else
            gh pr create --base main --head sync/llm-wiki-agent --title "chore: sync llm-wiki-agent upstream" --body "$body"
          fi

      - name: Create or update conflict issue
        if: steps.merge.outputs.state == 'conflict'
        env:
          GH_TOKEN: ${{ github.token }}
        run: |
          issue_number="$(gh issue list --state open --search 'llm-wiki-agent upstream conflicts in:title' --json number --jq '.[0].number // empty')"
          if [[ -n "$issue_number" ]]; then
            gh issue edit "$issue_number" --title "llm-wiki-agent upstream conflicts" --body-file /tmp/conflict-body.md
          else
            gh issue create --title "llm-wiki-agent upstream conflicts" --body-file /tmp/conflict-body.md
          fi
```

- [ ] **Step 2: Validate the workflow structure locally**

Run:

```bash
python -c "import pathlib; text=pathlib.Path('.github/workflows/check-llm-upstream.yml').read_text(); assert 'schedule:' in text; assert 'workflow_dispatch:' in text; assert 'git merge --no-ff' in text; assert 'gh pr create' in text; assert 'gh issue create' in text"
python -m unittest tests/test_upstream_sync.py -v
```

Expected: both commands exit 0 and 4 tests pass.

- [ ] **Step 3: Commit the workflow**

Run:

```bash
git add .github/workflows/check-llm-upstream.yml
git commit -m "ci: check llm-wiki-agent upstream weekly"
```

Expected: one commit containing only the workflow.

---

### Task 5: Promote the Integration Branch to Main and Publish

**Files:**
- Verify: all tracked repository files
- Do not touch: `/Users/haojiayu/Documents/qltx/权力的体香@sosdbot.txt`

**Interfaces:**
- Consumes: verified integration branch and immutable `storyforge-original` recovery branch.
- Produces: published `origin/main`, enabled scheduled workflow, and a local working clone ready for later novel ingestion.

- [ ] **Step 1: Run the complete local verification suite**

Run from `/Users/haojiayu/Documents/qltx/storyforge`:

```bash
python -m unittest tests/test_upstream_sync.py -v
python -m compileall -q tools
python tools/health.py
python tools/ingest.py --validate-only
test -f templates/wiki-section-templates.md
test -f tools/sync_to_quartz.py
test -f tools/_utils.py
test -f wiki/characters/.gitkeep
rg "extract_ingest_facts_mapreduce|split_text_into_chunks" tools/ingest.py
git diff --check
git status --short
```

Expected: 4 tests pass, health and validation report no structural failures, required files/functions are found, `git diff --check` exits 0, and status is clean.

- [ ] **Step 2: Confirm recovery and base ancestry before replacing main**

Run:

```bash
test "$(git rev-parse storyforge-original)" = "e05622343ee2999cef2d547465a28a92f9c673f6"
git merge-base --is-ancestor d499867afd933cebe3d351596f9a1c43a73e4261 HEAD
```

Expected: both commands exit 0.

- [ ] **Step 3: Replace the new Fork's main with the verified integration history**

Run:

```bash
git branch -M main
git push --force-with-lease origin main
```

Expected: `origin/main` points to the verified local `main`; `origin/storyforge-original` remains unchanged.

- [ ] **Step 4: Verify GitHub repository state and workflow availability**

Run:

```bash
gh repo view haojiayu/storyforge-wiki --json nameWithOwner,isFork,parent,url
gh workflow list --repo haojiayu/storyforge-wiki
git remote -v
```

Expected: repository is a Fork of `abrahamp47/storyforge-wiki`, the “Check llm-wiki-agent upstream” workflow is listed, and all three local remotes are present.

- [ ] **Step 5: Trigger one manual dry check and inspect its conclusion**

Run:

```bash
gh workflow run "Check llm-wiki-agent upstream" --repo haojiayu/storyforge-wiki
gh run list --repo haojiayu/storyforge-wiki --workflow "Check llm-wiki-agent upstream" --limit 1
```

Expected: the workflow queues successfully. Because `UPSTREAMS.md` records the current upstream SHA, the run concludes with `state=unchanged` and creates neither a sync PR nor a conflict Issue.

## Final Review Checklist

- [ ] Personal Fork exists and retains GitHub fork lineage.
- [ ] `storyforge-original` equals the audited original Storyforge head.
- [ ] `main` descends from the audited generic upstream head.
- [ ] Storyforge novel templates and long-source MapReduce functions remain present.
- [ ] `UPSTREAMS.md` documents both source repositories and current SHA.
- [ ] Weekly workflow opens PRs or Issues and contains no auto-merge command.
- [ ] Design and implementation plan are committed inside the personal Fork.
- [ ] Local clone has `origin`, `storyforge`, and `llm-upstream` remotes.
- [ ] Full no-model verification passes.
- [ ] Existing novel file remains untouched and outside the Fork.
