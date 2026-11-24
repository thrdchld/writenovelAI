# LAPORAN IMPLEMENTASI PERBAIKAN GENERATOR KONTEKS DAN PENGUJIAN ULANG (TAHAP 3)

- **Tanggal:** 24 November 2026
- **Target Repository:** `thrdchld/writenovelAI`
- **Branch:** `main`
- **Status Pekerjaan:** Selesai dan Lolos Uji

---

## 1. Berkas Kode yang Berubah

Perubahan dilakukan secara terukur pada dua berkas tanpa menyentuh dokumen premis, konsep, outline, blueprint, karakter, maupun canon cerita:

1. `novel_engine/project.py`:
   - Penulisan ulang fungsi `build_context()` untuk mengorganisasi konteks ke dalam 7 bagian terstruktur dengan pemisahan 3 lapis pengetahuan.
   - Penambahan fungsi pembantu `extract_blueprint_boundaries()` untuk mengekstrak batas pengetahuan tokoh, informasi pembaca, dan informasi yang ditahan secara otomatis dari blueprint bab target.
   - Penambahan fungsi pembantu `detect_source_conflicts()` untuk mendeteksi ketiadaan naskah/State Update sebelumnya, ketiadaan blueprint, atau *orphan state* secara deterministik.
   - Penyempurnaan `build_memory()` agar file di `continuity/` tanpa nomor bab diberi banner peringatan temporal eksplisit dan file `state-updates` dari bab mendatang tidak dimasukkan.
2. `tests/test_engine.py`:
   - Penambahan 8 unit test baru untuk memvalidasi pemisahan pengetahuan, penyaringan dokumen tidak relevan, deteksi konflik, batas Salma, dan proteksi penimpaan file.

---

## 2. Perubahan Perilaku Generator Konteks

### A. Pemisahan 3 Lapis Pengetahuan
Sebelumnya, seluruh informasi makro dimasukkan tanpa penanda lapis pengetahuan, sehingga AI penulis berisiko menganggap rahasia masa depan sebagai fakta yang diketahui tokoh di Bab 1. Pada generator baru, konteks dibagi menjadi:
1. **Pengetahuan Penulis (Author Macro Knowledge):** Diberi banner peringatan `> [!IMPORTANT] INFORMASI INI HANYA UNTUK PENULIS`. Kanon, mekanisme 2011, dan outline 30 bab tetap tersedia untuk menjaga konsistensi payoff, tetapi secara eksplisit dilarang masuk ke dialog atau monolog tokoh.
2. **Batas Pengetahuan Karakter (Character Knowledge):** Ditarik langsung dari fakta lapangan dan blueprint bab target. Pada Bab 1, ditegaskan bahwa Salma hanya mengetahui hasil survei lorong dan nama Hadi di kolom pengesahan 2011, serta **belum mengetahui** motif ayahnya.
3. **Batas Informasi Pembaca (Reader Knowledge):** Menegaskan misteri yang harus tetap ditahan (*withheld*) dari pembaca.

### B. Pembersihan Dokumen Tidak Relevan
Dokumen berikut **tidak lagi disuntikkan** ke dalam paket penulisan prosa:
- `AI_INSTRUCTIONS.md` (berisi instruksi CLI, Git commit, dan GitHub Actions untuk orchestrator).
- `docs/02-scene-blueprint.md` (teori perancangan blueprint).
- `docs/03-continuity.md` (teori manajemen kontinuitas).
- `docs/06-ai-operating-contract.md` (tahapan quality gate dan kontrak operasional).
- `stories/.../README.md` (dashboard checklist draf).

Dokumen gaya bahasa `docs/05-writing-standard.md` dipertahankan utuh pada Bagian 7 sebagai panduan prosa.

### C. Pelaporan Konflik Sumber Secara Eksplisit
Jika terdeteksi anomali (misalnya naskah/State Update bab sebelumnya belum dibuat untuk bab $N > 1$, blueprint hilang, atau orphan state), sistem tidak menyembunyikan masalah tersebut, melainkan menampilkan banner peringatan:
`> [!WARNING] TERDETEKSI INKONSISTENSI / KETIADAAN BERKAS SUMBER` pada awal paket konteks.

### D. Perlindungan Penimpaan Berkas
Perlindungan bawaan tetap dipertahankan: `build_context` melempar `FileExistsError` jika target naskah atau State Update sudah ada, kecuali jika parameter `rewrite=True` diaktifkan secara eksplisit.

---

## 3. Hasil Pengujian Teknis

Seluruh pengujian dijalankan langsung pada runtime Python:

### A. Kompilasi Python
```bash
python3 -m py_compile novel_engine/project.py tests/test_engine.py
```
- **Status:** Berhasil tanpa kesalahan sintaks.

