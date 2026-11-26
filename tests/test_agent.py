"""
Tahap 9 & 9B — Pengujian unit untuk Python Agent Interface (novel_engine.agent).
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
        "| 1 | Garis Merah |\n"
        "| 2 | Ruang Arsip |\n"
        "| 3 | Gudang Lama — Pengungkapan Kunci Brankas |\n",
        encoding="utf-8",
    )
    (story / "05-decision-log.md").write_text(
        "# Decision Log\n\n"
        "## D-001 — Dalang Perubahan Peta\n"
        "- **Status:** KANON\n"
        "- **Klasifikasi:** Rahasia Penulis\n"
        "- **Keputusan:** Kepala dinas memerintahkan perubahan peta tanpa diketahui Salma; bukti akhir ada di brankas 77.\n\n"
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
    def test_timeline_ignores_document_update_date_and_extracts_fakta_baru(self):
        """Regression: Tanggal pembaruan tidak boleh dianggap waktu kronologis cerita; heading Fakta baru (KANON) diekstrak bersih."""
        (self.story / "state-updates/chapter-001.md").write_text(
            "# State Update — Bab 1\n\n"
             "- **Status bab:** DRAFT\n"
            "- **Tanggal pembaruan:** 23 November 2026\n\n"
            "## Fakta baru (KANON)\n"
            "- Pada 15 Oktober, Salma menemukan berkas lama.\n\n"
            "## Story state\n"
            "- Lokasi tokoh: Salma berada di rumah.\n",
            encoding="utf-8",
        )
        rc, payload, _ = self._run_agent(["--story", "uji-agent", "timeline", "--before", "2"])
        self.assertEqual(rc, 0)
        entry = payload["data"]["entries"][0]
        self.assertIsNone(entry["recorded_time"])
        self.assertEqual(entry["location"], "Salma berada di rumah.")
        self.assertEqual(entry["events"], ["Pada 15 Oktober, Salma menemukan berkas lama."])
        
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
        self.assertEqual(payload["data"]["scope"], "all")
        self.assertEqual(payload["data"]["returned_matches"], 2)
        self.assertTrue(payload["data"]["truncated"])
        for m in payload["data"]["matches"]:
            self.assertIn("file", m)
            self.assertIn("line", m)
            self.assertIn("doc_category", m)
            self.assertIn("temporal_status", m)
            self.assertIn("may_contain_future_info", m)
            self.assertIsInstance(m["line"], int)
            self.assertGreaterEqual(m["line"], 1)
            self.assertNotIn("outside_secret.md", m["file"])

    def test_search_with_temporal_limit_excludes_future(self):
        rc, payload, _ = self._run_agent([
            "--story", "uji-agent", "search", "FAKTA_MASA_DEPAN_BAB_2", "--before", "2"
        ])
        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["data"]["scope"], "chronological")
        self.assertTrue(payload["data"]["all_results_temporally_bounded"])
        self.assertEqual(payload["data"]["temporal_guarantee"], "strict_before_chapter")
        self.assertEqual(payload["data"]["total_matches"], 0)
        self.assertEqual(payload["data"]["matches"], [])

    def test_search_before_excludes_outline_and_decision_log_by_default_and_global_scope_warns(self):
        """Pencarian --before N tidak memindai outline/decision log secara default; scope global/all memberi tanda risiko masa depan."""
        rc_chron, pay_chron, _ = self._run_agent([
            "--story", "uji-agent", "search", "brankas", "--before", "2"
        ])
        self.assertEqual(rc_chron, 0)
        self.assertEqual(pay_chron["data"]["scope"], "chronological")
        self.assertTrue(pay_chron["data"]["all_results_temporally_bounded"])
        self.assertEqual(pay_chron["data"]["total_matches"], 0)
        self.assertGreater(pay_chron["data"]["excluded_unbounded_files_count"], 0)

        rc_glob, pay_glob, _ = self._run_agent([
            "--story", "uji-agent", "search", "brankas", "--scope", "global"
        ])
        self.assertEqual(rc_glob, 0)
        self.assertEqual(pay_glob["data"]["scope"], "global")
        self.assertFalse(pay_glob["data"]["all_results_temporally_bounded"])
        self.assertEqual(pay_glob["data"]["temporal_guarantee"], "unbounded_global_only")
        self.assertIsNotNone(pay_glob["data"]["temporal_warning"])
        self.assertGreaterEqual(pay_glob["data"]["total_matches"], 2)
        categories = {m["doc_category"] for m in pay_glob["data"]["matches"]}
        self.assertIn("global_outline", categories)
        self.assertIn("global_decision_log", categories)
        for m in pay_glob["data"]["matches"]:
            self.assertEqual(m["temporal_status"], "unverified_temporal")
            self.assertTrue(m["may_contain_future_info"])

        rc_all, pay_all, _ = self._run_agent([
            "--story", "uji-agent", "search", "brankas", "--before", "2", "--scope", "all"
        ])
        self.assertEqual(rc_all, 0)
        self.assertEqual(pay_all["data"]["scope"], "all")
        self.assertFalse(pay_all["data"]["all_results_temporally_bounded"])
        self.assertEqual(pay_all["data"]["temporal_guarantee"], "partial_contains_unbounded_documents")
        self.assertIsNotNone(pay_all["data"]["temporal_warning"])
        self.assertGreater(pay_all["data"]["unbounded_match_count"], 0)

    def test_search_unnumbered_documents_classified_and_excluded_in_chronological(self):
        """Dokumen tanpa nomor bab (continuity umum / catatan umum) diklasifikasi jelas dan dikecualikan di scope chronological."""
        (self.story / "continuity/timeline-umum.md").write_text(
            "Kronologi umum memuat catatan rahasia_tanpa_bab_xyz di akhir cerita.\n",
            encoding="utf-8",
        )
        (self.story / "catatan-umum.md").write_text(
            "Catatan tambahan berisi rahasia_tanpa_bab_xyz.\n",
            encoding="utf-8",
        )

        rc_chron, pay_chron, _ = self._run_agent([
            "--story", "uji-agent", "search", "rahasia_tanpa_bab_xyz", "--before", "2"
        ])
        self.assertEqual(rc_chron, 0)
        self.assertEqual(pay_chron["data"]["total_matches"], 0)
        self.assertIn(
            "stories/uji-agent/continuity/timeline-umum.md",
            pay_chron["data"]["excluded_unbounded_files"],
        )

        rc_glob, pay_glob, _ = self._run_agent([
            "--story", "uji-agent", "search", "rahasia_tanpa_bab_xyz", "--scope", "global"
        ])
        self.assertEqual(rc_glob, 0)
        self.assertEqual(pay_glob["data"]["total_matches"], 2)
        cats = {m["doc_category"] for m in pay_glob["data"]["matches"]}
        self.assertEqual(cats, {"unnumbered_continuity", "unnumbered_document"})
        for m in pay_glob["data"]["matches"]:
            self.assertTrue(m["may_contain_future_info"])
            self.assertEqual(m["temporal_status"], "unverified_temporal")

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
        self.assertEqual(payload1["data"]["validation_status"], "valid")
        self.assertIn("lulus", payload1["data"]["status_reason"].lower())
        self.assertEqual(payload1["data"]["findings"], [])

        rc2, payload2, _ = self._run_agent(["--story", "uji-agent", "validate", "2"])
        self.assertEqual(rc2, 0)
        self.assertTrue(payload2["ok"])
        self.assertFalse(payload2["data"]["valid"])
        self.assertEqual(payload2["data"]["validation_status"], "invalid")
        codes = {f["code"] for f in payload2["data"]["findings"]}
        self.assertIn("MANUSCRIPT_MISSING", codes)
        self.assertIn("ORPHAN_STATE_CONFLICT", codes)
        self.assertIn("ORPHAN_STATE_CONFLICT", payload2["data"]["blocking_findings"])

    def test_validate_blocking_source_conflict_fails_validation(self):
        """Konflik sumber pemblokir (State Update Bab sebelumnya hilang) harus menggagalkan validasi Bab 2."""
        (self.story / "manuscript/chapter-002.md").write_text(
            "# Bab 2 — Ruang Arsip\n\nSalma memeriksa rak arsip bersama Dito.\n",
            encoding="utf-8",
        )
        (self.story / "state-updates/chapter-001.md").unlink()

        rc, payload, _ = self._run_agent(["--story", "uji-agent", "validate", "2"])
        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        data = payload["data"]
        self.assertFalse(data["valid"])
        self.assertEqual(data["validation_status"], "invalid")
        self.assertFalse(data["checks"]["no_blocking_conflicts"])
        self.assertIn("PREVIOUS_STATE_UPDATE_MISSING", data["blocking_findings"])
        self.assertIn("PREVIOUS_STATE_UPDATE_MISSING", data["status_reason"])

    def test_validate_warning_only_source_conflict_remains_valid_with_warning(self):
        """Konflik peringatan saja (naskah Bab 1 belum ada, tetapi State Update Bab 1 & seluruh berkas Bab 2 lengkap) tetap valid dengan peringatan."""
        (self.story / "manuscript/chapter-002.md").write_text(
            "# Bab 2 — Ruang Arsip\n\nSalma memeriksa rak arsip bersama Dito.\n",
            encoding="utf-8",
        )
        (self.story / "manuscript/chapter-001.md").unlink()

        rc, payload, _ = self._run_agent(["--story", "uji-agent", "validate", "2"])
        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        data = payload["data"]
        self.assertTrue(data["valid"])
        self.assertEqual(data["validation_status"], "valid_with_warnings")
        self.assertTrue(data["checks"]["no_blocking_conflicts"])
        self.assertEqual(data["blocking_findings"], [])
        self.assertIn("PREVIOUS_MANUSCRIPT_MISSING", data["warning_findings"])
        self.assertIn("PREVIOUS_MANUSCRIPT_MISSING", data["status_reason"])

    def test_unnumbered_continuity_flagged_in_context_and_timeline(self):
        """Berkas continuity tanpa nomor bab tetap disertakan tetapi ditandai unverified_temporal dan safe_as_prior_fact=False."""
        (self.story / "continuity/timeline-global.md").write_text(
            "Catatan kontinuitas lintas bab yang memuat detail akhir cerita.\n",
            encoding="utf-8",
        )
        (self.story / "continuity/chapter-001.md").write_text(
            "Catatan kontinuitas khusus Bab 1.\n",
            encoding="utf-8",
        )

        rc_ctx, pay_ctx, _ = self._run_agent(["--story", "uji-agent", "context", "2"])
        self.assertEqual(rc_ctx, 0)
        tb_ctx = pay_ctx["data"]["temporal_boundary"]
        self.assertTrue(tb_ctx["has_unverified_continuity"])
        self.assertIn("stories/uji-agent/continuity/timeline-global.md", tb_ctx["unverified_continuity_sources"])
        notes_by_src = {item["source"]: item for item in pay_ctx["data"]["continuity_notes"]}
        self.assertIn("stories/uji-agent/continuity/timeline-global.md", notes_by_src)
        unnumbered = notes_by_src["stories/uji-agent/continuity/timeline-global.md"]
        self.assertEqual(unnumbered["temporal_status"], "unverified_temporal")
        self.assertFalse(unnumbered["temporal_boundary_verified"])
        self.assertFalse(unnumbered["safe_as_prior_fact"])
        self.assertIsNotNone(unnumbered["warning"])

        numbered = notes_by_src["stories/uji-agent/continuity/chapter-001.md"]
        self.assertEqual(numbered["temporal_status"], "verified_before_chapter")
        self.assertTrue(numbered["temporal_boundary_verified"])
        self.assertTrue(numbered["safe_as_prior_fact"])

        rc_tl, pay_tl, _ = self._run_agent(["--story", "uji-agent", "timeline", "--before", "2"])
        self.assertEqual(rc_tl, 0)
        tb_tl = pay_tl["data"]["temporal_boundary"]
        self.assertTrue(tb_tl["has_unverified_continuity"])
        self.assertIn("stories/uji-agent/continuity/timeline-global.md", tb_tl["unverified_continuity_sources"])
        self.assertIsNotNone(tb_tl["warning"])
        rec_by_src = {item["source"]: item for item in pay_tl["data"]["continuity_records"]}
        self.assertFalse(rec_by_src["stories/uji-agent/continuity/timeline-global.md"]["safe_as_prior_fact"])
        self.assertEqual(
            rec_by_src["stories/uji-agent/continuity/timeline-global.md"]["temporal_status"],
            "unverified_temporal",
        )
        self.assertTrue(rec_by_src["stories/uji-agent/continuity/chapter-001.md"]["safe_as_prior_fact"])

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
            ["--story", "uji-agent", "search", "kata", "--scope", "ngawur"],
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
