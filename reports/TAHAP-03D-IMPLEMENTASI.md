# LAPORAN TAHAP 3D — PERBAIKAN EKSTRAKSI RAHASIA, VALIDASI SUMBER, DAN REGRESSION TEST

**Tanggal:** 24 November 2026  
**Repository:** `thrdchld/writenovelAI`  
**Tahap Sebelumnya:** Tahap 3C (`46859d282342481b454c58e746d38f7e81c7beab`)  
**Status:** Berhasil Diimplementasikan, Diaudit, dan Lulus 39/39 Unit Test  

---

## 1. Ringkasan Eksekutif

Tahap 3D menindaklanjuti audit independen terhadap implementasi Tahap 3C dengan fokus pada:
1. **Perbaikan Ekstraksi Author-Only Secrets:** Menghilangkan asumsi bahwa status `KANON` otomatis berarti `Author-Only Secret`. Memisahkan rahasia penulis eksplisit (*explicit secrets*) dari keputusan kanon biasa (*unclassified canon*).
2. **Perbaikan Klasifikasi Profil Karakter:** Menghentikan tebakan kata kunci serampangan (`diam`, `takut`, `janji`, `mengetahui bahwa`) dan menerapkan klasifikasi semantik 3 kategori: *Profil Umum & Hubungan*, *Rahasia Pribadi (Eksplisit)*, dan *Informasi Ambigu (Perlu Pemeriksaan)*.
3. **Penguatan Proteksi State Update & Orphan State:** Memastikan State Update yang ada tidak dapat ditimpa tanpa persetujuan eksplisit (`rewrite=True`), orphan State Update terdeteksi dan tidak dapat dilanjutkan diam-diam sebagai penulisan normal baru, serta proses rewrite tidak merusak berkas kanon lainnya.
4. **Pemulihan Regression Tests Tahap 3B & Penambahan Test Suite Tahap 3D:** Mengintegrasikan seluruh 12 skenario pengujian semantik Tahap 3B yang sempat tergantikan, 14 pengujian lintas cerita Tahap 3C, 6 pengujian struktural, dan 7 pengujian perilaku baru Tahap 3D (total **39 unit test**, lulus 100%).
5. **Penyajian Utuh Konteks Bab 1:** Memperbaiki laporan konteks Bab 1 pada `reports/TAHAP-03D-CONTEXT-B1.md` dengan menyertakan teks utuh hasil eksekusi engine (456 baris, 36.353 karakter), bukan sekadar path berkas.

---

## 2. Rincian Perbaikan Mesin (`novel_engine/`)

### A. Ekstraksi Rahasia Penulis (`extract_author_secrets`)
- **Masalah Lama:** Semua entri kanon dalam `05-decision-log.md` (misalnya D-001, D-002, D-003) otomatis diekstrak sebagai `Author-Only Secret` dan dilarang untuk diketahui oleh karakter maupun pembaca. Akibatnya, fakta kanon biasa (seperti hubungan keluarga atau prosedur kerja) ikut terblokir secara tidak sah.
- **Solusi Tahap 3D:**
  1. Status `KANON` tidak otomatis dianggap sebagai rahasia penulis.
  2. Hanya entri yang secara eksplisit memuat penanda kerahasiaan penulis (`[RAHASIA PENULIS]`, `[AUTHOR-ONLY]`, `- **Klasifikasi:** Rahasia Penulis`, `- **Sifat:** Rahasia Penulis`, atau `- **Status:** KANON [RAHASIA PENULIS]`) yang masuk ke dalam bagian *Author-Only Secrets* (Bagian 5).
  3. Keputusan kanon tanpa label kerahasiaan eksplisit dikelompokkan ke dalam kategori tersendiri: `Keputusan Kanon Tanpa Klasifikasi Kerahasiaan (Status Terbuka / Belum Ditentukan)` dan tetap tersedia sebagai referensi kanon global (Bagian 2) tanpa membatasi pengungkapan fakta yang sah sesuai blueprint bab target.
  4. Header berkas `# Decision Log` dan bagian belum diputuskan difilter secara bersih dari daftar ekstraksi.

