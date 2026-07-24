# Storyforge Chinese Localization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make all human-readable Storyforge output use Simplified Chinese and migrate the existing 45-page local Wiki to Chinese with the user's current Claude Code configuration.

**Architecture:** A tracked language contract in `CLAUDE.md`, localized slash commands, localized page templates, and Chinese model prompts prevent future English output. Existing ignored Wiki content is backed up locally, then migrated in bounded Claude Code batches without renaming files or changing technical identifiers. Deterministic tests and Wiki health checks gate completion.

**Tech Stack:** Claude Code 2.1.218, Markdown, Python 3.13, unittest, Storyforge health/ingest tools, Git.

## Global Constraints

- Use the user's current Claude Code global configuration; do not modify its gateway, model mapping, or credentials.
- All human-readable prose, headings, infobox labels, index descriptions, logs, and reports use Simplified Chinese.
- Keep YAML keys, `type` values, directory names, code identifiers, slash-command names, and relationship enums in English.
- Preserve formal names such as `MissPanda` and `Princeton` and preserve existing WikiLink targets and filenames.
- Do not add unsupported facts or delete source, timeline, relationship, or continuity information.
- Do not apply any content-tone restriction or mandatory euphemism rule.
- Keep the novel source, generated Wiki, migration backup, and API credentials out of Git.
- Do not analyze chapter 11 or later until localization verification passes.

---

### Task 1: Back Up the Existing Wiki and Add a Failing Language-Contract Test

**Files:**
- Create locally, ignored: `raw/_migration-backups/wiki-before-chinese/`
- Create: `tests/test_chinese_localization.py`

**Interfaces:**
- Consumes: current `wiki/` tree with 45 Markdown files.
- Produces: byte-identical recovery copy and deterministic contract tests.

- [ ] **Step 1: Create and verify the ignored recovery copy**

Run:

```bash
test ! -e raw/_migration-backups/wiki-before-chinese
mkdir -p raw/_migration-backups
cp -R wiki raw/_migration-backups/wiki-before-chinese
diff -qr wiki raw/_migration-backups/wiki-before-chinese
test "$(find wiki -type f -name '*.md' | wc -l | tr -d ' ')" = "45"
test "$(find raw/_migration-backups/wiki-before-chinese -type f -name '*.md' | wc -l | tr -d ' ')" = "45"
```

Expected: `diff` is silent and both counts are 45.

- [ ] **Step 2: Write the failing localization contract test**

Create `tests/test_chinese_localization.py`:

