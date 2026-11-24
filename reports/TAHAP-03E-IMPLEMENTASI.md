# LAPORAN TAHAP 3E — IMPLEMENTASI PEMISAHAN KLASIFIKASI RAHASIA DAN INFORMASI AMBIGU

**Tanggal:** 24 November 2026  
**Repository:** `thrdchld/writenovelAI`  
**Tahap Sebelumnya:** Tahap 3D (`eb65c2a459b6b02be6f5205b55ccff79b37576cf`)  
**Status:** Berhasil Diimplementasikan, Teruji Lintas Cerita, dan Lulus 42/42 Unit Test  

---

## 1. Ringkasan Eksekutif

Tahap 3E menyempurnakan ketelitian sistem klasifikasi pengetahuan pada *Context Engine* novel_engine:
1. **Pemisahan Tegas Author-Only Secrets dari Kategori Lain:**
   - Menghilangkan asumsi bahwa kata `rahasia`, `privat`, atau status `KANON` otomatis berarti rahasia khusus penulis (*Author-Only Secrets*).
   - Menetapkan aturan klasifikasi tegas 5 arah:
     - `RAHASIA_PENULIS`: Informasi yang secara eksplisit ditandai khusus penulis (`[RAHASIA PENULIS]`, `[AUTHOR-ONLY]`, `Klasifikasi: Rahasia Penulis`).
     - `RAHASIA_KARAKTER`: Rahasia yang dimiliki atau diketahui karakter (`[RAHASIA KARAKTER]`, `[RAHASIA]`, `Klasifikasi: Rahasia Karakter`, `Pemilik Rahasia: <Nama>`).
     - `INFORMASI_PUBLIK`: Informasi yang dinyatakan terbuka/umum (`[PUBLIK]`, `Klasifikasi: Publik`).
     - `PERLU_PEMERIKSAAN`: Klasifikasi kosong, bertentangan (misal: Author-Only memiliki pemilik karakter), atau ambigu.
     - `BELUM_DIKLASIFIKASIKAN`: Keputusan kanon tanpa penanda akses eksplisit (tetap dipertahankan dalam global canon, tidak dibuang dan tidak ditebak).

2. **Penghapusan Heuristik Kata Kerja / Kata Kunci pada Profil Karakter:**
   - Menghapus sepenuhnya ketergantungan pada pola kata kerja atau kata sifat tertentu dalam profil karakter.
   - Menggantinya dengan pencocokan penanda semantik eksplisit:
     - `Profil`, `Publik`, `Hubungan`, `Peran`, `Profesi`, `Relasi`, `Latar Belakang` -> Profil Umum & Hubungan.
     - `Rahasia`, `Rahasia Karakter`, `Rahasia Pribadi` -> Rahasia Pribadi Karakter.
     - `Rahasia Penulis`, `Author-Only` -> Rahasia Khusus Penulis dari Profil.
     - `Catatan Ambigu`, `Perlu Pemeriksaan` -> Informasi Ambigu / Perlu Pemeriksaan.
     - Kalimat naratif tanpa penanda eksplisit -> **Belum Diklasifikasikan** (tidak otomatis dijadikan publik dan tidak otomatis dijadikan rahasia).

3. **Pemisahan Akses Informasi dari Kepemilikan Rahasia:**
   - Membedakan secara independen tiga dimensi:
     1. *Apakah fakta ini benar dalam kanon cerita?* (Kanonitas)
     2. *Siapa saja yang mengetahui fakta ini?* (Kepemilikan dan Batas Pengetahuan Karakter)
     3. *Apakah pembaca sudah boleh mengetahui fakta ini?* (Batas Informasi Pembaca / Pacing Naratif)
   - Rahasia milik satu karakter tidak otomatis menjadi rahasia penulis jika diketahui oleh pihak lain.
   - Informasi yang ditahan dari pembaca tidak membatalkan atau mengaburkan pengetahuan sah tokoh POV di blueprint bab.

4. **Kompatibilitas Penuh Dokumen Legacy & Nol Hardcoding:**
   - Dokumen cerita lama (seperti `stories/gang-yang-hilang-dari-peta/`) yang belum mengadopsi format metadata baru tetap diproses tanpa error dan tanpa kehilangan informasi kanon.
   - Seluruh 39 unit test sebelumnya (Tahap 3B, 3C, 3D) tetap lulus 100%, ditambah 3 test suite baru khusus Tahap 3E (total **42 unit test**).

---

## 2. Format Standar Klasifikasi Pengetahuan

Untuk proyek cerita baru atau migrasi bertahap cerita berjalan, direkomendasikan format metadata kanon standar berikut:

### A. Format Keputusan Kanon (`05-decision-log.md`)

```markdown
## D-010 — Nama Keputusan
- **Status:** KANON
- **Klasifikasi:** Rahasia Penulis
- **Keputusan:** Penjelasan keputusan yang hanya boleh diketahui penulis dan engine untuk foreshadowing, dilarang bocor ke karakter dan pembaca.

## D-020 — Rahasia Milik Tokoh
- **Status:** KANON
- **Klasifikasi:** Rahasia Karakter
- **Pemilik Rahasia:** Nama Tokoh
- **Keputusan:** Fakta rahasia yang disimpan atau diketahui oleh tokoh tertentu.

## D-030 — Prosedur Terbuka
- **Status:** KANON
- **Klasifikasi:** Publik
- **Keputusan:** Fakta yang dapat diketahui oleh umum atau karakter lain yang relevan.

## D-040 — Keputusan Kanon Standar (Tanpa Klasifikasi Khusus)
- **Status:** KANON
- **Keputusan:** Keputusan kanon dunia atau plot yang belum memiliki batasan kerahasiaan khusus.
```

