# Audit Silang Cerita & Audit Kesiapan Penulisan — Gang yang Hilang dari Peta (001)

- **Proyek:** `stories/gang-yang-hilang-dari-peta/`
- **Repository / Branch:** `thrdchld/writenovelAI` (`main`)
- **Tanggal Audit:** 27 November 2026
- **Cakupan Dokumen yang Dibaca Utuh:**
  - Dokumen inti: `00-premise.md`, `01-concept.md`, `02-characters.md`, `03-world-and-rules.md`, `04-story-outline.md`, `05-decision-log.md`.
  - Bab 1–6 lengkap: `blueprint/chapter-001.md` s.d. `chapter-006.md`, `manuscript/chapter-001.md` s.d. `chapter-006.md`, `state-updates/chapter-001.md` s.d. `chapter-006.md`.
  - Blueprint lanjutan: `blueprint/chapter-007.md` s.d. `chapter-014.md` serta `blueprint/chapter-007-to-030.md` (Bab 15–30).
- **Status Audit:** Audit murni (hanya pelaporan; tidak ada perubahan manuskrip, blueprint, outline, karakter, Decision Log, atau kode Python).

---

## 1. Ringkasan Hasil Audit

Secara umum, **fondasi Bab 1–6 sudah konsisten secara kronologi, batas pengetahuan tokoh, dan mekanisme misteri**, serta lulus seluruh pengujian deterministik Python (`compileall`, 60/60 `unittest`, `novel.py audit`, dan `agent validate 1–6`). Urutan penyajian *in medias res* Bab 1 (17 Agustus 2026) yang mundur ke Bab 2–6 (4–8 Agustus 2026) tersambung rapi tanpa kebocoran pengetahuan masa depan.

Namun, **audit silang menemukan masalah nyata pada kesiapan blueprint Bab 7–14** yang tidak terdeteksi oleh audit deterministik Python karena bersifat semantik antar-dokumen. Tiga blueprint (**Bab 10, Bab 13, dan Bab 14**) belum siap ditulis sebelum diperbaiki, dan dua blueprint lain (**Bab 8 dan Bab 11**) memiliki ketidakcocokan format nama tokoh terhadap parser `novel_engine.agent`.

### Ringkasan Jumlah Temuan per Tingkat Prioritas
- **CRITICAL:** 1 temuan (`AUD-01`: kontradiksi pengakuan Yuni di `blueprint/chapter-010.md` vs `04-story-outline.md` & `blueprint/chapter-007-to-030.md` Bab 15).
- **HIGH:** 2 temuan (`AUD-02`: konflik fakta pelanggan listrik di `blueprint/chapter-013.md` vs Bab 6; `AUD-03`: jembatan Bab 14 → Bab 15 di `blueprint/chapter-014.md` salah arah).
- **MEDIUM:** 4 temuan (`AUD-04`: penamaan tokoh tidak dikenali parser `agent context` pada Bab 2, 5, 8, 11; `AUD-05`: relasi tenggat 21 hari vs 17 Agt vs 20 Agt belum dijabarkan eksplisit; `AUD-06`: ketidakpastian vs kesimpulan pada jembatan Bab 12 → Bab 13; `AUD-07`: sinkronisasi nama kolom tanda tangan Hadi di Bab 9–10 dengan Bab 1 & 16).
- **LOW:** 4 temuan (`AUD-08`: pembulatan `1,2 meter` vs `1,22 meter` di catatan lapangan Bab 4; `AUD-09`: pengulangan penjelasan batas kewenangan Salma pada Bab 2–6; `AUD-10`: tokoh figuran Bab 4 & 6 belum terindeks; `AUD-11`: teks penutup generik dan kotak centang kesiapan pada blueprint Bab 2–14).

### Ringkasan Kesiapan Penulisan Bab 7–14
- **Siap dengan catatan penyelarasan minor (3 bab):** Bab 7, Bab 9, Bab 12.
- **Belum siap — perlu perbaikan sebelum ditulis (5 bab):** Bab 8 (`MEDIUM` parser), Bab 10 (`CRITICAL` kontradiksi), Bab 11 (`MEDIUM` parser & risiko repetisi), Bab 13 (`HIGH` konflik fakta Bab 6 & tokoh Adegan 1), Bab 14 (`HIGH` jembatan Bab 15).

---

## 2. Temuan Kritis (`CRITICAL`)

### AUD-01 — Kontradiksi Pengakuan Yuni antara Blueprint Bab 10, Outline Bab 10, dan Blueprint Bab 15
- **Tingkat Prioritas:** `CRITICAL`
- **Lokasi File & Bab:**
  - `stories/gang-yang-hilang-dari-peta/blueprint/chapter-010.md` (Adegan 2 — *Pertanyaan kepada ibu*)
  - `stories/gang-yang-hilang-dari-peta/04-story-outline.md` (baris Bab 10 & Bab 15)
  - `stories/gang-yang-hilang-dari-peta/blueprint/chapter-007-to-030.md` (Bab 15, Adegan 1)