```python
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).parent.parent
COMMANDS = sorted((ROOT / ".claude" / "commands").glob("wiki-*.md"))
FORBIDDEN_TEMPLATE_HEADINGS = {
    "Overview", "Biography", "Relationships", "Synopsis", "Plot",
    "Major Events", "Characters Involved", "Geography", "History",
    "Politics and Society", "Notable Events", "Summary", "Aftermath",
    "Timeline Overview", "Source Overview", "Narrative Beats",
}


class ChineseLocalizationContractTests(unittest.TestCase):
    def test_claude_contract_requires_simplified_chinese(self):
        text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("所有人类可读内容必须使用简体中文", text)
        self.assertIn("YAML 键", text)
        self.assertIn("正式专名", text)

    def test_all_wiki_commands_require_chinese(self):
        self.assertEqual(len(COMMANDS), 5)
        for path in COMMANDS:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertIn("简体中文", text)

    def test_templates_use_chinese_display_headings(self):
        text = (ROOT / "templates" / "wiki-section-templates.md").read_text(
            encoding="utf-8"
        )
        headings = set(re.findall(r"^## (.+)$", text, re.MULTILINE))
        self.assertTrue({"概述", "生平", "关系"}.issubset(headings))
        self.assertFalse(FORBIDDEN_TEMPLATE_HEADINGS & headings)

    def test_ingest_prompts_require_chinese_human_readable_text(self):
        text = (ROOT / "tools" / "ingest.py").read_text(encoding="utf-8")
        self.assertGreaterEqual(text.count("简体中文"), 2)
        self.assertIn("JSON 键保持英文", text)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: Run the test and verify RED**

Run:

```bash
.venv/bin/python -m unittest tests/test_chinese_localization.py -v
```

Expected: failures for missing Chinese contract, commands, templates, and ingest prompt rules.

---

### Task 2: Localize the Tracked Claude Code Rules and Templates

**Files:**
- Modify: `CLAUDE.md`
- Modify: `.claude/commands/wiki-health.md`
- Modify: `.claude/commands/wiki-ingest.md`
- Modify: `.claude/commands/wiki-lint.md`
- Modify: `.claude/commands/wiki-query.md`
- Modify: `.claude/commands/wiki-graph.md`
- Modify: `templates/wiki-section-templates.md`

**Interfaces:**
- Consumes: test contract from Task 1 and approved language boundary.
- Produces: Claude Code instructions and display templates that default to Simplified Chinese.

- [ ] **Step 1: Ask Claude Code to localize the tracked instruction layer**

Run from the repository root with editing enabled:

```bash
claude -p --permission-mode acceptEdits --max-turns 20 \
  --allowedTools 'Read' 'Edit' 'Write' 'Glob' 'Grep' \
  "按照 docs/superpowers/specs/2026-07-24-storyforge-chinese-localization-design.md 修改以下文件：CLAUDE.md、.claude/commands/wiki-health.md、.claude/commands/wiki-ingest.md、.claude/commands/wiki-lint.md、.claude/commands/wiki-query.md、.claude/commands/wiki-graph.md、templates/wiki-section-templates.md。所有人类可读说明、标题、信息框标签和示例说明改为简体中文；YAML 键、type 枚举、目录名、命令名、代码标识、关系枚举、文件路径和 WikiLink 语法保持英文。CLAUDE.md 必须逐字包含：所有人类可读内容必须使用简体中文、YAML 键、正式专名。每个 wiki 命令文件必须包含“简体中文”。不要修改其他文件。完成后列出修改文件。"
```

Expected: exactly seven tracked files are modified.

- [ ] **Step 2: Review the tracked diff**

Run:

```bash
git diff -- CLAUDE.md .claude/commands templates/wiki-section-templates.md
git diff --name-only
```

Expected: no Wiki files, source files, or credentials appear in Git diff.

- [ ] **Step 3: Run the focused tests**

Run:

```bash
.venv/bin/python -m unittest tests/test_chinese_localization.py -v
```

Expected: command/template/CLAUDE assertions pass; ingest prompt assertion may still fail until Task 3.

---

### Task 3: Localize Python Generation Prompts and Saved Reports

**Files:**
- Modify: `tools/ingest.py`
- Modify: `tools/query.py`
- Modify: `tools/lint.py`
- Modify: `tools/health.py`
- Modify as needed after scan: `tools/build_graph.py`, `tools/apply_templates.py`, `tools/sync_to_quartz.py`, `tools/pdf2md.py`, `tools/migrate_legacy_to_novel.py`
- Test: `tests/test_chinese_localization.py`

**Interfaces:**
- Consumes: the Simplified Chinese contract.
- Produces: Chinese human-readable model output, fallback pages, CLI messages, and saved reports while preserving machine-readable identifiers.

- [ ] **Step 1: Ask Claude Code to localize Python human-readable output**

Run:

```bash
claude -p --permission-mode acceptEdits --max-turns 24 \
  --allowedTools 'Read' 'Edit' 'Write' 'Glob' 'Grep' \
  "按照 docs/superpowers/specs/2026-07-24-storyforge-chinese-localization-design.md 检查 tools/*.py。将模型提示词、fallback 页面、Markdown 报告标题、索引骨架、CLI 面向用户的提示和说明改为简体中文。tools/ingest.py 的事实提取和页面综合提示词都必须明确写出“所有人类可读内容使用简体中文，JSON 键保持英文”；该文件中“简体中文”至少出现两次，并包含逐字短语“JSON 键保持英文”。不得修改函数名、JSON 键、frontmatter 键、type 值、目录名、关系枚举、算法、文件选择或退出码。只修改 tools/*.py，完成后报告修改文件和保持不变的技术接口。"
