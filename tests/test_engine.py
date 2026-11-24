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
        (self.story / "blueprint/chapter-001.md").write_text(
            "# Blueprint Bab 1 — One\n\n"
            "## Adegan 1 — Rapat\n"
            "- **Tokoh hadir:** Salma, Dito\n"
            "- **Yang diketahui tokoh:** Salma tahu hasil survei lorong.\n"
            "- **Yang diketahui pembaca:** Pembaca tahu ada perbedaan peta dan kenyataan.\n"
            "- **Informasi yang ditahan:** Motif tanda tangan ayah 2011 ditahan.\n",
            encoding="utf-8"
        )

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

    def test_audit_detects_duplicate_outline_number(self):
        (self.story / "04-story-outline.md").write_text("| 1 | One |\n| 1 | Duplicate |\n", encoding="utf-8")
        found = deterministic_audit(self.story)
        self.assertTrue(any(x[1] == "DUPLICATE_OUTLINE_NUMBER" for x in found))

    def test_context_does_not_include_future_state(self):
        (self.story / "05-decision-log.md").write_text("Canon", encoding="utf-8")
        (self.story / "state-updates/chapter-002.md").write_text("future secret", encoding="utf-8")
        text = build_context(self.story, 1)
        self.assertNotIn("future secret", text)

    def test_context_refuses_to_overwrite_orphan_state(self):
        (self.story / "05-decision-log.md").write_text("Canon", encoding="utf-8")
        (self.story / "state-updates/chapter-001.md").write_text("existing state", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            build_context(self.story, 1)

    def test_chapter_numbers(self):
        self.assertEqual(chapter_numbers(self.story), [1, 2])

    def test_context_explicit_character_knowledge_boundaries(self):
        text = build_context(self.story, 1)
        self.assertIn("## 4. BATAS PENGETAHUAN KARAKTER BAB 1", text)
        self.assertIn("Salma tahu hasil survei lorong.", text)
        self.assertIn("Motif tanda tangan ayah 2011 ditahan.", text)
        self.assertIn("Salma, Dito", text)

    def test_author_global_info_separated_from_character_knowledge(self):
        (self.story / "01-concept.md").write_text("Ayah menandatangani tanpa suap pada 2011.", encoding="utf-8")
        text = build_context(self.story, 1)
        self.assertIn("## 2. KANON DAN ARAH CERITA (PENGETAHUAN KHUSUS PENULIS)", text)
        self.assertIn("INFORMASI INI HANYA UNTUK PENULIS (AUTHOR MACRO KNOWLEDGE)", text)
        self.assertIn("Ayah menandatangani tanpa suap pada 2011.", text)
        # Ensure author macro banner appears before the character boundary section
        idx_author = text.find("## 2. KANON DAN ARAH CERITA")
        idx_char = text.find("## 4. BATAS PENGETAHUAN KARAKTER")
        self.assertTrue(idx_author < idx_char)

    def test_writing_instructions_distinguish_three_knowledge_layers(self):
        text = build_context(self.story, 1)
        self.assertIn("Pengetahuan Penulis (Author Macro Knowledge)", text)
        self.assertIn("Batas Pengetahuan Karakter (Character Knowledge)", text)
        self.assertIn("Batas Informasi Pembaca (Reader Knowledge)", text)

    def test_irrelevant_docs_excluded_from_context(self):
        text = build_context(self.story, 1)
        self.assertNotIn("AI_INSTRUCTIONS.md", text)
        self.assertNotIn("docs/02-scene-blueprint.md", text)
        self.assertNotIn("docs/03-continuity.md", text)
        self.assertNotIn("docs/06-ai-operating-contract.md", text)
        # Writing standard should be included
        self.assertIn("docs/05-writing-standard.md", text)

    def test_source_conflicts_flagged(self):
        (self.story / "blueprint/chapter-002.md").write_text("# Blueprint Bab 2\n", encoding="utf-8")
        text = build_context(self.story, 2)
        self.assertIn("PERINGATAN KONFLIK SUMBER", text)
        self.assertIn("Naskah Bab 1 belum tersedia", text)
        self.assertIn("State Update Bab 1 belum tersedia", text)

    def test_subsequent_chapter_context_generation(self):
        (self.story / "blueprint/chapter-002.md").write_text("# Blueprint Bab 2\n", encoding="utf-8")
        (self.story / "manuscript/chapter-001.md").write_text("Naskah Bab 1 yang telah ditulis.", encoding="utf-8")
        (self.story / "state-updates/chapter-001.md").write_text("Fakta Bab 1 yang telah terverifikasi.", encoding="utf-8")
        text = build_context(self.story, 2)
        self.assertIn("PAKET KONTEKS BAB 002", text)
        self.assertIn("Naskah Bab 1 yang telah ditulis.", text)
        self.assertIn("Fakta Bab 1 yang telah terverifikasi.", text)
        self.assertNotIn("PERINGATAN KONFLIK SUMBER", text)

    def test_file_overwrite_protection_and_rewrite_flag(self):
        (self.story / "manuscript/chapter-001.md").write_text("Naskah ada", encoding="utf-8")
        (self.story / "state-updates/chapter-001.md").write_text("State ada", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            build_context(self.story, 1, rewrite=False)
        text_rewrite = build_context(self.story, 1, rewrite=True)
        self.assertIn("Mode: REWRITE", text_rewrite)

    def test_unversioned_continuity_temporal_warning(self):
        (self.story / "continuity").mkdir(parents=True, exist_ok=True)
        (self.story / "continuity/timeline.md").write_text("Global timeline", encoding="utf-8")
        mem = build_memory(self.story, before_chapter=1)
        self.assertIn("PERINGATAN KONTINUITAS: Berkas tanpa nomor bab", mem)


if __name__ == "__main__":
    unittest.main()
