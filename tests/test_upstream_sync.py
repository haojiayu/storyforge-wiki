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