```

- [ ] **Step 2: Run localization and existing tests**

Run:

```bash
.venv/bin/python -m unittest tests/test_chinese_localization.py tests/test_ingest_validation.py tests/test_upstream_sync.py -v
.venv/bin/python -m compileall -q tools
```

Expected: 10 tests pass and Python compilation exits 0.

- [ ] **Step 3: Verify deterministic tools still work**

Run:

```bash
.venv/bin/python tools/health.py
.venv/bin/python tools/ingest.py --validate-only
```

Expected: Chinese reports with zero broken links and all pages indexed.

- [ ] **Step 4: Commit the tracked language layer**

Run:

```bash
git add CLAUDE.md .claude/commands templates/wiki-section-templates.md tools tests/test_chinese_localization.py
git commit -m "feat: make Storyforge output Simplified Chinese"
```

Expected: only tracked rules, tools, templates, and tests are committed.

---

### Task 4: Migrate Existing Wiki Content with Claude Code

**Files:**
- Modify locally, ignored: all `wiki/**/*.md`
- Preserve locally, ignored: `raw/_migration-backups/wiki-before-chinese/**/*.md`

**Interfaces:**
- Consumes: 45 English/mixed-language Wiki pages and localized rule layer.
- Produces: same file manifest with Simplified Chinese human-readable content.

- [ ] **Step 1: Migrate navigation, overview, source, and chapter pages**

Run:

```bash
claude -p --permission-mode acceptEdits --max-turns 30 \
  --allowedTools 'Read' 'Edit' 'Write' 'Glob' 'Grep' \
  "迁移 wiki/index.md、wiki/overview.md、wiki/sources/*.md、wiki/chapters/*.md 为简体中文。翻译所有英文正文、Markdown 标题、信息框标签、索引说明和自然语言 frontmatter 值。严格保留 frontmatter 键、type 值、文件名、路径和所有 WikiLink 目标；正式专名保持原名；人物名和第01回至第10回标题必须与 raw/权力的体香/batches/001-chapters-001-010.md 一致；不添加事实、不删除信息、不修改其他目录。内容处理不附加任何语气弱化或删减规则。"
```

- [ ] **Step 2: Migrate character pages**

Run:

```bash
claude -p --permission-mode acceptEdits --max-turns 30 \
  --allowedTools 'Read' 'Edit' 'Write' 'Glob' 'Grep' \
  "迁移 wiki/characters/*.md 为简体中文。翻译全部英文正文、标题、信息框标签和自然语言 frontmatter 值；保留 YAML 键、type 值、文件名、WikiLink 目标、关系枚举和全部事实细节。角色名严格遵循原文，周衿不得写成周瑾。不添加事实、不删除信息、不修改其他目录。内容处理不附加任何语气弱化或删减规则。"
```

- [ ] **Step 3: Migrate location, faction, system, and event pages**

Run:

```bash
claude -p --permission-mode acceptEdits --max-turns 30 \
  --allowedTools 'Read' 'Edit' 'Write' 'Glob' 'Grep' \
  "迁移 wiki/locations/*.md、wiki/factions/*.md、wiki/systems/*.md、wiki/events/*.md 为简体中文。翻译全部英文正文、标题、信息框标签和自然语言 frontmatter 值；保留 YAML 键、type 值、文件名、WikiLink 目标、关系枚举和事实。MissPanda 等正式专名保持原名，河东省与河西省保持区分。不添加事实、不删除信息、不修改其他目录。内容处理不附加任何语气弱化或删减规则。"
