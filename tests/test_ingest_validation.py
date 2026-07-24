import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import ingest


class IngestValidationTests(unittest.TestCase):
    def test_validate_ingest_reports_broken_links(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            wiki_dir = Path(tmpdir) / "wiki"
            wiki_dir.mkdir()
            (wiki_dir / "hero.md").write_text("Meet [[Missing Person]].\n", encoding="utf-8")
            index_file = wiki_dir / "index.md"
            index_file.write_text("# Wiki Index\n\n- [Hero](hero.md)\n", encoding="utf-8")

            with patch.object(ingest, "WIKI_DIR", wiki_dir), patch.object(
                ingest, "INDEX_FILE", index_file
            ):
                result = ingest.validate_ingest()

        self.assertEqual(result["broken_links"], [("hero.md", "Missing Person")])

    def test_validate_only_exits_successfully_without_ingesting(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            wiki_dir = Path(tmpdir) / "wiki"
            wiki_dir.mkdir()
            index_file = wiki_dir / "index.md"
            index_file.write_text("# Wiki Index\n", encoding="utf-8")

            with patch.object(ingest, "WIKI_DIR", wiki_dir), patch.object(
                ingest, "INDEX_FILE", index_file
            ), patch.object(sys, "argv", ["ingest.py", "--validate-only"]), contextlib.redirect_stdout(
                io.StringIO()
            ):
                with self.assertRaises(SystemExit) as exit_context:
                    ingest.main()

        self.assertEqual(exit_context.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
