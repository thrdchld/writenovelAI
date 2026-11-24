# LAPORAN IMPLEMENTASI PEMISAHAN PENGETAHUAN DAN VALIDASI SEMANTIK (TAHAP 3B)

- **Tanggal:** 24 November 2026
- **Target Repository:** `thrdchld/writenovelAI`
- **Branch:** `main`
- **Status:** Selesai, Teruji, dan Terverifikasi Penuh

---

## 1. Berkas Kode yang Berubah

Perubahan dilakukan secara presisi dan modular pada dua berkas inti mesin:

1. `novel_engine/project.py`:
   - Penulisan ulang fungsi `extract_blueprint_boundaries(blueprint_text, story=None)` untuk membedah blueprint secara multi-adegan (*scene-by-scene*), mendeteksi karakter hadir vs tidak hadir, memecah klausa pengetahuan per karakter secara individual, dan membedakan antara informasi yang ditahan dari pembaca vs hal yang belum diketahui karakter.
   - Penyempurnaan `build_context()` pada **Bagian 4 (Batas Pengetahuan Setiap Karakter)** dan **Bagian 5 (Batas Informasi Pembaca)** untuk menyajikan isolasi pengetahuan yang ketat, identitas adegan, peringatan kebocoran rahasia tokoh tidak hadir (seperti Yuni), serta penanda eksplisit `(Belum ditentukan dalam blueprint)`.
2. `tests/test_engine.py`:
   - Penambahan rangkaian pengujian perilaku semantik komprehensif (total menjadi 18 unit test) yang menguji secara langsung 12 skenario pemisahan pengetahuan antar-karakter, isolasi pembaca, penanganan dugaan, blueprint gabungan, dan proteksi file.

---

## 2. Masalah yang Diperbaiki pada Tahap 3B

### A. Pemisahan Tegas Pengetahuan Karakter vs Pembaca
- **Kelemahan Sebelumnya (Tahap 3):** Poin *Informasi yang ditahan* secara otomatis dimasukkan ke dalam daftar hal yang belum diketahui tokoh sekaligus ditahan dari pembaca. Hal ini keliru karena tokoh POV (Salma) sebenarnya mengetahui alasan lapangannya mengapa ia yakin ada rumah di balik tembok, namun penjelasan lengkap tersebut sengaja ditahan dari pembaca pada Bab 1 demi tensi misteri.
- **Perbaikan Tahap 3B:** 
  - *Informasi yang ditahan* diklasifikasikan secara murni ke dalam **Batas Informasi Pembaca (Bagian 5)**.
  - Fakta yang belum diketahui karakter pada **Bagian 4** hanya diisi oleh klausa yang secara eksplisit menyatakan ketidaktahuan tokoh (misal: "belum tahu", "tidak tahu", atau batasan motif ayah pada pembuka). Jika tidak ada di blueprint, diberi label `(Belum ditentukan dalam blueprint)`.

### B. Pemisahan Pengetahuan per Individu Karakter (Character Isolation)
- **Kelemahan Sebelumnya:** Seluruh fakta tokoh digabung dalam satu daftar umum tanpa identitas jelas siapa mengetahui apa.
- **Perbaikan Tahap 3B:**
  - Setiap karakter hadir (Salma, Dito, Koordinator Proyek) memiliki subseksi tersendiri dengan 4 kategori analitis:
    1. *Fakta yang diketahui* (dikaitkan dengan judul adegan spesifik).
    2. *Fakta yang diduga* (diklasifikasikan dari kata kunci curiga, mengira, asumsi).
    3. *Fakta yang disalahpahami* (diklasifikasikan dari salah paham, keliru).
    4. *Fakta yang belum diketahui* (diklasifikasikan dari klausa ketidaktahuan faktual).
  - Karakter penting yang tidak hadir (khususnya **Yuni**) ditampilkan dengan batas isolasi keras:
    `> [!CAUTION] PENGETAHUAN YUNI INI TIDAK DIKETAHUI OLEH KARAKTER HADIR (Salma, Dito, Koordinator proyek).`

