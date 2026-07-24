import re
import unittest
from pathlib import Path

from tools import ingest


ROOT = Path(__file__).parent.parent
COMMANDS = sorted((ROOT / ".claude" / "commands").glob("wiki-*.md"))
FORBIDDEN_TEMPLATE_HEADINGS = {
    "Overview",
    "Biography",
    "Relationships",
    "Synopsis",
    "Plot",
    "Major Events",
    "Characters Involved",
    "Geography",
    "History",
    "Politics and Society",
    "Notable Events",
    "Summary",
    "Aftermath",
    "Timeline Overview",
    "Source Overview",
    "Narrative Beats",
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

    def test_query_instructions_use_a_chinese_sources_heading(self):
        paths = [ROOT / "CLAUDE.md", ROOT / ".claude" / "commands" / "wiki-query.md"]
        for path in paths:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertIn("## 来源", text)
                self.assertNotIn("## Sources", text)

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

    def test_ingest_keeps_english_json_keys_but_uses_chinese_index_labels(self):
        labels = getattr(ingest, "INDEX_SECTION_LABELS", {})
        self.assertEqual(labels.get("Sources"), "来源")
        self.assertEqual(labels.get("Characters"), "人物")
        self.assertEqual(labels.get("Chapters"), "章节")

    def test_python_page_templates_use_chinese_display_text(self):
        text = (ROOT / "tools" / "apply_templates.py").read_text(encoding="utf-8")
        self.assertIn("## 概述", text)
        self.assertIn("人物信息", text)
        self.assertNotIn("## Overview", text)
        self.assertNotIn("<td>TBD</td>", text)


if __name__ == "__main__":
    unittest.main()
