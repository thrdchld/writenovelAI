# LAPORAN TAHAP 3C — GENERALISASI CONTEXT ENGINE DAN PENGUJIAN LINTAS CERITA

**Tanggal:** 24 November 2026  
**Repository:** `thrdchld/writenovelAI`  
**Commit Acuan:** `28fb2a93cf7539d3b6064b4b6355632bb74ce946`  
**Status:** Berhasil Diimplementasikan dan Lulus Pengujian Menyeluruh  

---

## 1. Ringkasan Eksekutif

Tahap 3C bertujuan mengubah *Context Engine* pada `novel_engine/` agar menjadi **mesin yang sepenuhnya generik, agnostik cerita, dan modular**, siap digunakan untuk sembarang novel fiksi (misteri, drama keluarga, fantasi, fiksi ilmiah) tanpa ketergantungan atau *hardcoding* data spesifik proyek tertentu.

Pada tahap sebelumnya (Tahap 3B), pemisahan semantik karakter telah berhasil diimplementasikan, tetapi masih ditemukan *literal hardcoding* seperti nama Salma, Dito, Yuni, Hadi, berkas 2011, koordinator proyek, dan isolasi total karakter non-hadir yang menutup hubungan kekeluargaan yang seharusnya merupakan pengetahuan publik.

Pada Tahap 3C, seluruh ketergantungan tersebut telah dihilangkan secara tuntas:
1. **Penghapusan Total Hardcoding Literal Cerita:** Kode mesin `novel_engine/` kini bebas 100% dari literal spesifik seperti `Salma`, `Dito`, `Yuni`, `Hadi`, `2011`, `drainase`, `Gang Kenari`, atau `koordinator`.
2. **Pembedaan Profil Umum vs Rahasia Karakter Tidak Hadir:** Karakter yang tidak hadir tidak lagi diisolasi secara buta. Profil umum dan hubungan keluarga (misal: "Ibu Salma", "Paman Maya", "Guru Lyra") tetap diakui sebagai referensi kanon yang sah, sementara memori privat dan motif rahasia diisolasi ketat.
3. **Ekstraksi Rahasia Penulis Secara Dinamis (`extract_author_secrets`):** Rahasia penulis (*author-only secrets*) diekstrak secara otomatis dari dokumen kanon (`05-decision-log.md` atau `01-concept.md`), tanpa literal yang ditanam dalam generator Python.
4. **Normalisasi & Pencocokan Karakter Multi-Kata Generik:** Algoritma pencocokan klausul mengenali nama majemuk (misal: "Pangeran Arthur" vs "Arthur Pendragon", "Kepala Cabang") tanpa tabrakan dan tanpa manipulasi string hardcoded.
5. **Dua Fixture Cerita Multi-Genre Baru:** Ditambahkan *Cerita A* (Misteri Realis / Audit Forensik) dan *Cerita B* (Drama Istana / Fantasi Ringan) dalam suite pengujian.
6. **20 Unit Test Lulus 100%:** Termasuk 14 pengujian kebutuhan perilaku spesifik lintas genre.

---

## 2. Berkas yang Dimodifikasi

1. `novel_engine/project.py`:
   - Menambahkan fungsi helper `parse_character_profile(text)` untuk memilah profil umum dan rahasia privat berbasis deteksi semantik kata kunci kerahasiaan (*secret keywords*).
   - Menambahkan fungsi `extract_author_secrets(story)` untuk mengekstrak keputusan kanon secara dinamis dari `05-decision-log.md` dan/atau `01-concept.md`.
   - Menambahkan fungsi `normalize_character_name(raw_name, known_names)` dan `match_characters_in_clause(clause, candidate_chars)` untuk menangani nama multi-kata dan penentuan identitas tokoh secara agnostik.
   - Menghapus percabangan khusus `c_name.lower() == "salma" and number == 1`.
   - Menghapus daftar hardcoded rahasia Hadi/Yuni pada Bagian 5 `build_context()`.
   - Memperbaiki Bagian 4.B agar menampilkan Profil Umum & Hubungan secara terpisah dari Rahasia Pribadi (Isolasi Ketat).
2. `tests/test_engine.py`:
   - Menyediakan fixture `setup_story_a` (Audit Forensik / Kasus Kas Fiktif).
   - Menyediakan fixture `setup_story_b` (Fantasi Ringan / Sumpah Darah Naga).
   - Menambahkan implementasi pengujian untuk 14 kebutuhan perilaku spesifik Tahap 3C di samping 6 pengujian struktural engine bawaan.