- **Bukti / Kutipan Singkat:**
  - `blueprint/chapter-010.md`: *"Yuni mengenali dokumen; ia berkata Hadi pernah berjanji bahwa perubahan itu hanya sementara; ia tidak tahu siapa yang menyusun peta; ia meminta Salma tidak membuat kesimpulan sebelum melihat catatan lain."*
  - `04-story-outline.md` (Bab 10): *"Lampiran menunjukkan Hadi menandatangani perubahan yang mencatat tiga rumah sebagai bangunan penyimpanan sementara; Yuni menolak menjelaskan."*
  - `blueprint/chapter-007-to-030.md` (Bab 15, Adegan 1): *"Yuni yang sebelumnya mengelak (Bab 10) akhirnya mengakui bahwa setelah banjir 2011, Hadi pernah bercerita di rumah bahwa tiga keluarga di halaman belakang hanya diberi waktu sementara—sekitar enam bulan..."*
- **Klasifikasi Auditor:** **Fakta terbukti** (kontradiksi teks langsung antar tiga dokumen kanon rancangan).
- **Penjelasan Masalah:** `blueprint/chapter-010.md` membuat Yuni sudah mengakui janji sementara Hadi pada 12 Agustus, padahal outline Bab 10 dan blueprint Bab 15 secara eksplisit mensyaratkan Yuni masih menolak/mengelak di Bab 10 dan baru membuka pengakuan soal janji sementara (enam bulan) pada Bab 15 (16 Agustus).
- **Dampak terhadap Cerita:** Jika Bab 10 ditulis mengikuti `blueprint/chapter-010.md`, perkembangan hubungan Salma–Yuni melompat terlalu cepat, momen pengakuan Yuni di Bab 15 menjadi redundan, dan kalimat *"sebelumnya mengelak (Bab 10)"* di Bab 15 menjadi keliru.
- **Rekomendasi Tindakan:** Memerlukan **keputusan struktural ringan** (pilih satu dan selaraskan): (Opsi disarankan) pertahankan `04-story-outline.md` & Bab 15 — revisi Adegan 2 `blueprint/chapter-010.md` agar Yuni mengenali dokumen namun menolak menjelaskan/mengelak sehingga pengakuan janji enam bulan tetap menjadi titik balik Bab 15.

---

## 3. Temuan Penting (`HIGH` & `MEDIUM`)

### AUD-02 — Konflik Informasi yang Ditahan di Blueprint Bab 13 terhadap Fakta Kanon Bab 6
- **Tingkat Prioritas:** `HIGH`
- **Lokasi File & Bab:**
  - `stories/gang-yang-hilang-dari-peta/blueprint/chapter-013.md` (Adegan 1 & Adegan 2)
  - `stories/gang-yang-hilang-dari-peta/manuscript/chapter-006.md` & `state-updates/chapter-006.md`
- **Bukti / Kutipan Singkat:**
  - `blueprint/chapter-013.md` (Adegan 2 — *Jejak sambungan*): *"Informasi yang ditahan: Siapa nama pelanggan resmi."*
  - `state-updates/chapter-006.md`: *"Belasan lembar kuitansi pembayaran listrik rentang 2012–2018 ... atas nama Rudianto."*
  - `blueprint/chapter-013.md` (Adegan 1): `Tokoh hadir: Salma, Sari`, namun di `Urutan kejadian` tertulis *"Dimas mengoreksi satu tahun berdasarkan usia sekolahnya."*
- **Klasifikasi Auditor:** **Fakta terbukti** (konflik langsung dengan fakta kanon Bab 6 yang sudah tertulis dan tervalidasi).
- **Penjelasan Masalah:** Pertama, pada 8 Agustus (Bab 6), Salma sudah mengetahui dan mencatat nama pelanggan di kuitansi listrik 2012–2018 adalah Rudianto (kakak Sari). Menahan *"Siapa nama pelanggan resmi"* di Bab 13 (15 Agustus) akan membuat Salma seolah melupakan temuan Bab 6, kecuali yang dimaksud khusus adalah pelanggan *sebelum 2012* atau pelanggan dua rumah lain (Pak Haris / Bu Lastri). Kedua, Dimas berbicara di Adegan 1 padahal tidak tercantum di `Tokoh hadir` Adegan 1.
- **Dampak terhadap Cerita:** Risiko kontradiksi memori tokoh POV (Salma) terhadap Bab 6 serta kekeliruan batas kehadiran tokoh pada `agent context 13`.
- **Rekomendasi Tindakan:** Perbaiki `blueprint/chapter-013.md` sebelum menulis Bab 13: spesifikkan bahwa yang belum terkonfirmasi di Adegan 2 adalah *nama pelanggan resmi pada meter lama sebelum 2012 atau pada dua rumah tetangga*, dan tambahkan `Dimas` ke `Tokoh hadir` Adegan 1.

### AUD-03 — Jembatan Bab 14 Menuju Bab 15 Salah Arah
- **Tingkat Prioritas:** `HIGH`
- **Lokasi File & Bab:**
  - `stories/gang-yang-hilang-dari-peta/blueprint/chapter-014.md` (`Posisi cerita` & `Penutup bab`)
  - `stories/gang-yang-hilang-dari-peta/blueprint/chapter-007-to-030.md` (Bab 15)
- **Bukti / Kutipan Singkat:**
  - `blueprint/chapter-014.md`: *"Jembatan menuju bab berikutnya: Bab 15 membuat konflik warga dengan proyek menjadi langsung."*
  - `blueprint/chapter-007-to-030.md` (Bab 15): Lokasi *Rumah Yuni*, Tokoh hadir *Salma, Yuni*, Kondisi awal: *"Salma baru saja memastikan bersama Dito (Bab 14) bahwa rancangan dinding penahan akan mengganggu akses lorong 1,22 meter."*