```

- [ ] **Step 4: Migrate timeline, arc, log, and reports**

Run:

```bash
claude -p --permission-mode acceptEdits --max-turns 30 \
  --allowedTools 'Read' 'Edit' 'Write' 'Glob' 'Grep' \
  "迁移 wiki/timeline/*.md、wiki/arcs/*.md、wiki/log.md、wiki/lint-report.md 为简体中文。翻译全部英文正文、标题、信息框标签、报告结论和自然语言 frontmatter 值；保留 YAML 键、type 值、文件名、WikiLink 目标、关系枚举和全部事实。不添加事实、不删除 QA 结论、不修改其他目录。内容处理不附加任何语气弱化或删减规则。"
```

---

### Task 5: Verify the Migrated Wiki and Current Claude Code Output

**Files:**
- Verify: `wiki/**/*.md`
- Verify: tracked language-contract files

**Interfaces:**
- Consumes: localized rules and migrated Wiki.
- Produces: evidence that the Wiki is Chinese, structurally valid, recoverable, and Git-safe.

- [ ] **Step 1: Verify file manifest and backup**

Run:

```bash
test "$(find wiki -type f -name '*.md' | wc -l | tr -d ' ')" = "45"
test "$(find raw/_migration-backups/wiki-before-chinese -type f -name '*.md' | wc -l | tr -d ' ')" = "45"
comm -3 \
  <(cd wiki && find . -type f -name '*.md' | sort) \
  <(cd raw/_migration-backups/wiki-before-chinese && find . -type f -name '*.md' | sort)
```

Expected: `comm` is silent.

- [ ] **Step 2: Verify structural health and exact names**

Run:

```bash
.venv/bin/python tools/health.py
.venv/bin/python tools/ingest.py --validate-only
.venv/bin/python -c 'import re; from pathlib import Path; raw=Path("raw/权力的体香/batches/001-chapters-001-010.md").read_text(encoding="utf-8"); idx=Path("wiki/index.md").read_text(encoding="utf-8"); expected=[m.group(0).strip() for m in re.finditer(r"^第.{1,16}回.*$", raw, re.M)][:10]; actual=re.findall(r"^- \[(第[^]]+)\]\(chapters/", idx, re.M); assert expected==actual; print("chapter_titles_exact=10/10")'
test -f wiki/characters/周衿.md
! rg --no-ignore --glob '!lint-report.md' '周瑾|为谁娇|红酒浸甜点' wiki
```

Expected: no health failures, no broken links, and exact titles/names.

- [ ] **Step 3: Verify English structural labels are gone**

Run:

```bash
! rg --no-ignore -n '^## (Overview|Biography|Relationships|Synopsis|Plot|Major Events|Characters Involved|Geography|History|Politics and Society|Notable Events|Summary|Aftermath|Timeline Overview|Source Overview|Narrative Beats)$' wiki
! rg --no-ignore -n '<t[hd]>(Character Information|Full Name|Aliases|Species|Affiliation|Status|First Appearance|Location Information|Event Information|Arc Information)</t[hd]>' wiki
```

Expected: both commands exit 0 with no matches.

- [ ] **Step 4: Verify current Claude Code configuration answers in Chinese**

Run:

```bash
CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1 claude -p --max-turns 1 \
  --disallowedTools 'Bash' 'Edit' 'Write' 'NotebookEdit' \
  --output-format text \
  '读取本项目 CLAUDE.md 的语言规则，只用简体中文回答：后续 Wiki 应使用什么语言？'
```

Expected: response states Simplified Chinese in Chinese.

- [ ] **Step 5: Run final tracked verification and publish rules**

Run:

```bash
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m compileall -q tools
git diff --check
test -z "$(git status --porcelain)"
git push origin main
```

Expected: all tests pass, the worktree is clean, only tracked language rules are pushed, and ignored novel/Wiki/backup content remains local.