3. `reports/TAHAP-03C-CONTEXT-B1.md`:
   - Salinan paket konteks Bab 1 proyek `gang-yang-hilang-dari-peta` yang dihasilkan secara riil oleh engine baru.
4. `reports/TAHAP-03C-IMPLEMENTASI.md`:
   - Laporan teknis lengkap implementasi dan verifikasi Tahap 3C.

---

## 3. Detail Perubahan Arsitektur & Generalisasi

### A. Algoritma Pencocokan Karakter Multi-Kata Tanpa Hardcoding
Sebelumnya, penanganan "Koordinator proyek" dilakukan melalui kondisi literal `if "koordinator" in p_name.lower()`.
Pada Tahap 3C, sistem menggunakan pendekatan generik dua tingkat:
1. **Pencarian Nama Lengkap (*Exact Full-Phrase Matching*):** Diurutkan berdasarkan panjang karakter menurun (`sorted(candidate_chars, key=len, reverse=True)`). Hal ini menjamin nama yang lebih panjang seperti `"Arthur Pendragon"` atau `"Pangeran Arthur"` diuji sebelum nama pendek seperti `"Arthur"`.
2. **Pencarian Kata Distingtif Unik (*Unique Distinctive Word Matching*):** Jika klausul hanya menyebut satu kata (misal: "koordinator hanya tahu peta kerja awal" atau "Pendragon terdiam"), sistem menghitung frekuensi kemunculan kata tersebut di seluruh daftar karakter kandidat. Jika kata tersebut memiliki frekuensi 1 (unik hanya untuk karakter tersebut), maka klausul diatribusikan ke karakter tersebut. Jika tidak unik (misal "Arthur" muncul pada "Pangeran Arthur" dan "Arthur Pendragon"), klausul tidak diatribusikan sembarangan sehingga mencegah tabrakan atribusi (*collision prevention*).

### B. Isolasi Karakter Tidak Hadir yang Bernuansa (*Nuanced Non-Present Character Isolation*)
Sebelumnya, seluruh paragraf profil karakter non-hadir ditandai sebagai:
`PENGETAHUAN {NPC} INI TIDAK DIKETAHUI OLEH KARAKTER HADIR`.
Akibatnya, AI Writer berisiko menganggap Salma bahkan tidak mengetahui bahwa Yuni adalah ibunya atau tinggal di rumah keluarga lama.

Pada Tahap 3C, teks profil karakter dipilah secara semantik:
- **Profil Umum & Hubungan (Referensi Kanon):** Memuat peran sosial, hubungan kekeluargaan, profesi, dan lokasi tempat tinggal. Karakter hadir diizinkan mengetahui hal ini sesuai relasi mereka di dunia cerita.
- **Rahasia Pribadi / Motif Tersembunyi (Isolasi Ketat):** Kalimat yang mengandung indikator kerahasiaan (*rahasia, janji, diam, sembunyi, privat, motif, takut*) diisolasi ke dalam sub-bagian tersendiri dengan peringatan `[!CAUTION]` agar tidak bocor ke dalam prosa karakter hadir.

### C. Ekstraksi Rahasia Penulis Dinamis
Daftar rahasia makro pada Bagian 5 (*Author-Only Secrets*) sebelumnya memuat teks literal Hadi dan Yuni.
Pada Tahap 3C, generator memanggil `extract_author_secrets(story)` yang secara dinamis memindai berkas `05-decision-log.md` (mengambil entri bernomor `D-xxx` yang bertanda status KANON) atau `01-concept.md` (bagian `Mekanisme misteri` dan `Akhir yang dituju`).
Jika sebuah cerita tidak memiliki entri rahasia eksplisit, mesin mengeluarkan pesan standar:
`*(Tidak ada rahasia khusus yang tercatat dalam dokumen kanon)*`.

---

## 4. Pengujian Lintas Cerita dan 14 Kebutuhan Perilaku

Suite pengujian pada `tests/test_engine.py` dijalankan menggunakan modul `unittest` Python 3.14.

