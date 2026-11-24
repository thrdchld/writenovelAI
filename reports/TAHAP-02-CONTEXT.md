# LAPORAN AUDIT PAKET KONTEKS BAB 1 (TAHAP 2)

- **Proyek:** `gang-yang-hilang-dari-peta`
- **Target Bab:** Bab 001 (*Garis Merah di Atas Peta*)
- **Perintah Eksekusi:** `python3 novel.py --story gang-yang-hilang-dari-peta context 1`
- **Berkas Hasil Aktual:** `stories/gang-yang-hilang-dari-peta/workbench/context-chapter-001.md`
- **Salinan Arsip Laporan:** `reports/TAHAP-02-CONTEXT-B1.md`
- **Tanggal Pengujian:** 24 November 2026

---

## 1. Ukuran Paket Konteks

Berdasarkan penghitungan aktual pada berkas hasil kompilasi Python:
- **Jumlah Karakter:** **52.699 karakter**
- **Jumlah Baris:** **772 baris**
- **Jumlah Kata:** **7.263 kata**
- **Ukuran Berkas:** **52.773 bytes (~51,5 KB)**
- **Estimasi Token:** **~11.000 – 13.000 token** (berdasarkan rasio tokenisasi teks bahasa Indonesia campuran format Markdown).

---

## 2. Berkas yang Dimasukkan

Generator `build_context` di `novel_engine/project.py` menggabungkan total **13 berkas sumber** ke dalam satu dokumen linear:

| No | Sumber Berkas | Bagian dalam Paket | Kategori |
|---|---|---|---|
| 1 | `AI_INSTRUCTIONS.md` | `## Instruksi AI` | Pedoman Operasional AI Umum |
| 2 | `docs/02-scene-blueprint.md` | `## Panduan blueprint adegan` | Metodologi Perancangan Blueprint |
| 3 | `docs/03-continuity.md` | `## Panduan kontinuitas` | Metodologi Kontinuitas & State |
| 4 | `docs/05-writing-standard.md` | `## Standar prosa` | Pedoman Penulisan Prosa |
| 5 | `docs/06-ai-operating-contract.md` | `## Kontrak kerja` | Kontrak Kerja & Quality Gate |
| 6 | `stories/gang-yang-hilang-dari-peta/README.md` | `## README proyek` | Dashboard & Status Proyek |
| 7 | `stories/gang-yang-hilang-dari-peta/00-premise.md` | `## SOURCE: .../00-premise.md` | Memori Proyek: Premis |
| 8 | `stories/gang-yang-hilang-dari-peta/01-concept.md` | `## SOURCE: .../01-concept.md` | Memori Proyek: Konsep Cerita |
| 9 | `stories/gang-yang-hilang-dari-peta/02-characters.md` | `## SOURCE: .../02-characters.md` | Memori Proyek: Lembar Karakter |
| 10 | `stories/gang-yang-hilang-dari-peta/03-world-and-rules.md` | `## SOURCE: .../03-world-and-rules.md` | Memori Proyek: Dunia & Aturan |
| 11 | `stories/gang-yang-hilang-dari-peta/04-story-outline.md` | `## SOURCE: .../04-story-outline.md` | Memori Proyek: Outline 30 Bab |
| 12 | `stories/gang-yang-hilang-dari-peta/05-decision-log.md` | `## SOURCE: .../05-decision-log.md` | Memori Proyek: Decision Log |
| 13 | `stories/gang-yang-hilang-dari-peta/blueprint/chapter-001.md` | `## BLUEPRINT BAB 1` | Blueprint Target Bab 1 |

*(Catatan: Seksi `## NASKAH BAB SEBELUMNYA` tidak muncul karena Bab 1 merupakan bab pertama).*

---

## 3. Relevansi Isi Konteks untuk Penulisan Bab 1

Dari total 13 berkas yang disuntikkan, dilakukan pemisahan antara materi yang esensial dengan materi yang redundan:

### A. Sangat Relevan (Esensial untuk Eksekusi Bab 1)
- **`blueprint/chapter-001.md`:** Menjadi kompas utama adegan (Adegan 1 di ruang rapat bersama koordinator proyek dan Dito; Adegan 2 penemuan nama Hadi pada lampiran dokumen 2011).
- **`02-characters.md` (bagian Salma dan Dito):** Memberikan profil psikologis, kebiasaan, dan pola relasi dua tokoh yang hadir secara fisik di Bab 1.
- **`03-world-and-rules.md`:** Menetapkan batasan teknis dunia cerita (kewenangan teknisi pemetaan vs pengesahan hak tanah, mekanisme proyek drainase, dan batas prosedur konsultan).
- **`00-premise.md` & `01-concept.md`:** Memberikan kompas tone *in medias res*, orientasi waktu 17 Agustus 2026, dan premis utama.
- **`docs/05-writing-standard.md`:** Memberikan batasan gaya narasi, dialog alami, ritme adegan, dan larangan pola klise AI.