### B. Unit Test Komprehensif
```text
Ran 14 tests in 0.093s

OK
```
Rincian 14 pengujian yang dijalankan:
1. `test_audit_detects_duplicate_outline_number`: Memvalidasi deteksi duplikasi nomor outline.
2. `test_audit_detects_missing_blueprint`: Memvalidasi deteksi ketiadaan blueprint.
3. `test_author_global_info_separated_from_character_knowledge`: Memvalidasi bahwa informasi global penulis berada pada seksi tersendiri dan tidak tercampur ke batas tokoh.
4. `test_chapter_numbers`: Memvalidasi penghitungan nomor bab dari outline dan blueprint.
5. `test_combined_blueprint_split`: Memvalidasi pemotongan blueprint gabungan (`chapter-*-to-*.md`).
6. `test_context_does_not_include_future_state`: Memvalidasi State Update bab mendatang tidak bocor ke bab sebelumnya.
7. `test_context_explicit_character_knowledge_boundaries`: Memvalidasi ekstraksi batas pengetahuan Salma dan Dito dari blueprint.
8. `test_context_refuses_to_overwrite_orphan_state`: Memvalidasi proteksi timpa saat State Update sudah ada.
9. `test_file_overwrite_protection_and_rewrite_flag`: Memvalidasi mode rewrite diizinkan hanya dengan flag eksplisit.
10. `test_irrelevant_docs_excluded_from_context`: Memvalidasi dokumen metodologi dan instruksi internal tidak masuk ke paket konteks.
11. `test_source_conflicts_flagged`: Memvalidasi deteksi dan peringatan eksplisit bila naskah/State Update bab sebelumnya hilang.
12. `test_subsequent_chapter_context_generation`: Memvalidasi alur penulisan Bab 2 menyertakan naskah dan State Update Bab 1 dengan benar.
13. `test_unversioned_continuity_temporal_warning`: Memvalidasi berkas kontinuitas tanpa nomor bab mendapatkan peringatan filter waktu.
14. `test_writing_instructions_distinguish_three_knowledge_layers`: Memvalidasi keberadaan instruksi pembedaan 3 lapis pengetahuan.

### C. Eksekusi Aktual CLI
```bash
python3 novel.py --story gang-yang-hilang-dari-peta context 1
```
- **Output:** `stories/gang-yang-hilang-dari-peta/workbench/context-chapter-001.md` (Exit code: `0`).

---

## 4. Metrik Ukuran dan Perbandingan Paket Konteks Bab 1

| Parameter | Paket Tahap 2 (Lama) | Paket Tahap 3 (Baru) | Perubahan |
|---|---|---|---|
| **Jumlah Karakter** | 52.699 | **32.232** | Turun **20.467 karakter (-38,8%)** |
| **Jumlah Baris** | 772 | **404** | Turun **368 baris (-47,7%)** |
| **Jumlah Kata** | 7.263 | **4.472** | Turun **2.791 kata (-38,4%)** |
| **Ukuran Berkas** | 52.773 bytes | **32.292 bytes** | Berkurang **~20,5 KB** |
| **Estimasi Token** | ~11.000 – 13.000 | **~6.800 – 7.500** | Lebih hemat dan fokus |

Salinan paket konteks baru tersimpan di [reports/TAHAP-03-CONTEXT-B1.md](TAHAP-03-CONTEXT-B1.md).

---

## 5. Ringkasan Pembagian Informasi dalam Paket Konteks Baru

### Informasi yang Tetap Disediakan bagi AI Penulis
- **Arah Makro & Kausalitas:** Premis lengkap (`00`), Konsep & Mekanisme Misteri (`01`), Aturan Dunia & Batas Teknis (`03`), Decision Log Kanon (`05`), serta Outline 30 bab & 10 butir Rantai Sebab-Akibat (`04`).
- **Blueprint Bab Target:** Seluruh perincian Adegan 1 dan Adegan 2, POV, waktu, lokasi, detail wajib, dan ruang pengembangan.
- **Profil Karakter Relevan:** Karakter hadir (Salma, Dito) dan lembar karakter lengkap untuk referensi.
- **Standar Bahasa:** Seluruh pedoman narasi, dialog, dan ritme dari `docs/05-writing-standard.md`.

### Informasi yang Dipisahkan atau Tidak Lagi Disertakan
- **Diberi Pembatas Khusus:** Rahasia 2011 (motif Hadi menolong warga pasca-banjir tanpa suap) kini diberi label keras sebagai **Author Macro Knowledge**. AI dilarang menaruh pengetahuan ini ke dalam monolog atau dialog Salma pada Bab 1.
- **Dikeluarkan Sepenuhnya:** File instruksi CLI/Git (`AI_INSTRUCTIONS.md`), teori penyusunan blueprint (`docs/02`), teori kontinuitas (`docs/03`), kontrak operasional tahapan (`docs/06`), dan dashboard draf (`README.md`).

---

## 6. Temuan dan Analisis Kronologi Bab 1 dan Bab 18 (Tugas C)

