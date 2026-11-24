import tempfile
import unittest
from pathlib import Path
from novel_engine.project import blueprints, chapter_numbers, build_context, build_memory
from novel_engine.audit import deterministic_audit


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.story = Path(self.tmp.name) / "sample"
        (self.story / "blueprint").mkdir(parents=True)
        (self.story / "manuscript").mkdir()
        (self.story / "state-updates").mkdir()
        (self.story / "04-story-outline.md").write_text("| 1 | One |\n| 2 | Two |\n", encoding="utf-8")
        (self.story / "02-characters.md").write_text(
            "# Karakter\n\n"
            "## Salma — 29\nTeknisi pemetaan teliti.\n\n"
            "## Dito — 32\nRekan kerja survei berorientasi prosedur.\n\n"
            "## Yuni — 56\nIbu Salma. Mengetahui Hadi pernah berjanji memperbaiki catatan tiga rumah setelah banjir 2011 dan memilih diam.\n",
            encoding="utf-8"
        )
        (self.story / "blueprint/chapter-001.md").write_text(
            "# Blueprint Bab 1 — One\n\n"
            "## Adegan 1 — Peta final\n"
            "- **Tokoh hadir:** Salma, Dito, koordinator proyek\n"
            "- **Yang diketahui tokoh:** Salma tahu hasil surveinya; Dito tahu catatan lapangan; koordinator hanya tahu peta kerja awal.\n"
            "- **Yang diketahui pembaca:** Pembaca tahu ada perbedaan peta dan kenyataan.\n"
            "- **Informasi yang ditahan:** Alasan Salma yakin ada rumah di balik tembok ditahan.\n\n"
            "## Adegan 2 — Nama di kolom pemeriksa\n"
            "- **Tokoh hadir:** Salma, Dito\n"
            "- **Yang diketahui tokoh:** Salma tahu Hadi ayahnya; Dito baru tahu nama itu punya hubungan pribadi.\n"
            "- **Yang diketahui pembaca:** Pembaca mengetahui ayah Salma terlibat, belum tahu perannya.\n"
            "- **Informasi yang ditahan:** Isi dan motif perubahan peta 2011.\n",
            encoding="utf-8"
        )

    def tearDown(self):
        self.tmp.cleanup()

    # --- Pengujian Bawaan & Struktural ---

    def test_combined_blueprint_split(self):
        (self.story / "blueprint/chapter-002-to-003.md").write_text(
            "## Bab 2 — Two\nIsi dua\n## Bab 3 — Three\nIsi tiga\n", encoding="utf-8")
        self.assertIn(2, blueprints(self.story))
        self.assertIn(3, blueprints(self.story))

    def test_audit_detects_missing_blueprint(self):
        found = deterministic_audit(self.story)
        self.assertTrue(any(x[1] == "BLUEPRINT_MISSING" and "Bab 2" in x[2] for x in found))

    def test_audit_detects_duplicate_outline_number(self):
        (self.story / "04-story-outline.md").write_text("| 1 | One |\n| 1 | Duplicate |\n", encoding="utf-8")
        found = deterministic_audit(self.story)
        self.assertTrue(any(x[1] == "DUPLICATE_OUTLINE_NUMBER" for x in found))

    def test_chapter_numbers(self):
        self.assertEqual(chapter_numbers(self.story), [1, 2])

    def test_unversioned_continuity_temporal_warning(self):
        (self.story / "continuity").mkdir(parents=True, exist_ok=True)
        (self.story / "continuity/timeline.md").write_text("Global timeline", encoding="utf-8")
        mem = build_memory(self.story, before_chapter=1)
        self.assertIn("PERINGATAN KONTINUITAS: Berkas tanpa nomor bab", mem)

    def test_source_conflicts_flagged(self):
        (self.story / "blueprint/chapter-002.md").write_text("# Blueprint Bab 2\n", encoding="utf-8")
        text = build_context(self.story, 2)
        self.assertIn("PERINGATAN KONFLIK SUMBER", text)
        self.assertIn("Naskah Bab 1 belum tersedia", text)
        self.assertIn("State Update Bab 1 belum tersedia", text)

    # --- 12 Skenario Pengujian Validasi Semantik Tahap 3B ---

    def test_1_salma_knowledge_not_attributed_to_dito(self):
        """1. Fakta yang diketahui Salma tidak otomatis dianggap diketahui Dito."""
        text = build_context(self.story, 1)
        dito_start = text.find("#### Dito")
        dito_end = text.find("#### Koordinator proyek")
        dito_section = text[dito_start:dito_end]
        self.assertIn("Dito tahu catatan lapangan", dito_section)
        self.assertIn("Dito baru tahu nama itu punya hubungan pribadi", dito_section)
        self.assertNotIn("Salma tahu hasil surveinya", dito_section)
        self.assertNotIn("Salma tahu Hadi ayahnya", dito_section)

    def test_2_yuni_knowledge_isolated_from_salma(self):
        """2. Fakta yang diketahui Yuni tidak otomatis dianggap diketahui Salma."""
        text = build_context(self.story, 1)
        salma_start = text.find("#### Salma")
        salma_end = text.find("#### Dito")
        salma_section = text[salma_start:salma_end]
        # Salma's knowledge section must NOT contain Yuni's private knowledge
        self.assertNotIn("Hadi pernah berjanji memperbaiki catatan", salma_section)
        # Yuni's section must have explicit isolation boundary
        self.assertIn("#### Yuni — 56 (Tidak Hadir di Bab Ini)", text)
        self.assertIn("PENGETAHUAN YUNI INI TIDAK DIKETAHUI OLEH KARAKTER HADIR", text)

    def test_3_reader_withheld_not_conflated_with_character_knowledge(self):
        """3. Informasi yang ditahan dari pembaca tidak otomatis berarti tokoh POV juga tidak mengetahuinya."""
        text = build_context(self.story, 1)
        reader_section_idx = text.find("## 5. BATAS INFORMASI PEMBACA BAB 1")
        reader_section = text[reader_section_idx:]
        # The withheld info must appear in Reader Withheld
        self.assertIn("Alasan Salma yakin ada rumah di balik tembok ditahan.", reader_section)
        # But must NOT be listed under Salma's unknown facts
        salma_start = text.find("#### Salma")
        salma_end = text.find("#### Dito")
        salma_section = text[salma_start:salma_end]
        self.assertNotIn("Alasan Salma yakin ada rumah di balik tembok ditahan", salma_section)

    def test_4_author_secrets_not_character_facts(self):
        """4. Rahasia penulis tidak muncul sebagai fakta yang diketahui karakter."""
        (self.story / "05-decision-log.md").write_text(
            "## D-001 — Motif perubahan peta 2011\nHadi bermaksud menunda pengosongan tanpa suap.\n",
            encoding="utf-8"
        )
        text = build_context(self.story, 1)
        salma_start = text.find("#### Salma")
        salma_end = text.find("#### Dito")
        salma_section = text[salma_start:salma_end]
        dito_start = text.find("#### Dito")
        dito_end = text.find("#### Koordinator proyek")
        dito_section = text[dito_start:dito_end]
        # Secret must not be in character known facts
        self.assertNotIn("Hadi bermaksud menunda pengosongan tanpa suap", salma_section)
        self.assertNotIn("Hadi bermaksud menunda pengosongan tanpa suap", dito_section)
        # But MUST be in Author Macro Knowledge & Reader Author Secrets
        self.assertIn("INFORMASI INI HANYA UNTUK PENULIS (AUTHOR MACRO KNOWLEDGE)", text)
        self.assertIn("Hadi bermaksud menunda pengosongan tanpa suap", text)

    def test_5_suspicions_not_promoted_to_facts(self):
        """5. Dugaan karakter tidak dinaikkan menjadi fakta."""
        (self.story / "blueprint/chapter-001.md").write_text(
            "# Blueprint Bab 1\n\n"
            "## Adegan 1 — Rapat\n"
            "- **Tokoh hadir:** Salma, Dito\n"
            "- **Yang diketahui tokoh:** Salma curiga dokumen sengaja dihilangkan; Dito menduga ada kesalahan input.\n",
            encoding="utf-8"
        )
        text = build_context(self.story, 1)
        salma_start = text.find("#### Salma")
        salma_end = text.find("#### Dito")
        salma_section = text[salma_start:salma_end]
        # Salma's suspicion must be under "Fakta yang diduga", NOT under "Fakta yang diketahui"
        self.assertIn("- **Fakta yang diduga:**", salma_section)
        self.assertIn("Salma curiga dokumen sengaja dihilangkan", salma_section)
        # Under known facts, it should be marked as undetermined
        fakta_diketahui_part = salma_section.split("- **Fakta yang diduga:**")[0]
        self.assertIn("(Belum ditentukan dalam blueprint)", fakta_diketahui_part)

    def test_6_missing_info_marked_as_undetermined(self):
        """6. Informasi yang tidak tersedia ditandai sebagai belum ditentukan."""
        text = build_context(self.story, 1)
        # Dito has no suspected or misunderstood facts in sample chapter 1
        dito_start = text.find("#### Dito")
        dito_end = text.find("#### Koordinator proyek")
        dito_section = text[dito_start:dito_end]
        self.assertIn("- **Fakta yang diduga:**\n  - *(Belum ditentukan dalam blueprint)*", dito_section)
        self.assertIn("- **Fakta yang disalahpahami:**\n  - *(Belum ditentukan dalam blueprint)*", dito_section)

    def test_7_scenes_separated_with_identity(self):
        """7. Informasi dari adegan berbeda tidak tercampur."""
        text = build_context(self.story, 1)
        salma_start = text.find("#### Salma")
        salma_end = text.find("#### Dito")
        salma_section = text[salma_start:salma_end]
        # Must retain scene identity tags
        self.assertIn("Adegan 1 — Peta final:", salma_section)
        self.assertIn("Adegan 2 — Nama di kolom pemeriksa:", salma_section)

    def test_8_present_characters_not_duplicated(self):
        """8. Karakter yang hadir tidak terduplikasi."""
        text = build_context(self.story, 1)
        sec4_idx = text.find("## 4. BATAS PENGETAHUAN SETIAP KARAKTER BAB 1")
        sec4_text = text[sec4_idx:text.find("### B. Karakter yang Tidak Hadir")]
        self.assertEqual(sec4_text.count("#### Salma"), 1)
        self.assertEqual(sec4_text.count("#### Dito"), 1)

    def test_9_combined_blueprint_processing(self):
        """9. Blueprint gabungan tetap bisa diproses."""
        (self.story / "blueprint/chapter-002-to-003.md").write_text(
            "## Bab 2 — Dua\n\n"
            "### Adegan 1 — Lapangan\n"
            "- **Batas pengetahuan:** Salma tahu batas gang; Dimas curiga pendataan.\n"
            "### Adegan 2 — Pulang\n"
            "- **Batas pengetahuan:** Salma belum tahu riwayat lengkap.\n\n"
            "## Bab 3 — Tiga\n\n"
            "### Adegan 1 — Arsip\n"
            "- **Batas pengetahuan:** Dito memeriksa buku.\n",
            encoding="utf-8"
        )
        text = build_context(self.story, 2)
        self.assertIn("PAKET KONTEKS BAB 002", text)
        self.assertIn("## 4. BATAS PENGETAHUAN SETIAP KARAKTER BAB 2", text)
        self.assertIn("Salma tahu batas gang", text)

    def test_10_context_generation_ch1_and_ch2(self):
        """10. Pembuatan konteks Bab 1 dan Bab 2 tetap berjalan."""
        (self.story / "blueprint/chapter-002.md").write_text(
            "# Blueprint Bab 2\n\n"
            "## Adegan 1 — Briefing\n"
            "- **Tokoh hadir:** Salma, Dito\n"
            "- **Yang diketahui tokoh:** Salma dan Dito tahu tugas survei.\n",
            encoding="utf-8"
        )
        (self.story / "manuscript/chapter-001.md").write_text("Prosa bab 1 selesai.", encoding="utf-8")
        (self.story / "state-updates/chapter-001.md").write_text("State bab 1 terekam.", encoding="utf-8")
        text1 = build_context(self.story, 1, rewrite=True)
        text2 = build_context(self.story, 2)
        self.assertIn("PAKET KONTEKS BAB 001", text1)
        self.assertIn("PAKET KONTEKS BAB 002", text2)
        self.assertIn("Prosa bab 1 selesai.", text2)
        self.assertIn("State bab 1 terekam.", text2)

    def test_11_future_state_updates_excluded(self):
        """11. State Update masa depan tetap tidak masuk ke konteks."""
        (self.story / "state-updates/chapter-002.md").write_text("Rahasia bab dua yang belum terjadi", encoding="utf-8")
        text = build_context(self.story, 1)
        self.assertNotIn("Rahasia bab dua yang belum terjadi", text)

    def test_12_file_overwrite_protection(self):
        """12. Perlindungan file yang sudah ada tetap berfungsi."""
        (self.story / "manuscript/chapter-001.md").write_text("Naskah ada", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            build_context(self.story, 1, rewrite=False)
        text_rewrite = build_context(self.story, 1, rewrite=True)
        self.assertIn("Mode: REWRITE", text_rewrite)


if __name__ == "__main__":
    unittest.main()
