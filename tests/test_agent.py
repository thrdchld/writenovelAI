"""
Tahap 9 — Pengujian unit untuk Python Agent Interface (novel_engine.agent).
"""

import io
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from novel_engine import agent, cli, project


def _create_sample_story(stories_root: Path, slug: str = "uji-agent") -> Path:
    story = stories_root / slug
    for sub in ("blueprint", "manuscript", "state-updates", "continuity"):
        (story / sub).mkdir(parents=True, exist_ok=True)

    (story / "00-premise.md").write_text(
        "# Premis\nArsip kota menyimpan peta lama yang hilang.\n",
        encoding="utf-8",
    )
    (story / "01-concept.md").write_text(
        "# Konsep\n\n## Mekanisme Misteri [RAHASIA PENULIS]\nPeta diubah secara diam-diam pada 2011.\n",
        encoding="utf-8",
    )
    (story / "02-characters.md").write_text(
        "# Karakter\n\n"
        "## Salma — 29\n"
        "- **Profil:** Teknisi pemetaan kontrak yang teliti.\n"
        "- **Rahasia:** Salma menyimpan salinan peta saku milik ayahnya.\n"
        "- **Rahasia Penulis:** Salma kelak menemukan buku catatan rahasia di gudang.\n"
        "Catatan tambahan lama tanpa label.\n\n"
        "## Dito — 32\n"
        "- **Profil:** Rekan survei lapangan.\n\n"
        "## Arthur Pendragon — 50\n"
        "- **Profil:** Pengawas arsip senior.\n\n"
        "## Pangeran Arthur — 24\n"
        "- **Profil:** Kurir dokumen.\n",
        encoding="utf-8",
    )
    (story / "03-world-and-rules.md").write_text(
        "# Dunia\nSemua berkas resmi wajib dicap basah.\n",
        encoding="utf-8",
    )
    (story / "04-story-outline.md").write_text(
        "| 1 | Garis Merah |\n| 2 | Ruang Arsip |\n| 3 | Gudang Lama |\n",
        encoding="utf-8",
    )
    (story / "05-decision-log.md").write_text(
        "# Decision Log\n\n"
        "## D-001 — Dalang Perubahan Peta\n"
        "- **Status:** KANON\n"
        "- **Klasifikasi:** Rahasia Penulis\n"
        "- **Keputusan:** Kepala dinas memerintahkan perubahan peta tanpa diketahui Salma.\n\n"
        "## D-002 — Salinan Peta Saku\n"
        "- **Status:** KANON\n"
        "- **Klasifikasi:** Rahasia Karakter\n"
        "- **Pemilik Rahasia:** Salma\n"
        "- **Keputusan:** Salma menyembunyikan salinan peta saku di tas kerjanya.\n",
        encoding="utf-8",
    )
    (story / "blueprint/chapter-001.md").write_text(
        "# Blueprint Bab 1 — Garis Merah\n\n"
        "## Adegan 1 — Ruang Rapat\n"
        "- **Tokoh hadir:** Salma, Dito\n"
        "- **Yang diketahui tokoh:** Salma tahu hasil surveinya berbeda; Dito tahu catatan lapangan.\n"
        "- **Yang diketahui pembaca:** Ada selisih antara peta dan kondisi lapangan.\n"
        "- **Informasi yang ditahan:** Motif perubahan peta 2011 ditahan.\n",
        encoding="utf-8",
    )
    (story / "blueprint/chapter-002.md").write_text(
        "# Blueprint Bab 2 — Ruang Arsip\n\n"
        "## Adegan 1 — Meja Arsip\n"
        "- **Tokoh hadir:** Salma, Dito\n"
        "- **Yang diketahui tokoh:** Salma dan Dito tahu kode rak arsip.\n",
        encoding="utf-8",
    )
    (story / "blueprint/chapter-003.md").write_text(
        "# Blueprint Bab 3 — Gudang Lama\n\n"
        "## Adegan 1 — Pintu Besi\n"
        "- **Tokoh hadir:** Salma\n"
        "- **Yang diketahui tokoh:** Salma tahu lokasi gudang.\n",
        encoding="utf-8",
    )
    (story / "manuscript/chapter-001.md").write_text(
        "# Bab 1 — Garis Merah\n\n"
        "Salma meletakkan peta survei di atas meja rapat dan menunjuk garis merah yang terputus.\n",
        encoding="utf-8",
    )
    (story / "state-updates/chapter-001.md").write_text(
        "# State Update — Bab 1: Garis Merah\n\n"
        "- **Waktu kronologis:** 17 Agustus 2026, 14.00-14.35\n"
        "- **Lokasi:** Ruang rapat kantor konsultan\n"
        "- **POV:** Salma\n\n"
        "## Peristiwa yang Terjadi\n"
        "- Salma membandingkan peta final dengan foto lapangan bersama Dito.\n"
        "- Dito mencatat selisih batas gang di buku survei.\n",
        encoding="utf-8",
    )
    (story / "state-updates/chapter-002.md").write_text(
        "# State Update — Bab 2: Ruang Arsip\n\n"
        "- **Waktu kronologis:** 18 Agustus 2026, 09.15-10.00\n"
        "- **Lokasi:** Ruang arsip kota\n"
        "- **POV:** Salma\n\n"
        "## Peristiwa yang Terjadi\n"
        "- FAKTA_MASA_DEPAN_BAB_2: Salma menemukan kunci brankas arsip bernomor 77.\n",
        encoding="utf-8",
    )
    return story


class AgentInterfaceTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.stories_dir = self.root / "stories"
        self.stories_dir.mkdir(parents=True)
        self.story = _create_sample_story(self.stories_dir, "uji-agent")
        self.patch_root = patch.object(project, "ROOT", self.root)
        self.patch_stories = patch.object(project, "STORIES", self.stories_dir)
        self.patch_root.start()
        self.patch_stories.start()

    def tearDown(self):
        self.patch_stories.stop()
        self.patch_root.stop()
        self.tmp.cleanup()

    def _run_agent(self, argv):
        out = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = agent.main(argv)
        raw_out = out.getvalue()
        payload = json.loads(raw_out)
        return rc, payload, err.getvalue()

    def test_status_operation(self):
        rc, payload, _ = self._run_agent(["--story", "uji-agent", "status"])
        self.assertEqual(rc, 0)
        self.assertEqual(payload["schema_version"], 1)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["operation"], "status")
        self.assertEqual(payload["story"], "uji-agent")
        self.assertIsInstance(payload["sources"], list)
        self.assertEqual(payload["data"]["progress"]["total_chapters"], 3)
        self.assertEqual(payload["data"]["progress"]["manuscripts_written"], 1)
        self.assertEqual(payload["data"]["progress"]["state_updates_written"], 2)
        self.assertEqual(payload["data"]["progress"]["completed_chapters"], 1)

    def test_context_operation_and_no_future_leak(self):
        rc, payload, _ = self._run_agent(["--story", "uji-agent", "context", "1"])
        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["operation"], "context")
        self.assertEqual(payload["data"]["chapter"], 1)
        self.assertTrue(payload["data"]["temporal_boundary"]["excludes_current_and_future_state_updates"])

        serialized = json.dumps(payload, ensure_ascii=False)
        self.assertNotIn("FAKTA_MASA_DEPAN_BAB_2", serialized)
        self.assertNotIn("state-updates/chapter-002.md", serialized)

        rc2, payload2, _ = self._run_agent(["--story", "uji-agent", "context", "2"])
        self.assertEqual(rc2, 0)
        serialized2 = json.dumps(payload2, ensure_ascii=False)
        self.assertIn("Salma membandingkan peta final", serialized2)
        self.assertNotIn("FAKTA_MASA_DEPAN_BAB_2", serialized2)
        self.assertNotIn("state-updates/chapter-002.md", payload2["sources"])

    def test_context_does_not_overwrite_existing_manuscript(self):
        ms = self.story / "manuscript/chapter-001.md"
        before = ms.read_text(encoding="utf-8")
        rc, payload, _ = self._run_agent(["--story", "uji-agent", "context", "1"])
        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(ms.read_text(encoding="utf-8"), before)

    def test_character_operation_separates_author_and_character_knowledge(self):
        rc, payload, _ = self._run_agent(["--story", "uji-agent", "character", "Salma"])
        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["operation"], "character")
        data = payload["data"]
        self.assertEqual(data["name"], "Salma")
        self.assertIn("Teknisi pemetaan kontrak yang teliti.", data["character_known"]["public_profile"])
        self.assertIn("Salma menyimpan salinan peta saku milik ayahnya.", data["character_known"]["character_secrets"])
        self.assertIn("Salma kelak menemukan buku catatan rahasia di gudang.", data["author_known"]["author_secrets"])
        self.assertTrue(len(data["author_known"]["decision_log_mentions"]["author_secrets"]) > 0)
        self.assertTrue(len(data["author_known"]["decision_log_mentions"]["character_secrets"]) > 0)

    def test_character_not_found(self):
        rc, payload, _ = self._run_agent(["--story", "uji-agent", "character", "TokohFiktif"])
        self.assertNotEqual(rc, 0)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["operation"], "character")
        self.assertEqual(payload["error"]["code"], "CHARACTER_NOT_FOUND")

    def test_character_ambiguous(self):
        rc, payload, _ = self._run_agent(["--story", "uji-agent", "character", "Arthur"])
        self.assertNotEqual(rc, 0)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error"]["code"], "CHARACTER_AMBIGUOUS")

    def test_timeline_operation_respects_before_chapter(self):
        rc, payload, _ = self._run_agent(["--story", "uji-agent", "timeline", "--before", "2"])
        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["operation"], "timeline")
        entries = payload["data"]["entries"]
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["chapter"], 1)
        self.assertEqual(entries[0]["recorded_time"], "17 Agustus 2026, 14.00-14.35")
        self.assertNotIn("FAKTA_MASA_DEPAN_BAB_2", json.dumps(payload, ensure_ascii=False))

    def test_timeline_before_chapter_1_returns_empty_without_inventing(self):
        rc, payload, _ = self._run_agent(["--story", "uji-agent", "timeline", "--before", "1"])
        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["data"]["entries"], [])
        self.assertEqual(payload["data"]["total_entries"], 0)

    def test_search_operation_scoped_with_line_numbers_and_limit(self):
        (self.root / "outside_secret.md").write_text("garis merah rahasia luar\n", encoding="utf-8")

        rc, payload, _ = self._run_agent(["--story", "uji-agent", "search", "Salma", "--limit", "2"])
        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["operation"], "search")
        self.assertEqual(payload["data"]["returned_matches"], 2)
        self.assertTrue(payload["data"]["truncated"])
        for m in payload["data"]["matches"]:
            self.assertIn("file", m)
            self.assertIn("line", m)
            self.assertIsInstance(m["line"], int)
            self.assertGreaterEqual(m["line"], 1)
            self.assertNotIn("outside_secret.md", m["file"])

    def test_search_with_temporal_limit_excludes_future(self):
        rc, payload, _ = self._run_agent([
            "--story", "uji-agent", "search", "FAKTA_MASA_DEPAN_BAB_2", "--before", "2"
        ])
        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["data"]["total_matches"], 0)
        self.assertEqual(payload["data"]["matches"], [])

    def test_search_no_results(self):
        rc, payload, _ = self._run_agent(["--story", "uji-agent", "search", "kata_yang_tidak_ada_xyz"])
        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["data"]["total_matches"], 0)
        self.assertEqual(payload["data"]["matches"], [])
        self.assertFalse(payload["data"]["truncated"])

    def test_validate_operation_valid_and_invalid_chapter(self):
        rc1, payload1, _ = self._run_agent(["--story", "uji-agent", "validate", "1"])
        self.assertEqual(rc1, 0)
        self.assertTrue(payload1["ok"])
        self.assertEqual(payload1["operation"], "validate")
        self.assertTrue(payload1["data"]["valid"])
        self.assertEqual(payload1["data"]["findings"], [])

        rc2, payload2, _ = self._run_agent(["--story", "uji-agent", "validate", "2"])
        self.assertEqual(rc2, 0)
        self.assertTrue(payload2["ok"])
        self.assertFalse(payload2["data"]["valid"])
        codes = {f["code"] for f in payload2["data"]["findings"]}
        self.assertIn("MANUSCRIPT_MISSING", codes)

    def test_story_not_found(self):
        rc, payload, _ = self._run_agent(["--story", "tidak-ada", "status"])
        self.assertNotEqual(rc, 0)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error"]["code"], "STORY_NOT_FOUND")

    def test_path_traversal_rejected(self):
        rc, payload, _ = self._run_agent(["--story", "../etc", "status"])
        self.assertNotEqual(rc, 0)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error"]["code"], "PATH_OUT_OF_BOUNDS")

    def test_chapter_not_found(self):
        rc, payload, _ = self._run_agent(["--story", "uji-agent", "context", "99"])
        self.assertNotEqual(rc, 0)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["operation"], "context")
        self.assertEqual(payload["error"]["code"], "CHAPTER_NOT_FOUND")

        rc_val, payload_val, _ = self._run_agent(["--story", "uji-agent", "validate", "99"])
        self.assertNotEqual(rc_val, 0)
        self.assertFalse(payload_val["ok"])
        self.assertEqual(payload_val["error"]["code"], "CHAPTER_NOT_FOUND")

    def test_invalid_arguments(self):
        for bad_argv in (
            [],
            ["operasi-ngawur"],
            ["--story", "uji-agent", "context", "abc"],
            ["--story", "uji-agent", "context", "0"],
            ["--story", "uji-agent", "search", "kata", "--limit", "0"],
            ["--story", "uji-agent", "timeline", "--before", "-1"],
        ):
            with self.subTest(argv=bad_argv):
                rc, payload, _ = self._run_agent(bad_argv)
                self.assertEqual(rc, 2)
                self.assertFalse(payload["ok"])
                self.assertEqual(payload["schema_version"], 1)
                self.assertEqual(payload["error"]["code"], "INVALID_ARGUMENTS")

    def test_cli_routes_agent_subcommand_cleanly(self):
        out = io.StringIO()
        with redirect_stdout(out):
            rc = cli.main(["--story", "uji-agent", "agent", "status"])
        self.assertEqual(rc, 0)
        payload = json.loads(out.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["operation"], "status")
        self.assertEqual(payload["story"], "uji-agent")

    def test_agent_import_does_not_import_agy(self):
        script = r'''
import builtins
original = builtins.__import__
def guarded(name, *args, **kwargs):
    if name.endswith(".agy") or name == "novel_engine.agy":
        raise AssertionError("Agent interface attempted to import AGY")
    return original(name, *args, **kwargs)
builtins.__import__ = guarded
import novel_engine.agent
import novel_engine.cli
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