### A. Bukti Tekstual Aktual
1. **`blueprint/chapter-001.md`:**
   - Waktu: 17 Agustus 2026, pukul 14.00–14.35.
   - Adegan 1 (14.00): Rapat berlangsung di kantor konsultan. Koordinator menuntut tanda tangan; Salma menolak; rapat ditunda untuk verifikasi lapangan.
   - Adegan 2 (14.20–14.35): Rapat telah usai, koordinator keluar ruangan. Salma berdua dengan Dito melihat nama Hadi di lampiran 2011.
2. **`04-story-outline.md`:**
   - Bab 1 (17 Agustus 14.00): *Pembuka in medias res: Salma menolak mengesahkan peta...*
   - Bab 2–17 (4–17 Agustus): Kilas balik penyelidikan lapangan hingga penyusunan laporan (Bab 17 pukul 11.00).
   - Bab 18 (17 Agustus 13.45): *Rapat yang telah dibuka di bab 1 berlangsung; pengesahan segmen ditahan untuk verifikasi.*
3. **`blueprint/chapter-007-to-030.md` (Entri Bab 18):**
   - Waktu: 17 Agustus 13.45.
   - Adegan 1: Salma menyerahkan laporan dan menolak mengesahkan segmen; koordinator menahan pengesahan.
   - Detail Wajib Adegan 2: *"Jangan ulangi dialog pembuka secara verbatim."*
4. **`01-concept.md:7-9`:**
   - *"Cerita dibuka pada 17 Agustus 2026 ... Bab 2–18 bergerak maju sampai kembali ke hari rapat tersebut ... Pembuka bukan adegan yang harus diulang utuh. Bab 19 melanjutkan dari sesudah penolakan di rapat."*

### B. Analisis Masalah
- **Bukan Kontradiksi Logika Mutlak:** Alur cerita memiliki logika kausal yang jelas: Bab 1 memperlihatkan cuplikan dramatis penolakan tanda tangan (*in medias res*), Bab 2–17 menjelaskan bagaimana Salma menemukan kejanggalan, dan Bab 18 kembali ke momen rapat resmi.
- **Inkonsistensi Jam & Deskripsi yang Kurang Tepat:**
  - Bab 1 mencatat waktu 14.00–14.35. Bab 18 mencatat waktu 13.45 (15 menit sebelum Bab 1).
  - Deskripsi outline menyatakan *"rapat yang telah dibuka di bab 1 berlangsung pada bab 18"*, yang mengesankan pengulangan adegan yang sama.
  - Namun, secara riil, pukul 13.45 adalah saat para pihak berkumpul dan Salma menyerahkan berkas lampiran teknis (yang disusun di Bab 17 pukul 11.00). Pukul 14.00 adalah puncak ketegangan ketika koordinator mendesak tanda tangan pengesahan dan Salma menolaknya.

### C. Usulan Perbaikan Minimum (Tanpa Mengubah Kanon)
Jika nantinya dilakukan perapian dokumen cerita pada tahap berikutnya, perbaikan minimum yang diusulkan adalah:
1. **Penyesuaian Deskripsi Bab 18 pada `04-story-outline.md`:**
   - Ubah deskripsi Bab 18 menjadi: *"Rapat koordinasi teknis 17 Agustus dimulai (13.45); Salma mempresentasikan laporan anomali lapangan yang mengubah arah rapat pembuka."*
2. **Penegasan Irisan Adegan pada Blueprint Bab 18:**
   - Tetapkan bahwa Bab 18 mengambil perspektif ruang rapat secara utuh (argumen teknis tim desain dan reaksi pihak proyek) dan langsung melompat ke keputusan penahanan segmen, tanpa menduplikasi percakapan antara Salma dan Dito yang sudah selesai di Bab 1 Adegan 2.

---

## 7. Risiko yang Masih Tersisa (*Unresolved Risks*)

Meskipun generator konteks sudah jauh lebih bersih, aman, dan teruji, terdapat beberapa risiko sistemik dari audit Tahap 1 yang berada di luar cakupan generator konteks:
1. **Tumpang Tindih Blueprint Bab 7–14:**
   - Keberadaan file individual `chapter-007.md` s.d. `chapter-014.md` dan entri di `chapter-007-to-030.md` belum diselaraskan (perlu diputuskan apakah menggunakan format file tunggal atau gabungan sebelum masuk ke penulisan Bab 7).
2. **Kesiapan Otomasi CLI AGY (`novel_engine/agy.py`):**
   - Subproses pemanggilan `agy` masih belum dilengkapi parameter perizinan non-interaktif (`--dangerously-skip-permissions`). Jalur penulisan yang aman saat ini adalah penulisan semi-otomatis melalui paket konteks.
3. **Penanganan Format JSON pada `github_bot.py`:**
   - Chatbot issue belum dikonfigurasi dengan mode JSON terstruktur bawaan API.
