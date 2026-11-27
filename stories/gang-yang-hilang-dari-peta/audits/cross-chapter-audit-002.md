# Audit Ulang Terbatas Kesiapan Penulisan Bab 7–14 — Gang yang Hilang dari Peta (002)

- **Proyek:** `stories/gang-yang-hilang-dari-peta/`
- **Repository / Branch:** `thrdchld/writenovelAI` (`main`)
- **Tanggal Audit Ulang:** 27 November 2026
- **Acuan Sebelumnya:** `stories/gang-yang-hilang-dari-peta/audits/cross-chapter-audit-001.md`
- **Cakupan:** Audit ulang terbatas atas perbaikan blueprint Bab 8–14 terhadap `04-story-outline.md`, `05-decision-log.md`, `state-updates/chapter-001.md` s.d. `chapter-006.md`, dan `blueprint/chapter-007-to-030.md` (Bab 15–30). Tidak ada perubahan pada manuskrip Bab 1–6, dokumen inti, atau kode Python.

## 1. Daftar File yang Diubah / Ditambahkan

1. `stories/gang-yang-hilang-dari-peta/blueprint/chapter-008.md` (`AUD-04`)
2. `stories/gang-yang-hilang-dari-peta/blueprint/chapter-009.md` (`AUD-07`)
3. `stories/gang-yang-hilang-dari-peta/blueprint/chapter-010.md` (`AUD-01` Opsi A + `AUD-07`)
4. `stories/gang-yang-hilang-dari-peta/blueprint/chapter-011.md` (`AUD-04`)
5. `stories/gang-yang-hilang-dari-peta/blueprint/chapter-012.md` (`AUD-06`)
6. `stories/gang-yang-hilang-dari-peta/blueprint/chapter-013.md` (`AUD-02`)
7. `stories/gang-yang-hilang-dari-peta/blueprint/chapter-014.md` (`AUD-03`)
8. `stories/gang-yang-hilang-dari-peta/audits/cross-chapter-audit-002.md` (laporan audit ulang ini)

## 2. Status Temuan dari Audit 001

### Sudah Diselesaikan
- **`AUD-01` (`CRITICAL`) — Selesai (Opsi A):** `blueprint/chapter-010.md` (Adegan 2) direvisi agar Yuni mengenali dokumen 2011 dan tampak terguncang, tetapi menolak menjelaskan dan mengelak tanpa mengakui janji sementara/enam bulan. Selaras penuh dengan `04-story-outline.md` Bab 10 (*Yuni menolak menjelaskan*) dan `blueprint/chapter-007-to-030.md` Bab 15 (*Yuni yang sebelumnya mengelak di Bab 10 akhirnya mengakui*).
- **`AUD-02` (`HIGH`) — Selesai:** `blueprint/chapter-013.md` diperbarui dengan menambahkan `Dimas` ke `Tokoh hadir` Adegan 1 dan menspesifikkan `Informasi yang ditahan` Adegan 2 menjadi nama pelanggan resmi pada meter lama sebelum 2012 serta dua rumah tetangga (menghormati fakta kanon Bab 6 bahwa Salma sudah mengetahui nama **Rudianto** pada kuitansi listrik 2012–2018).
- **`AUD-03` (`HIGH`) — Selesai:** Jembatan `blueprint/chapter-014.md` diubah agar mengarah ke keputusan Salma menemui Yuni sore harinya (16 Agustus, 16.00) dengan membawa sketsa dampak dinding penahan terhadap lorong akses (Bab 15).
- **`AUD-04` (`MEDIUM`, Bab 8 & 11) — Selesai:** `Tokoh hadir` Adegan 2 `blueprint/chapter-008.md` diubah menjadi `Salma, Bu Rukmini` dan `Tokoh hadir` Adegan 2 `blueprint/chapter-011.md` diubah menjadi `Salma, Niken` (keterangan telepon dipindah ke `Situasi awal`).
- **`AUD-06` (`MEDIUM`) — Selesai:** Jembatan Bab 12 → Bab 13 pada `blueprint/chapter-012.md` diperhalus agar tidak menyimpulkan janji Hadi tidak pernah dituntaskan hanya karena ketiadaan catatan tindak lanjut.
- **`AUD-07` (`MEDIUM`) — Selesai:** Nama kolom kanon Bab 1 (*Pemeriksa dan Pengantar Permohonan — Lingkungan Hidup Kelurahan*) dicantumkan konsisten pada `blueprint/chapter-009.md` dan `blueprint/chapter-010.md`.

### Masih Tersisa (Disengaja / Non-Pemblokir)
- **`AUD-04` (`MEDIUM`, Bab 2 & Bab 5):** Label `koordinator proyek` pada `blueprint/chapter-002.md` dan `chapter-005.md` sengaja tidak diubah karena manuskrip dan State Update Bab 2 & Bab 5 sudah selesai dan konsisten memakai nama kanon **Pak Rendy**.
- **`AUD-05` (`MEDIUM`):** Tanggal kanon dan hierarki tenggat (21 hari / 25 Agustus; pengesahan internal 17 Agustus; evaluasi klien 20 Agustus) dipertahankan tanpa perubahan; cukup dijaga kejelasannya saat penulisan Bab 14 & Bab 17.
- **`AUD-08` (`LOW`):** Pembulatan `1,2 meter` pada catatan lapangan Bab 4 tidak diubah (manuskrip Bab 1–6 tidak disentuh); angka ukur kanonis tetap `1,22 meter`.
- **`AUD-09` (`LOW`):** Pengulangan penjelasan batas kewenangan di Bab 2–6 menjadi perhatian gaya penulisan untuk Bab 7–14.
- **`AUD-10` (`LOW`):** Tokoh figuran Bab 4 & 6 (*Pak Haris*, *Bu Lastri*, *Rudianto*) tetap dirujuk lewat State Update Bab 4 & 6.
- **`AUD-11` (`LOW`):** Teks penutup generik dan kotak centang `Audit silang` / `Audit kelayakan teknis` pada blueprint Bab 2–14 dibiarkan tidak dicentang sepihak.

