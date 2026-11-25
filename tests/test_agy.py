"""
Tahap 5R — Pengujian regresi dan validasi keamanan/hasil untuk novel_engine.agy.
"""

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from novel_engine import agy
from novel_engine.project import manuscript, state_update


def _setup_temp_story(root: Path) -> Path:
    story = root / "test_story"
    (story / "blueprint").mkdir(parents=True)
    (story / "manuscript").mkdir()
    (story / "state-updates").mkdir()
    (story / "00-premise.md").write_text("# Premis\nUji tulis singkat.\n", encoding="utf-8")
    (story / "02-characters.md").write_text(
        "# Karakter\n\n## Rina — 25\n- **Profil:** Petugas arsip kota.\n",
        encoding="utf-8",
    )
    (story / "04-story-outline.md").write_text(
        "| 1 | Surat Pagi |\n| 2 | Ruang Arsip |\n",
        encoding="utf-8",
    )
    (story / "blueprint/chapter-001.md").write_text(
        "# Blueprint Bab 1 — Surat Pagi\n\n"
        "## Adegan 1 — Meja Kerja\n"
        "- **Tokoh hadir:** Rina\n"
        "- **Yang diketahui tokoh:** Rina tahu amplop datang pagi ini.\n"
        "- **Yang diketahui pembaca:** Pembaca melihat amplop tanpa nama pengirim.\n"
        "- **Informasi yang ditahan:** Isi surat ditahan.\n",
        encoding="utf-8",
    )
    (story / "blueprint/chapter-002.md").write_text(
        "# Blueprint Bab 2 — Ruang Arsip\n\n"
        "## Adegan 1 — Rak Lama\n"
        "- **Tokoh hadir:** Rina\n"
        "- **Yang diketahui tokoh:** Rina tahu nomor rak.\n",
        encoding="utf-8",
    )
    return story


class AgyRunnerTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.story = _setup_temp_story(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_no_dangerously_skip_permissions_in_source(self):
        """Pastikan --dangerously-skip-permissions tidak digunakan di novel_engine/agy.py."""
        agy_src = Path(agy.__file__).read_text(encoding="utf-8")
        self.assertNotIn("--dangerously-skip-permissions", agy_src)
        self.assertIn("--mode", agy_src)
        self.assertIn("accept-edits", agy_src)

    @patch("novel_engine.agy.shutil.which", return_value="/usr/bin/agy")
    @patch("novel_engine.agy.subprocess.run")
    def test_agy_called_with_safe_mode_and_scoped_cwd(self, mock_run, _mock_which):
        """AGY dipanggil dengan --mode accept-edits dan cwd terbatas ke folder cerita."""
        def fake_run(cmd, cwd=None, **kwargs):
            self.assertNotIn("--dangerously-skip-permissions", cmd)
            self.assertIn("--mode", cmd)
            self.assertEqual(cmd[cmd.index("--mode") + 1], "accept-edits")
            self.assertEqual(Path(cwd).resolve(), self.story.resolve())
            manuscript(self.story, 1).write_text(
                "# Bab 1\n\nRina menatap amplop cokelat di meja kerjanya pagi itu.",
                encoding="utf-8",
            )
            state_update(self.story, 1).write_text(
                "# State Update Bab 1\n\n- Rina menerima amplop tanpa nama pengirim.",
                encoding="utf-8",
            )
            return subprocess.CompletedProcess(
                cmd, 0, stdout=json.dumps({"status": "SUCCESS"}), stderr=""
            )

        mock_run.side_effect = fake_run
        res = agy.run_one(self.story, 1)
        self.assertEqual(res, "success")
        self.assertTrue(mock_run.called)
        self.assertTrue(manuscript(self.story, 1).is_file())
        self.assertTrue(state_update(self.story, 1).is_file())

    @patch("novel_engine.agy.shutil.which", return_value="/usr/bin/agy")
    @patch("novel_engine.agy.subprocess.run")
    def test_invalid_json_response_not_treated_as_success(self, mock_run, _mock_which):
        """Exit code 0 dengan stdout bukan JSON valid tidak boleh dianggap sukses."""
        def fake_run(cmd, **kwargs):
            manuscript(self.story, 1).write_text("# Bab 1\n\nParagraf valid.", encoding="utf-8")
            state_update(self.story, 1).write_text("# State\n\n- Fakta valid.", encoding="utf-8")
            return subprocess.CompletedProcess(cmd, 0, stdout="not-json", stderr="")

        mock_run.side_effect = fake_run
        self.assertEqual(agy.run_one(self.story, 1), "error")

    @patch("novel_engine.agy.shutil.which", return_value="/usr/bin/agy")
    @patch("novel_engine.agy.subprocess.run")
    def test_error_status_and_denied_actions_fail(self, mock_run, _mock_which):
        """Status ERROR atau denied_actions harus menghasilkan status error."""
        mock_run.return_value = subprocess.CompletedProcess(
            ["agy"], 0, stdout=json.dumps({"status": "ERROR", "error": "gagal"}), stderr=""
        )
        self.assertEqual(agy.run_one(self.story, 1), "error")

        mock_run.return_value = subprocess.CompletedProcess(
            ["agy"], 0,
            stdout=json.dumps({"status": "SUCCESS", "denied_actions": ["write_file"]}),
            stderr="",
        )
        self.assertEqual(agy.run_one(self.story, 1), "error")

    @patch("novel_engine.agy.shutil.which", return_value="/usr/bin/agy")
    @patch("novel_engine.agy.subprocess.run")
    def test_empty_or_placeholder_files_rejected(self, mock_run, _mock_which):
        """File kosong atau hanya placeholder/heading tidak dianggap berhasil."""
        def fake_placeholder(cmd, **kwargs):
            manuscript(self.story, 1).write_text("# Bab 1\n\nTODO\n", encoding="utf-8")
            state_update(self.story, 1).write_text("# State\n\n- Fakta valid.", encoding="utf-8")
            return subprocess.CompletedProcess(
                cmd, 0, stdout=json.dumps({"status": "SUCCESS"}), stderr=""
            )

        mock_run.side_effect = fake_placeholder
        self.assertEqual(agy.run_one(self.story, 1), "incomplete")

    @patch("novel_engine.agy.shutil.which", return_value="/usr/bin/agy")
    @patch("novel_engine.agy.subprocess.run")
    def test_existing_files_not_overwritten_without_rewrite(self, mock_run, _mock_which):
        """File yang sudah ada tidak ditimpa dan AGY tidak dipanggil tanpa rewrite=True."""
        manuscript(self.story, 1).write_text("Naskah lama.", encoding="utf-8")
        state_update(self.story, 1).write_text("State lama.", encoding="utf-8")
        res = agy.run_one(self.story, 1, rewrite=False)
        self.assertEqual(res, "skipped")
        self.assertFalse(mock_run.called)
        self.assertEqual(manuscript(self.story, 1).read_text(encoding="utf-8"), "Naskah lama.")

    @patch("novel_engine.agy.shutil.which", return_value="/usr/bin/agy")
    @patch("novel_engine.agy.subprocess.run")
    def test_rewrite_unchanged_file_rejected(self, mock_run, _mock_which):
        """Rewrite yang tidak mengubah file tidak dianggap berhasil."""
        manuscript(self.story, 1).write_text("Naskah lama yang cukup panjang.", encoding="utf-8")
        state_update(self.story, 1).write_text("State lama yang cukup panjang.", encoding="utf-8")
        mock_run.return_value = subprocess.CompletedProcess(
            ["agy"], 0, stdout=json.dumps({"status": "SUCCESS"}), stderr=""
        )
        self.assertEqual(agy.run_one(self.story, 1, rewrite=True), "incomplete")

    @patch("novel_engine.agy.run_one")
    def test_batch_stops_after_failure(self, mock_run_one):
        """Batch berhenti pada bab yang gagal dan tidak menjalankan bab berikutnya."""
        mock_run_one.side_effect = ["error", "success"]
        rc = agy.run_batch(self.story, "1-2", [1, 2])
        self.assertEqual(rc, 1)
        self.assertEqual(mock_run_one.call_count, 1)

    def test_placeholder_detection_cases(self):
        """Deteksi placeholder menolak placeholder/heading/komentar kosong tapi menerima prosa dengan kata TODO."""
        invalid_samples = [
            "TODO",
            "TODO: tulis bab",
            "TBD",
            "Belum ditulis",
            "Isi di sini",
            "# Bab 1\n\n## Adegan 1\n",
            "<!-- TODO: tulis bab nanti -->",
        ]
        for sample in invalid_samples:
            with self.subTest(sample=sample):
                self.assertFalse(agy._is_meaningful_content(sample))

        valid_with_todo = (
            "# Bab 1\n\n"
            "Di sudut meja tertempel catatan kecil bertuliskan TODO dari rapat kemarin. "
            "Salma menggesernya pelan sebelum membuka peta."
        )
        self.assertTrue(agy._is_meaningful_content(valid_with_todo))

    @patch("novel_engine.agy.shutil.which", return_value="/usr/bin/agy")
    @patch("novel_engine.agy.subprocess.run")
    def test_existing_both_placeholder_incomplete_and_no_agy(self, mock_run, _mock_which):
        """Kedua file existing berisi placeholder: incomplete, AGY tidak dipanggil, tidak ditimpa."""
        manuscript(self.story, 1).write_text("# Bab 1\n\nTODO: tulis bab\n", encoding="utf-8")
        state_update(self.story, 1).write_text("# State\n\nBelum ditulis\n", encoding="utf-8")
        self.assertEqual(agy.run_one(self.story, 1), "incomplete")
        self.assertFalse(mock_run.called)
        self.assertIn("TODO: tulis bab", manuscript(self.story, 1).read_text(encoding="utf-8"))

    @patch("novel_engine.agy.shutil.which", return_value="/usr/bin/agy")
    @patch("novel_engine.agy.subprocess.run")
    def test_existing_valid_manuscript_placeholder_state_incomplete(self, mock_run, _mock_which):
        """Naskah valid, State Update placeholder: incomplete, AGY tidak dipanggil."""
        manuscript(self.story, 1).write_text("# Bab 1\n\nProsa lengkap bab pertama.", encoding="utf-8")
        state_update(self.story, 1).write_text("TBD", encoding="utf-8")
        self.assertEqual(agy.run_one(self.story, 1), "incomplete")
        self.assertFalse(mock_run.called)

    @patch("novel_engine.agy.shutil.which", return_value="/usr/bin/agy")
    @patch("novel_engine.agy.subprocess.run")
    def test_existing_placeholder_manuscript_valid_state_incomplete(self, mock_run, _mock_which):
        """Naskah placeholder, State Update valid: incomplete, AGY tidak dipanggil."""
        manuscript(self.story, 1).write_text("<!-- kosong -->", encoding="utf-8")
        state_update(self.story, 1).write_text("# State\n\n- Rina datang pagi hari.", encoding="utf-8")
        self.assertEqual(agy.run_one(self.story, 1), "incomplete")
        self.assertFalse(mock_run.called)

    @patch("novel_engine.agy.shutil.which", return_value="/usr/bin/agy")
    @patch("novel_engine.agy.subprocess.run")
    def test_existing_manuscript_without_state_incomplete(self, mock_run, _mock_which):
        """Naskah ada, State Update tidak ada: incomplete, AGY tidak dipanggil."""
        manuscript(self.story, 1).write_text("# Bab 1\n\nProsa lengkap bab pertama.", encoding="utf-8")
        self.assertEqual(agy.run_one(self.story, 1), "incomplete")
        self.assertFalse(mock_run.called)

    @patch("novel_engine.agy.shutil.which", return_value="/usr/bin/agy")
    @patch("novel_engine.agy.subprocess.run")
    def test_batch_stops_on_incomplete_existing_files(self, mock_run, _mock_which):
        """Batch berhenti jika menemukan file existing tidak lengkap dan tidak memanggil AGY."""
        manuscript(self.story, 1).write_text("# Bab 1\n\nIsi di sini\n", encoding="utf-8")
        state_update(self.story, 1).write_text("# State\n\n- Fakta valid.", encoding="utf-8")
        rc = agy.run_batch(self.story, "1-2", [1, 2], rewrite=False)
        self.assertEqual(rc, 1)
        self.assertFalse(mock_run.called)
        self.assertFalse(manuscript(self.story, 2).exists())


if __name__ == "__main__":
    unittest.main()