### B. Klasifikasi Profil Karakter (`parse_character_profile`)
- **Masalah Lama:** Mesin menebak kerahasiaan kalimat semata-mata dari keberadaan substring kata seperti `diam`, `takut`, `janji`, `motif`, atau `mengetahui bahwa`. Hal ini menyebabkan karakter yang "pendiam", "takut ketinggian", "berjanji pada ayah untuk belajar giat", atau "warga mengetahui bahwa ia dermawan" salah dikira menyimpan rahasia konspirasi.
- **Solusi Tahap 3D:**
  1. **Profil Umum & Hubungan:** Memuat relasi sosial, profesi, domisili, ciri fisik/watak (termasuk sifat pendiam, fobia umum, janji hidup personal, dan reputasi publik).
  2. **Rahasia Pribadi (Eksplisit dari Sumber):** Hanya diaktifkan jika terdapat penanda eksplisit seperti `Rahasia:`, `Rahasia pribadi:`, `Secret:`, `[RAHASIA]`, `[SECRET]`, atau `[PRIVAT]`. Kalimat tanpa kata kunci "diam"/"takut"/"janji" tetap dikenali dengan benar jika bertanda eksplisit.
  3. **Informasi Ambigu / Belum Diklasifikasikan (Perlu Pemeriksaan):** Kalimat prosa tidak bertanda yang mendeskripsikan tindakan menyembunyikan/memilih diam atas peristiwa plot atau memendam fakta tertentu dipisahkan dan diberi label `[!NOTE] INFORMASI PERLU PEMERIKSAAN`. Mesin melarang AI mengasumsikan seluruh karakter hadir otomatis tahu atau otomatis tidak tahu fakta tersebut.

### C. Proteksi State Update & Orphan State
- State Update yang sudah ada (baik dengan manuskrip maupun tanpa manuskrip / orphan state) diproteksi secara deterministik.
- Pemanggilan `build_context(rewrite=False)` saat State Update ada otomatis melempar `FileExistsError`.
- Mode rewrite untuk orphan State Update secara eksplisit ditandai dalam paket konteks sebagai:  
  `Mode: REWRITE (Penyelesaian Orphan State Update)`.
- Verifikasi membuktikan eksekusi rewrite tidak mengubah atau menghapus dokumen kanon lainnya (`00-premise.md`, `01-concept.md`, `04-story-outline.md`, dll.).

---

## 3. Daftar Regression Tests yang Dipulihkan dan Dipertahankan

Suite pengujian pada `tests/test_engine.py` kini mencakup **39 test case**, yang terbagi dalam 4 kelompok:

### Kelompok 1: Pengujian Struktural Dasar (6 Test)
1. `test_combined_blueprint_split`: Validasi pemisahan blueprint multi-bab.
2. `test_audit_detects_missing_blueprint`: Deteksi blueprint hilang pada audit.
3. `test_audit_detects_duplicate_outline_number`: Deteksi duplikasi nomor bab outline.
4. `test_chapter_numbers`: Pengambilan daftar nomor bab yang valid.
5. `test_unversioned_continuity_temporal_warning`: Peringatan berkas kontinuitas tanpa nomor bab.
6. `test_source_conflicts_flagged`: Peringatan konflik sumber pada bab tanpa dependensi lengkap.

### Kelompok 2: Restored Regression Tests Tahap 3B (12 Test)
7. `test_r01_salma_knowledge_not_attributed_to_dito`: Pengetahuan Salma tidak berpindah ke Dito.
8. `test_r02_yuni_knowledge_isolated_from_salma`: Pengetahuan pribadi Yuni tidak bocor ke Salma.
9. `test_r03_reader_withheld_not_conflated_with_character_knowledge`: Fakta ditahan dari pembaca tidak otomatis menjadi ketidaktahuan tokoh POV.
10. `test_r04_salma_suspicions_not_elevated_to_known_facts`: Dugaan Salma tidak dinaikkan status menjadi fakta kanon.
11. `test_r05_suspected_facts_categorized_correctly`: Kategorisasi tepat pada fakta yang diduga.
12. `test_r06_missing_info_marked_as_undetermined`: Informasi yang hilang ditandai `(Belum ditentukan dalam blueprint)`.
13. `test_r07_scenes_separated_with_identity`: Pemisahan per adegan mempertahankan identitas judul adegan.
14. `test_r08_present_characters_not_duplicated`: Tokoh hadir tidak terduplikasi.
15. `test_r09_combined_blueprint_processing_legacy`: Pemrosesan blueprint gabungan pada fixture kanon.
16. `test_r10_context_generation_ch1_and_ch2_legacy`: Konteks Bab 1 dan 2 berhasil dibuat pada fixture kanon.
17. `test_r11_future_state_updates_excluded_legacy`: State Update masa depan tidak bocor ke bab sebelumnya.
18. `test_r12_file_overwrite_protection_legacy`: Proteksi file yang sudah ada dari overwrite tanpa izin.