- **Klasifikasi Auditor:** **Fakta terbukti**.
- **Penjelasan Masalah:** Jembatan pada `blueprint/chapter-014.md` masih merujuk pada rancangan lama sebelum penyelarasan Bab 15. Konflik warga langsung dengan proyek justru sudah dimulai di Adegan 2 Bab 14 (Dimas melihat patok), sedangkan Bab 15 adalah Salma membawa sketsa dampak dinding penahan tersebut kepada Yuni.
- **Dampak terhadap Cerita:** Penulis Bab 14 dapat menutup bab dengan pemicu yang keliru (menjanjikan pertemuan warga–proyek di Bab 15), padahal Bab 15 berfokus pada percakapan Salma–Yuni.
- **Rekomendasi Tindakan:** Perbarui jembatan `blueprint/chapter-014.md` agar mengarah ke keputusan Salma menemui Yuni sore harinya (16 Agustus 16.00) membawa sketsa dampak dinding penahan.

### AUD-04 — Label Tokoh di Blueprint Bab 2, 5, 8, dan 11 Tidak Terdeteksi oleh Parser `novel_engine.agent`
- **Tingkat Prioritas:** `MEDIUM`
- **Lokasi File & Bab:**
  - `blueprint/chapter-002.md` & `blueprint/chapter-005.md` (`koordinator proyek`)
  - `blueprint/chapter-008.md` (`warga lama bernama Bu Rukmini`)
  - `blueprint/chapter-011.md` (`Niken melalui telepon`)
- **Bukti / Kutipan Singkat:**
  - Hasil `agent context 8`: `present_raw=['Salma', 'Pak Bowo', 'warga lama bernama Bu Rukmini']` → `present_profiles=['Salma', 'Pak Bowo']` (`Bu Rukmini` jatuh ke `non_present_characters`).
  - Hasil `agent context 11`: `present_raw=['Salma', 'Staf kelurahan', 'Niken melalui telepon']` → `present_profiles=['Salma']` (`Niken` jatuh ke `non_present_characters`).
  - Hasil `agent context 5`: `present_raw=['Salma', 'Dito', 'Koordinator proyek']` → `present_profiles=['Salma', 'Dito']` (`Pak Rendy` jatuh ke `non_present_characters`).
- **Klasifikasi Auditor:** **Fakta terbukti** (diverifikasi langsung melalui eksekusi `novel.py agent context`).
- **Penjelasan Masalah:** Parser karakter mencocokkan nama pada baris `Tokoh hadir` terhadap heading `02-characters.md`. Frasa deskriptif tambahan menyebabkan profil tokoh hadir tidak terinjeksi ke Bagian 4A paket konteks.
- **Dampak terhadap Cerita:** Saat menulis Bab 8 dan Bab 11 melalui Python Agent Interface, AI penulis tidak otomatis menerima profil **Bu Rukmini** dan **Niken** di seksi tokoh hadir.
- **Rekomendasi Tindakan:** Sebelum menulis Bab 8 dan Bab 11, ubah `Tokoh hadir` di `blueprint/chapter-008.md` menjadi `Salma, Bu Rukmini` dan di `blueprint/chapter-011.md` menjadi `Salma, Niken` (keterangan *"melalui telepon"* dipindah ke `Situasi awal`). Untuk Bab 2 & 5 bersifat opsional karena manuskripnya sudah selesai dan konsisten memakai nama `Pak Rendy`.

### AUD-05 — Hubungan Tenggat 21 Hari (Bab 2) vs 17 Agustus (Bab 1) vs 20 Agustus (Bab 1 & 23) Belum Dijelaskan Eksplisit
- **Tingkat Prioritas:** `MEDIUM`
- **Lokasi File & Bab:** `manuscript/chapter-002.md`, `manuscript/chapter-001.md`, `manuscript/chapter-005.md`, `04-story-outline.md`.
- **Bukti / Kutipan Singkat:**
  - `manuscript/chapter-002.md` (4 Agt): *"Tenggat kita dua puluh satu hari"* (4 Agt + 21 hari = **25 Agustus 2026**).
  - `manuscript/chapter-005.md` (7 Agt): *"draf gambar final segmen barat sudah dijadwalkan masuk tahap peninjauan minggu depan."*
  - `manuscript/chapter-001.md` (17 Agt): *"tenggat pengesahan dokumen segmen barat ditetapkan hari ini, pukul 16.00"* → ditunda menjadi *"sebelum Kamis pagi"* (**20 Agustus 2026**) untuk rapat evaluasi klien.