### C. Ekstraksi Blueprint Multi-Format & Multi-Adegan
- Generator membedah blueprint menjadi blok-blok adegan (`## Adegan` atau `### Adegan`), sehingga fakta Adegan 1 dan Adegan 2 tidak bercampur tanpa konteks.
- Daftar karakter hadir dibersihkan dari duplikasi (*deduplicated*) dengan tetap mempertahankan urutan kemunculan pertama.
- Baris format tambahan atau tidak dikenal dalam adegan tidak dibuang, melainkan ditampung pada seksi catatan tambahan.
- Klausa ambigu yang tidak dapat diatribusikan secara pasti ke nama karakter ditandai dengan label `[Catatan pengetahuan bersama/perlu pemeriksaan]`.

---

## 3. Hasil Pengujian Otomatis (18 Unit Test)

Rangkaian tes dijalankan melalui perintah standar Python:
```bash
python3 -m unittest discover -s tests -v
```

Hasil eksekusi:
```text
test_10_context_generation_ch1_and_ch2 (test_engine.EngineTests.test_10_context_generation_ch1_and_ch2)
10. Pembuatan konteks Bab 1 dan Bab 2 tetap berjalan. ... ok
test_11_future_state_updates_excluded (test_engine.EngineTests.test_11_future_state_updates_excluded)
11. State Update masa depan tetap tidak masuk ke konteks. ... ok
test_12_file_overwrite_protection (test_engine.EngineTests.test_12_file_overwrite_protection)
12. Perlindungan file yang sudah ada tetap berfungsi. ... ok
test_1_salma_knowledge_not_attributed_to_dito (test_engine.EngineTests.test_1_salma_knowledge_not_attributed_to_dito)
1. Fakta yang diketahui Salma tidak otomatis dianggap diketahui Dito. ... ok
test_2_yuni_knowledge_isolated_from_salma (test_engine.EngineTests.test_2_yuni_knowledge_isolated_from_salma)
2. Fakta yang diketahui Yuni tidak otomatis dianggap diketahui Salma. ... ok
test_3_reader_withheld_not_conflated_with_character_knowledge (test_engine.EngineTests.test_3_reader_withheld_not_conflated_with_character_knowledge)
3. Informasi yang ditahan dari pembaca tidak otomatis berarti tokoh POV juga tidak mengetahuinya. ... ok
test_4_author_secrets_not_character_facts (test_engine.EngineTests.test_4_author_secrets_not_character_facts)
4. Rahasia penulis tidak muncul sebagai fakta yang diketahui karakter. ... ok
test_5_suspicions_not_promoted_to_facts (test_engine.EngineTests.test_5_suspicions_not_promoted_to_facts)
5. Dugaan karakter tidak dinaikkan menjadi fakta. ... ok
test_6_missing_info_marked_as_undetermined (test_engine.EngineTests.test_6_missing_info_marked_as_undetermined)
6. Informasi yang tidak tersedia ditandai sebagai belum ditentukan. ... ok
test_7_scenes_separated_with_identity (test_engine.EngineTests.test_7_scenes_separated_with_identity)
7. Informasi dari adegan berbeda tidak tercampur. ... ok
test_8_present_characters_not_duplicated (test_engine.EngineTests.test_8_present_characters_not_duplicated)
8. Karakter yang hadir tidak terduplikasi. ... ok
test_9_combined_blueprint_processing (test_engine.EngineTests.test_9_combined_blueprint_processing)
9. Blueprint gabungan tetap bisa diproses. ... ok
test_audit_detects_duplicate_outline_number (test_engine.EngineTests.test_audit_detects_duplicate_outline_number) ... ok
test_audit_detects_missing_blueprint (test_engine.EngineTests.test_audit_detects_missing_blueprint) ... ok
test_chapter_numbers (test_engine.EngineTests.test_chapter_numbers) ... ok
test_combined_blueprint_split (test_engine.EngineTests.test_combined_blueprint_split) ... ok
test_source_conflicts_flagged (test_engine.EngineTests.test_source_conflicts_flagged) ... ok
test_unversioned_continuity_temporal_warning (test_engine.EngineTests.test_unversioned_continuity_temporal_warning) ... ok

----------------------------------------------------------------------
Ran 18 tests in 0.179s

OK
```

---

## 4. Validasi Ulang Paket Konteks Bab 1 (`gang-yang-hilang-dari-peta`)

Paket konteks Bab 1 dibuat ulang melalui perintah aktual:
```bash
python3 novel.py --story gang-yang-hilang-dari-peta context 1
```
Salinan lengkap tersimpan di [reports/TAHAP-03B-CONTEXT-B1.md](TAHAP-03B-CONTEXT-B1.md).