### Kelompok 3: Pengujian Lintas Cerita Tahap 3C (14 Test)
19. `test_01_no_cross_story_hardcoded_content`: Tidak ada kebocoran literal atau fakta antarcerita.
20. `test_02_character_knowledge_not_cross_attributed`: Pengetahuan Karakter A tidak diatribusikan ke Karakter B pada cerita lain.
21. `test_03_general_relationships_not_isolated_as_secrets`: Relasi publik tidak diisolasi sebagai rahasia.
22. `test_04_specific_secrets_strictly_isolated`: Isolasi rahasia spesifik terjaga ketat.
23. `test_05_reader_withheld_not_conflated_with_character_knowledge`: Pemisahan batas pembaca pada cerita multi-genre.
24. `test_06_author_secrets_dynamically_available`: Ketersediaan rahasia penulis secara dinamis.
25. `test_07_missing_info_marked_as_undetermined`: Penandaan belum ditentukan pada cerita multi-genre.
26. `test_08_scene_knowledge_separated_with_identity`: Identitas adegan terjaga pada cerita multi-genre.
27. `test_09_combined_blueprint_processing`: Blueprint gabungan multi-genre.
28. `test_10_future_state_updates_excluded`: Eksklusi State Update masa depan multi-genre.
29. `test_11_file_overwrite_protection`: Proteksi overwrite pada fixture multi-genre.
30. `test_12_orphan_state_update_detected`: Deteksi orphan State Update.
31. `test_13_context_generation_ch1_and_ch2_both_stories`: Pembuatan konteks Bab 1 & 2 untuk kedua fixture.
32. `test_14_multiword_and_similar_name_attribution`: Pencocokan nama majemuk / mirip tanpa tabrakan.

### Kelompok 4: Pengujian Spesifik Tahap 3D (7 Test Baru)
33. `test_3d_01_canon_decisions_not_automatically_author_secrets`: Keputusan kanon biasa (`D-002`) tidak otomatis menjadi rahasia penulis.
34. `test_3d_02_explicit_author_secrets_correctly_classified`: Keputusan bertanda `Klasifikasi: Rahasia Penulis` (`D-001`) masuk ke Author-Only Secrets.
35. `test_3d_03_profile_non_secret_keywords_not_misclassified`: Kalimat dengan `pendiam`, `takut ketinggian`, `berjanji`, `mengetahui bahwa` masuk ke Profil Umum, bukan rahasia.
36. `test_3d_04_explicit_secret_without_keywords_classified_as_secret`: Rahasia eksplisit tanpa kata kunci kerahasiaan dikenali sebagai rahasia pribadi.
37. `test_3d_05_ambiguous_profile_sentence_labeled_for_review`: Kalimat tindakan diam/menahan info diberi label review ambigu.
38. `test_3d_06_orphan_state_update_blocks_normal_write_and_preserves_other_sources`: Kondisi orphan State Update memblokir penulisan normal tanpa rewrite=True, dan rewrite tidak merusak sumber kanon lain.
39. `test_3d_07_state_update_overwrite_protection_without_manuscript`: State Update yang ada dilindungi dari penimpaan meskipun manuskrip belum ada.

---

## 4. Contoh Konkret Klasifikasi