- **Klasifikasi Auditor:** **Fakta terbukti** (tanggal kalender cocok) + **Interpretasi auditor** (bukan kontradiksi, tetapi hierarki tenggat masih implisit).
- **Penjelasan Masalah:** Pada kalender nyata Agustus 2026: 4 Agt = Selasa, 7 Agt = Jumat, 17 Agt = Senin, 20 Agt = Kamis, 25 Agt = Selasa. Artinya ketiga tenggat **tidak saling bertentangan**: 25 Agustus (21 hari) adalah tenggat keseluruhan verifikasi lapangan segmen barat dari dinas, 17 Agustus adalah batas internal pengesahan segmen barat sebelum evaluasi, dan 20 Agustus adalah rapat evaluasi klien. Namun, pembaca yang teliti bisa mengira 17 Agt menyalahi "21 hari" jika hierarki ini tidak diperjelas.
- **Dampak terhadap Cerita:** Tidak merusak plot, tetapi memperjelas hierarki tenggat pada Bab 14/17 (atau catatan kontinuitas) akan mengunci logika jadwal agar bebas tafsir ganda.
- **Rekomendasi Tindakan:** Pertahankan seluruh tanggal yang ada; cukup tegaskan secara natural di Bab 14 atau Bab 17 bahwa pengesahan internal 17 Agustus dan evaluasi klien 20 Agustus adalah tahapan menuju tenggat final 21 hari (25 Agustus).

### AUD-06 — Pergeseran Makna "Tidak Ada Catatan" Menjadi "Janji Tidak Pernah Dituntaskan" di Blueprint Bab 12
- **Tingkat Prioritas:** `MEDIUM`
- **Lokasi File & Bab:** `stories/gang-yang-hilang-dari-peta/blueprint/chapter-012.md` (`Posisi cerita` & `Adegan 2`).
- **Bukti / Kutipan Singkat:**
  - `Adegan 2`: *"Jangan menyamakan tidak adanya catatan dengan bukti tidak ada tindakan sama sekali."*
  - `Posisi cerita` & `Penutup bab`: *"Jembatan menuju bab berikutnya: Bab 13 menunjukkan bahwa janji itu tidak pernah dituntaskan."*
- **Klasifikasi Auditor:** **Fakta terbukti** + **Interpretasi auditor**.
- **Penjelasan Masalah:** Ada ketegangan kecil di dalam `blueprint/chapter-012.md` sendiri: Adegan 2 berhati-hati menjaga agar ketiadaan catatan tidak langsung disimpulkan sebagai ketiadaan tindakan, tetapi teks jembatan menuju Bab 13 langsung menyimpulkan *"janji itu tidak pernah dituntaskan"*. Secara pembuktian, Bab 13 hanya menunjukkan bahwa *rumah tetap dihuni tanpa perubahan status peta*, bukan membuktikan apakah Hadi pernah mengajukan koreksi yang kemudian macet di kelurahan.
- **Dampak terhadap Cerita:** Risiko Salma melompat pada kesimpulan terlalu dini sebelum Bab 16 & Bab 21.
- **Rekomendasi Tindakan:** Perhalus kalimat jembatan Bab 12 → Bab 13 menjadi *"Bab 13 menguji kesinambungan hunian warga pasca-2011 dan memastikan belum ada perubahan status peta yang tercatat bagi mereka"*, sembari tetap mempertahankan `D-001` sebagai kebenaran kanon di lapisan penulis.

### AUD-07 — Penamaan Kolom Tanda Tangan Hadi Belum Disinkronkan di Blueprint Bab 9–10
- **Tingkat Prioritas:** `MEDIUM`
- **Lokasi File & Bab:** `blueprint/chapter-009.md`, `blueprint/chapter-010.md` vs `manuscript/chapter-001.md` & `blueprint/chapter-007-to-030.md` (Bab 16).
- **Bukti / Kutipan Singkat:**
  - `manuscript/chapter-001.md`: `*Pemeriksa dan Pengantar Permohonan — Lingkungan Hidup Kelurahan.* ... **HADI WIBOWO.**`
  - `blueprint/chapter-009.md` & `chapter-010.md`: hanya menyebut *"pengantar lingkungan"* / *"tanda tangan pengantar Hadi"*.
- **Klasifikasi Auditor:** **Fakta terbukti**.
- **Penjelasan Masalah:** Bab 1 (yang sudah menjadi manuskrip kanon) dan Bab 16 sudah menetapkan bunyi kolom persis (*Pemeriksa dan Pengantar Permohonan*). Blueprint Bab 9–10 belum mencantumkan bunyi kolom tersebut sebagai detail wajib.
- **Dampak terhadap Cerita:** Risiko ketidakkonsistenan istilah administratif ketika Bab 9–10 ditulis.
- **Rekomendasi Tindakan:** Tambahkan bunyi kolom kanon (*Pemeriksa dan Pengantar Permohonan — Lingkungan Hidup Kelurahan*) ke catatan penulisan/detail wajib Bab 9–10 sebelum penulisan.

---

## 4. Temuan Minor (`LOW`)

### AUD-08 — Pembulatan `1,2 meter` pada Catatan Lapangan Tertulis Bab 4 vs `1,22 meter` Kanonis
- **Tingkat Prioritas:** `LOW`
- **Lokasi File & Bab:** `manuscript/chapter-004.md` (baris 37) vs `manuscript/chapter-003.md` & `manuscript/chapter-005.md`.
- **Bukti / Kutipan Singkat:** Di Bab 3, Dito mengukur `Satu koma dua dua meter` (`1,22 m`). Di Bab 4, Salma berkata: *"Di catatan lapangan, saya tulis saja ... terhubung lewat lorong selebar satu koma dua meter."* Di Bab 5, angka kembali persis `1,22 meter`.
- **Klasifikasi Auditor:** **Fakta terbukti**.
- **Penjelasan & Dampak:** Pembulatan informal *"sekitar satu koma dua meter"* dalam dialog lisan (Bab 1, Bab 4) wajar, namun pada kalimat kutipan catatan tertulis di Bab 4 lebih presisi bila merujuk `1,22 meter`. Tidak merusak kontinuitas karena Bab 5 langsung memakai `1,22 meter`.
- **Rekomendasi Tindakan:** Jangan ubah data ukur kanonis (`1,22 meter`). Untuk bab selanjutnya (Bab 7–30), gunakan `1,22 meter` untuk setiap catatan teknis/dokumen, dan boleh memakai `sekitar 1,2 meter` hanya dalam dialog informal.