### B. Kurang Relevan / Redundan (Membebani Konteks Tanpa Fungsi Langsung)
- **`AI_INSTRUCTIONS.md`:** Memuat instruksi command-line CLI, mode kerja ARCHITECT/LIBRARIAN, petunjuk push Git, dan konfigurasi GitHub Actions. Informasi ini relevan untuk agen orchestrator, tetapi tidak relevan bagi AI yang sedang bertugas menulis prosa adegan.
- **`docs/02-scene-blueprint.md` & `docs/03-continuity.md`:** Panduan tentang *cara menyusun blueprint* dan *cara mengelola kontinuitas lintas bab*. Karena blueprint Bab 1 sudah selesai dan bab sebelumnya belum ada, teori penyusunan ini memakan ribuan karakter tanpa faedah langsung bagi penulisan prosa.
- **`docs/06-ai-operating-contract.md`:** Menjelaskan pembagian fase kerja, kriteria acceptance, dan quality gates.
- **`README.md` proyek:** Berisi tabel checklist draf dan tautan navigasi markdown.
- **Tokoh non-hadir di `02-characters.md`:** Profil mendalam Yuni, Sari, Dimas, Pak Bowo, dan Niken belum berinteraksi di Bab 1.

---

## 4. Evaluasi Kebocoran Masa Depan & Penyelesaian Misteri

### Temuan Fakta
Paket konteks Bab 1 memuat **seluruh rahasia, plot twist, dan resolusi akhir novel secara terbuka**:

1. **Pengungkapan Motif Hadi (Rahasia Utama 2011):**
   - Di `01-concept.md` dan `05-decision-log.md` (D-001), tertulis gamblang bahwa Hadi menandatangani pencatatan sementara untuk menunda pengosongan demi menolong warga pasca-banjir tanpa menerima suap, namun ia lalai tidak menindaklanjutinya.
2. **Pengungkapan Rangkaian Sebab-Akibat 30 Bab:**
   - Di `04-story-outline.md` bagian `## Rangkaian sebab-akibat`, tertera ringkasan plot butir 1 sampai 10, termasuk peran Yuni yang ikut diam (D-003), hasil penelusuran buku agenda Niken, buku catatan Hadi, hingga resolusi akhir di Bab 30.
3. **Tabel Sinopsis Bab 2 sampai Bab 30:**
   - AI penulis diberikan ringkasan kejadian seluruh bab mendatang (Bab 10 "Tanda Tangan Ayah", Bab 21 "Buku Ayah", Bab 26 "Apa yang Ditinggalkan Ayah").

### Analisis Dampak
Bab 1 dirancang sebagai pembuka *in medias res* di mana:
- Salma **hanya melihat nama ayahnya** di kolom pengesahan dan **belum tahu apa pun** mengenai motif atau latar belakang peristiwa 2011.
- Blueprint Bab 1 secara tegas menyatakan: *"Informasi yang ditahan: Isi dan motif perubahan 2011"* dan *"Ruang pengembangan prosa: Jangan ungkap motif ayah pada pembuka."*

Adanya seluruh spoiler di dalam konteks menciptakan **risiko kontaminasi naratif yang tinggi**:
- AI penulis berisiko menyelipkan monolog batin, nada kecurigaan yang terlalu spesifik, atau pilihan kata yang mengarahkan pembaca sebelum waktunya.
- Karakter Salma berisiko kehilangan ketegangan emosional murni seorang anak yang tiba-tiba menemukan nama ayahnya di dokumen bermasalah.

---

## 5. Pemeriksaan Konsistensi Antar-Sumber

Secara umum, sumber-sumber inti (`00` s.d. `05` dan `blueprint`) saling mengunci dengan baik, namun terdapat catatan sinkronisasi:

1. **Penataan Adegan Rapat Bab 1 vs Bab 18:**
   - Di `01-concept.md:7`: Cerita dibuka 17 Agustus 2026 pada rapat penolakan peta; Bab 2–18 bergerak maju sampai kembali ke hari rapat tersebut; Bab 19 melanjutkan sesudah penolakan.
   - Di `blueprint/chapter-001.md`: Bab 1 sudah menyelesaikan rapat (Adegan 1 Salma menolak, koordinator keluar) dan Adegan 2 (14.20–14.35) menunjukkan Salma berdiskusi berdua dengan Dito setelah rapat selesai.
   - Di `04-story-outline.md`: Bab 18 (17 Agustus 13.45) bertajuk *Rapat yang Tertunda* dengan deskripsi *"Rapat yang telah dibuka di bab 1 berlangsung"*.
   - *Catatan:* Outline sendiri mencatat pertanyaan audit: *"Apakah bab 18 mengulang terlalu banyak adegan bab 1?"*. Struktur Bab 1 dan Bab 18 membutuhkan kehati-hatian agar Bab 18 tidak menjadi repetisi hampa dari Adegan 1 Bab 1.
2. **Ketiadaan Entri Tokoh "Koordinator Proyek":**
   - Tokoh antagonis prosedural di Adegan 1 adalah "koordinator proyek". Tokoh ini tidak terdaftar di `02-characters.md`. Hal ini tidak fatal karena statusnya adalah peran fungsional kantor, namun nama atau panggilannya belum dibakukan.

---

## 6. Kelengkapan Informasi bagi Penulis Prosa

