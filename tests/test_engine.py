import tempfile
import unittest
from pathlib import Path
from novel_engine.project import blueprints, chapter_numbers, build_context
from novel_engine.audit import deterministic_audit


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.story = Path(self.tmp.name) / "sample"
        (self.story / "blueprint").mkdir(parents=True)
        (self.story / "manuscript").mkdir()
        (self.story / "state-updates").mkdir()
        (self.story / "04-story-outline.md").write_text("| 1 | One |\n| 2 | Two |\n", encoding="utf-8")
        (self.story / "blueprint/chapter-001.md").write_text("# Blueprint Bab 1 — One\n", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_combined_blueprint_split(self):
        (self.story / "blueprint/chapter-002-to-003.md").write_text(
            "## Bab 2 — Two\nIsi dua\n## Bab 3 — Three\nIsi tiga\n", encoding="utf-8")
        self.assertIn(2, blueprints(self.story))
        self.assertIn(3, blueprints(self.story))

    def test_audit_detects_missing_blueprint(self):
        found = deterministic_audit(self.story)
        self.assertTrue(any(x[1] == "BLUEPRINT_MISSING" and "Bab 2" in x[2] for x in found))

    def test_audit_detects_duplicate_outline_number(self):\n        (self.story / "04-story-outline.md").write_text("| 1 | One |\\n| 1 | Duplicate |\\n", encoding="utf-8")\n        found = deterministic_audit(self.story)\n        self.assertTrue(any(x[1] == "DUPLICATE_OUTLINE_NUMBER" for x in found))\n\n    def test_context_does_not_include_future_state(self):
        (self.story / "05-decision-log.md").write_text("Canon", encoding="utf-8")
        (self.story / "state-updates/chapter-002.md").write_text("future secret", encoding="utf-8")
        text = build_context(self.story, 1)
        self.assertNotIn("future secret", text)

    def test_chapter_numbers(self):
        self.assertEqual(chapter_numbers(self.story), [1, 2])


if __name__ == "__main__":
    unittest.main()