### AUD-09 — Pengulangan Penjelasan Batas Kewenangan Salma pada Bab 2–6
- **Tingkat Prioritas:** `LOW`
- **Lokasi File & Bab:** `manuscript/chapter-002.md` s.d. `chapter-006.md`.
- **Bukti / Kutipan Singkat:** Batasan *"bukan penentu hak tanah / tidak bisa menjanjikan kompensasi / hanya teknisi pemetaan"* diulang eksplisit di Bab 2 (Pak Rendy), Bab 3 (Salma ke Dimas), Bab 4 (Salma ke Sari), Bab 5 (Dito & Salma), dan Bab 6 (Salma ke Sari).
- **Klasifikasi Auditor:** **Interpretasi auditor** (penilaian kualitas bacaan).
- **Penjelasan & Dampak:** Secara logika situasi masuk akal karena lawan bicara berbeda, tetapi bila dibaca berurutan dari Bab 2 ke Bab 6 terasa sedikit repetitif.
- **Rekomendasi Tindakan:** Pada Bab 7–14, sampaikan batas kewenangan secara lebih ringkas atau lewat tindakan/sikap Salma agar tidak mengulang kalimat yang sama di setiap bab.

### AUD-10 — Tokoh Figuran Bab 4 & Bab 6 Belum Tercatat di Indeks Karakter
- **Tingkat Prioritas:** `LOW`
- **Lokasi File & Bab:** `manuscript/chapter-004.md` (*Pak Haris*, *Bu Lastri*), `manuscript/chapter-006.md` (*Rudianto*), dan `02-characters.md`.
- **Klasifikasi Auditor:** **Fakta terbukti**.
- **Penjelasan & Dampak:** Ketiga nama tersebut muncul konsisten di manuskrip dan State Update Bab 4 & 6. Tidak wajib memiliki profil penuh di `02-characters.md`, tetapi perlu diingat saat menulis Bab 13, 19, dan 29 agar tidak terganti nama secara tidak sengaja.
- **Rekomendasi Tindakan:** Pertahankan nama-nama tersebut melalui rujukan `state-updates/chapter-004.md` dan `chapter-006.md` (opsional: tambahkan catatan ringkas tokoh pendukung di `02-characters.md` bila diperlukan di tahap pemolesan).

### AUD-11 — Template Penutup Generik & Kotak Centang Kesiapan Belum Diperbarui pada Blueprint Bab 2–14
- **Tingkat Prioritas:** `LOW`
- **Lokasi File & Bab:** `blueprint/chapter-002.md` s.d. `chapter-014.md`.
- **Bukti / Kutipan Singkat:** Bagian `Penutup bab` pada Bab 2–14 memuat kalimat generik *"Salma memiliki satu informasi, keputusan, atau konsekuensi baru yang mengubah langkah berikutnya"*, dan dua kotak centang (`Audit silang dengan seluruh bab`, `Audit kelayakan teknis dan prosedural`) masih `[ ]`.
- **Klasifikasi Auditor:** **Fakta terbukti**.
- **Penjelasan & Dampak:** Tidak mengganggu penulisan Bab 2–6 (karena Adegan 1 & 2 sudah spesifik), tetapi pada Bab 7–14 sebaiknya kotak centang hanya dicentang setelah temuan `AUD-01` s.d. `AUD-07` diperbaiki.
- **Rekomendasi Tindakan:** Perbarui kotak centang kesiapan Bab 7–14 hanya setelah perbaikan pada Bagian 10 selesai diterapkan.

---

## 5. Tabel Konsistensi Bab 1–6