### Output Eksekusi Pengujian:
```text
test_01_no_cross_story_hardcoded_content (test_engine.EngineTests.test_01_no_cross_story_hardcoded_content)
1. Tidak ada nama atau fakta hardcoded dari cerita lain dalam konteks yang dihasilkan. ... ok
test_02_character_knowledge_not_cross_attributed (test_engine.EngineTests.test_02_character_knowledge_not_cross_attributed)
2. Pengetahuan Karakter A tidak diatribusikan ke Karakter B. ... ok
test_03_general_relationships_not_isolated_as_secrets (test_engine.EngineTests.test_03_general_relationships_not_isolated_as_secrets)
3. Hubungan umum (misal orang tua-anak, rekan kerja, paman) tidak diisolasi sebagai rahasia. ... ok
test_04_specific_secrets_strictly_isolated (test_engine.EngineTests.test_04_specific_secrets_strictly_isolated)
4. Rahasia spesifik diisolasi ketat sesuai sumber. ... ok
test_05_reader_withheld_not_conflated_with_character_knowledge (test_engine.EngineTests.test_05_reader_withheld_not_conflated_with_character_knowledge)
5. Informasi yang ditahan dari pembaca tidak otomatis membuat tokoh POV tidak tahu. ... ok
test_06_author_secrets_dynamically_available (test_engine.EngineTests.test_06_author_secrets_dynamically_available)
6. Rahasia penulis tetap tersedia di Bagian 2 dan Bagian 5 secara dinamis. ... ok
test_07_missing_info_marked_as_undetermined (test_engine.EngineTests.test_07_missing_info_marked_as_undetermined)
7. Informasi yang hilang ditandai sebagai '(Belum ditentukan dalam blueprint)'. ... ok
test_08_scene_knowledge_separated_with_identity (test_engine.EngineTests.test_08_scene_knowledge_separated_with_identity)
8. Pengetahuan per adegan tetap terpisah dengan identitas adegan. ... ok
test_09_combined_blueprint_processing (test_engine.EngineTests.test_09_combined_blueprint_processing)
9. Blueprint gabungan diproses dengan bersih. ... ok
test_10_future_state_updates_excluded (test_engine.EngineTests.test_10_future_state_updates_excluded)
10. State Update masa depan tidak masuk ke bab sebelumnya. ... ok
test_11_file_overwrite_protection (test_engine.EngineTests.test_11_file_overwrite_protection)
11. Naskah dan State Update yang ada dilindungi dari penimpaan tanpa rewrite=True. ... ok
test_12_orphan_state_update_detected (test_engine.EngineTests.test_12_orphan_state_update_detected)
12. Orphan State Update terdeteksi dan dilindungi. ... ok
test_13_context_generation_ch1_and_ch2_both_stories (test_engine.EngineTests.test_13_context_generation_ch1_and_ch2_both_stories)
13. Pembuatan konteks berhasil untuk Bab 1 dan Bab 2 pada kedua fixture cerita. ... ok
test_14_multiword_and_similar_name_attribution (test_engine.EngineTests.test_14_multiword_and_similar_name_attribution)
14. Penanganan nama karakter multi-kata atau mirip diatribusikan dengan akurat tanpa tabrakan. ... ok
test_audit_detects_duplicate_outline_number (test_engine.EngineTests.test_audit_detects_duplicate_outline_number) ... ok
test_audit_detects_missing_blueprint (test_engine.EngineTests.test_audit_detects_missing_blueprint) ... ok
test_chapter_numbers (test_engine.EngineTests.test_chapter_numbers) ... ok
test_combined_blueprint_split (test_engine.EngineTests.test_combined_blueprint_split) ... ok
test_source_conflicts_flagged (test_engine.EngineTests.test_source_conflicts_flagged) ... ok
test_unversioned_continuity_temporal_warning (test_engine.EngineTests.test_unversioned_continuity_temporal_warning) ... ok

----------------------------------------------------------------------
Ran 20 tests in 0.737s

OK
```

---

## 5. Verifikasi 8 Kriteria Kualitas pada Bab 1 `gang-yang-hilang-dari-peta`

Paket konteks Bab 1 dihasilkan melalui perintah:
```bash
python3 novel.py --story gang-yang-hilang-dari-peta context 1
```

Hasil evaluasi terhadap 8 kriteria kualitas:

1. **Ukuran Paket Konteks:**
   - Baris: **455 baris**
   - Karakter: **36.258 karakter**
   - Ukuran ideal untuk memuat kanon lengkap, aturan dunia, blueprint adegan, batasan karakter, batasan pembaca, kontinuitas, dan panduan penulisan prosa.
