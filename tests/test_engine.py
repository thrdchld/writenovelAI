import tempfile
import unittest
from pathlib import Path
from novel_engine.project import (
    blueprints,
    chapter_numbers,
    build_context,
    build_memory,
    detect_source_conflicts,
    manuscript,
    state_update,
    read,
)
from novel_engine.audit import deterministic_audit


def setup_mock_story(root: Path) -> Path:
    """Setup legacy mock story fixture for Tahap 3B regression testing."""
    story = root / "mock_story"
    (story / "blueprint").mkdir(parents=True)
    (story / "manuscript").mkdir()
    (story / "state-updates").mkdir()
    (story / "04-story-outline.md").write_text("| 1 | One |\n| 2 | Two |\n", encoding="utf-8")
    (story / "02-characters.md").write_text(
        "# Karakter\n\n"
        "## Salma — 29\nTeknisi pemetaan teliti.\n\n"
        "## Dito — 32\nRekan kerja survei berorientasi prosedur.\n\n"
        "## Yuni — 56\nIbu Salma. Mengetahui Hadi pernah berjanji memperbaiki catatan tiga rumah setelah banjir 2011 dan memilih diam.\n",
        encoding="utf-8"
    )
    (story / "blueprint/chapter-001.md").write_text(
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
    return story


def setup_story_a(root: Path) -> Path:
    """Setup Story A: Realistic Mystery / Forensic Audit."""
    story = root / "story_a_mystery"
    (story / "blueprint").mkdir(parents=True)
    (story / "manuscript").mkdir()
    (story / "state-updates").mkdir()

    (story / "00-premise.md").write_text(
        "# Premis Cerita A\nAudit forensik menemukan selisih kas mencurigakan di firma konsultan finansial.\n",
        encoding="utf-8"
    )
    (story / "01-concept.md").write_text(
        "# Konsep Cerita A\n\n## Mekanisme misteri\nPenggelapan dilakukan melalui akun yayasan fiktif oleh direktur keuangan.\n\n## Akhir yang dituju\nBrankas lama dibuka dan laporan diserahkan ke kurator independen.\n",
        encoding="utf-8"
    )
    (story / "02-characters.md").write_text(
        "# Karakter Cerita A\n\n"
        "## Arya Pratama — 34\n"
        "Detektif swasta spesialis audit forensik. Teliti dan selalu memeriksa dokumen fisik.\n\n"
        "## Maya Indah — 28\n"
        "Akuntan forensik rekan kerja Arya. Ahli rekonsiliasi data digital.\n\n"
        "## Kepala Cabang — 52\n"
        "Pimpinan kantor cabang yang memprioritaskan ketenangan operasional.\n\n"
        "## Hendra Kusuma — 45\n"
        "Pustakawan firma yang pendiam dan takut ketinggian. Ia berjanji pada mendiang ayahnya untuk bekerja jujur. Rekan kantor mengetahui bahwa ia selalu datang tepat waktu.\n\n"
        "## Budi Santoso — 60\n"
        "Mantan kepala gudang. Paman Maya.\n"
        "- **Rahasia:** Menggelapkan dana kas kecil yayasan sebesar 50 juta rupiah.\n"
        "- **Catatan Ambigu:** Memilih diam saat diinterogasi karena takut diancam komplotan penggelapan.\n",
        encoding="utf-8"
    )
    (story / "04-story-outline.md").write_text(
        "| 1 | Selisih Kas |\n| 2 | Verifikasi Dokumen |\n",
        encoding="utf-8"
    )
    (story / "05-decision-log.md").write_text(
        "# Decision Log Cerita A\n\n"
        "## D-001 — Aliran dana ke rekening luar negeri\n"
        "- **Status:** KANON\n"
        "- **Klasifikasi:** Rahasia Penulis\n"
        "- **Keputusan:** Dana penggelapan dialirkan ke yayasan fiktif oleh direktur keuangan tanpa sepengetahuan dewan pengawas.\n"
        "- **Dampak:** Bukti transfer disimpan di brankas arsip lama.\n\n"
        "## D-002 — Prosedur Audit Cabang\n"
        "- **Status:** KANON\n"
        "- **Keputusan:** Verifikasi fisik brankas dilakukan setiap triwulan bersama tim audit eksternal.\n",
        encoding="utf-8"
    )
    (story / "blueprint/chapter-001.md").write_text(
        "# Blueprint Bab 1 — Selisih Kas\n\n"
        "## Adegan 1 — Kantor Firma\n"
        "- **Tokoh hadir:** Arya Pratama, Maya Indah, Kepala Cabang\n"
        "- **Yang diketahui tokoh:** Arya tahu selisih laporan kas; Maya tahu kode sandi berkas; kepala cabang hanya tahu jadwal audit.\n"
        "- **Yang diketahui pembaca:** Pembaca tahu ada manipulasi data kas, belum tahu siapa dalangnya.\n"
        "- **Informasi yang ditahan:** Alasan Arya mencurigai keterlibatan direktur ditahan dari pembaca.\n\n"
        "## Adegan 2 — Ruang Arsip\n"
        "- **Tokoh hadir:** Arya Pratama, Maya Indah\n"
        "- **Yang diketahui tokoh:** Arya mencurigai cap stempel palsu; Maya menduga berkas sengaja diganti.\n"
        "- **Yang diketahui pembaca:** Pembaca melihat paraf mencurigakan di lembar audit.\n"
        "- **Informasi yang ditahan:** Nomor rekening yayasan fiktif belum diungkap.\n",
        encoding="utf-8"
    )
    (story / "blueprint/chapter-002.md").write_text(
        "# Blueprint Bab 2 — Verifikasi Dokumen\n\n"
        "## Adegan 1 — Wawancara Saksi\n"
        "- **Tokoh hadir:** Arya Pratama, Maya Indah\n"
        "- **Yang diketahui tokoh:** Arya dan Maya tahu waktu pengiriman berkas fisik.\n"
        "- **Yang diketahui pembaca:** Pembaca mengetahui jadwal kurir arsip.\n"
        "- **Informasi yang ditahan:** Isi percakapan telepon kurir ditahan.\n",
        encoding="utf-8"
    )
    return story


def setup_story_b(root: Path) -> Path:
    """Setup Story B: Family Drama / Fantasy / Royal Court."""
    story = root / "story_b_fantasy"
    (story / "blueprint").mkdir(parents=True)
    (story / "manuscript").mkdir()
    (story / "state-updates").mkdir()

    (story / "00-premise.md").write_text(
        "# Premis Cerita B\nPerebutan pengaruh takhta di kerajaan timur saat segel magis kuno mulai retak.\n",
        encoding="utf-8"
    )
    (story / "01-concept.md").write_text(
        "# Konsep Cerita B\n\n## Mekanisme misteri\nSegel naga retak karena kutukan sumpah darah garis keturunan raja pertama.\n\n## Akhir yang dituju\nSegel diperbarui melalui pengorbanan pusaka leluhur tanpa perang saudara.\n",
        encoding="utf-8"
    )
    (story / "02-characters.md").write_text(
        "# Karakter Cerita B\n\n"
        "## Putri Lyra — 19\n"
        "Pewaris takhta kerajaan timur. Menguasai sihir pelindung dasar.\n\n"
        "## Pangeran Arthur — 24\n"
        "Kakak tiri Lyra. Komandan ksatria kerajaan.\n\n"
        "## Arthur Pendragon — 50\n"
        "Ksatria legendaris pengawal raja. Menguasai pedang pusaka kerajaan.\n\n"
        "## Penyihir Alden — 65\n"
        "Penasihat sihir istana. Guru Lyra.\n"
        "- **Rahasia:** Mengetahui kutukan sumpah darah segel naga.\n"
        "- **Catatan Ambigu:** Memilih diam demi mencegah perang saudara.\n",
        encoding="utf-8"
    )
    (story / "04-story-outline.md").write_text(
        "| 1 | Perjamuan Malam |\n| 2 | Menara Barat |\n",
        encoding="utf-8"
    )
    (story / "05-decision-log.md").write_text(
        "# Decision Log Cerita B\n\n"
        "## D-001 — Sumpah darah segel naga\n"
        "- **Status:** KANON\n"
        "- **Klasifikasi:** Rahasia Penulis\n"
        "- **Keputusan:** Segel naga di bawah kastel retak bukan karena sihir gelap musuh melainkan akibat kutukan sumpah darah raja pertama.\n"
        "- **Dampak:** Hanya darah keturunan sah yang bisa menstabilkan segel.\n\n"
        "## D-002 — Pertahanan Gerbang Timur\n"
        "- **Status:** KANON\n"
        "- **Keputusan:** Pasukan tombak ditempatkan di gerbang timur selama festival.\n",
        encoding="utf-8"
    )
    (story / "blueprint/chapter-001.md").write_text(
        "# Blueprint Bab 1 — Perjamuan Malam\n\n"
        "## Adegan 1 — Balairung Utama\n"
        "- **Tokoh hadir:** Putri Lyra, Pangeran Arthur, Arthur Pendragon\n"
        "- **Yang diketahui tokoh:** Pangeran Arthur mencurigai racun pada piala perjamuan; Arthur Pendragon memegang pedang pusaka; Lyra tahu mantra pelindung dasar.\n"
        "- **Yang diketahui pembaca:** Pembaca melihat piala bergetar saat upacara perjamuan.\n"
        "- **Informasi yang ditahan:** Alasan Lyra menyembunyikan jimat leluhur ditahan dari pembaca.\n\n"
        "## Adegan 2 — Lorong Menara\n"
        "- **Tokoh hadir:** Putri Lyra, Pangeran Arthur\n"
        "- **Yang diketahui tokoh:** Pangeran Arthur menduga ada penyusup di istana; Lyra belum tahu arti getaran segel.\n"
        "- **Yang diketahui pembaca:** Suara dengung magis terdengar dari ruang bawah tanah.\n"
        "- **Informasi yang ditahan:** Lokasi pintu segel naga dirahasiakan.\n",
        encoding="utf-8"
    )
    (story / "blueprint/chapter-002.md").write_text(
        "# Blueprint Bab 2 — Menara Barat\n\n"
        "## Adegan 1 — Ruang Buku Terlarang\n"
        "- **Tokoh hadir:** Putri Lyra, Arthur Pendragon\n"
        "- **Yang diketahui tokoh:** Lyra dan Pendragon memeriksa naskah kuno segel.\n"
        "- **Yang diketahui pembaca:** Lambang segel naga cocok dengan pedang pusaka.\n"
        "- **Informasi yang ditahan:** Bab terakhir buku terlarang telah disobek.\n",
        encoding="utf-8"
    )
    return story


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.mock_story = setup_mock_story(self.root)
        self.story_a = setup_story_a(self.root)
        self.story_b = setup_story_b(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    # ==========================================================
    # 1. Pengujian Bawaan & Struktural Dasar Engine
    # ==========================================================

    def test_combined_blueprint_split(self):
        (self.story_a / "blueprint/chapter-002-to-003.md").write_text(
            "## Bab 2 — Two\nIsi dua\n## Bab 3 — Three\nIsi tiga\n", encoding="utf-8"
        )
        self.assertIn(2, blueprints(self.story_a))
        self.assertIn(3, blueprints(self.story_a))

    def test_audit_detects_missing_blueprint(self):
        (self.story_a / "blueprint/chapter-002.md").unlink()
        found = deterministic_audit(self.story_a)
        self.assertTrue(any(x[1] == "BLUEPRINT_MISSING" and "Bab 2" in x[2] for x in found))

    def test_audit_detects_duplicate_outline_number(self):
        (self.story_a / "04-story-outline.md").write_text("| 1 | One |\n| 1 | Duplicate |\n", encoding="utf-8")
        found = deterministic_audit(self.story_a)
        self.assertTrue(any(x[1] == "DUPLICATE_OUTLINE_NUMBER" for x in found))

    def test_chapter_numbers(self):
        self.assertEqual(chapter_numbers(self.story_a), [1, 2])

    def test_unversioned_continuity_temporal_warning(self):
        (self.story_a / "continuity").mkdir(parents=True, exist_ok=True)
        (self.story_a / "continuity/timeline.md").write_text("Global timeline", encoding="utf-8")
        mem = build_memory(self.story_a, before_chapter=1)
        self.assertIn("PERINGATAN KONTINUITAS: Berkas tanpa nomor bab", mem)

    def test_source_conflicts_flagged(self):
        text = build_context(self.story_a, 2)
        self.assertIn("PERINGATAN KONFLIK SUMBER", text)
        self.assertIn("Naskah Bab 1 belum tersedia", text)
        self.assertIn("State Update Bab 1 belum tersedia", text)

    # ==========================================================
    # 2. Restored Regression Tests Tahap 3B (Mock Fixture)
    # ==========================================================

    def test_r01_salma_knowledge_not_attributed_to_dito(self):
        """R1. Fakta yang diketahui Salma tidak otomatis dianggap diketahui Dito."""
        text = build_context(self.mock_story, 1)
        dito_start = text.find("#### Dito")
        dito_end = text.find("#### Koordinator proyek")
        dito_section = text[dito_start:dito_end]
        self.assertIn("Dito tahu catatan lapangan", dito_section)
        self.assertIn("Dito baru tahu nama itu punya hubungan pribadi", dito_section)
        self.assertNotIn("Salma tahu hasil surveinya", dito_section)
        self.assertNotIn("Salma tahu Hadi ayahnya", dito_section)

    def test_r02_yuni_knowledge_isolated_from_salma(self):
        """R2. Fakta yang diketahui Yuni tidak otomatis dianggap diketahui Salma."""
        text = build_context(self.mock_story, 1)
        salma_start = text.find("#### Salma")
        salma_end = text.find("#### Dito")
        salma_section = text[salma_start:salma_end]
        self.assertNotIn("Hadi pernah berjanji memperbaiki catatan", salma_section)

    def test_r03_reader_withheld_not_conflated_with_character_knowledge(self):
        """R3. Informasi yang ditahan dari pembaca tidak otomatis menjadi hal yang belum diketahui karakter."""
        text = build_context(self.mock_story, 1)
        reader_section = text[text.find("## 5. BATAS INFORMASI PEMBACA BAB 1"):]
        self.assertIn("Alasan Salma yakin ada rumah di balik tembok ditahan", reader_section)

    def test_r04_salma_suspicions_not_elevated_to_known_facts(self):
        """R4. Dugaan Salma tidak dinaikkan statusnya menjadi fakta kanon."""
        (self.mock_story / "blueprint/chapter-001.md").write_text(
            "# Blueprint Bab 1\n\n"
            "## Adegan 1 — Peta final\n"
            "- **Tokoh hadir:** Salma, Dito\n"
            "- **Yang diketahui tokoh:** Salma curiga dokumen sengaja dihilangkan; Dito tahu catatan lapangan.\n",
            encoding="utf-8"
        )
        text = build_context(self.mock_story, 1)
        salma_start = text.find("#### Salma")
        salma_end = text.find("#### Dito")
        salma_section = text[salma_start:salma_end]
        self.assertIn("- **Fakta yang diduga:**", salma_section)
        self.assertIn("Salma curiga dokumen sengaja dihilangkan", salma_section)
        fakta_diketahui_part = salma_section.split("- **Fakta yang diduga:**")[0]
        self.assertIn("(Belum ditentukan dalam blueprint)", fakta_diketahui_part)

    def test_r05_suspected_facts_categorized_correctly(self):
        """R5. Fakta dugaan dikategorikan ke daftar dugaan."""
        (self.mock_story / "blueprint/chapter-001.md").write_text(
            "# Blueprint Bab 1\n\n"
            "## Adegan 1 — Ruang rapat\n"
            "- **Tokoh hadir:** Salma\n"
            "- **Yang diketahui tokoh:** Salma menduga ada berkas lain yang disembunyikan.\n",
            encoding="utf-8"
        )
        text = build_context(self.mock_story, 1)
        salma_sec = text[text.find("#### Salma"):text.find("### B. Karakter yang Tidak Hadir")]
        self.assertIn("- **Fakta yang diduga:**", salma_sec)
        self.assertIn("Salma menduga ada berkas lain yang disembunyikan", salma_sec)

    def test_r06_missing_info_marked_as_undetermined(self):
        """R6. Informasi yang tidak tersedia ditandai sebagai belum ditentukan."""
        text = build_context(self.mock_story, 1)
        dito_start = text.find("#### Dito")
        dito_end = text.find("#### Koordinator proyek")
        dito_section = text[dito_start:dito_end]
        self.assertIn("- **Fakta yang diduga:**\n  - *(Belum ditentukan dalam blueprint)*", dito_section)
        self.assertIn("- **Fakta yang disalahpahami:**\n  - *(Belum ditentukan dalam blueprint)*", dito_section)

    def test_r07_scenes_separated_with_identity(self):
        """R7. Informasi dari adegan berbeda tidak tercampur dan mencantumkan judul adegan."""
        text = build_context(self.mock_story, 1)
        salma_start = text.find("#### Salma")
        salma_end = text.find("#### Dito")
        salma_section = text[salma_start:salma_end]
        self.assertIn("Adegan 1 — Peta final:", salma_section)
        self.assertIn("Adegan 2 — Nama di kolom pemeriksa:", salma_section)

    def test_r08_present_characters_not_duplicated(self):
        """R8. Karakter yang hadir tidak terduplikasi."""
        text = build_context(self.mock_story, 1)
        sec4_idx = text.find("## 4. BATAS PENGETAHUAN SETIAP KARAKTER BAB 1")
        sec4_text = text[sec4_idx:text.find("### B. Karakter yang Tidak Hadir")]
        self.assertEqual(sec4_text.count("#### Salma"), 1)
        self.assertEqual(sec4_text.count("#### Dito"), 1)

    def test_r09_combined_blueprint_processing_legacy(self):
        """R9. Blueprint gabungan tetap bisa diproses pada cerita legacy."""
        (self.mock_story / "blueprint/chapter-002-to-003.md").write_text(
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
        text = build_context(self.mock_story, 2)
        self.assertIn("PAKET KONTEKS BAB 002", text)
        self.assertIn("## 4. BATAS PENGETAHUAN SETIAP KARAKTER BAB 2", text)
        self.assertIn("Salma tahu batas gang", text)

    def test_r10_context_generation_ch1_and_ch2_legacy(self):
        """R10. Pembuatan konteks Bab 1 dan Bab 2 tetap berjalan pada cerita legacy."""
        (self.mock_story / "blueprint/chapter-002.md").write_text(
            "# Blueprint Bab 2\n\n"
            "## Adegan 1 — Briefing\n"
            "- **Tokoh hadir:** Salma, Dito\n"
            "- **Yang diketahui tokoh:** Salma dan Dito tahu tugas survei.\n",
            encoding="utf-8"
        )
        (self.mock_story / "manuscript/chapter-001.md").write_text("Prosa bab 1 selesai.", encoding="utf-8")
        (self.mock_story / "state-updates/chapter-001.md").write_text("State bab 1 terekam.", encoding="utf-8")
        text1 = build_context(self.mock_story, 1, rewrite=True)
        text2 = build_context(self.mock_story, 2)
        self.assertIn("PAKET KONTEKS BAB 001", text1)
        self.assertIn("PAKET KONTEKS BAB 002", text2)
        self.assertIn("Prosa bab 1 selesai.", text2)
        self.assertIn("State bab 1 terekam.", text2)

    def test_r11_future_state_updates_excluded_legacy(self):
        """R11. State Update masa depan tetap tidak masuk ke konteks cerita legacy."""
        (self.mock_story / "state-updates/chapter-002.md").write_text("Rahasia bab dua yang belum terjadi", encoding="utf-8")
        text = build_context(self.mock_story, 1)
        self.assertNotIn("Rahasia bab dua yang belum terjadi", text)

    def test_r12_file_overwrite_protection_legacy(self):
        """R12. Perlindungan file yang sudah ada tetap berfungsi pada cerita legacy."""
        (self.mock_story / "manuscript/chapter-001.md").write_text("Naskah ada", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            build_context(self.mock_story, 1, rewrite=False)
        text_rewrite = build_context(self.mock_story, 1, rewrite=True)
        self.assertIn("Mode: REWRITE", text_rewrite)

    # ==========================================================
    # 3. Pengujian Lintas Cerita Tahap 3C (14 Skenario)
    # ==========================================================

    def test_01_no_cross_story_hardcoded_content(self):
        """1. Tidak ada nama atau fakta hardcoded dari cerita lain dalam konteks yang dihasilkan."""
        text_a = build_context(self.story_a, 1)
        text_b = build_context(self.story_b, 1)

        import re
        forbidden_in_a = ["Salma", "Dito", "Yuni", "Hadi", "Kenari", "drainase", "2011", "Lyra", "Arthur", "Alden"]
        for forbidden in forbidden_in_a:
            self.assertIsNone(
                re.search(rf"\b{re.escape(forbidden)}\b", text_a, re.I),
                f"Story A context leaked whole word '{forbidden}'"
            )

        forbidden_in_b = ["Salma", "Dito", "Yuni", "Hadi", "Kenari", "drainase", "2011", "Arya", "Maya", "Budi"]
        for forbidden in forbidden_in_b:
            self.assertIsNone(
                re.search(rf"\b{re.escape(forbidden)}\b", text_b, re.I),
                f"Story B context leaked whole word '{forbidden}'"
            )

    def test_02_character_knowledge_not_cross_attributed(self):
        """2. Pengetahuan Karakter A tidak diatribusikan ke Karakter B."""
        text = build_context(self.story_a, 1)

        arya_start = text.find("#### Arya Pratama")
        maya_start = text.find("#### Maya Indah")
        kepala_start = text.find("#### Kepala Cabang")
        non_present_start = text.find("### B. Karakter yang Tidak Hadir")

        arya_sec = text[arya_start:maya_start]
        maya_sec = text[maya_start:kepala_start]
        kepala_sec = text[kepala_start:non_present_start]

        self.assertIn("Arya tahu selisih laporan kas", arya_sec)
        self.assertNotIn("Maya tahu kode sandi berkas", arya_sec)
        self.assertNotIn("kepala cabang hanya tahu jadwal audit", arya_sec)

        self.assertIn("Maya tahu kode sandi berkas", maya_sec)
        self.assertNotIn("Arya tahu selisih laporan kas", maya_sec)

        self.assertIn("kepala cabang hanya tahu jadwal audit", kepala_sec)
        self.assertNotIn("Arya tahu selisih laporan kas", kepala_sec)

    def test_03_general_relationships_not_isolated_as_secrets(self):
        """3. Hubungan umum (misal orang tua-anak, rekan kerja, paman) tidak diisolasi sebagai rahasia."""
        text_a = build_context(self.story_a, 1)
        text_b = build_context(self.story_b, 1)

        self.assertIn("#### Budi Santoso — 60 (Tidak Hadir di Bab Ini)", text_a)
        self.assertIn("Profil Umum & Hubungan (Referensi Kanon):", text_a)
        self.assertIn("Mantan kepala gudang. Paman Maya.", text_a)

        self.assertIn("#### Penyihir Alden — 65 (Tidak Hadir di Bab Ini)", text_b)
        self.assertIn("Profil Umum & Hubungan (Referensi Kanon):", text_b)
        self.assertIn("Penasihat sihir istana. Guru Lyra.", text_b)

    def test_04_specific_secrets_strictly_isolated(self):
        """4. Rahasia spesifik diisolasi ketat sesuai sumber."""
        text_a = build_context(self.story_a, 1)
        text_b = build_context(self.story_b, 1)

        self.assertIn("Rahasia Pribadi (Eksplisit dari Sumber):", text_a)
        self.assertIn("Menggelapkan dana kas kecil yayasan sebesar 50 juta rupiah", text_a)
        self.assertIn("ISOLASI RAHASIA", text_a)

        arya_sec = text_a[text_a.find("#### Arya Pratama"):text_a.find("### B. Karakter yang Tidak Hadir")]
        self.assertNotIn("Menggelapkan dana kas kecil", arya_sec)

        self.assertIn("Rahasia Pribadi (Eksplisit dari Sumber):", text_b)
        self.assertIn("Mengetahui kutukan sumpah darah segel naga", text_b)

    def test_05_reader_withheld_not_conflated_with_character_knowledge(self):
        """5. Informasi yang ditahan dari pembaca tidak otomatis membuat tokoh POV tidak tahu."""
        text = build_context(self.story_a, 1)
        reader_sec = text[text.find("## 5. BATAS INFORMASI PEMBACA BAB 1"):]

        self.assertIn("Alasan Arya mencurigai keterlibatan direktur ditahan dari pembaca", reader_sec)

        arya_sec = text[text.find("#### Arya Pratama"):text.find("#### Maya Indah")]
        self.assertNotIn("Alasan Arya mencurigai keterlibatan direktur ditahan", arya_sec)

    def test_06_author_secrets_dynamically_available(self):
        """6. Rahasia penulis eksplisit tetap tersedia secara dinamis."""
        text_a = build_context(self.story_a, 1)
        text_b = build_context(self.story_b, 1)

        self.assertIn("D-001 — Aliran dana ke rekening luar negeri", text_a)
        sec5_a = text_a[text_a.find("### Rahasia yang HANYA DIKETAHUI PENULIS (Author-Only Secrets):"):]
        self.assertIn("Aliran dana ke rekening luar negeri", sec5_a)

        self.assertIn("D-001 — Sumpah darah segel naga", text_b)
        sec5_b = text_b[text_b.find("### Rahasia yang HANYA DIKETAHUI PENULIS (Author-Only Secrets):"):]
        self.assertIn("Sumpah darah segel naga", sec5_b)

    def test_07_missing_info_marked_as_undetermined(self):
        """7. Informasi yang hilang ditandai sebagai '(Belum ditentukan dalam blueprint)'."""
        text = build_context(self.story_a, 1)
        kepala_sec = text[text.find("#### Kepala Cabang"):text.find("### B. Karakter yang Tidak Hadir")]

        self.assertIn("- **Fakta yang diduga:**\n  - *(Belum ditentukan dalam blueprint)*", kepala_sec)
        self.assertIn("- **Fakta yang disalahpahami:**\n  - *(Belum ditentukan dalam blueprint)*", kepala_sec)
        self.assertIn("- **Fakta yang belum diketahui:**\n  - *(Belum ditentukan dalam blueprint)*", kepala_sec)

    def test_08_scene_knowledge_separated_with_identity(self):
        """8. Pengetahuan per adegan tetap terpisah dengan identitas adegan."""
        text = build_context(self.story_a, 1)
        arya_sec = text[text.find("#### Arya Pratama"):text.find("#### Maya Indah")]

        self.assertIn("Adegan 1 — Kantor Firma:", arya_sec)
        self.assertIn("Arya tahu selisih laporan kas", arya_sec)
        self.assertIn("Adegan 2 — Ruang Arsip:", arya_sec)
        self.assertIn("Arya mencurigai cap stempel palsu", arya_sec)

    def test_09_combined_blueprint_processing(self):
        """9. Blueprint gabungan diproses dengan bersih."""
        (self.story_a / "blueprint/chapter-002.md").unlink()
        (self.story_a / "blueprint/chapter-002-to-003.md").write_text(
            "## Bab 2 — Verifikasi Dokumen\n\n"
            "### Adegan 1 — Ruang Rapat\n"
            "- **Tokoh hadir:** Arya Pratama, Maya Indah\n"
            "- **Yang diketahui tokoh:** Arya dan Maya tahu tanggal berkas.\n\n"
            "## Bab 3 — Kunjungan Gudang\n\n"
            "### Adegan 1 — Gerbang\n"
            "- **Yang diketahui tokoh:** Arya memeriksa gembok.\n",
            encoding="utf-8"
        )
        text = build_context(self.story_a, 2)
        self.assertIn("PAKET KONTEKS BAB 002", text)
        self.assertIn("Arya dan Maya tahu tanggal berkas", text)
        self.assertNotIn("Arya memeriksa gembok", text)

    def test_10_future_state_updates_excluded(self):
        """10. State Update masa depan tidak masuk ke bab sebelumnya."""
        (self.story_a / "state-updates/chapter-002.md").write_text(
            "Peristiwa masa depan Bab 2 yang rahasia.", encoding="utf-8"
        )
        text = build_context(self.story_a, 1)
        self.assertNotIn("Peristiwa masa depan Bab 2 yang rahasia.", text)

    def test_11_file_overwrite_protection(self):
        """11. Naskah dan State Update yang ada dilindungi dari penimpaan tanpa rewrite=True."""
        (self.story_a / "manuscript/chapter-001.md").write_text("Prosa bab 1 ada.", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            build_context(self.story_a, 1, rewrite=False)
        text = build_context(self.story_a, 1, rewrite=True)
        self.assertIn("Mode: REWRITE", text)

    def test_12_orphan_state_update_detected(self):
        """12. Orphan State Update terdeteksi dan dilindungi."""
        (self.story_a / "state-updates/chapter-001.md").write_text("State ada tanpa naskah.", encoding="utf-8")
        conflicts = detect_source_conflicts(self.story_a, 1)
        self.assertTrue(any("orphan state" in c.lower() for c in conflicts))

    def test_13_context_generation_ch1_and_ch2_both_stories(self):
        """13. Pembuatan konteks berhasil untuk Bab 1 dan Bab 2 pada kedua fixture cerita."""
        ctx_a1 = build_context(self.story_a, 1)
        self.assertIn("PAKET KONTEKS BAB 001", ctx_a1)

        (self.story_a / "manuscript/chapter-001.md").write_text("Naskah Bab 1 selesai.", encoding="utf-8")
        (self.story_a / "state-updates/chapter-001.md").write_text("State Bab 1 terekam.", encoding="utf-8")
        ctx_a2 = build_context(self.story_a, 2)
        self.assertIn("PAKET KONTEKS BAB 002", ctx_a2)
        self.assertIn("Naskah Bab 1 selesai.", ctx_a2)

        ctx_b1 = build_context(self.story_b, 1)
        self.assertIn("PAKET KONTEKS BAB 001", ctx_b1)

        (self.story_b / "manuscript/chapter-001.md").write_text("Naskah Fantasi Bab 1 selesai.", encoding="utf-8")
        (self.story_b / "state-updates/chapter-001.md").write_text("State Fantasi Bab 1 terekam.", encoding="utf-8")
        ctx_b2 = build_context(self.story_b, 2)
        self.assertIn("PAKET KONTEKS BAB 002", ctx_b2)
        self.assertIn("Naskah Fantasi Bab 1 selesai.", ctx_b2)

    def test_14_multiword_and_similar_name_attribution(self):
        """14. Penanganan nama karakter multi-kata atau mirip diatribusikan dengan akurat tanpa tabrakan."""
        text_b = build_context(self.story_b, 1)

        pangeran_start = text_b.find("#### Pangeran Arthur")
        arthur_pendragon_start = text_b.find("#### Arthur Pendragon")
        non_present_start = text_b.find("### B. Karakter yang Tidak Hadir")

        pangeran_sec = text_b[pangeran_start:arthur_pendragon_start]
        arthur_pendragon_sec = text_b[arthur_pendragon_start:non_present_start]

        self.assertIn("Pangeran Arthur mencurigai racun pada piala perjamuan", pangeran_sec)
        self.assertNotIn("Arthur Pendragon memegang pedang pusaka", pangeran_sec)

        self.assertIn("Arthur Pendragon memegang pedang pusaka", arthur_pendragon_sec)
        self.assertNotIn("Pangeran Arthur mencurigai racun", arthur_pendragon_sec)

        text_a = build_context(self.story_a, 1)
        self.assertIn("#### Kepala Cabang", text_a)
        kepala_sec = text_a[text_a.find("#### Kepala Cabang"):text_a.find("### B. Karakter yang Tidak Hadir")]
        self.assertIn("kepala cabang hanya tahu jadwal audit", kepala_sec)

    # ==========================================================
    # 4. Pengujian Baru Tahap 3D
    # ==========================================================

    def test_3d_01_canon_decisions_not_automatically_author_secrets(self):
        """3D-1: Keputusan kanon biasa tidak otomatis menjadi rahasia penulis."""
        text_a = build_context(self.story_a, 1)
        sec5 = text_a[text_a.find("## 5. BATAS INFORMASI PEMBACA BAB 1"):]

        author_secrets_part = sec5.split("### Keputusan Kanon Tanpa Klasifikasi Kerahasiaan")[0]
        # D-002 is regular canon (no secret classification); must NOT be in Author-Only Secrets
        self.assertNotIn("D-002 — Prosedur Audit Cabang", author_secrets_part)

        # D-002 must appear in Keputusan Kanon Tanpa Klasifikasi Kerahasiaan
        unclassified_part = sec5.split("### Keputusan Kanon Tanpa Klasifikasi Kerahasiaan")[1]
        self.assertIn("D-002 — Prosedur Audit Cabang", unclassified_part)
        self.assertIn("Verifikasi fisik brankas dilakukan setiap triwulan", unclassified_part)

    def test_3d_02_explicit_author_secrets_correctly_classified(self):
        """3D-2: Rahasia penulis eksplisit (bertanda Klasifikasi: Rahasia Penulis) masuk ke Author-Only Secrets."""
        text_a = build_context(self.story_a, 1)
        sec5 = text_a[text_a.find("### Rahasia yang HANYA DIKETAHUI PENULIS (Author-Only Secrets):"):]
        author_secrets_part = sec5.split("### Keputusan Kanon Tanpa Klasifikasi Kerahasiaan")[0]

        # D-001 has Klasifikasi: Rahasia Penulis
        self.assertIn("D-001 — Aliran dana ke rekening luar negeri", author_secrets_part)
        self.assertIn("Dana penggelapan dialirkan ke yayasan fiktif", author_secrets_part)

    def test_3d_03_profile_non_secret_keywords_not_misclassified(self):
        """3D-3: Kalimat profil yang memuat 'pendiam', 'takut', 'janji', 'mengetahui bahwa' tidak salah diklasifikasikan sebagai rahasia."""
        text_a = build_context(self.story_a, 1)
        self.assertIn("#### Hendra Kusuma — 45 (Tidak Hadir di Bab Ini)", text_a)

        hendra_start = text_a.find("#### Hendra Kusuma — 45")
        budi_start = text_a.find("#### Budi Santoso — 60")
        hendra_sec = text_a[hendra_start:budi_start]

        # All sentences must be under Profil Umum & Hubungan
        self.assertIn("Profil Umum & Hubungan (Referensi Kanon):", hendra_sec)
        self.assertIn("Pustakawan firma yang pendiam dan takut ketinggian.", hendra_sec)
        self.assertIn("Ia berjanji pada mendiang ayahnya untuk bekerja jujur.", hendra_sec)
        self.assertIn("Rekan kantor mengetahui bahwa ia selalu datang tepat waktu.", hendra_sec)

        # There must be NO secrets recorded for Hendra
        self.assertIn("- **Rahasia Pribadi (Eksplisit dari Sumber):** *(Tidak ada rahasia pribadi spesifik yang tercatat)*", hendra_sec)

    def test_3d_04_explicit_secret_without_keywords_classified_as_secret(self):
        """3D-4: Rahasia bertanda eksplisit tanpa kata kunci 'diam'/'takut'/'janji' berhasil dikenali sebagai rahasia."""
        text_a = build_context(self.story_a, 1)
        budi_sec = text_a[text_a.find("#### Budi Santoso — 60"):text_a.find("### C. Catatan Pengetahuan Ambigu")]

        # Budi's secret: "Menggelapkan dana kas kecil yayasan sebesar 50 juta rupiah." (no secret keywords)
        self.assertIn("- **Rahasia Pribadi (Eksplisit dari Sumber):**", budi_sec)
        self.assertIn("Menggelapkan dana kas kecil yayasan sebesar 50 juta rupiah", budi_sec)

    def test_3d_05_ambiguous_profile_sentence_labeled_for_review(self):
        """3D-5: Kalimat ambigu (tindakan memilih diam/menahan info) diberi label perlu pemeriksaan."""
        text_a = build_context(self.story_a, 1)
        budi_sec = text_a[text_a.find("#### Budi Santoso — 60"):text_a.find("### C. Catatan Pengetahuan Ambigu")]

        self.assertIn("- **Informasi Ambigu / Belum Diklasifikasikan (Perlu Pemeriksaan):**", budi_sec)
        self.assertIn("Memilih diam saat diinterogasi karena takut diancam komplotan penggelapan.", budi_sec)
        self.assertIn("INFORMASI PERLU PEMERIKSAAN", budi_sec)

    def test_3d_06_orphan_state_update_blocks_normal_write_and_preserves_other_sources(self):
        """3D-6: Kondisi orphan State Update memblokir penulisan normal tanpa rewrite=True, dan rewrite tidak merusak sumber lain."""
        # Create orphan State Update
        (self.story_a / "state-updates/chapter-001.md").write_text("State orphan Bab 1.", encoding="utf-8")

        # Must raise FileExistsError if rewrite=False (cannot proceed quietly as normal write)
        with self.assertRaises(FileExistsError):
            build_context(self.story_a, 1, rewrite=False)

        # Read original sources before rewrite
        premise_before = read(self.story_a / "00-premise.md")
        blueprint_before = read(self.story_a / "blueprint/chapter-001.md")
        outline_before = read(self.story_a / "04-story-outline.md")

        # Generate context with explicit rewrite=True
        ctx_rewrite = build_context(self.story_a, 1, rewrite=True)
        self.assertIn("Mode: REWRITE (Penyelesaian Orphan State Update)", ctx_rewrite)
        self.assertIn("Terdeteksi orphan state: State Update Bab 1", ctx_rewrite)

        # Sources must NOT be damaged or modified
        self.assertEqual(read(self.story_a / "00-premise.md"), premise_before)
        self.assertEqual(read(self.story_a / "blueprint/chapter-001.md"), blueprint_before)
        self.assertEqual(read(self.story_a / "04-story-outline.md"), outline_before)

    def test_3d_07_state_update_overwrite_protection_without_manuscript(self):
        """3D-7: State Update yang ada dilindungi dari penimpaan meskipun manuskrip belum ada."""
        (self.story_a / "state-updates/chapter-001.md").write_text("Catatan fakta ada.", encoding="utf-8")
        self.assertFalse((self.story_a / "manuscript/chapter-001.md").exists())

        # Calling without rewrite must raise FileExistsError
        with self.assertRaises(FileExistsError) as cm:
            build_context(self.story_a, 1, rewrite=False)
        self.assertIn("File target sudah ada", str(cm.exception))

    # ==========================================================
    # 5. Pengujian Baru Tahap 3E
    # ==========================================================

    def test_3e_01_decision_log_classification_rigor(self):
        """3E-1: Uji ketat klasifikasi Decision Log (Author-Only vs Karakter vs Publik vs Review)."""
        (self.story_a / "05-decision-log.md").write_text(
            "# Decision Log Uji 3E\n\n"
            "## D-010 — Rahasia Penulis Murni\n"
            "- **Status:** KANON\n"
            "- **Klasifikasi:** Rahasia Penulis\n"
            "- **Keputusan:** Hanya penulis yang tahu dalang sebenarnya adalah pejabat kementerian.\n\n"
            "## D-020 — Rahasia Milik Karakter\n"
            "- **Status:** KANON\n"
            "- **Klasifikasi:** Rahasia Karakter\n"
            "- **Pemilik Rahasia:** Maya Indah\n"
            "- **Keputusan:** Maya diam-diam menyimpan salinan kunci brankas digital.\n\n"
            "## D-030 — Rahasia Berstatus Tag Bracket [RAHASIA]\n"
            "- **Status:** KANON [RAHASIA]\n"
            "- **Keputusan:** Arya pernah diberhentikan dari kepolisian karena investigasi ilegal.\n\n"
            "## D-040 — Informasi Publik Dinyatakan Terbuka\n"
            "- **Status:** KANON\n"
            "- **Klasifikasi:** Publik\n"
            "- **Keputusan:** Kantor cabang resmi dibuka pada tahun 2015.\n\n"
            "## D-050 — Keputusan Kanon Tanpa Klasifikasi\n"
            "- **Status:** KANON\n"
            "- **Keputusan:** Format berkas audit menggunakan standar ISO.\n\n"
            "## D-060 — Klasifikasi Kosong\n"
            "- **Status:** KANON\n"
            "- **Klasifikasi:**\n"
            "- **Keputusan:** Pengarsipan digital diperbarui setiap bulan.\n\n"
            "## D-070 — Klasifikasi Bertentangan [RAHASIA PENULIS]\n"
            "- **Status:** KANON\n"
            "- **Klasifikasi:** Publik\n"
            "- **Keputusan:** Bukti fisik disembunyikan di bawah lantai ruang arsip.\n",
            encoding="utf-8"
        )
        ctx = build_context(self.story_a, 1)
        sec5 = ctx[ctx.find("## 5. BATAS INFORMASI PEMBACA BAB 1"):]

        author_sec = sec5[sec5.find("### Rahasia yang HANYA DIKETAHUI PENULIS (Author-Only Secrets):"):sec5.find("### Rahasia Karakter")]
        char_sec = sec5[sec5.find("### Rahasia Karakter dalam Dokumen Keputusan (Bukan Rahasia Penulis):"):sec5.find("### Keputusan Kanon Perlu Pemeriksaan")]
        review_sec = sec5[sec5.find("### Keputusan Kanon Perlu Pemeriksaan (Klasifikasi Kosong atau Bertentangan):"):sec5.find("### Keputusan Kanon Tanpa Klasifikasi")]
        unclassified_sec = sec5[sec5.find("### Keputusan Kanon Tanpa Klasifikasi Kerahasiaan (Status Terbuka / Belum Ditentukan):"):sec5.find("### Keputusan Kanon Publik")]
        public_sec = sec5[sec5.find("### Keputusan Kanon Publik (Informasi Terbuka):"):]

        # 1. Klasifikasi: Rahasia Penulis masuk Author-Only
        self.assertIn("D-010 — Rahasia Penulis Murni", author_sec)
        self.assertIn("pejabat kementerian", author_sec)

        # 2. Klasifikasi: Rahasia Karakter TIDAK masuk Author-Only, masuk Rahasia Karakter
        self.assertNotIn("D-020 — Rahasia Milik Karakter", author_sec)
        self.assertIn("D-020 — Rahasia Milik Karakter", char_sec)
        self.assertIn("Maya diam-diam menyimpan salinan kunci", char_sec)

        # 3. [RAHASIA] TIDAK otomatis masuk Author-Only, masuk Rahasia Karakter
        self.assertNotIn("D-030 — Rahasia Berstatus Tag Bracket", author_sec)
        self.assertIn("D-030 — Rahasia Berstatus Tag Bracket", char_sec)
        self.assertIn("Arya pernah diberhentikan dari kepolisian", char_sec)

        # 4. Klasifikasi: Publik TIDAK masuk Author-Only, masuk Publik
        self.assertNotIn("D-040 — Informasi Publik Dinyatakan Terbuka", author_sec)
        self.assertIn("D-040 — Informasi Publik Dinyatakan Terbuka", public_sec)

        # 5. Keputusan KANON tanpa klasifikasi TIDAK masuk Author-Only, masuk Belum Diklasifikasikan
        self.assertNotIn("D-050 — Keputusan Kanon Tanpa Klasifikasi", author_sec)
        self.assertIn("D-050 — Keputusan Kanon Tanpa Klasifikasi", unclassified_sec)

        # 6. Klasifikasi kosong atau bertentangan masuk ke Perlu Pemeriksaan
        self.assertIn("D-060 — Klasifikasi Kosong", review_sec)
        self.assertIn("D-070 — Klasifikasi Bertentangan", review_sec)

    def test_3e_02_character_profile_classification_cases(self):
        """3E-2: Uji klasifikasi profil karakter (Rahasia Karakter, Author-Only, Profil Umum, Unclassified, Ambigu)."""
        (self.story_a / "02-characters.md").write_text(
            "# Karakter Cerita A Uji 3E\n\n"
            "## Arya Pratama — 34\n"
            "- **Profil:** Detektif swasta spesialis audit forensik.\n\n"
            "## Maya Indah — 28\n"
            "- **Profil:** Akuntan forensik rekan kerja Arya.\n\n"
            "## Kepala Cabang — 52\n"
            "- **Profil:** Pimpinan kantor cabang.\n\n"
            "## Saksi Kunci — 40\n"
            "Profil: Ia bekerja sebagai arsiparis.\n"
            "Rahasia: Ia memindahkan dokumen sebelum audit.\n"
            "Rahasia Penulis: Ia mengetahui hasil akhir sejak awal.\n"
            "Ia menyembunyikan berkas audit di loteng.\n"
            "Ia gemar merawat kebun mawar di akhir pekan.\n"
            "- **Catatan Ambigu:** Keterangannya mengenai tanggal rapat saling bertentangan.\n",
            encoding="utf-8"
        )
        ctx = build_context(self.story_a, 1)
        saksi_sec = ctx[ctx.find("#### Saksi Kunci — 40"):ctx.find("### C. Catatan Pengetahuan Ambigu")]

        # 1. Profil: ... masuk profil umum
        self.assertIn("- **Profil Umum & Hubungan (Referensi Kanon):** Ia bekerja sebagai arsiparis.", saksi_sec)

        # 2. Rahasia: ... masuk rahasia karakter
        self.assertIn("- **Rahasia Pribadi (Eksplisit dari Sumber):**", saksi_sec)
        self.assertIn("Ia memindahkan dokumen sebelum audit.", saksi_sec)

        # 3. Rahasia Penulis: ... masuk rahasia khusus penulis profil
        self.assertIn("- **Rahasia Khusus Penulis (Author-Only dari Profil):**", saksi_sec)
        self.assertIn("Ia mengetahui hasil akhir sejak awal.", saksi_sec)

        # 4. Kalimat tanpa penanda menyembunyikan info TIDAK boleh otomatis menjadi publik
        self.assertNotIn("Ia menyembunyikan berkas audit di loteng.", saksi_sec.split("- **Rahasia")[0])

        # 5. Kalimat tanpa penanda fakta biasa TIDAK boleh otomatis dianggap diketahui semua karakter
        # Keduanya masuk ke Informasi Ambigu / Belum Diklasifikasikan
        self.assertIn("- **Informasi Ambigu / Belum Diklasifikasikan (Perlu Pemeriksaan):**", saksi_sec)
        self.assertIn("Ia menyembunyikan berkas audit di loteng. *(Belum diklasifikasikan)*", saksi_sec)
        self.assertIn("Ia gemar merawat kebun mawar di akhir pekan. *(Belum diklasifikasikan)*", saksi_sec)

        # 6. Catatan Ambigu masuk ke Perlu Pemeriksaan
        self.assertIn("Keterangannya mengenai tanggal rapat saling bertentangan. *(Perlu pemeriksaan", saksi_sec)

    def test_3e_03_secret_ownership_separated_from_access(self):
        """3E-3: Pemisahan tegas antara fakta kanon, siapa yang tahu (ownership), dan batas pembaca."""
        (self.story_a / "05-decision-log.md").write_text(
            "# Decision Log\n\n"
            "## D-001 — Rahasia Pembelian Tanah Yayasan\n"
            "- **Status:** KANON\n"
            "- **Klasifikasi:** Rahasia Karakter\n"
            "- **Pemilik Rahasia:** Maya Indah\n"
            "- **Keputusan:** Maya membeli tanah yayasan atas nama adiknya.\n",
            encoding="utf-8"
        )
        ctx = build_context(self.story_a, 1)

        # 1. Rahasia Maya (karakter hadir) tidak otomatis menjadi rahasia penulis
        sec5_author = ctx[ctx.find("### Rahasia yang HANYA DIKETAHUI PENULIS"):ctx.find("### Rahasia Karakter")]
        self.assertNotIn("Rahasia Pembelian Tanah Yayasan", sec5_author)

        # 2. Rahasia Maya tidak otomatis masuk pengetahuan Arya atau Kepala Cabang di Bab 1
        arya_sec = ctx[ctx.find("#### Arya Pratama"):ctx.find("#### Maya Indah")]
        kepala_sec = ctx[ctx.find("#### Kepala Cabang"):ctx.find("### B. Karakter yang Tidak Hadir")]
        self.assertNotIn("membeli tanah yayasan", arya_sec)
        self.assertNotIn("membeli tanah yayasan", kepala_sec)

        # 3. Informasi ditahan dari pembaca tidak membuat POV Arya otomatis tidak tahu fakta yang sah ia ketahui
        sec5_reader = ctx[ctx.find("## 5. BATAS INFORMASI PEMBACA BAB 1"):]
        self.assertIn("Alasan Arya mencurigai keterlibatan direktur ditahan dari pembaca", sec5_reader)
        self.assertIn("Arya tahu selisih laporan kas", arya_sec)

        # 4. Hubungan umum seperti keluarga tidak diisolasi sebagai rahasia
        self.assertIn("Paman Maya", ctx)
        # Rahasia karakter tetap tercatat dalam kanon keputusan di bagian rahasia karakter
        self.assertIn("### Rahasia Karakter dalam Dokumen Keputusan", ctx)
        self.assertIn("Maya membeli tanah yayasan atas nama adiknya.", ctx)


if __name__ == "__main__":
    unittest.main()