| Bab | Waktu & Hari (Kalender 2026) | Urutan Penyajian | Konsistensi Pengetahuan Tokoh | Kesesuaian State Update vs Manuskrip | Status Konsistensi |
|---|---|---|---|---|---|
| **Bab 1** | 17 Agt (Senin), 14.00–14.35 | Pembuka *in medias res* | **Konsisten:** Salma sudah tahu keterlibatan Hadi (pasca-Bab 9–16), menahan berkas 2011 di rapat, baru mengaku ke Dito setelah Pak Rendy keluar; Pak Rendy tidak tahu. | **Sesuai penuh:** Memuat penundaan segmen, tenggat Kamis 20 Agt, pengakuan Salma–Dito, dan niat cek catatan pribadi Hadi. | **Konsisten** |
| **Bab 2** | 4 Agt (Selasa), 09.00–10.30 | Kilas balik #1 | **Konsisten:** Salma & Dito belum tahu soal 3 rumah/2011; Yuni waspada tanpa membocorkan rahasia; Hadi hanya disebut pernah aktif di lingkungan. | **Sesuai penuh:** Tenggat 21 hari, ruang lingkup teknis, peta lama dinas, reaksi Yuni terekam akurat. | **Konsisten** (catatan `AUD-05` tenggat) |
| **Bab 3** | 5 Agt (Rabu), 08.00–11.00 | Kilas balik #2 | **Konsisten:** Pak Bowo tahu lorong dipakai warga; Salma & Dito baru menemukan lorong `1,22 m`; Dimas menolak foto/data, memberi keterangan lisan ada rumah. | **Sesuai penuh:** Angka `3,2 m`, `60 cm`, `1,22 m`, dan pembedaan fakta fisik vs keterangan lisan Dimas terekam tepat. | **Konsisten** |
| **Bab 4** | 6 Agt (Kamis), 15.00–17.00 | Kilas balik #3 | **Konsisten:** Salma baru melihat 3 rumah & baru mendengar ada pendataan lama dari Dimas; Sari menolak dokumen asli; belum ada bahasan 2011/Hadi. | **Sesuai penuh:** Seluruh detail halaman bersama, Sari, Pak Haris/Bu Lastri (lisan), syarat salinan tertulis terekam akurat. | **Konsisten** (catatan minor `AUD-08` `1,2 m`) |
| **Bab 5** | 7 Agt (Jumat), 09.00–12.00 | Kilas balik #4 | **Konsisten:** Dito & Salma memakai istilah netral; Pak Rendy tidak tahu soal Hadi/2011, meminta bukti bertanggal dan melarang ubah peta sendiri. | **Sesuai penuh:** Formulir anomali, istilah *"bangunan eksisting tidak terpetakan"*, larangan ubah peta, tenggat minggu depan. | **Konsisten** (catatan `AUD-04` label blueprint) |
| **Bab 6** | 8 Agt (Sabtu), 10.00–13.00 | Kilas balik #5 | **Konsisten:** Salma hanya mendapat foto kuitansi 2012–2018 (nama Rudianto), iuran, nota 2014; Sari tidak hafal semua tanggal; tidak ada bocoran 2011/Hadi. | **Sesuai penuh:** Daftar dokumen, keterangan lisan Rudianto pindah 2016, dan status *belum terkonfirmasi* sebelum Mei 2012 terekam tepat. | **Konsisten** |

---

## 6. Tabel Kesiapan Blueprint Bab 7–14

| Bab | Judul & Waktu | Kausalitas & Transisi | Kesiapan Adegan & Batas Pengetahuan | Keselarasan dengan Bab 15–30 | Status Kesiapan | Catatan Kunci |
|---|---|---|---|---|---|---|
| **Bab 7** | *Foto Sebelum Tembok* (9 Agt, 14.00–16.30) | Kuat: menjawab celah sebelum Mei 2012 dari Bab 6. | Cukup; batas pengetahuan Yuni & tanggal foto terjaga. | Baik: menanam awal kecurigaan personal Salma menuju Bab 9–10. | **Siap (Catatan Minor)** | Pastikan foto tidak mencantumkan tanggal lengkap yang mendahului Bab 8–9. |
| **Bab 8** | *Orang yang Mengingat Banjir* (10 Agt, 08.00–11.00) | Kuat: menguji foto Bab 7 lewat 2 saksi berbeda. | Baik secara dramatik, tetapi label `Tokoh hadir` gagal dikenali parser (`AUD-04`). | Baik: mendorong Salma ke arsip kelurahan (Bab 9). | **Belum Siap** (`MEDIUM`) | Ubah `warga lama bernama Bu Rukmini` → `Bu Rukmini` di `Tokoh hadir`. |
| **Bab 9** | *Berkas yang Tidak Lengkap* (11 Agt, 09.00–12.00) | Kuat: permintaan arsip kelurahan realistis pasca-Bab 8. | Cukup; tidak ada akses instan; nama Hadi baru muncul di indeks. | Baik: menyiapkan pengungkapan lampiran Bab 10 & Bab 16. | **Siap (Catatan Penyelarasan)** | Selaraskan penyebutan kolom kanon Bab 1 (`AUD-07`). |
| **Bab 10** | *Tanda Tangan Ayah* (12 Agt, 13.00–16.00) | Adegan 1 kuat, tetapi Adegan 2 bertabrakan dengan Outline & Bab 15. | **Kontradiksi (`AUD-01`):** Yuni sudah mengaku soal janji sementara di blueprint ini. | **Bentrok dengan Bab 15** (*"Yuni yang sebelumnya mengelak di Bab 10"*). | **Belum Siap** (`CRITICAL`) | Wajib selaraskan Adegan 2 dengan Outline Bab 10 & Bab 15 sebelum ditulis. |
| **Bab 11** | *Istilah Sementara* (13 Agt, 09.00–12.00) | Cukup, tetapi risiko terasa mengulang kunjungan kelurahan Bab 9–10. | Label `Niken melalui telepon` tidak terdeteksi parser (`AUD-04`). | Baik: membuka jalur pertemuan Niken di Bab 12. | **Belum Siap** (`MEDIUM`) | Perbaiki label `Tokoh hadir` → `Niken`; tajamkan tujuan kunjungan ke kelurahan agar bebas repetisi eksposisi. |
| **Bab 12** | *Catatan di Pinggir Buku* (14 Agt, 10.00–13.00) | Kuat: agenda Niken memberi konteks niat penundaan tanpa bukti final. | Adegan 2 sangat tepat membedakan *tiada catatan* vs *tiada tindakan*, tapi teks jembatan ke Bab 13 terlalu menyimpulkan (`AUD-06`). | Baik: langsung dikutip di Bab 15 & Bab 17. | **Siap (Catatan Penyelarasan)** | Perhalus kalimat jembatan menuju Bab 13 agar konsisten dengan Adegan 2. |
| **Bab 13** | *Rumah yang Tidak Pernah Kosong* (15 Agt, 08.00–12.00) | Kuat: triangulasi lisan & fisik pasca-catatan Niken. | **Konflik (`AUD-02`):** Menahan nama pelanggan resmi padahal sudah tahu `Rudianto` di Bab 6; Dimas muncul di Adegan 1 tanpa terdaftar di `Tokoh hadir`. | Baik: menyiapkan kronologi hunian untuk paket Bab 17. | **Belum Siap** (`HIGH`) | Perbaiki `Informasi yang ditahan` Adegan 2 dan `Tokoh hadir` Adegan 1. |
| **Bab 14** | *Garis yang Berbeda* (16 Agt, 09.00–12.00) | Adegan 1–2 sangat kuat (dampak fisik dinding penahan & kecemasan Dimas). | Batas pengetahuan Salma, Dito, dan Dimas terjaga baik. | **Jembatan salah arah (`AUD-03`):** Menyebut Bab 15 konflik warga–proyek, padahal Bab 15 adalah Salma–Yuni. | **Belum Siap** (`HIGH`) | Perbarui jembatan Bab 14 → Bab 15 agar mengarah ke pertemuan Salma–Yuni. |