### Hasil Pemeriksaan 8 Poin Validasi

| No | Poin Pemeriksaan | Hasil Aktual pada Berkas Konteks | Status |
|---|---|---|---|
| 1 | Salma mengetahui hasil surveinya | Tertera di bawah Salma pada *Adegan 1 — Peta final: Salma tahu hasil surveinya*. | **Valid (Lolos)** |
| 2 | Dito mengetahui catatan pengukuran | Tertera di bawah Dito pada *Adegan 1 — Peta final: Dito tahu catatan lapangan*. | **Valid (Lolos)** |
| 3 | Koordinator hanya mengetahui peta kerja awal | Tertera di bawah Koordinator pada *Adegan 1 — Peta final: koordinator hanya tahu peta kerja awal*. Tidak ada data survei Salma yang diatribusikan padanya. | **Valid (Lolos)** |
| 4 | Salma mengetahui Hadi adalah ayahnya | Tertera di bawah Salma pada *Adegan 2 — Nama di kolom pemeriksa: Salma tahu Hadi ayahnya*. | **Valid (Lolos)** |
| 5 | Salma belum mengetahui motif perubahan 2011 | Tertera di bawah Salma bagian Fakta Belum Diketahui: *Bab 1: Tokoh belum mengetahui motif perubahan peta 2011 (tanda tangan ayah) maupun rahasia yang disimpan Yuni*. | **Valid (Lolos)** |
| 6 | Pembaca mengetahui keterlibatan Hadi sebatas Bab 1 | Tertera pada Bagian 5: *Adegan 2: Pembaca mengetahui ayah Salma terlibat, belum tahu apa perannya*. Rincian isi/motif 2011 masuk daftar ditahan dari pembaca. | **Valid (Lolos)** |
| 7 | Pengetahuan Yuni tidak bocor ke Salma | Pengetahuan Yuni mengenai janji 2011 dipisahkan di Subseksi Karakter Tidak Hadir dengan peringatan: `PENGETAHUAN YUNI INI TIDAK DIKETAHUI OLEH KARAKTER HADIR (Salma, Dito, Koordinator proyek)`. Tidak masuk ke blok Salma. | **Valid (Lolos)** |
| 8 | Informasi global penulis tetap tersedia untuk arah cerita | Seluruh dokumen premis, konsep misteri, aturan dunia, decision log, dan outline 30 bab tetap ada pada Bagian 2 dengan label `INFORMASI INI HANYA UNTUK PENULIS (AUTHOR MACRO KNOWLEDGE)` dan dilarang masuk ke dialog tokoh. | **Valid (Lolos)** |

### Ukuran Berkas Paket Baru (Tahap 3B)
- **Panjang Karakter:** **34.837 karakter** (naik sedikit dari 32.232 karena penambahan struktur detail per-karakter dan isolasi Yuni, namun tetap jauh lebih hemat dibandingkan draf Tahap 2 awal sebesar 52.699 karakter).
- **Jumlah Baris:** **443 baris**
- **Jumlah Kata:** **4.862 kata**
- **Estimasi Token:** **~7.200 – 8.000 token**.

---

## 5. Keterbatasan dan Risiko yang Masih Tersisa

1. **Blueprint Lama dengan Rincian Minimal:**
   - Pada bab-bab gabungan yang hanya memuat satu kalimat batas pengetahuan umum, generator menandai kategori yang tidak disebutkan sebagai `(Belum ditentukan dalam blueprint)`. Hal ini sesuai prinsip anti-halusinasi (tidak mengarang batas jika sumber tidak menyediakannya).
2. **Kesiapan Eksekusi Otomatis AGY (`novel_engine/agy.py`):**
   - Perbaikan Tahap 3B fokus pada generator konteks Python dan pemisahan pengetahuan naratif. Modul adapter CLI AGY yang memanggil subproses `agy -p` masih perlu diuji langsung dengan runner lingkungan sebelum penulisan otomatis dijalankan tanpa intervensi manusia.
3. **Harmonisasi Berkas Blueprint Bab 7–14:**
   - File duplikat `chapter-007.md` s.d. `chapter-014.md` dan entri di `chapter-007-to-030.md` masih perlu diselaraskan sebelum melangkah melewati Bab 6.