Informasi yang dibutuhkan untuk menulis Bab 1 secara umum sudah tersedia, dengan sedikit ruang detail yang dibiarkan terbuka:

1. **Nama Lembaga / Perusahaan Konsultan:**
   - Belum memiliki nama spesifik (hanya disebut "kantor konsultan infrastruktur"). Sesuai `05-decision-log.md`, hal ini fleksibel dan diizinkan untuk ditetapkan saat penulisan.
2. **Nama Koordinator Proyek:**
   - Belum diberi nama diri, sehingga penulis bebas memberikan nama formal (misalnya Pak Hendra, Pak Aris, dsb.).
3. **Format Fisik Peta Segmen Gang Kenari:**
   - Belum dispesifikasikan apakah berupa cetakan lembar kerja A0/A1 di atas meja rapat atau tampilan digital CAD/GIS di layar proyektor. Penulis memiliki kebebasan menentukan mise-en-scène adegan.

---

## 7. Batas Pengetahuan Tokoh POV (Salma) pada Bab 1

Batas pengetahuan Salma pada Bab 1 **terdefinisi dengan sangat tajam dan jelas** pada `blueprint/chapter-001.md`:

- **Yang Diketahui Salma:**
  - Mengetahui bahwa hasil survei lapangannya membuktikan adanya 3 bangunan dan lorong akses aktif selebar ~1,2 meter di balik tembok.
  - Mengetahui bahwa peta final yang disodorkan koordinator keliru karena menggambarkan area tersebut sebagai lahan kosong tak berpenghuni.
  - Mengetahui nama Hadi tertera pada kolom tanda tangan lampiran berkas pembaruan wilayah tahun 2011.
  - Mengetahui bahwa Hadi adalah almarhum ayahnya (meninggal 2022) yang dulu menjabat sekretaris lingkungan.
- **Yang TIDAK Diketahui Salma (Ketat Ditahan):**
  - Tidak tahu apa alasan Hadi menandatangani berkas tersebut.
  - Tidak tahu apakah Hadi ditekan, disuap, atau berinisiatif sendiri.
  - Tidak tahu bahwa status "bangunan penyimpanan sementara" dibuat untuk melindungi warga dari pengosongan pasca-banjir.
  - Tidak tahu bahwa ibunya (Yuni) mengetahui rahasia janji 6 bulan tersebut.

---

## 8. Ruang Kreativitas AI dalam Mengembangkan Prosa

Konteks Bab 1 memberikan **keseimbangan yang sangat baik** antara batas struktural dan kebebasan sastra:

1. **Batas Struktural yang Terkunci Aman:**
   - Fungsi bab tidak boleh digeser (Salma menolak mengesahkan peta $\rightarrow$ rapat ditunda $\rightarrow$ Salma menemukan nama ayahnya di lampiran 2011).
   - Salma tidak boleh diberi kewenangan fiktif (ia teknisi pemetaan kontrak, bukan pengambil keputusan proyek dan bukan penentu status kepemilikan tanah).
   - Hasil bab tidak boleh dramatisasi palsu (tidak ada konspirasi pembunuhan, suap jutaan rupiah, atau pengakuan histeris).
2. **Ruang Prosa yang Terbuka Lebar:**
   - **Dialog Rapat:** Kebebasan menyusun tensi percakapan profesional antara desakan koordinator yang terikat tenggat dengan keteguhan teknis Salma.
   - **Dinamika Karakter Dito:** Dito dapat digambarkan sebagai rekan kerja yang suportif namun berhati-hati terhadap prosedur kantor.
   - **Sensori & Atmosfer:** Ruang rapat konsultan pendingin udara yang dingin, aroma kertas berkas lama tahun 2011, kontras antara garis merah di atas kertas putih dan ingatan fisik lorong sempit yang disurvei Salma.

---

## 9. Rekomendasi Perbaikan Sistem Konteks

Berdasarkan fakta hasil audit, berikut rekomendasi untuk penyempurnaan generator konteks ke depan:

1. **Pemangkasan Dokumen Panduan Metodologi pada Paket Konteks:**
   - Keluarkan `docs/02-scene-blueprint.md`, `docs/03-continuity.md`, dan `docs/06-ai-operating-contract.md` dari fungsi `build_context()`.
   - Cukup sertakan `AI_INSTRUCTIONS.md` (atau ringkasan khusus writer) dan `docs/05-writing-standard.md` agar konteks hemat ~15.000 karakter.
2. **Penyaringan Outline Masa Depan (*Outline Scoping*):**
   - Saat menyusun paket konteks Bab $N$, jangan masukkan rincian bab $N+1$ sampai 30 serta penyelesaian misteri di `05-decision-log.md`.
   - Cukup berikan: Premis, Konsep Umum, Dunia/Aturan, Profil Tokoh yang relevan, Blueprint Bab $N$, dan naskah Bab $N-1$.
3. **Pemberian Nama Baku untuk Koordinator Proyek:**
   - Tambahkan profil singkat 2 baris mengenai koordinator proyek di `02-characters.md` atau catatan blueprint Bab 1 agar konsisten di seluruh bab kantor.