### A. Keputusan Kanon Biasa yang Tidak Lagi Salah Diklasifikasikan sebagai Rahasia
Pada `05-decision-log.md` proyek Cerita A:
```markdown
## D-002 — Prosedur Audit Cabang
- **Status:** KANON
- **Keputusan:** Verifikasi fisik brankas dilakukan setiap triwulan bersama tim audit eksternal.
```
- **Sebelum Tahap 3D:** D-002 dimasukkan ke `Author-Only Secrets` dan diberi peringatan keras `DILARANG DIUNGKAP KEPADA PEMBACA ATAU DIJADIKAN FAKTA YANG DIKETAHUI KARAKTER`.
- **Sesudah Tahap 3D:** D-002 dimasukkan ke `Keputusan Kanon Tanpa Klasifikasi Kerahasiaan (Status Terbuka / Belum Ditentukan)` sebagai acuan global terbuka, tanpa larangan rahasia palsu.
- **Pada Cerita Utama (`gang-yang-hilang-dari-peta`):** D-001 (motif Hadi), D-002 (hasil akhir), dan D-003 (hubungan keluarga) yang berstatus `KANON UNTUK RANCANGAN UJI` kini tidak lagi dilarang secara kaku sebagai rahasia penulis, melainkan menjadi referensi kanon terbuka dengan peringatan bahwa resolusi akhir tidak boleh dibocorkan sebelum waktunya.

### B. Rahasia Eksplisit yang Berhasil Diklasifikasikan
1. **Author-Only Secret Eksplisit:**
   ```markdown
   ## D-001 — Aliran dana ke rekening luar negeri
   - **Status:** KANON
   - **Klasifikasi:** Rahasia Penulis
   - **Keputusan:** Dana penggelapan dialirkan ke yayasan fiktif oleh direktur keuangan...
   ```
   *Hasil:* Masuk secara tepat ke `### Rahasia yang HANYA DIKETAHUI PENULIS (Author-Only Secrets)`.
2. **Rahasia Karakter Eksplisit Tanpa Kata Kunci:**
   ```markdown
   ## Budi Santoso — 60
   - **Rahasia:** Menggelapkan dana kas kecil yayasan sebesar 50 juta rupiah.
   ```
   *Hasil:* Dikenali secara tepat sebagai `Rahasia Pribadi (Eksplisit dari Sumber)` meskipun tidak mengandung kata "diam", "takut", "janji", atau "motif".

### C. Profil Umum dengan Kata Kunci Ambigu yang Tidak Salah Diklasifikasikan
```markdown
## Hendra Kusuma — 45
Pustakawan firma yang pendiam dan takut ketinggian. Ia berjanji pada mendiang ayahnya untuk bekerja jujur. Rekan kantor mengetahui bahwa ia selalu datang tepat waktu.
```
- Mengandung kata: `pendiam`, `takut`, `berjanji`, `mengetahui bahwa`.
- *Hasil:* 100% ditempatkan pada `Profil Umum & Hubungan (Referensi Kanon)`. `Rahasia Pribadi` berstatus kosong `*(Tidak ada rahasia pribadi spesifik yang tercatat)*`.

---

## 5. Hasil Verifikasi dan Kualitas Implementasi

1. **Unit Testing:**
   - Command: `python -m unittest -v tests/test_engine.py`
   - Hasil: **39/39 OK (0.626 detik)**.
2. **Kompilasi Python:**
   - Command: `python -m py_compile novel_engine/*.py tests/*.py novel.py`
   - Hasil: Bebas kesalahan sintaks (*clean exit code 0*).
3. **Pemeriksaan Diff Cerita Asli:**
   - Tidak ada modifikasi pada direktori `stories/gang-yang-hilang-dari-peta/`.
   - Tidak ada bab novel yang ditulis.

---

## 6. Batasan yang Masih Tersisa (*Remaining Limitations*)

Meskipun sistem telah mengalami peningkatan besar dalam generalisasi dan modularitas, terdapat beberapa batasan yang perlu dicatat secara transparan:
1. **Dokumen Tidak Bertanda (*Unannotated Legacy Documents*):** Pada dokumen karakter yang ditulis sebagai satu paragraf narasi tanpa bullet/tag (seperti pada draf awal novel lama), kalimat yang mendeskripsikan tindakan menyembunyikan masa lalu dikategorikan sebagai *Informasi Ambigu (Perlu Pemeriksaan)*. Untuk hasil optimal, disarankan dokumen kanon baru menggunakan format terstruktur (`- **Rahasia:** ...` dan `- **Klasifikasi:** ...`).
2. **Resolusi Plot Makro pada Bab Awal:** Pada cerita di mana seluruh keputusan kanon belum diberi label klasifikasi akses, mesin memberikan catatan acuan terbuka. Tanggung jawab pemilihan saat pengungkapan fakta tetap mengacu pada *Blueprint Bab Target*. AI Writer diarahkan untuk tidak melompati tahapan adegan blueprint.