## 3. Hasil Pengujian yang Benar-Benar Dijalankan

| Pengujian | Perintah | Hasil |
|---|---|---|
| Compile Python | `python3 -m compileall -q novel.py novel_engine tests` | **Lulus** (exit code 0, tanpa error) |
| Unit Test Suite | `python3 -m unittest discover -s tests -q` | **Lulus** (`Ran 60 tests in 0.215s — OK`) |
| Audit Deterministik | `python3 novel.py --story gang-yang-hilang-dari-peta audit` | **Lulus** (*Tidak ada masalah struktural sederhana yang terdeteksi*) |
| Agent Status | `python3 novel.py --story gang-yang-hilang-dari-peta agent status` | **Lulus** (`ok: true`, `blueprints_available: 30`, `completed_chapters: 6`) |
| Agent Context 7–14 | `python3 novel.py --story gang-yang-hilang-dari-peta agent context 7..14` | **Lulus** (`ok: true` untuk seluruh 8 bab; profil Bu Rukmini, Niken, dan Dimas terinjeksi tepat) |

## 4. Status `agent context` Bab 7–14

| Bab | `ok` | `present_characters` | `present_profiles` (Bagian 4A) | `conflicts` (Kontinuitas) |
|---|---|---|---|---|
| **Bab 7** | `true` | `Salma, Sari, Dimas, Yuni` | `Salma, Sari, Dimas, Yuni` | `0` (Bab 6 lengkap) |
| **Bab 8** | `true` | `Salma, Pak Bowo, Bu Rukmini` | `Salma, Pak Bowo, Bu Rukmini` (**terinjeksi**) | `2` (wajar: Bab 7 belum ditulis) |
| **Bab 9** | `true` | `Salma, Staf kelurahan` | `Salma` | `2` (wajar: Bab 8 belum ditulis) |
| **Bab 10** | `true` | `Salma, Staf kelurahan, Yuni` | `Salma, Yuni` | `2` (wajar: Bab 9 belum ditulis) |
| **Bab 11** | `true` | `Salma, Staf kelurahan, Niken` | `Salma, Niken` (**terinjeksi**) | `2` (wajar: Bab 10 belum ditulis) |
| **Bab 12** | `true` | `Salma, Niken` | `Salma, Niken` | `2` (wajar: Bab 11 belum ditulis) |
| **Bab 13** | `true` | `Salma, Sari, Dimas` | `Salma, Sari, Dimas` (**terinjeksi**) | `2` (wajar: Bab 12 belum ditulis) |
| **Bab 14** | `true` | `Salma, Dito, Dimas` | `Salma, Dito, Dimas` | `2` (wajar: Bab 13 belum ditulis) |

## 5. Status Kesiapan Bab 7–14 Setelah Perbaikan

Seluruh **8 bab (Bab 7 sampai Bab 14)** kini berstatus **SIAP DITULIS** secara berurutan menggunakan Python Agent Interface, tanpa kontradiksi baru terhadap `04-story-outline.md`, `05-decision-log.md`, State Update Bab 1–6, maupun `blueprint/chapter-007-to-030.md` (Bab 15–30):
- **Bab 7:** Siap ditulis langsung (`agent context 7` memiliki `0 conflicts`).
- **Bab 8–14:** Siap ditulis secara berurutan setelah bab sebelumnya memiliki manuskrip dan State Update yang lulus `agent validate`.

## 6. Risiko & Ketidakpastian yang Tetap Perlu Dijaga Saat Penulisan

1. **Ritme kunjungan ke kantor kelurahan (Bab 9, 10, 11, 16):** Karena ada tiga kunjungan berturut-turut pada Bab 9–11 (plus Bab 16), penulis perlu membedakan fokus tiap kunjungan agar dialog dengan staf kelurahan tidak terasa repetitif atau terlalu ekspositori.
2. **Batas tanggal foto Bab 7:** Foto kerja bakti hanya menampilkan tahun/tidak bertanggal lengkap; penulis Bab 7 harus menjaga agar tidak melompat menyimpulkan tahun 2011 dari foto saja sebelum arsip Bab 9.
3. **Kejelasan hierarki tenggat (`AUD-05`):** Saat menulis Bab 14 (16 Agustus), selipkan secara wajar bahwa rapat pengesahan besok (17 Agustus) merupakan tahapan internal menuju tenggat keseluruhan 21 hari (25 Agustus).
4. **Kepatuhan angka ukur kanonis:** Gunakan `1,22 meter` untuk setiap catatan teknis/dokumen pada Bab 7–14 (hindari pembulatan `1,2 meter` pada catatan tertulis).

## 7. Rekomendasi Langkah Berikutnya

Mulai pengujian penulisan berurutan **batch berikutnya dari Bab 7** menggunakan alur standar Python Agent Interface (`agent context 7` → penulisan manuskrip & State Update Bab 7 → `agent validate 7`), lalu lanjutkan satu per satu ke Bab 8 dan seterusnya.