### B. Format Profil Karakter (`02-characters.md`)

```markdown
## Nama Karakter — Usia
- **Profil:** Pekerjaan, peran sosial, relasi keluarga, dan fakta umum.
- **Rahasia:** Fakta rahasia pribadi yang disembunyikan oleh karakter ini.
- **Rahasia Penulis:** Informasi masa depan atau latar belakang konseptual yang hanya dipegang penulis.
- **Catatan Ambigu:** Catatan peristiwa atau rumor yang sumbernya belum jelas atau bertentangan.
```

### C. Penanganan Dokumen Lama (Legacy Support)
Bila dokumen tidak memuat metadata di atas:
- Teks profil atau keputusan kanon **tidak dihapus** dan **tidak ditebak**.
- Dimasukkan ke dalam kategori `Informasi Ambigu / Belum Diklasifikasikan` dengan instruksi peringatan:
  > `[!NOTE] INFORMASI PERLU PEMERIKSAAN: Untuk catatan ambigu/belum diklasifikasikan di atas, sumber tidak mencatat siapa saja yang mengetahuinya; jangan mengasumsikan seluruh karakter hadir otomatis tahu atau otomatis tidak tahu, melainkan batasi sesuai bukti nyata dalam blueprint bab ini.`

---

## 3. Rincian Modifikasi Mesin (`novel_engine/project.py`)

1. **`classify_decision_entry(sec_strip)`**:
   - Fungsi parser khusus untuk mengevaluasi header judul, tag bracket, field metadata (`Klasifikasi:`, `Sifat:`, `Akses:`, `Kerahasiaan:`), status KANON, dan field `Pemilik Rahasia:`.
   - Mengembalikan 5 enum tegas: `'RAHASIA_PENULIS'`, `'RAHASIA_KARAKTER'`, `'INFORMASI_PUBLIK'`, `'PERLU_PEMERIKSAAN'`, atau `'BELUM_DIKLASIFIKASIKAN'`.
   - Menandai kontradiksi (seperti kombinasi Author-Only dengan Pemilik Karakter, atau tag bertentangan) sebagai `PERLU_PEMERIKSAAN`.

2. **`parse_character_profile(text)`**:
   - Memproses setiap baris profil karakter dan memecah kalimat berdasarkan penanda semantik eksplisit.
   - Menghapus heuristik tebakan kata kerja/kata sifat (`diam`, `takut`, `janji`, `mengetahui bahwa`).
   - Mengelompokkan hasil ke dalam dictionary:
     `{"public": [...], "character_secrets": [...], "author_secrets": [...], "needs_review": [...], "unclassified": [...]}`.

3. **`extract_author_secrets(story)`**:
   - Mengembalikan tuple 5 kategori:
     `(author_secrets, character_secrets, unclassified_canon, needs_review_canon, public_canon)`.

4. **`extract_blueprint_boundaries(blueprint_text, story=None)`**:
   - Mempertahankan pemisahan baris (`"\n".join(...)`) saat mengekstrak profil karakter non-hadir dari `02-characters.md`, sehingga kalimat terpisah tidak terlebur.

5. **`build_context(story, number, rewrite=False)`**:
   - **Bagian 4.B (Karakter yang Tidak Hadir):** Menampilkan *Profil Umum & Hubungan*, *Rahasia Pribadi (Eksplisit)*, *Rahasia Khusus Penulis (Author-Only)*, serta *Informasi Ambigu / Belum Diklasifikasikan* dengan blok instruksi isolasi yang presisi.
   - **Bagian 5 (Batas Informasi Pembaca & Penulis):** Menampilkan sub-bagian terpisah:
     - *Rahasia yang HANYA DIKETAHUI PENULIS (Author-Only Secrets)*
     - *Rahasia Karakter dalam Dokumen Keputusan (Bukan Rahasia Penulis)*
     - *Keputusan Kanon Perlu Pemeriksaan (Klasifikasi Kosong atau Bertentangan)*
     - *Keputusan Kanon Tanpa Klasifikasi Kerahasiaan (Status Terbuka / Belum Ditentukan)*
     - *Keputusan Kanon Publik (Informasi Terbuka)*

---

## 4. Hasil Verifikasi dan Pengujian

- **Kompilasi Sintaks:** `python -m py_compile novel_engine/*.py tests/*.py novel.py` -> **SUKSES (0 error)**.
- **Eksekusi Test Suite:** `python -m unittest discover tests` -> **42 tests passed in 0.676s (OK)**.
- **Audit File Cerita:** `git diff stories/` -> **Bersih (0 baris berubah pada cerita asli)**.
- **Uji Konteks Proyek Nyata:** `python novel.py --story gang-yang-hilang-dari-peta context 1` -> Berhasil membuat paket konteks terstruktur tanpa kesalahan klasifikasi.