---

## 7. Penilaian Kualitas Manuskrip Bab 1–6 (Sebagai Bacaan Novel)

- **Kekuatan Utama:**
  - **Nada dan ritme konsisten:** Bab 1–6 memiliki suara narasi yang tenang, konkret, dan membumi—tidak melodramatis, tidak puitis berlebihan, dan tidak terasa seperti ringkasan blueprint yang ditempelkan.
  - **Detail fisik yang menghidupkan ruang:** Peta A1 terlipat dan lampu proyektor menguning (Bab 1), bau tinta biru peta dasar dan panas atap seng (Bab 2), tembok kapur kusam dan bekas ban motor di cor retak (Bab 3), suara mesin jahit listrik Sari dan jemuran di halaman bersama (Bab 4), label kuning *menunggu tinjauan* yang tak mengubah blok abu-abu peta (Bab 5), serta karet gelang getas dan kotak plastik bertutup biru (Bab 6).
  - **Konflik manusia di balik prosedur:** Pertemuan Salma dengan Dimas (Bab 3–4) dan Sari (Bab 4 & 6) terasa manusiawi—warga tidak dibuat langsung percaya atau antagonis karikatural, dan Pak Rendy (Bab 1, 2, 5) tampil realistis sebagai koordinator berbasis jadwal, bukan tokoh jahat.
  - **Daya dorong antarbab:** Setiap bab menutup dengan perubahan keadaan konkret yang wajar tanpa *cliffhanger* buatan (misalnya pengakuan tenang Salma ke Dito di Bab 1, celah tanggal sebelum Mei 2012 di Bab 6).
- **Hal yang Perlu Diperhatikan (Tidak Memblokir, untuk Penulisan Lanjutan):**
  - **Pengulangan deklarasi batas kewenangan (`AUD-09`):** Kalimat mengenai batas kewenangan Salma (*bukan penentu hak tanah / tidak bisa menjanjikan kompensasi*) muncul di Bab 2, 3, 4, 5, dan 6. Pada Bab 7–14 sebaiknya tidak diulang secara verbal penuh kecuali ada pemicu dialog baru.
  - **Keseimbangan dialog teknis di Bab 5:** Adegan 1 Bab 5 (diskusi istilah *"bangunan eksisting tidak terpetakan"* bersama Dito) sedikit mendekati gaya penjelasan prosedural meski masih tertolong oleh penekanan bahwa peta digital tetap tak berubah. Pada Bab 9–11 (serangkaian kunjungan kelurahan), hindari pola dialog tanya-jawab informatif yang terlalu panjang dengan staf arsip.

---

## 8. Penilaian Kelayakan Teknis dan Prosedural