2. **File yang Dimasukkan:**
   - `00-premise.md`
   - `01-concept.md`
   - `03-world-and-rules.md`
   - `04-story-outline.md`
   - `05-decision-log.md`
   - `blueprint/chapter-001.md`
   - `docs/05-writing-standard.md`
3. **Relevansi Isi untuk Bab 1:**
   - 100% relevan. Informasi terstruktur rapi ke dalam 7 lapis instruksi dan batasan tanpa duplikasi tak berguna.
4. **Perlindungan Rahasia Masa Depan / Resolusi:**
   - Informasi masa depan di Bagian 2 dan Bagian 5 diberi label tegas `AUTHOR MACRO KNOWLEDGE` dan `Author-Only Secrets`.
   - Tidak ada rahasia masa depan yang bocor ke daftar fakta yang diketahui Salma, Dito, atau Koordinator proyek pada Bab 1.
5. **Ketiadaan Kontradiksi Antar-Sumber:**
   - Tidak ada konflik status atau benturan data antar-sumber.
6. **Ketersediaan Informasi Penulis Secara Dinamis:**
   - Rahasia penulis pada Bagian 5 diekstrak secara otomatis dari entri KANON `05-decision-log.md` (D-001, D-002, D-003) tanpa satu baris pun kode hardcoding di Python.
7. **Kejelasan dan Kealamian Batas Pengetahuan Karakter:**
   - Fakta yang diketahui Salma, Dito, dan Koordinator proyek tertera jelas per adegan.
   - Fakta yang tidak tercantum dalam blueprint ditandai secara objektif sebagai `*(Belum ditentukan dalam blueprint)*`, bukan diasumsikan atau diinjeksi secara artifisial.
   - Hubungan kekeluargaan Yuni sebagai ibu Salma diakui sebagai referensi umum, sementara janji Hadi dan alasan Yuni diam diisolasi ketat.
8. **Ruang Pengembangan Dialog dan Prosa:**
   - Konteks menyajikan panduan detail adegan (Adegan 1: ruang rapat kantor konsultan; Adegan 2: ruang arsip) dan ruang improvisasi dialog teknis/reaksi spontan tanpa membatasi kreativitas AI Writer.

---

## 6. Perbandingan Metrik Antar-Tahap

| Metrik | Tahap 2 | Tahap 3 | Tahap 3B | Tahap 3C (Kini) |
| :--- | :--- | :--- | :--- | :--- |
| **Jumlah Baris Konteks Bab 1** | 206 baris | 425 baris | 439 baris | **455 baris** |
| **Ukuran Karakter Konteks Bab 1** | 16.732 char | 34.619 char | 35.845 char | **36.258 char** |
| **Struktur Bagian Konteks** | 1 bagian datar | 7 bagian terstruktur | 7 bagian + semantik | **7 bagian generik modular** |
| **Ketergantungan Hardcoding Mesin** | Rendah (hanya baca) | Sedang (nama & peran) | Tinggi (Salma, Dito, Hadi) | **NOL (100% Agnostik Cerita)** |
| **Isolasi Karakter Non-Hadir** | Tidak ada | Belum rapi | Isolasi total (kaku) | **Profil umum vs Rahasia privat** |
| **Ekstraksi Rahasia Penulis** | Datar di awal | Ditandai manual | Hardcoded literal | **Dinamis dari `05-decision-log.md`** |
| **Jumlah Pengujian Unit Test** | 6 test | 14 test | 18 test | **20 test (Lulus 100%)** |
| **Fixture Pengujian Multi-Genre** | 1 sampel tiruan | 1 sampel tiruan | 1 sampel tiruan | **2 fixture (Misteri + Fantasi)** |

---

## 7. Status Kesiapan

- Mesin generator konteks `novel_engine/project.py` kini telah berstatus **production-ready dan multi-genre**.
- Mesin dapat digunakan untuk menulis novel baru mana pun cukup dengan menyediakan berkas kanon di folder cerita (`00-premise.md` s.d. `05-decision-log.md`) dan blueprint bab target.
- Tidak ada modifikasi yang dilakukan pada dokumen cerita asli `stories/gang-yang-hilang-dari-peta/`.
- Tidak ada teks prosa bab yang ditulis pada tahap ini.
