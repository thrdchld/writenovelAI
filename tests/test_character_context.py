"""
Tahap 5 — Pengujian konteks karakter untuk proyek gang-yang-hilang-dari-peta.

Memastikan:
1. Profil tokoh yang hadir (Salma, Dito) masuk ke Bagian 4A konteks.
2. Klasifikasi profil (unclassified/public/secrets) tidak bocor ke bagian
   pengetahuan karakter (Fakta yang diketahui/diduga/dsb).
3. Profil author_secrets tidak muncul di Bagian 4A.
4. Profil tokoh tidak hadir TIDAK ada di Bagian 4A.
5. Karakter tidak hadir muncul di Bagian 4B.
"""

import tempfile
import unittest
from pathlib import Path

from novel_engine.project import (
    build_context,
    extract_blueprint_boundaries,
    parse_character_profile,
)


CHARACTERS_MD = """\
# Karakter

## Salma — 29
Teknisi pemetaan kontrak di perusahaan konsultan infrastruktur. Teliti, \
cenderung percaya bahwa data yang rapi berarti data yang benar. Ia kembali \
ke Gang Kenari karena tugas lapangan, bukan karena ingin menyelidiki ayahnya. \
Ayahnya, Hadi, meninggal pada 2022. Salma mengingat Hadi sebagai orang yang \
tertib dan disegani, tetapi hubungan mereka tidak terlalu terbuka. \
Kelemahan: ketika fakta mengganggu gambaran yang ia pegang, ia menunda \
mengambil kesimpulan.

## Dito — 32
Rekan Salma di tim survei. Bertanggung jawab pada pengukuran lapangan dan \
dokumentasi teknis. Berorientasi prosedur, tetapi tidak kaku. Ia mengingatkan \
Salma bahwa kesaksian dan foto harus dicatat sumber serta tanggalnya.

## Yuni — 56
Ibu Salma. Tinggal di rumah lama keluarga. Mengetahui Hadi pernah berjanji \
memperbaiki catatan tiga rumah. Ia memilih diam karena takut Salma merusak \
nama ayahnya.

## Sari — 54
Penghuni salah satu rumah di halaman belakang. Menyimpan kuitansi dan surat \
yang menunjukkan mereka telah tinggal di sana, tetapi tidak memiliki sertifikat.
"""

BLUEPRINT_CH1 = """\
# Blueprint Bab 1 — Garis Merah di Atas Peta

## Identitas
- **POV:** Salma

## Adegan 1 — Peta final
- **Tokoh hadir:** Salma, Dito, koordinator proyek
- **Yang diketahui tokoh:** Salma tahu hasil surveinya; Dito tahu catatan lapangan; koordinator hanya tahu peta kerja awal.
- **Yang diketahui pembaca:** Pembaca tahu ada perbedaan peta dan kondisi nyata.
- **Informasi yang ditahan:** Alasan Salma yakin ada rumah ditahan.

## Adegan 2 — Nama di kolom pemeriksa
- **Tokoh hadir:** Salma, Dito
- **Yang diketahui tokoh:** Salma tahu Hadi ayahnya; Dito baru tahu nama itu punya hubungan pribadi.
- **Yang diketahui pembaca:** Pembaca mengetahui ayah Salma terlibat.
- **Informasi yang ditahan:** Isi dan motif perubahan 2011.
"""


def _make_story(root: Path) -> Path:
    story = root / "gang_test"
    for d in ("blueprint", "manuscript", "state-updates"):
        (story / d).mkdir(parents=True)
    (story / "04-story-outline.md").write_text("| 1 | Garis Merah |\n", encoding="utf-8")
    (story / "02-characters.md").write_text(CHARACTERS_MD, encoding="utf-8")
    (story / "blueprint/chapter-001.md").write_text(BLUEPRINT_CH1, encoding="utf-8")
    return story


class CharacterContextTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.story = _make_story(self.root)
        self.ctx = build_context(self.story, 1)
        self.sec4 = self.ctx[self.ctx.find("## 4. BATAS PENGETAHUAN SETIAP KARAKTER BAB 1"):]
        self.sec4a = self.ctx[
            self.ctx.find("### A. Karakter yang Hadir"):
            self.ctx.find("### B. Karakter yang Tidak Hadir")
        ]
        self.sec4b = self.ctx[self.ctx.find("### B. Karakter yang Tidak Hadir"):]

    def tearDown(self):
        self.tmp.cleanup()

    # ------------------------------------------------------------------
    # 1. Profil tokoh hadir muncul di Bagian 4A
    # ------------------------------------------------------------------

    def test_salma_profile_in_section_4a(self):
        """T5-01: Profil Salma muncul di Bagian 4A konteks."""
        self.assertIn("#### Salma", self.sec4a,
                      "Bagian 4A harus memuat header Salma")
        self.assertIn("Teknisi pemetaan kontrak", self.sec4a,
                      "Deskripsi profil Salma harus ada di 4A")

    def test_dito_profile_in_section_4a(self):
        """T5-02: Profil Dito muncul di Bagian 4A konteks."""
        self.assertIn("#### Dito", self.sec4a,
                      "Bagian 4A harus memuat header Dito")
        self.assertIn("pengukuran lapangan dan dokumentasi teknis", self.sec4a,
                      "Deskripsi profil Dito harus ada di 4A")

    # ------------------------------------------------------------------
    # 2. Profil tokoh tidak hadir TIDAK ada di 4A, ada di 4B
    # ------------------------------------------------------------------

    def test_yuni_not_in_section_4a(self):
        """T5-03: Profil Yuni (tidak hadir) tidak muncul di Bagian 4A."""
        self.assertNotIn("#### Yuni", self.sec4a,
                         "Yuni tidak hadir; tidak boleh ada di 4A")

    def test_sari_not_in_section_4a(self):
        """T5-04: Profil Sari (tidak hadir) tidak muncul di Bagian 4A."""
        self.assertNotIn("#### Sari", self.sec4a,
                         "Sari tidak hadir; tidak boleh ada di 4A")

    def test_non_present_chars_in_section_4b(self):
        """T5-05: Karakter tidak hadir muncul di Bagian 4B."""
        self.assertIn("Yuni", self.sec4b)
        self.assertIn("Sari", self.sec4b)

    # ------------------------------------------------------------------
    # 3. Klasifikasi tidak bocor ke bagian pengetahuan karakter
    # ------------------------------------------------------------------

    def test_salma_profile_not_in_character_knowledge_section(self):
        """T5-06: Profil Salma tidak masuk ke seksi 'Fakta yang diketahui' Dito."""
        dito_start = self.sec4a.find("#### Dito")
        coord_start = self.sec4a.find("#### Koordinator")
        end = coord_start if coord_start > 0 else len(self.sec4a)
        dito_knowledge_part = self.sec4a[dito_start:end]
        # Ambil hanya bagian "Fakta yang diketahui:" milik Dito, bukan profil
        if "- **Fakta yang diketahui:**" in dito_knowledge_part:
            facts_part = dito_knowledge_part[
                dito_knowledge_part.find("- **Fakta yang diketahui:**"):
            ]
            self.assertNotIn("Teknisi pemetaan kontrak", facts_part,
                             "Profil Salma tidak boleh masuk ke Fakta diketahui Dito")

    def test_dito_profile_not_in_salma_knowledge_section(self):
        """T5-07: Profil Dito tidak masuk ke seksi 'Fakta yang diketahui' Salma."""
        salma_start = self.sec4a.find("#### Salma")
        dito_start = self.sec4a.find("#### Dito")
        salma_section = self.sec4a[salma_start:dito_start]
        if "- **Fakta yang diketahui:**" in salma_section:
            facts_part = salma_section[
                salma_section.find("- **Fakta yang diketahui:**"):
            ]
            self.assertNotIn("pengukuran lapangan dan dokumentasi teknis", facts_part,
                             "Profil Dito tidak boleh masuk ke Fakta diketahui Salma")

    # ------------------------------------------------------------------
    # 4. author_secrets tidak bocor ke Bagian 4A
    # ------------------------------------------------------------------

    def test_no_author_only_label_bleeds_into_section_4a_character_facts(self):
        """T5-08: Label 'Rahasia Khusus Penulis' di profil tidak bocor ke seksi fakta karakter."""
        # Tambahkan story dengan profil yang memuat rahasia penulis
        story2 = self.root / "gang_test2"
        for d in ("blueprint", "manuscript", "state-updates"):
            (story2 / d).mkdir(parents=True)
        (story2 / "04-story-outline.md").write_text("| 1 | Test |\n", encoding="utf-8")
        (story2 / "02-characters.md").write_text(
            "# Karakter\n\n"
            "## Salma — 29\n"
            "- **Profil:** Teknisi pemetaan.\n"
            "- **Rahasia Penulis:** Salma adalah kunci misteri yang belum terkuak.\n\n"
            "## Dito — 32\n"
            "Rekan survei berorientasi prosedur.\n",
            encoding="utf-8"
        )
        (story2 / "blueprint/chapter-001.md").write_text(BLUEPRINT_CH1, encoding="utf-8")
        ctx2 = build_context(story2, 1)
        sec4a2 = ctx2[
            ctx2.find("### A. Karakter yang Hadir"):
            ctx2.find("### B. Karakter yang Tidak Hadir")
        ]
        # Rahasia penulis bisa muncul di profil header, tapi TIDAK sebagai "Fakta yang diketahui"
        salma_start = sec4a2.find("#### Salma")
        dito_start = sec4a2.find("#### Dito")
        salma_sec = sec4a2[salma_start:dito_start]
        if "- **Fakta yang diketahui:**" in salma_sec:
            facts_part = salma_sec[salma_sec.find("- **Fakta yang diketahui:**"):]
            self.assertNotIn("kunci misteri", facts_part,
                             "Rahasia penulis tidak boleh masuk ke seksi 'Fakta yang diketahui'")

    # ------------------------------------------------------------------
    # 5. parse_character_profile — klasifikasi konservatif untuk teks lama
    # ------------------------------------------------------------------

    def test_parse_legacy_profile_all_unclassified(self):
        """T5-09: Teks profil lama tanpa label klasifikasi seluruhnya masuk ke 'unclassified'."""
        text = (
            "Teknisi pemetaan kontrak. Teliti dan percaya data yang rapi. "
            "Ayahnya Hadi meninggal 2022."
        )
        result = parse_character_profile(text)
        self.assertEqual(result["public"], [],
                         "Profil tanpa label 'Profil:' tidak boleh otomatis jadi publik")
        self.assertEqual(result["character_secrets"], [],
                         "Profil tanpa label 'Rahasia:' tidak boleh otomatis jadi rahasia")
        self.assertEqual(result["author_secrets"], [],
                         "Profil tanpa label 'Rahasia Penulis:' tidak boleh jadi author secret")
        self.assertTrue(len(result["unclassified"]) > 0,
                        "Teks tanpa label harus masuk ke unclassified")

    def test_parse_explicit_secret_label(self):
        """T5-10: Teks dengan label 'Rahasia:' masuk ke character_secrets."""
        text = "Rahasia: Ia menyembunyikan dokumen kunci dari tim."
        result = parse_character_profile(text)
        self.assertTrue(len(result["character_secrets"]) > 0,
                        "Teks berlabel 'Rahasia:' harus masuk character_secrets")
        self.assertEqual(result["public"], [])
        self.assertEqual(result["author_secrets"], [])

    def test_parse_explicit_author_secret_label(self):
        """T5-11: Teks dengan label 'Rahasia Penulis:' masuk ke author_secrets."""
        text = "Rahasia Penulis: Dialah dalang perubahan peta 2011."
        result = parse_character_profile(text)
        self.assertTrue(len(result["author_secrets"]) > 0,
                        "Teks berlabel 'Rahasia Penulis:' harus masuk author_secrets")
        self.assertEqual(result["character_secrets"], [])
        self.assertEqual(result["public"], [])

    # ------------------------------------------------------------------
    # 6. Profil watak dipakai sebagai referensi penulis (ada note)
    # ------------------------------------------------------------------

    def test_profile_reference_note_present_for_salma(self):
        """T5-12: Ada catatan bahwa profil adalah referensi penulis, bukan fakta otomatis semua tokoh."""
        salma_start = self.sec4a.find("#### Salma")
        dito_start = self.sec4a.find("#### Dito")
        salma_sec = self.sec4a[salma_start:dito_start]
        self.assertIn(
            "referensi watak untuk penulis; bukan fakta yang otomatis diketahui karakter lain",
            salma_sec,
            "Harus ada note bahwa profil adalah referensi penulis"
        )

    def test_profile_reference_note_present_for_dito(self):
        """T5-13: Ada catatan referensi penulis untuk Dito."""
        dito_start = self.sec4a.find("#### Dito")
        coord_start = self.sec4a.find("#### Koordinator")
        end = coord_start if coord_start > 0 else len(self.sec4a)
        dito_sec = self.sec4a[dito_start:end]
        self.assertIn(
            "referensi watak untuk penulis; bukan fakta yang otomatis diketahui karakter lain",
            dito_sec,
            "Harus ada note bahwa profil Dito adalah referensi penulis"
        )

    # ------------------------------------------------------------------
    # 7. Integrasi dengan real story gang-yang-hilang-dari-peta (read-only)
    # ------------------------------------------------------------------

    def test_real_story_salma_dito_in_section_4a(self):
        """T5-14: Pada proyek nyata, profil Salma & Dito muncul di Bagian 4A Bab 1."""
        real_story = Path(__file__).resolve().parents[1] / \
                     "stories" / "gang-yang-hilang-dari-peta"
        if not real_story.is_dir():
            self.skipTest("Proyek gang-yang-hilang-dari-peta tidak ditemukan")
        ctx = build_context(real_story, 1, rewrite=True)
        sec4a = ctx[
            ctx.find("### A. Karakter yang Hadir"):
            ctx.find("### B. Karakter yang Tidak Hadir")
        ]
        self.assertIn("#### Salma", sec4a,
                      "Profil Salma harus ada di Bagian 4A pada proyek nyata")
        self.assertIn("#### Dito", sec4a,
                      "Profil Dito harus ada di Bagian 4A pada proyek nyata")
        self.assertIn("Teknisi pemetaan kontrak", sec4a,
                      "Deskripsi watak Salma harus ada di Bagian 4A")
        self.assertIn("pengukuran lapangan", sec4a,
                      "Deskripsi watak Dito harus ada di Bagian 4A")

    def test_real_story_no_author_only_in_character_facts(self):
        """T5-15: Pada proyek nyata, 'author_secrets' tidak masuk ke Fakta yang diketahui karakter."""
        real_story = Path(__file__).resolve().parents[1] / \
                     "stories" / "gang-yang-hilang-dari-peta"
        if not real_story.is_dir():
            self.skipTest("Proyek gang-yang-hilang-dari-peta tidak ditemukan")
        ctx = build_context(real_story, 1, rewrite=True)
        sec4a = ctx[
            ctx.find("### A. Karakter yang Hadir"):
            ctx.find("### B. Karakter yang Tidak Hadir")
        ]
        # Tidak boleh ada label Author-Only dari profil di dalam seksi fakta karakter
        # (muncul di profil header OK, tapi tidak di "Fakta yang diketahui")
        self.assertNotIn(
            "Rahasia Khusus Penulis (Author-Only dari Profil)",
            sec4a,
            "02-characters.md tidak memiliki label author-only; "
            "tidak boleh ada di 4A pada proyek nyata"
        )


if __name__ == "__main__":
    unittest.main()