| Aspek Teknis / Prosedural | Penilaian | Catatan & Batas Verifikasi |
|---|---|---|
| **Pengukuran lapangan (Bab 3–4)** | **Layak & realistis** | Menggunakan meteran gulung, titik koordinat, pengukuran jalan (`3,2 m`), selokan (`60 cm`), dan lorong (`1,22 m`). |
| **Dokumentasi koordinat & foto (Bab 3–6)** | **Layak & realistis** | Meminta izin sebelum memotret, menjaga privasi penghuni (tidak memotret wajah/isi rumah), memberi penanda tanggal dan sumber pada foto dokumen. |
| **Pelaporan anomali & larangan ubah peta sepihak (Bab 5)** | **Layak & realistis** | Penggunaan istilah netral *"bangunan eksisting tidak terpetakan"*, sistem tiket/formulir internal, dan larangan mengubah peta kerja dasar tanpa persetujuan koordinator sesuai praktik kerja konsultan pemetaan pada umumnya. |
| **Penggunaan kuitansi, nota, dan kesaksian (Bab 4, 6, 8)** | **Layak & sangat terjaga** | Secara konsisten memisahkan bukti aktivitas hunian dari bukti kepemilikan tanah, memisahkan keterangan lisan dari fakta dokumen, serta mencatat celah tanggal dan perbedaan nama pembayar (*Rudianto*). |
| **Permintaan & pemeriksaan arsip kelurahan (Bab 9–11, 16)** | **Perlu verifikasi kewajaran prosedural ringan** | Alur membawa surat tugas, menunggu pencarian bundel fisik 2011, dan meminta persetujuan atasan kelurahan sebelum menyalin berkas sudah realistis dan bebas akses ajaib. *Catatan auditor (perlu verifikasi):* Salma mendatangi ruang arsip kelurahan empat kali dalam rentang 11–19 Agustus (Bab 9, 10, 11, 16, lalu Bab 21); secara naratif perlu dijaga agar alasan kunjungan Bab 11 dan Bab 16 terasa proporsional dan tidak terlalu dipermudah. |
| **Peninjauan desain & batas kewenangan konsultan (Bab 1, 5, 14)** | **Layak & realistis** | Tim konsultan tidak membatalkan proyek atau memutuskan hak tanah, melainkan mencatat konflik geometri dan mendorong peninjauan desain akses. |

---

## 9. Daftar Masalah yang Membutuhkan Keputusan Struktural

1. **Keputusan untuk `AUD-01` (Bab 10 vs Bab 15 — Arc Pengakuan Yuni):**
   - **Inti keputusan:** Menetapkan secara final kapan Yuni pertama kali mengakui keberadaan *"janji sementara"* Hadi.
   - **Opsi A (Disarankan — selaras dengan `04-story-outline.md` dan `blueprint/chapter-007-to-030.md`):** Yuni tetap **menolak menjelaskan/mengelak** di Bab 10 saat ditunjukkan salinan lampiran 2011 (hanya tampak terguncang dan menutup pembicaraan), lalu baru mengakui soal *"janji enam bulan"* pada Bab 15 setelah Salma membawa sketsa dinding penahan yang mengancam akses tiga rumah.
   - **Opsi B:** Mempertahankan pengakuan awal Yuni di Bab 10, tetapi merevisi `04-story-outline.md` Bab 10 dan `blueprint/chapter-007-to-030.md` Bab 15 agar Bab 15 berfokus pada detail baru (angka "enam bulan" + keberadaan kardus kerja Hadi) tanpa menyebut Yuni sebelumnya mengelak.
2. **Konfirmasi `AUD-05` (Hierarki Tenggat Proyek):**
   - Tidak memerlukan perubahan tanggal kanon (tetap 21 hari/25 Agt, 17 Agt, dan 20 Agt), cukup konfirmasi bahwa 25 Agustus adalah tenggat total proyek dinas sedangkan 17 Agustus (internal) dan 20 Agustus (evaluasi klien) adalah tonggak segmen barat.

---

## 10. Rekomendasi Urutan Perbaikan (Sebelum Menulis Bab 7–14)

Urutan perbaikan disusun dari dampak tertinggi agar penulisan Bab 7–14 berjalan mulus tanpa memicu konflik berantai:

1. **Perbaiki `AUD-01` (`CRITICAL`) pada `blueprint/chapter-010.md`:** Selaraskan Adegan 2 Bab 10 dengan `04-story-outline.md` dan Bab 15 (pilih Opsi A: Yuni mengelak/menolak menjelaskan di Bab 10).
2. **Perbaiki `AUD-02` (`HIGH`) pada `blueprint/chapter-013.md`:** Koreksi `Informasi yang ditahan` Adegan 2 agar menghormati fakta kanon Bab 6 (Salma sudah tahu nama `Rudianto` pada kuitansi 2012–2018) dan tambahkan `Dimas` pada `Tokoh hadir` Adegan 1.
3. **Perbaiki `AUD-03` (`HIGH`) pada `blueprint/chapter-014.md`:** Selaraskan `Jembatan menuju bab berikutnya` agar mengarah ke pertemuan Salma–Yuni di Bab 15.
4. **Perbaiki `AUD-04` (`MEDIUM`) pada `blueprint/chapter-008.md` dan `blueprint/chapter-011.md`:** Standarkan baris `Tokoh hadir` (`Bu Rukmini` dan `Niken`) agar `agent context 8` dan `agent context 11` menginjeksi profil karakter yang tepat ke Bagian 4A.
5. **Selaraskan `AUD-06` dan `AUD-07` (`MEDIUM`) pada `blueprint/chapter-009.md`, `chapter-010.md`, dan `chapter-012.md`:** Cantumkan nama kolom kanon Bab 1 (*Pemeriksa dan Pengantar Permohonan — Lingkungan Hidup Kelurahan*) pada Bab 9–10 dan perhalus jembatan Bab 12 → Bab 13 agar tetap membedakan *ketiadaan catatan* dengan *ketiadaan tindakan*.
6. **Validasi ulang melalui Python Agent Interface:** Jalankan `agent context 7` s.d. `agent context 14` setelah perbaikan blueprint untuk memastikan seluruh `present_profiles` akurat, lalu baru mulai penulisan Bab 7 secara berurutan.
