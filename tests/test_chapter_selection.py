import builtins
import subprocess
import sys
import unittest
from pathlib import Path

from novel_engine.chapter_selection import parse_chapter_numbers


class ChapterSelectionTests(unittest.TestCase):
    def test_single_number(self):
        self.assertEqual(parse_chapter_numbers("3", [1, 2, 3, 4]), [3])

    def test_range_and_list(self):
        self.assertEqual(parse_chapter_numbers("1-3,5,7-8", range(1, 9)), [1, 2, 3, 5, 7, 8])

    def test_duplicates_are_removed_and_sorted(self):
        self.assertEqual(parse_chapter_numbers("3,1-3,2", [1, 2, 3]), [1, 2, 3])

    def test_invalid_inputs(self):
        for raw in ("", " ", "1,,2", ",1", "1,", "x", "3-1", "0", "-2", "1-2-3"):
            with self.subTest(raw=raw):
                self.assertIsNone(parse_chapter_numbers(raw, range(1, 10)))

    def test_unavailable_chapter_rejected(self):
        self.assertIsNone(parse_chapter_numbers("1-4", [1, 2, 3]))

    def test_non_string_rejected(self):
        self.assertIsNone(parse_chapter_numbers(None, [1, 2]))


class CoreImportIndependenceTests(unittest.TestCase):
    def test_core_cli_import_does_not_import_or_require_agy(self):
        script = r'''
import builtins
original = builtins.__import__
def guarded(name, *args, **kwargs):
    if name.endswith(".agy") or name == "novel_engine.agy":
        raise AssertionError("Core import attempted to load AGY")
    return original(name, *args, **kwargs)
builtins.__import__ = guarded
import novel_engine.cli
import novel_engine.project
import novel_engine.chapter_selection
'''
        result = subprocess.run(
            [sys.executable, "-c", script],
            cwd=Path(__file__).resolve().parents[1],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
