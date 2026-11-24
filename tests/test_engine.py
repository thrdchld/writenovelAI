import tempfile
import unittest
from pathlib import Path
from novel_engine.project import (
    blueprints,
    chapter_numbers,
    build_context,
    build_memory,
    detect_source_conflicts,
)
from novel_engine.audit import deterministic_audit


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
        "## Budi Santoso — 60\n"
        "Mantan kepala gudang. Paman Maya. Mengetahui ada catatan ganda tahun 2018 di brankas lama dan memilih diam karena diancam komplotan penggelapan.\n",
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
        "- **Keputusan:** Dana penggelapan dialirkan ke yayasan fiktif oleh direktur keuangan tanpa sepengetahuan dewan pengawas.\n"
        "- **Dampak:** Bukti transfer disimpan di brankas arsip lama.\n",
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
        "Penasihat sihir istana. Guru Lyra. Mengetahui sumpah darah segel naga dan memilih diam karena takut perang saudara pecah.\n",
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
        "- **Keputusan:** Segel naga di bawah kastel retak bukan karena sihir gelap musuh melainkan akibat kutukan sumpah darah raja pertama.\n"
        "- **Dampak:** Hanya darah keturunan sah yang bisa menstabilkan segel.\n",
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
        self.story_a = setup_story_a(self.root)
        self.story_b = setup_story_b(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    # ==========================================================
    # Pengujian Bawaan & Struktural Dasar Engine
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
    # 14 Kebutuhan Perilaku Spesifik Tahap 3C
    # ==========================================================

    def test_01_no_cross_story_hardcoded_content(self):
        """1. Tidak ada nama atau fakta hardcoded dari cerita lain dalam konteks yang dihasilkan."""
        text_a = build_context(self.story_a, 1)
        text_b = build_context(self.story_b, 1)

        import re

        # Story A must NOT contain any names or facts from Gang yang Hilang or Story B
        forbidden_in_a = ["Salma", "Dito", "Yuni", "Hadi", "Kenari", "drainase", "2011", "Lyra", "Arthur", "Alden"]
        for forbidden in forbidden_in_a:
            self.assertIsNone(
                re.search(rf"\b{re.escape(forbidden)}\b", text_a, re.I),
                f"Story A context leaked whole word '{forbidden}'"
            )

        # Story B must NOT contain any names or facts from Gang yang Hilang or Story A
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

        # Arya knows "selisih laporan kas", Maya knows "kode sandi berkas", Kepala Cabang knows "jadwal audit"
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

        # In Story A, Budi is absent. His public relation "Paman Maya" / "Mantan kepala gudang" is reference, not isolated secret
        self.assertIn("#### Budi Santoso — 60 (Tidak Hadir di Bab Ini)", text_a)
        self.assertIn("Profil Umum & Hubungan (Referensi Kanon):", text_a)
        self.assertIn("Mantan kepala gudang. Paman Maya.", text_a)

        # In Story B, Alden is absent. His relation "Guru Lyra" / "Penasihat sihir istana" is public reference
        self.assertIn("#### Penyihir Alden — 65 (Tidak Hadir di Bab Ini)", text_b)
        self.assertIn("Profil Umum & Hubungan (Referensi Kanon):", text_b)
        self.assertIn("Penasihat sihir istana. Guru Lyra.", text_b)

    def test_04_specific_secrets_strictly_isolated(self):
        """4. Rahasia spesifik diisolasi ketat sesuai sumber."""
        text_a = build_context(self.story_a, 1)
        text_b = build_context(self.story_b, 1)

        # Story A: Budi's secret
        self.assertIn("Rahasia Pribadi / Motif Tersembunyi (Isolasi Ketat):", text_a)
        self.assertIn("Mengetahui ada catatan ganda tahun 2018 di brankas lama dan memilih diam", text_a)
        self.assertIn("ISOLASI RAHASIA BUDI SANTOSO", text_a)

        # Ensure Budi's secret is NOT in present characters' knowledge
        arya_sec = text_a[text_a.find("#### Arya Pratama"):text_a.find("### B. Karakter yang Tidak Hadir")]
        self.assertNotIn("catatan ganda tahun 2018", arya_sec)

        # Story B: Alden's secret
        self.assertIn("Rahasia Pribadi / Motif Tersembunyi (Isolasi Ketat):", text_b)
        self.assertIn("Mengetahui sumpah darah segel naga dan memilih diam", text_b)
        self.assertIn("ISOLASI RAHASIA PENYIHIR ALDEN", text_b)

    def test_05_reader_withheld_not_conflated_with_character_knowledge(self):
        """5. Informasi yang ditahan dari pembaca tidak otomatis membuat tokoh POV tidak tahu."""
        text = build_context(self.story_a, 1)
        reader_sec = text[text.find("## 5. BATAS INFORMASI PEMBACA BAB 1"):]

        # Withheld info is listed in Reader Withheld
        self.assertIn("Alasan Arya mencurigai keterlibatan direktur ditahan dari pembaca", reader_sec)

        # But Arya's section does NOT list it as an unknown fact
        arya_sec = text[text.find("#### Arya Pratama"):text.find("#### Maya Indah")]
        self.assertNotIn("Alasan Arya mencurigai keterlibatan direktur ditahan", arya_sec)

    def test_06_author_secrets_dynamically_available(self):
        """6. Rahasia penulis tetap tersedia di Bagian 2 dan Bagian 5 secara dinamis."""
        text_a = build_context(self.story_a, 1)
        text_b = build_context(self.story_b, 1)

        # Story A: extracted from 05-decision-log.md
        self.assertIn("D-001 — Aliran dana ke rekening luar negeri", text_a)
        self.assertIn("Dana penggelapan dialirkan ke yayasan fiktif", text_a)
        sec5_a = text_a[text_a.find("### Rahasia yang HANYA DIKETAHUI PENULIS (Author-Only Secrets):"):]
        self.assertIn("Aliran dana ke rekening luar negeri", sec5_a)

        # Story B: extracted dynamically
        self.assertIn("D-001 — Sumpah darah segel naga", text_b)
        self.assertIn("Segel naga di bawah kastel retak bukan karena sihir gelap", text_b)
        sec5_b = text_b[text_b.find("### Rahasia yang HANYA DIKETAHUI PENULIS (Author-Only Secrets):"):]
        self.assertIn("Sumpah darah segel naga", sec5_b)

    def test_07_missing_info_marked_as_undetermined(self):
        """7. Informasi yang hilang ditandai sebagai '(Belum ditentukan dalam blueprint)'."""
        text = build_context(self.story_a, 1)
        kepala_sec = text[text.find("#### Kepala Cabang"):text.find("### B. Karakter yang Tidak Hadir")]

        # Kepala Cabang has no suspected, misunderstood, or unknown facts in blueprint
        self.assertIn("- **Fakta yang diduga:**\n  - *(Belum ditentukan dalam blueprint)*", kepala_sec)
        self.assertIn("- **Fakta yang disalahpahami:**\n  - *(Belum ditentukan dalam blueprint)*", kepala_sec)
        self.assertIn("- **Fakta yang belum diketahui:**\n  - *(Belum ditentukan dalam blueprint)*", kepala_sec)

    def test_08_scene_knowledge_separated_with_identity(self):
        """8. Pengetahuan per adegan tetap terpisah dengan identitas adegan."""
        text = build_context(self.story_a, 1)
        arya_sec = text[text.find("#### Arya Pratama"):text.find("#### Maya Indah")]

        # Scene 1 and Scene 2 tags must be retained with their respective clauses
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
        # Story A Chapter 1 & 2
        ctx_a1 = build_context(self.story_a, 1)
        self.assertIn("PAKET KONTEKS BAB 001", ctx_a1)

        (self.story_a / "manuscript/chapter-001.md").write_text("Naskah Bab 1 selesai.", encoding="utf-8")
        (self.story_a / "state-updates/chapter-001.md").write_text("State Bab 1 terekam.", encoding="utf-8")
        ctx_a2 = build_context(self.story_a, 2)
        self.assertIn("PAKET KONTEKS BAB 002", ctx_a2)
        self.assertIn("Naskah Bab 1 selesai.", ctx_a2)

        # Story B Chapter 1 & 2
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

        # "Pangeran Arthur mencurigai racun" must be in Pangeran Arthur ONLY
        self.assertIn("Pangeran Arthur mencurigai racun pada piala perjamuan", pangeran_sec)
        self.assertNotIn("Arthur Pendragon memegang pedang pusaka", pangeran_sec)

        # "Arthur Pendragon memegang pedang pusaka" must be in Arthur Pendragon ONLY
        self.assertIn("Arthur Pendragon memegang pedang pusaka", arthur_pendragon_sec)
        self.assertNotIn("Pangeran Arthur mencurigai racun", arthur_pendragon_sec)

        # Multi-word name without characters doc entry ("Kepala Cabang" in Story A)
        text_a = build_context(self.story_a, 1)
        self.assertIn("#### Kepala Cabang", text_a)
        kepala_sec = text_a[text_a.find("#### Kepala Cabang"):text_a.find("### B. Karakter yang Tidak Hadir")]
        self.assertIn("kepala cabang hanya tahu jadwal audit", kepala_sec)


if __name__ == "__main__":
    unittest.main()
